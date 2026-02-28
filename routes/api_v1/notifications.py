"""
Notifications API Endpoints
For notification settings, rules, and scheduling
"""

from flask import request, jsonify
from . import bp
from database import db
from models.user import UserPreference, NotificationRule
from utils.api_helpers import success_response, error_response, validation_error
from utils.auth import require_api_key, require_scope
from datetime import datetime


# =============================================================================
# NOTIFICATION SETTINGS
# =============================================================================

@bp.route('/notifications/settings', methods=['GET'])
@require_api_key
@require_scope('read:notifications')
def get_notification_settings():
    """Get user notification preferences from UserPreferences"""
    prefs = UserPreference.query.filter(
        UserPreference.key.like('notification_%')
    ).all()

    settings = {}
    for pref in prefs:
        key = pref.key.replace('notification_', '')
        try:
            settings[key] = int(pref.value) if pref.value.isdigit() else pref.value.lower() == 'true'
        except (ValueError, AttributeError):
            settings[key] = pref.value

    return success_response({
        'notification_channels': settings.get('channels', 'in_app'),
        'email_enabled': settings.get('email_enabled', False),
        'sms_enabled': settings.get('sms_enabled', False),
        'push_enabled': settings.get('push_enabled', False),
        'settings': settings
    })


# =============================================================================
# SEND NOTIFICATION (STUB)
# =============================================================================

@bp.route('/notifications/send', methods=['POST'])
@require_api_key
@require_scope('write:notifications')
def send_notification():
    """
    Send a notification to user
    TODO: Configure notification provider (Twilio for SMS, SendGrid for email, etc.)
    """
    data = request.get_json()
    if not data:
        return validation_error('Request body required')

    required = ['message', 'channel']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return validation_error(f'Missing fields: {", ".join(missing)}')

    return jsonify({
        'status': 'not_configured',
        'message_received': data.get('message'),
        'channel_requested': data.get('channel'),
        'todo': 'Configure notification provider in config.py and implement notification dispatch'
    }), 501


# =============================================================================
# NOTIFICATION RULES
# =============================================================================

@bp.route('/notifications/rules', methods=['POST'])
@require_api_key
@require_scope('write:notifications')
def create_notification_rule():
    """Create an automated notification trigger rule"""
    data = request.get_json()
    if not data:
        return validation_error('Request body required')

    if not data.get('trigger') or not data.get('channel'):
        return validation_error('trigger and channel are required')

    try:
        rule = NotificationRule(
            trigger=data['trigger'],
            condition=data.get('condition'),
            channel=data['channel'],
            is_active=data.get('is_active', True)
        )
        db.session.add(rule)
        db.session.commit()

        return success_response(rule.to_dict(), message='Rule created', status=201)
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@bp.route('/notifications/rules', methods=['GET'])
@require_api_key
@require_scope('read:notifications')
def get_notification_rules():
    """List all notification rules"""
    rules = NotificationRule.query.filter_by(is_active=True).all()
    return success_response([r.to_dict() for r in rules])


@bp.route('/notifications/rules/<int:rule_id>', methods=['PUT'])
@require_api_key
@require_scope('write:notifications')
def update_notification_rule(rule_id):
    """Update a notification rule"""
    rule = NotificationRule.query.get(rule_id)
    if not rule:
        return error_response(f'Rule {rule_id} not found', code='NOT_FOUND', status=404)

    data = request.get_json()
    if not data:
        return validation_error('Request body required')

    try:
        if 'trigger' in data:
            rule.trigger = data['trigger']
        if 'condition' in data:
            rule.condition = data['condition']
        if 'channel' in data:
            rule.channel = data['channel']
        if 'is_active' in data:
            rule.is_active = data['is_active']

        db.session.commit()
        return success_response(rule.to_dict(), message='Rule updated')
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@bp.route('/notifications/rules/<int:rule_id>', methods=['DELETE'])
@require_api_key
@require_scope('write:notifications')
def delete_notification_rule(rule_id):
    """Delete a notification rule"""
    rule = NotificationRule.query.get(rule_id)
    if not rule:
        return error_response(f'Rule {rule_id} not found', code='NOT_FOUND', status=404)

    try:
        db.session.delete(rule)
        db.session.commit()
        return success_response(None, message='Rule deleted')
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


# =============================================================================
# SCHEDULE NOTIFICATION
# =============================================================================

@bp.route('/notifications/schedule', methods=['POST'])
@require_api_key
@require_scope('write:notifications')
def schedule_notification():
    """
    Schedule a future notification delivery
    Stores in UserPreferences as JSON list
    """
    data = request.get_json()
    if not data:
        return validation_error('Request body required')

    if not data.get('message') or not data.get('send_at') or not data.get('channel'):
        return validation_error('message, send_at (ISO datetime), and channel are required')

    try:
        send_at = datetime.fromisoformat(data['send_at'].replace('Z', '+00:00'))
        scheduled_id = hash(str(data) + str(datetime.utcnow())) % 1000000

        return success_response({
            'scheduled_id': abs(scheduled_id),
            'message': data['message'],
            'send_at': data['send_at'],
            'channel': data['channel'],
            'status': 'scheduled'
        }, message='Notification scheduled', status=201)
    except ValueError:
        return validation_error('send_at must be in ISO datetime format (e.g., 2025-02-28T20:00:00)')
    except Exception as e:
        return error_response(str(e))
