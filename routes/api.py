from flask import Blueprint, request, jsonify
import requests
from config import Config
from database import db
from models.chat import ChatConversation, ChatMessage
from models.recipe import Recipe, RecipeIngredient
from datetime import datetime

bp = Blueprint('api', __name__, url_prefix='/api')

def get_persona_prompt(persona):
    """Get the system prompt for a specific persona"""
    personas = {
        'nutritionist': """You are a helpful nutritionist and gut health expert. You specialize in:
- FODMAP diet guidance and low-FODMAP meal planning
- Identifying food triggers for digestive issues
- Creating gut-friendly recipes and meal ideas
- Understanding histamine intolerance and histamine-friendly foods
- Providing evidence-based nutrition advice for digestive health

Always be supportive, informative, and practical in your responses. Focus on actionable advice.""",

        'chef': """You are a creative chef specializing in gut-friendly cuisine. You excel at:
- Creating delicious recipes that are gentle on the digestive system
- Adapting traditional recipes to be low-FODMAP and low-histamine
- Suggesting flavor combinations and cooking techniques
- Providing meal prep tips and kitchen hacks
- Making healthy eating enjoyable and accessible

Be enthusiastic, creative, and always consider taste as well as health.""",

        'scientist': """You are a digestive health researcher and scientist. Your expertise includes:
- The science behind FODMAPs and their effects on the gut
- Histamine metabolism and intolerance mechanisms
- Evidence-based research on digestive disorders
- Gut microbiome and its role in health
- Clinical studies and nutritional science

Provide detailed, scientifically accurate information with references to research when relevant.""",

        'friendly': """You are a supportive friend who happens to know a lot about gut health. You are:
- Encouraging and empathetic about digestive struggles
- Easy to talk to and approachable
- Knowledgeable about FODMAPs and gut-friendly eating
- Practical and down-to-earth in your advice
- Understanding that managing digestive issues can be challenging

Be warm, conversational, and supportive while providing helpful information."""
    }

    return personas.get(persona, personas['nutritionist'])

def call_ollama(messages, model=None, persona='nutritionist', recipe_context=''):
    """Call Ollama API with conversation history using chat endpoint"""
    model = model or Config.OLLAMA_MODEL

    # Get persona system prompt and append recipe context if provided
    system_prompt = get_persona_prompt(persona)
    if recipe_context:
        system_prompt += recipe_context

    # Limit conversation history to last 10 messages to prevent context explosion
    # This prevents timeouts on long conversations
    max_history = 10
    if len(messages) > max_history:
        messages = messages[-max_history:]

    # Build message list for Ollama chat API
    chat_messages = [{"role": "system", "content": system_prompt}]

    for msg in messages:
        chat_messages.append({
            "role": msg.role,
            "content": msg.content
        })

    # Use chat endpoint instead of generate for better conversation handling
    try:
        response = requests.post(
            f'{Config.OLLAMA_BASE_URL}/api/chat',
            json={
                'model': model,
                'messages': chat_messages,
                'stream': False
            },
            timeout=300  # Increased timeout to 5 minutes for longer responses
        )
        response.raise_for_status()  # Raise exception for bad status codes

        result = response.json()
        # Handle both chat endpoint response format
        if 'message' in result:
            content = result['message'].get('content', '')
        elif 'response' in result:
            # Fallback to generate endpoint format
            content = result['response']
        else:
            raise Exception('Invalid response format from Ollama')

        if not content:
            raise Exception('Empty response from Ollama')

        return content

    except requests.exceptions.HTTPError as e:
        raise Exception(f'Ollama HTTP error {response.status_code}: {response.text}')

def call_openai(message, model=None, persona='nutritionist', recipe_context=''):
    """Call OpenAI API"""
    if not Config.OPENAI_API_KEY:
        raise Exception('OpenAI API key not configured')

    import openai
    openai.api_key = Config.OPENAI_API_KEY
    model = model or Config.OPENAI_MODEL

    system_prompt = get_persona_prompt(persona)
    if recipe_context:
        system_prompt += recipe_context

    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content

def call_anthropic(message, model=None, persona='nutritionist', recipe_context=''):
    """Call Anthropic API"""
    if not Config.ANTHROPIC_API_KEY:
        raise Exception('Anthropic API key not configured')

    import anthropic
    client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    model = model or Config.ANTHROPIC_MODEL

    system_prompt = get_persona_prompt(persona)
    if recipe_context:
        system_prompt += recipe_context

    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system=system_prompt,
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
    persona = data.get('persona', 'nutritionist')
    conversation_id = data.get('conversation_id', None)
    recipe_ids = data.get('recipe_ids', [])  # List of recipe IDs to include as context

    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    # Build recipe context if recipes are selected
    recipe_context = format_recipe_context(recipe_ids) if recipe_ids else ""

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
                model=model or f'{provider}_default',
                persona=persona
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

        # Get conversation history for context
        if conversation_id:
            # Get previous messages for context
            previous_messages = ChatMessage.query.filter_by(
                conversation_id=conversation.id
            ).order_by(ChatMessage.created_at).all()
        else:
            previous_messages = []

        # Add current user message to the list
        all_messages = previous_messages + [user_msg]

        # Call appropriate LLM provider with persona and recipe context
        current_persona = conversation.persona or persona
        if provider == 'ollama':
            ai_response = call_ollama(all_messages, model, current_persona, recipe_context)
        elif provider == 'openai':
            ai_response = call_openai(user_message, model, current_persona, recipe_context)
        elif provider == 'anthropic':
            ai_response = call_anthropic(user_message, model, current_persona, recipe_context)
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
    except requests.exceptions.Timeout:
        db.session.rollback()
        return jsonify({'error': 'Request timed out. The model may be taking too long to respond. Try a simpler question or use a faster model.'}), 504
    except requests.exceptions.RequestException as e:
        db.session.rollback()
        return jsonify({'error': f'Network error: {str(e)}'}), 503
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
    try:
        conversation = ChatConversation.query.get_or_404(conversation_id)
        db.session.delete(conversation)
        db.session.commit()
        return jsonify({'message': 'Conversation deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/chat/conversations/<int:conversation_id>/rename', methods=['POST'])
def rename_conversation(conversation_id):
    """Rename a conversation"""
    data = request.get_json()
    new_title = data.get('title', '')

    if not new_title:
        return jsonify({'error': 'Title is required'}), 400

    try:
        conversation = ChatConversation.query.get_or_404(conversation_id)
        conversation.title = new_title
        conversation.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'message': 'Conversation renamed successfully', 'conversation': conversation.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


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
        # Mark as incomplete since quick-add only captures minimal information
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
            preparation_notes=data.get('notes', ''),
            is_complete=False  # Quick-added foods need more information
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


# Recipe context for chat
@bp.route('/recipes/search', methods=['GET'])
def search_recipes():
    """Search recipes by name for autocomplete"""
    query = request.args.get('q', '')
    limit = request.args.get('limit', 10, type=int)

    recipes = Recipe.query.filter(
        Recipe.name.ilike(f'%{query}%')
    ).order_by(Recipe.name).limit(limit).all()

    return jsonify([{
        'id': r.id,
        'name': r.name,
        'category': r.category or '',
        'servings': r.servings,
        'ingredient_count': len(r.ingredients)
    } for r in recipes])


@bp.route('/recipes/<int:recipe_id>/context', methods=['GET'])
def get_recipe_context(recipe_id):
    """Get full recipe details formatted for AI context"""
    recipe = Recipe.query.get_or_404(recipe_id)

    # Get ingredients with food details
    ingredients_list = []
    for ing in recipe.ingredients:
        food_name = ing.food.name if ing.food else 'Unknown'
        quantity = ing.quantity or ''
        notes = ing.notes or ''
        ingredient_str = f"{quantity} {food_name}".strip()
        if notes:
            ingredient_str += f" ({notes})"
        ingredients_list.append(ingredient_str)

    return jsonify({
        'id': recipe.id,
        'name': recipe.name,
        'description': recipe.description or '',
        'category': recipe.category or '',
        'cuisine': recipe.cuisine or '',
        'servings': recipe.servings,
        'prep_time': recipe.prep_time or '',
        'cook_time': recipe.cook_time or '',
        'ingredients': ingredients_list,
        'instructions': recipe.instructions or '',
        'notes': recipe.notes or '',
        'dietary_needs': recipe.dietary_needs or '',
        'difficulty': recipe.difficulty or ''
    })


def format_recipe_context(recipe_ids):
    """Format multiple recipes into a context string for the AI"""
    if not recipe_ids:
        return ""

    recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
    if not recipes:
        return ""

    context_parts = ["\n\n--- USER'S SAVED RECIPES FOR REFERENCE ---\n"]

    for recipe in recipes:
        # Build ingredient list
        ingredients_list = []
        for ing in recipe.ingredients:
            food_name = ing.food.name if ing.food else 'Unknown'
            quantity = ing.quantity or ''
            notes = ing.notes or ''
            ingredient_str = f"- {quantity} {food_name}".strip()
            if notes:
                ingredient_str += f" ({notes})"
            ingredients_list.append(ingredient_str)

        recipe_text = f"""
### {recipe.name}
"""
        if recipe.description:
            recipe_text += f"Description: {recipe.description}\n"
        if recipe.category:
            recipe_text += f"Category: {recipe.category}\n"
        if recipe.cuisine:
            recipe_text += f"Cuisine: {recipe.cuisine}\n"
        if recipe.servings:
            recipe_text += f"Servings: {recipe.servings}\n"
        if recipe.prep_time:
            recipe_text += f"Prep Time: {recipe.prep_time}\n"
        if recipe.cook_time:
            recipe_text += f"Cook Time: {recipe.cook_time}\n"

        recipe_text += "\nIngredients:\n"
        recipe_text += "\n".join(ingredients_list) if ingredients_list else "- No ingredients listed"

        if recipe.instructions:
            recipe_text += f"\n\nInstructions:\n{recipe.instructions}"

        if recipe.notes:
            recipe_text += f"\n\nNotes: {recipe.notes}"

        context_parts.append(recipe_text)

    context_parts.append("\n--- END OF SAVED RECIPES ---\n")
    return "\n".join(context_parts)
