from flask import Blueprint, request, jsonify
import requests
from config import Config
from database import db
from models.chat import ChatConversation, ChatMessage
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

def call_ollama(message, model=None):
    """Call Ollama API"""
    model = model or Config.OLLAMA_MODEL
    response = requests.post(
        f'{Config.OLLAMA_BASE_URL}/api/generate',
        json={
            'model': model,
            'prompt': message,
            'stream': False
        },
        timeout=120
    )
    if response.status_code == 200:
        result = response.json()
        return result.get('response', '')
    else:
        raise Exception('Ollama service error')

def call_openai(message, model=None):
    """Call OpenAI API"""
    if not Config.OPENAI_API_KEY:
        raise Exception('OpenAI API key not configured')

    import openai
    openai.api_key = Config.OPENAI_API_KEY
    model = model or Config.OPENAI_MODEL

    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": message}]
    )
    return response.choices[0].message.content

def call_anthropic(message, model=None):
    """Call Anthropic API"""
    if not Config.ANTHROPIC_API_KEY:
        raise Exception('Anthropic API key not configured')

    import anthropic
    client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    model = model or Config.ANTHROPIC_MODEL

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": message}]
    )
    return response.content[0].text

@bp.route('/chat', methods=['POST'])
def chat():
    """LLM chat endpoint with multi-provider support"""
    data = request.get_json()
    user_message = data.get('message', '')
    provider = data.get('provider', 'ollama')
    model = data.get('model', None)
    conversation_id = data.get('conversation_id', None)

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    try:
        # Get or create conversation
        if conversation_id:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation:
                return jsonify({'error': 'Conversation not found'}), 404
        else:
            # Create new conversation
            conversation = ChatConversation(
                title=user_message[:50] + ('...' if len(user_message) > 50 else ''),
                provider=provider,
                model=model or f'{provider}_default'
            )
            db.session.add(conversation)
            db.session.flush()

        # Save user message
        user_msg = ChatMessage(
            conversation_id=conversation.id,
            role='user',
            content=user_message
        )
        db.session.add(user_msg)

        # Call appropriate LLM provider
        if provider == 'ollama':
            ai_response = call_ollama(user_message, model)
        elif provider == 'openai':
            ai_response = call_openai(user_message, model)
        elif provider == 'anthropic':
            ai_response = call_anthropic(user_message, model)
        else:
            return jsonify({'error': f'Unknown provider: {provider}'}), 400

        # Save assistant message
        assistant_msg = ChatMessage(
            conversation_id=conversation.id,
            role='assistant',
            content=ai_response
        )
        db.session.add(assistant_msg)

        # Update conversation timestamp
        conversation.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'response': ai_response,
            'conversation_id': conversation.id
        })

    except requests.exceptions.ConnectionError:
        db.session.rollback()
        return jsonify({'error': 'Cannot connect to Ollama. Make sure it is running.'}), 503
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Chat history management endpoints
@bp.route('/chat/conversations', methods=['GET'])
def get_conversations():
    """Get all chat conversations"""
    conversations = ChatConversation.query.order_by(ChatConversation.updated_at.desc()).all()
    return jsonify([conv.to_dict() for conv in conversations])


@bp.route('/chat/conversations/<int:conversation_id>', methods=['GET'])
def get_conversation(conversation_id):
    """Get a specific conversation with all messages"""
    conversation = ChatConversation.query.get_or_404(conversation_id)
    messages = ChatMessage.query.filter_by(conversation_id=conversation_id).order_by(ChatMessage.created_at).all()

    return jsonify({
        'conversation': conversation.to_dict(),
        'messages': [msg.to_dict() for msg in messages]
    })


@bp.route('/chat/conversations/<int:conversation_id>', methods=['DELETE'])
def delete_conversation(conversation_id):
    """Delete a conversation"""
    conversation = ChatConversation.query.get_or_404(conversation_id)
    db.session.delete(conversation)
    db.session.commit()
    return jsonify({'message': 'Conversation deleted successfully'})


@bp.route('/chat/conversations/<int:conversation_id>/rename', methods=['POST'])
def rename_conversation(conversation_id):
    """Rename a conversation"""
    data = request.get_json()
    new_title = data.get('title', '')

    if not new_title:
        return jsonify({'error': 'Title is required'}), 400

    conversation = ChatConversation.query.get_or_404(conversation_id)
    conversation.title = new_title
    conversation.updated_at = datetime.utcnow()
    db.session.commit()

    return jsonify({'message': 'Conversation renamed successfully', 'conversation': conversation.to_dict()})


@bp.route('/foods/search', methods=['GET'])
def search_foods():
    """API endpoint for food search"""
    from models.food import Food

    query = request.args.get('q', '')
    foods = Food.query.filter(Food.name.ilike(f'%{query}%')).limit(20).all()

    return jsonify([food.to_dict() for food in foods])


@bp.route('/foods/quick-add', methods=['POST'])
def quick_add_food():
    """Quick add food from recipe creation form"""
    from models.food import Food

    try:
        data = request.get_json()

        # Create new food with provided data
        new_food = Food(
            name=data.get('name'),
            category=data.get('category', 'Other'),
            fructans=data.get('fructans', 'Green'),
            gos=data.get('gos', 'Green'),
            lactose=data.get('lactose', 'Green'),
            fructose=data.get('fructose', 'Green'),
            polyols=data.get('polyols', 'Green'),
            mannitol=data.get('mannitol', 'Green'),
            sorbitol=data.get('sorbitol', 'Green'),
            histamine_level=data.get('histamine_level', 'Low'),
            histamine_liberator=data.get('histamine_liberator', 'No'),
            dao_blocker=data.get('dao_blocker', 'No'),
            safe_serving=data.get('safe_serving', ''),
            moderate_serving=data.get('moderate_serving', ''),
            high_serving=data.get('high_serving', ''),
            preparation_notes=data.get('notes', '')
        )

        db.session.add(new_food)
        db.session.commit()

        return jsonify({
            'success': True,
            'food': {
                'id': new_food.id,
                'name': new_food.name,
                'category': new_food.category,
                'fructans': new_food.fructans,
                'gos': new_food.gos,
                'lactose': new_food.lactose,
                'fructose': new_food.fructose,
                'polyols': new_food.polyols,
                'mannitol': new_food.mannitol,
                'sorbitol': new_food.sorbitol,
                'histamine_level': new_food.histamine_level,
                'safe_serving': new_food.safe_serving
            }
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 400
