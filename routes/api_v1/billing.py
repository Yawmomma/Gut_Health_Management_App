"""
Billing & Subscription API Endpoints
"""

from flask import request, jsonify, current_app
from . import bp
from database import db
from models.webhooks import BillingEvent
from utils.auth import require_api_key, require_scope
import json


@bp.route('/billing/status', methods=['GET'])
@require_api_key
@require_scope('read:billing')
def billing_status():
    """
    Get current subscription/premium status
    Returns current plan (free, pro, premium) and status
    """
    return jsonify({
        'status': 'not_configured',
        'plan': 'free',
        'tier': 'free_tier',
        'message': 'Billing integration not configured',
        'features': {
            'diary_logging': True,
            'analytics': True,
            'recipes': True,
            'education': True,
            'ai_chat': False,
            'api_access': False,
            'export_pdf': False
        },
        'todo': 'Configure Stripe/App Store integration for subscription webhooks and billing status tracking'
    }), 200


@bp.route('/billing/webhook', methods=['POST'])
def billing_webhook():
    """
    POST /api/v1/billing/webhook
    Receive subscription/payment webhooks from Stripe or App Store

    Expected JSON:
    {
        "provider": "stripe",                    // Required: stripe, app_store, google_play
        "event_type": "subscription.created",    // Required: see valid types below
        "event_id": "evt_1234567890",           // Required: external event ID for idempotency
        "timestamp": "2026-02-28T10:00:00Z",    // Optional
        "data": {                                // Required: event-specific data
            "subscription_id": "sub_xxx",
            "plan": "pro",
            "amount": 999,
            "currency": "usd",
            "customer_email": "user@example.com"
        }
    }

    Headers:
    - Stripe-Signature: <stripe_signature>      (for Stripe webhooks)
    - X-Webhook-Signature: sha256=<hex_digest>  (for other providers)

    Valid event types:
    - subscription.created: New subscription started
    - subscription.renewed: Subscription renewed successfully
    - subscription.cancelled: Subscription cancelled
    - subscription.expired: Subscription expired
    - subscription.upgraded: Plan upgraded
    - subscription.downgraded: Plan downgraded
    - payment.succeeded: Payment processed successfully
    - payment.failed: Payment failed
    - payment.refunded: Payment refunded
    - trial.started: Free trial started
    - trial.ending: Free trial ending soon

    Returns:
    {
        "success": true,
        "event_log_id": 123,
        "provider": "stripe",
        "event_type": "subscription.created",
        "signature_verified": null,
        "processed": false,
        "message": "Billing webhook received and logged successfully"
    }
    """
    try:
        # Get raw body for signature verification
        raw_body = request.get_data()

        # Parse JSON payload
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Invalid or missing JSON payload'}), 400

        # Validate provider first (needed for signature routing)
        provider = data.get('provider', '').strip().lower()
        valid_providers = ['stripe', 'app_store', 'google_play']
        if not provider or provider not in valid_providers:
            return jsonify({
                'error': f'provider must be one of: {", ".join(valid_providers)}',
                'received': provider
            }), 400

        # Verify signature based on provider
        from utils.api_helpers import verify_webhook_signature

        sig_valid = None
        signature = ''
        if provider == 'stripe':
            secret = current_app.config.get('STRIPE_WEBHOOK_SECRET', '')
            signature = request.headers.get('Stripe-Signature', '')
            sig_valid = verify_webhook_signature(raw_body, signature, secret)
        elif provider == 'app_store':
            secret = current_app.config.get('APPLE_STORE_SHARED_SECRET', '')
            signature = request.headers.get('X-Webhook-Signature', '')
            sig_valid = verify_webhook_signature(raw_body, signature, secret)
        else:
            signature = request.headers.get('X-Webhook-Signature', '')
            sig_valid = None  # No validation configured for this provider

        # Reject if signature validation fails
        if sig_valid is False:
            failed_log = BillingEvent(
                provider=provider,
                event_type='signature_failed',
                event_id=data.get('event_id', ''),
                payload=raw_body.decode('utf-8', errors='replace')[:10000],
                signature_header=signature[:500] if signature else None,
                signature_valid=False,
                processed=False,
                processing_notes='Signature validation failed'
            )
            db.session.add(failed_log)
            db.session.commit()
            return jsonify({'error': 'Invalid webhook signature'}), 401

        # Validate required fields
        event_type = data.get('event_type', '').strip()
        event_id = data.get('event_id', '').strip()
        payload_data = data.get('data')

        valid_event_types = [
            'subscription.created', 'subscription.renewed', 'subscription.cancelled',
            'subscription.expired', 'subscription.upgraded', 'subscription.downgraded',
            'payment.succeeded', 'payment.failed', 'payment.refunded',
            'trial.started', 'trial.ending'
        ]

        if not event_type or event_type not in valid_event_types:
            return jsonify({
                'error': f'event_type must be one of: {", ".join(valid_event_types)}',
                'received': event_type
            }), 400

        if not event_id:
            return jsonify({'error': 'event_id is required for idempotency'}), 400

        if payload_data is None:
            return jsonify({'error': 'data object is required'}), 400

        # Idempotency check: if event_id already exists, return success without reprocessing
        existing = BillingEvent.query.filter_by(event_id=event_id).first()
        if existing:
            return jsonify({
                'success': True,
                'event_log_id': existing.id,
                'duplicate': True,
                'message': 'Event already received and logged (idempotent)'
            }), 200

        # Log the billing event
        billing_event = BillingEvent(
            provider=provider,
            event_type=event_type,
            event_id=event_id,
            payload=json.dumps(data)[:50000],
            signature_header=signature[:500] if signature else None,
            signature_valid=sig_valid,
            processed=False,
            processing_notes='Received and logged. Subscription status update pending implementation.'
        )
        db.session.add(billing_event)
        db.session.commit()

        # Log as internal event for SSE/webhook broadcasting
        from routes.api_v1.realtime import log_event
        log_event(
            event_type='billing_webhook_received',
            entity_type='billing',
            entity_id=billing_event.id,
            data={
                'provider': provider,
                'event_type': event_type,
                'event_id': event_id,
                'log_id': billing_event.id
            }
        )

        return jsonify({
            'success': True,
            'event_log_id': billing_event.id,
            'provider': provider,
            'event_type': event_type,
            'signature_verified': sig_valid,
            'processed': False,
            'message': 'Billing webhook received and logged successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
