"""
Gamification API Endpoints
For challenges, badges, and engagement tracking
"""

from flask import jsonify
from . import bp
from database import db
from models.gamification import Challenge, Badge
from utils.api_helpers import success_response, error_response
from utils.auth import require_api_key, require_scope


@bp.route('/gamification/challenges', methods=['GET'])
@require_api_key
@require_scope('read:gamification')
def get_challenges():
    """
    Get all active challenges with current progress
    Progress is computed from diary data where available
    """
    challenges = Challenge.query.filter_by(is_active=True).order_by(Challenge.created_at.desc()).all()

    return success_response({
        'challenges': [c.to_dict() for c in challenges],
        'total_count': len(challenges),
        'active_count': sum(1 for c in challenges if c.is_active),
        'completed_count': sum(1 for c in challenges if c.completed)
    })


@bp.route('/gamification/challenges', methods=['POST'])
@require_api_key
@require_scope('write:gamification')
def create_challenge():
    """Create a new challenge (admin endpoint)"""
    from flask import request
    data = request.get_json()
    if not data:
        return error_response('Request body required', status=400)

    if not data.get('title') or not data.get('type') or not data.get('target'):
        return error_response('title, type, and target are required', status=400)

    try:
        from datetime import date, timedelta
        challenge = Challenge(
            title=data['title'],
            description=data.get('description'),
            type=data['type'],
            target=data['target'],
            start_date=date.today(),
            end_date=date.today() + timedelta(days=data.get('duration_days', 7))
        )
        db.session.add(challenge)
        db.session.commit()
        return success_response(challenge.to_dict(), message='Challenge created', status=201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@bp.route('/gamification/badges', methods=['GET'])
@require_api_key
@require_scope('read:gamification')
def get_badges():
    """Get all earned badges with date earned"""
    badges = Badge.query.order_by(Badge.earned_at.desc()).all()

    return success_response({
        'badges': [b.to_dict() for b in badges],
        'total_earned': len(badges),
        'by_challenge': {}  # Grouped by challenge if desired
    })
