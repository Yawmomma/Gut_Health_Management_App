"""
Integrations API Endpoints
Wearables, voice logging, and external integrations
"""

from flask import request, jsonify
from . import bp
from utils.api_helpers import success_response, error_response
from utils.auth import require_api_key, require_scope


# =============================================================================
# WEARABLES
# =============================================================================

@bp.route('/wearables/connect', methods=['POST'])
@require_api_key
@require_scope('write:integrations')
def wearables_connect():
    """
    Connect a wearable device (Fitbit, Apple Watch, Oura Ring)
    TODO: Implement OAuth flow for chosen wearable provider
    """
    return jsonify({
        'status': 'not_configured',
        'supported_devices': ['Fitbit', 'Apple Watch', 'Oura Ring', 'Google Fit'],
        'message': 'Wearable integration not configured',
        'todo': 'Implement OAuth 2.0 flow for chosen wearable provider in config.py'
    }), 501


@bp.route('/wearables/sync', methods=['POST'])
@require_api_key
@require_scope('write:integrations')
def wearables_sync():
    """
    Sync data from connected wearable
    TODO: Implement wearable API data sync
    """
    return jsonify({
        'status': 'not_configured',
        'message': 'No wearable device connected',
        'todo': 'Implement data sync from wearable APIs (Fitbit, Apple HealthKit, etc.)'
    }), 501


# =============================================================================
# VOICE LOGGING
# =============================================================================

@bp.route('/voice/log', methods=['POST'])
@require_api_key
@require_scope('write:integrations')
def voice_log():
    """
    Process voice command into diary entry
    Input: {"transcript": "I had oatmeal with blueberries and felt bloated"}
    TODO: Implement NLP parser to convert transcript to diary entry
    """
    data = request.get_json()
    transcript = data.get('transcript', '') if data else ''

    if not transcript:
        return error_response('transcript is required', status=400)

    return jsonify({
        'status': 'not_configured',
        'transcript_received': True,
        'transcript': transcript,
        'message': 'Voice logging not configured',
        'todo': 'Implement NLP parser to extract meals, symptoms, and notes from transcript. Convert to /diary/entries/bulk call.'
    }), 501
