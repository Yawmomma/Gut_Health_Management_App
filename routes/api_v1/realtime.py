"""
Real-time Updates API v1 Endpoints
Provides Server-Sent Events and Webhook management for real-time notifications
"""

from flask import request, jsonify, Response, current_app
from datetime import datetime, timedelta
import json
import time
import requests
from . import bp
from database import db
from models.webhooks import Webhook, EventLog, ExternalWebhookLog
from utils.auth import require_api_key, require_scope


# =============================================================================
# PHASE 3: REAL-TIME UPDATES ENDPOINTS
# =============================================================================

@bp.route('/events/stream', methods=['GET'])
@require_api_key
@require_scope('stream:realtime')
def events_stream():
    """
    GET /api/v1/events/stream?since=2026-02-12T10:00:00&events=entry_created,symptom_logged
    Server-Sent Events stream for real-time updates

    Query Parameters:
    - since: ISO timestamp to get events since (optional, default: last 5 minutes)
    - events: Comma-separated list of event types to listen for (optional, default: all)
      Options: entry_created, entry_updated, entry_deleted, symptom_logged, meal_logged
    - timeout: Max connection time in seconds (optional, default: 300, max: 3600)

    Response:
    Server-Sent Events stream with events in format:
    ```
    event: entry_created
    data: {"id": 123, "type": "meal", "date": "2026-02-12"}

    event: symptom_logged
    data: {"id": 456, "type": "bloating", "severity": 5}
    ```

    Usage:
    ```javascript
    const eventSource = new EventSource('/api/v1/events/stream');
    eventSource.addEventListener('entry_created', (e) => {
        const data = JSON.parse(e.data);
        console.log('New entry:', data);
    });
    ```
    """
    def generate_events():
        """Generator function for SSE events"""
        # Parse parameters
        since_str = request.args.get('since', '').strip()
        events_str = request.args.get('events', '').strip()
        timeout = int(request.args.get('timeout', 300))

        # Limit timeout
        if timeout < 10:
            timeout = 10
        if timeout > 3600:
            timeout = 3600

        # Parse since timestamp
        if since_str:
            try:
                since = datetime.fromisoformat(since_str.replace('Z', '+00:00'))
            except ValueError:
                since = datetime.utcnow() - timedelta(minutes=5)
        else:
            since = datetime.utcnow() - timedelta(minutes=5)

        # Parse event types filter
        event_types = []
        if events_str:
            event_types = [e.strip() for e in events_str.split(',') if e.strip()]

        # Send initial connection message
        yield f"data: {json.dumps({'status': 'connected', 'timestamp': datetime.utcnow().isoformat()})}\n\n"

        start_time = time.time()
        last_event_id = 0

        # Poll for events
        while True:
            # Check timeout
            if time.time() - start_time > timeout:
                yield f"data: {json.dumps({'status': 'timeout', 'message': 'Connection timed out'})}\n\n"
                break

            try:
                # Query for new events
                query = EventLog.query.filter(
                    EventLog.id > last_event_id,
                    EventLog.created_at >= since
                )

                # Filter by event types if specified
                if event_types:
                    query = query.filter(EventLog.event_type.in_(event_types))

                # Get events ordered by ID
                events = query.order_by(EventLog.id).limit(10).all()

                # Send events
                for event in events:
                    event_data = event.to_dict()
                    yield f"event: {event.event_type}\n"
                    yield f"id: {event.id}\n"
                    yield f"data: {json.dumps(event_data)}\n\n"
                    last_event_id = event.id

                # Send heartbeat every 30 seconds
                if not events:
                    yield f": heartbeat\n\n"

            except Exception as e:
                yield f"event: error\n"
                yield f"data: {json.dumps({'error': str(e)})}\n\n"

            # Sleep before next poll
            time.sleep(5)

    return Response(
        generate_events(),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )


@bp.route('/webhooks/register', methods=['POST'])
@require_api_key
@require_scope('write:webhooks')
def register_webhook():
    """
    POST /api/v1/webhooks/register
    Register a webhook URL for event notifications

    Expected JSON:
    {
        "name": "My Webhook",
        "url": "https://example.com/webhook",
        "events": ["entry_created", "symptom_logged"],
        "secret": "optional_secret_for_hmac"  // optional
    }

    Returns:
    {
        "success": true,
        "webhook_id": 123,
        "name": "My Webhook",
        "url": "https://example.com/webhook",
        "events": ["entry_created", "symptom_logged"],
        "is_active": true,
        "message": "Webhook registered successfully"
    }

    Event Types:
    - entry_created: New diary entry created
    - entry_updated: Diary entry updated
    - entry_deleted: Diary entry deleted
    - symptom_logged: New symptom logged
    - meal_logged: New meal logged
    - bowel_logged: New bowel movement logged
    - stress_logged: New stress log created
    - note_created: New note created
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Validate required fields
        name = data.get('name', '').strip()
        url = data.get('url', '').strip()
        events = data.get('events', [])
        secret = data.get('secret', '').strip()

        if not name:
            return jsonify({'error': 'name is required'}), 400

        if not url:
            return jsonify({'error': 'url is required'}), 400

        if not url.startswith('http://') and not url.startswith('https://'):
            return jsonify({'error': 'url must start with http:// or https://'}), 400

        if not isinstance(events, list) or len(events) == 0:
            return jsonify({'error': 'events must be a non-empty array'}), 400

        # Validate event types
        valid_events = [
            'entry_created', 'entry_updated', 'entry_deleted',
            'symptom_logged', 'meal_logged', 'bowel_logged',
            'stress_logged', 'note_created'
        ]
        invalid_events = [e for e in events if e not in valid_events]
        if invalid_events:
            return jsonify({
                'error': f'Invalid event types: {", ".join(invalid_events)}',
                'valid_events': valid_events
            }), 400

        # Create webhook
        webhook = Webhook(
            name=name,
            url=url,
            events=','.join(events),
            secret=secret if secret else None
        )
        db.session.add(webhook)
        db.session.commit()

        return jsonify({
            'success': True,
            'webhook_id': webhook.id,
            'name': webhook.name,
            'url': webhook.url,
            'events': webhook.event_list,
            'is_active': webhook.is_active,
            'message': 'Webhook registered successfully'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/webhooks', methods=['GET'])
@require_api_key
@require_scope('read:webhooks')
def list_webhooks():
    """
    GET /api/v1/webhooks
    List all registered webhooks

    Returns:
    {
        "webhooks": [
            {
                "id": 123,
                "name": "My Webhook",
                "url": "https://example.com/webhook",
                "events": ["entry_created", "symptom_logged"],
                "is_active": true,
                "created_at": "2026-02-12T10:00:00",
                "last_triggered": "2026-02-12T11:30:00",
                "trigger_count": 45
            }
        ],
        "total_count": 3
    }
    """
    try:
        webhooks = Webhook.query.order_by(Webhook.created_at.desc()).all()
        return jsonify({
            'webhooks': [w.to_dict() for w in webhooks],
            'total_count': len(webhooks)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/webhooks/<int:webhook_id>', methods=['GET'])
@require_api_key
@require_scope('read:webhooks')
def get_webhook(webhook_id):
    """
    GET /api/v1/webhooks/{id}
    Get details of a specific webhook

    Returns:
    {
        "id": 123,
        "name": "My Webhook",
        "url": "https://example.com/webhook",
        "events": ["entry_created", "symptom_logged"],
        "is_active": true,
        "created_at": "2026-02-12T10:00:00",
        "last_triggered": "2026-02-12T11:30:00",
        "trigger_count": 45,
        "last_error": null
    }
    """
    try:
        webhook = Webhook.query.get(webhook_id)
        if not webhook:
            return jsonify({'error': 'Webhook not found'}), 404

        return jsonify(webhook.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/webhooks/<int:webhook_id>', methods=['PUT'])
@require_api_key
@require_scope('write:webhooks')
def update_webhook(webhook_id):
    """
    PUT /api/v1/webhooks/{id}
    Update a webhook

    Expected JSON:
    {
        "name": "Updated Name",
        "url": "https://new-url.com/webhook",
        "events": ["entry_created", "meal_logged"],
        "is_active": true
    }
    """
    try:
        webhook = Webhook.query.get(webhook_id)
        if not webhook:
            return jsonify({'error': 'Webhook not found'}), 404

        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        # Update fields if provided
        if 'name' in data:
            webhook.name = data['name'].strip()

        if 'url' in data:
            url = data['url'].strip()
            if not url.startswith('http://') and not url.startswith('https://'):
                return jsonify({'error': 'url must start with http:// or https://'}), 400
            webhook.url = url

        if 'events' in data:
            events = data['events']
            if not isinstance(events, list) or len(events) == 0:
                return jsonify({'error': 'events must be a non-empty array'}), 400
            webhook.events = ','.join(events)

        if 'is_active' in data:
            webhook.is_active = bool(data['is_active'])

        if 'secret' in data:
            webhook.secret = data['secret'].strip() if data['secret'] else None

        db.session.commit()

        return jsonify({
            'success': True,
            'webhook': webhook.to_dict(),
            'message': 'Webhook updated successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/webhooks/<int:webhook_id>', methods=['DELETE'])
@require_api_key
@require_scope('write:webhooks')
def delete_webhook(webhook_id):
    """
    DELETE /api/v1/webhooks/{id}
    Delete a webhook

    Returns:
    {
        "success": true,
        "message": "Webhook deleted successfully"
    }
    """
    try:
        webhook = Webhook.query.get(webhook_id)
        if not webhook:
            return jsonify({'error': 'Webhook not found'}), 404

        webhook_name = webhook.name
        db.session.delete(webhook)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Webhook "{webhook_name}" deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/webhooks/<int:webhook_id>/test', methods=['POST'])
@require_api_key
@require_scope('write:webhooks')
def test_webhook(webhook_id):
    """
    POST /api/v1/webhooks/{id}/test
    Test a webhook by sending a test event

    Returns:
    {
        "success": true,
        "status_code": 200,
        "response": "...",
        "message": "Test event sent successfully"
    }
    """
    try:
        webhook = Webhook.query.get(webhook_id)
        if not webhook:
            return jsonify({'error': 'Webhook not found'}), 404

        # Create test payload
        test_payload = {
            'event_type': 'test',
            'entity_type': 'test',
            'entity_id': 0,
            'data': {
                'message': 'This is a test webhook notification',
                'timestamp': datetime.utcnow().isoformat()
            }
        }

        # Send webhook
        try:
            response = requests.post(
                webhook.url,
                json=test_payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            webhook.last_triggered = datetime.utcnow()
            webhook.trigger_count += 1

            if response.status_code >= 400:
                webhook.last_error = f'HTTP {response.status_code}: {response.text[:200]}'
            else:
                webhook.last_error = None

            db.session.commit()

            return jsonify({
                'success': response.status_code < 400,
                'status_code': response.status_code,
                'response': response.text[:500],
                'message': 'Test event sent successfully' if response.status_code < 400 else 'Test failed'
            })

        except requests.exceptions.RequestException as req_err:
            webhook.last_error = str(req_err)[:200]
            db.session.commit()

            return jsonify({
                'success': False,
                'error': str(req_err),
                'message': 'Failed to send test event'
            }), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# =============================================================================
# INBOUND WEBHOOK ENDPOINTS
# =============================================================================

@bp.route('/webhooks/external/receive', methods=['POST'])
def receive_external_webhook():
    """
    POST /api/v1/webhooks/external/receive
    Receive inbound webhooks from external services (wearables, meal trackers, health apps)

    Expected JSON:
    {
        "source": "wearable_sync",       // Required: wearable_sync, meal_tracker, health_app
        "provider": "fitbit",             // Required: fitbit, oura, apple_watch, myfitnesspal, etc.
        "event_type": "heart_rate",       // Required: heart_rate, sleep, stress, steps, meal_import, etc.
        "timestamp": "2026-02-28T10:00:00Z",  // Optional: when the data was generated
        "data": { ... }                   // Required: the actual payload data
    }

    Headers:
    - X-Webhook-Signature: sha256=<hex_digest>  (optional, validated if EXTERNAL_WEBHOOK_SECRET is set)

    Returns:
    {
        "success": true,
        "log_id": 123,
        "source": "wearable_sync",
        "provider": "fitbit",
        "event_type": "heart_rate",
        "signature_verified": null,
        "processed": false,
        "message": "Webhook received and logged successfully"
    }
    """
    try:
        # Get raw body for signature verification
        raw_body = request.get_data()

        # Verify HMAC signature if secret is configured
        from utils.api_helpers import verify_webhook_signature
        secret = current_app.config.get('EXTERNAL_WEBHOOK_SECRET', '')
        signature = request.headers.get('X-Webhook-Signature', '')
        sig_valid = verify_webhook_signature(raw_body, signature, secret)

        # If signature validation is configured and fails, reject
        if sig_valid is False:
            log_entry = ExternalWebhookLog(
                source='unknown',
                provider='unknown',
                event_type='signature_failed',
                payload=raw_body.decode('utf-8', errors='replace')[:10000],
                signature_header=signature[:500] if signature else None,
                signature_valid=False,
                processed=False,
                processing_notes='HMAC signature validation failed',
                http_status_returned=401
            )
            db.session.add(log_entry)
            db.session.commit()
            return jsonify({'error': 'Invalid webhook signature'}), 401

        # Parse JSON payload
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid or missing JSON payload'}), 400

        # Validate required fields
        source = data.get('source', '').strip()
        provider = data.get('provider', '').strip()
        event_type = data.get('event_type', '').strip()
        payload_data = data.get('data')

        valid_sources = ['wearable_sync', 'meal_tracker', 'health_app']
        if not source or source not in valid_sources:
            return jsonify({
                'error': f'source must be one of: {", ".join(valid_sources)}',
                'received': source
            }), 400

        if not provider:
            return jsonify({'error': 'provider is required'}), 400

        if not event_type:
            return jsonify({'error': 'event_type is required'}), 400

        if payload_data is None:
            return jsonify({'error': 'data object is required'}), 400

        # Log the webhook
        log_entry = ExternalWebhookLog(
            source=source,
            provider=provider,
            event_type=event_type,
            payload=json.dumps(data)[:50000],
            signature_header=signature[:500] if signature else None,
            signature_valid=sig_valid,
            processed=False,
            processing_notes='Received and logged. Data conversion to diary entries pending implementation.',
            http_status_returned=200
        )
        db.session.add(log_entry)
        db.session.commit()

        # Also log as an internal event so SSE/outbound webhooks can broadcast it
        log_event(
            event_type='external_webhook_received',
            entity_type=source,
            entity_id=log_entry.id,
            data={
                'source': source,
                'provider': provider,
                'event_type': event_type,
                'log_id': log_entry.id
            }
        )

        return jsonify({
            'success': True,
            'log_id': log_entry.id,
            'source': source,
            'provider': provider,
            'event_type': event_type,
            'signature_verified': sig_valid,
            'processed': False,
            'message': 'Webhook received and logged successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# =============================================================================
# EVENT LOGGING HELPER FUNCTIONS
# =============================================================================

def log_event(event_type, entity_type=None, entity_id=None, data=None):
    """
    Helper function to log an event to the event log
    This should be called whenever an event occurs that webhooks/SSE should know about

    Args:
        event_type: Type of event (entry_created, symptom_logged, etc.)
        entity_type: Type of entity (meal, symptom, etc.)
        entity_id: ID of the entity
        data: Dictionary of additional data

    Usage:
        from routes.api_v1.realtime import log_event
        log_event('entry_created', 'meal', meal_id, {'meal_type': 'Lunch'})
    """
    try:
        event_log = EventLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            data=json.dumps(data) if data else None
        )
        db.session.add(event_log)
        db.session.commit()

        # Trigger webhooks asynchronously (in a real app, use Celery or similar)
        trigger_webhooks(event_type, event_log.to_dict())

    except Exception as e:
        # Don't fail the main operation if event logging fails
        print(f"Failed to log event: {str(e)}")


def trigger_webhooks(event_type, event_data):
    """
    Trigger all active webhooks that subscribe to this event type

    Args:
        event_type: Type of event
        event_data: Event data dictionary
    """
    try:
        # Find all active webhooks that subscribe to this event
        webhooks = Webhook.query.filter(
            Webhook.is_active == True
        ).all()

        for webhook in webhooks:
            if event_type in webhook.event_list:
                # Send webhook asynchronously (simplified version)
                try:
                    response = requests.post(
                        webhook.url,
                        json=event_data,
                        headers={'Content-Type': 'application/json'},
                        timeout=5
                    )

                    webhook.last_triggered = datetime.utcnow()
                    webhook.trigger_count += 1

                    if response.status_code >= 400:
                        webhook.last_error = f'HTTP {response.status_code}'
                    else:
                        webhook.last_error = None

                except requests.exceptions.RequestException as e:
                    webhook.last_error = str(e)[:200]

                db.session.commit()

    except Exception as e:
        print(f"Failed to trigger webhooks: {str(e)}")
