# Webhooks & Real-Time Events Reference

**Version**: 1.0.0
**Last Updated**: February 28, 2026

Complete guide to webhooks, Server-Sent Events (SSE), and real-time event handling in the Gut Health API.

---

## Table of Contents

1. [Overview](#overview)
2. [Setting Up Webhooks](#setting-up-webhooks)
3. [Event Types](#event-types)
4. [Webhook Payloads](#webhook-payloads)
5. [Server-Sent Events (SSE)](#server-sent-events-sse)
6. [Signature Verification](#signature-verification)
7. [Retry Logic](#retry-logic)
8. [Best Practices](#best-practices)

---

## Overview

The Gut Health API supports two real-time mechanisms:

### 1. Webhooks (Push)
- You register a URL to receive events
- API pushes events to your URL when they occur
- Good for: Integrations, mobile apps, real-time dashboards
- **Authentication**: HMAC signature verification

### 2. Server-Sent Events (SSE)
- You connect to the API and receive a continuous event stream
- Good for: Browser-based UIs, monitoring, live dashboards
- **Authentication**: API key (Bearer token)

---

## Setting Up Webhooks

### Step 1: Register a Webhook

```bash
curl -X POST http://localhost:5000/api/v1/webhooks/register \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-domain.com/webhooks/events",
    "events": ["meal.logged", "symptom.recorded", "entry.updated"],
    "active": true
  }'
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "url": "https://your-domain.com/webhooks/events",
    "events": ["meal.logged", "symptom.recorded", "entry.updated"],
    "secret": "whsec_1234567890abcdef1234567890abcdef",
    "active": true,
    "created_at": "2026-02-28T12:00:00Z",
    "last_triggered": null,
    "last_error": null
  },
  "message": "Webhook registered successfully. Store the secret securely."
}
```

**Important**: Save the `secret` — it's never shown again. You'll need it to verify signatures.

### Step 2: Receive Webhook Events

Your endpoint should accept POST requests and return `200 OK` immediately:

```python
from flask import Flask, request
import hmac
import hashlib
import json

app = Flask(__name__)
WEBHOOK_SECRET = "whsec_1234567890abcdef1234567890abcdef"

@app.route('/webhooks/events', methods=['POST'])
def handle_webhook():
    # Verify signature (see Signature Verification section)
    signature = request.headers.get('X-Gut-Health-Signature')
    body = request.get_data()

    expected_sig = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected_sig):
        return {'error': 'Invalid signature'}, 401

    # Process the event
    event = request.json
    event_type = event['type']

    if event_type == 'meal.logged':
        handle_meal_logged(event['data'])
    elif event_type == 'symptom.recorded':
        handle_symptom_recorded(event['data'])

    # Return 200 immediately (process asynchronously if needed)
    return {'status': 'received'}, 200

def handle_meal_logged(data):
    print(f"Meal logged: {data['meal_id']}")

def handle_symptom_recorded(data):
    print(f"Symptom recorded: {data['symptom']}")
```

### Step 3: Manage Webhooks

```bash
# List webhooks
curl http://localhost:5000/api/v1/webhooks \
  -H "X-API-Key: YOUR_API_KEY"

# Get specific webhook
curl http://localhost:5000/api/v1/webhooks/1 \
  -H "X-API-Key: YOUR_API_KEY"

# Update webhook
curl -X PUT http://localhost:5000/api/v1/webhooks/1 \
  -H "X-API-Key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "events": ["meal.logged", "symptom.recorded", "entry.created"],
    "active": true
  }'

# Test webhook
curl -X POST http://localhost:5000/api/v1/webhooks/1/test \
  -H "X-API-Key: YOUR_API_KEY"

# Delete webhook
curl -X DELETE http://localhost:5000/api/v1/webhooks/1 \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## Event Types

### Diary Events

#### meal.logged
Fired when a meal is added to the diary.

**Payload**:
```json
{
  "type": "meal.logged",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "meal_id": 123,
    "date": "2026-02-28",
    "meal_type": "breakfast",
    "foods": [
      {
        "food_id": 456,
        "name": "Salmon",
        "serving_size": "150g",
        "fodmap_rating": "green",
        "histamine": "low"
      }
    ],
    "nutrition": {
      "calories": 450,
      "protein_g": 35,
      "carbs_g": 0,
      "fat_g": 36
    },
    "notes": "Felt great"
  }
}
```

#### meal.updated
Fired when a meal is modified.

**Payload**: Similar to `meal.logged`, includes `previous_data` field with old values

#### meal.deleted
Fired when a meal is removed.

**Payload**:
```json
{
  "type": "meal.deleted",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "meal_id": 123,
    "date": "2026-02-28"
  }
}
```

#### symptom.recorded
Fired when a symptom is logged.

**Payload**:
```json
{
  "type": "symptom.recorded",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "symptom_id": 789,
    "date": "2026-02-28",
    "symptom": "Bloating",
    "severity": 5,
    "notes": "Started after breakfast",
    "related_meals": [123]
  }
}
```

#### symptom.updated
Fired when a symptom entry is modified.

#### symptom.deleted
Fired when a symptom is removed.

### Food & Recipe Events

#### recipe.created
Fired when a new recipe is added.

**Payload**:
```json
{
  "type": "recipe.created",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "recipe_id": 5,
    "name": "Grilled Salmon with Rice",
    "ingredients": [
      {"food_id": 456, "name": "Salmon", "quantity": "150g"}
    ],
    "tags": ["low-fodmap", "quick"],
    "fodmap_rating": "green"
  }
}
```

#### recipe.updated
Fired when recipe details change.

#### recipe.deleted
Fired when a recipe is removed.

#### food.created
Fired when a new food is added to the compendium.

**Payload**:
```json
{
  "type": "food.created",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "food_id": 789,
    "name": "Custom Food",
    "category": "Vegetables",
    "traffic_light": "green",
    "serving_sizes": [...]
  }
}
```

### Analytics Events

#### analysis.updated
Fired when analytics data changes (useful for cache invalidation).

**Payload**:
```json
{
  "type": "analysis.updated",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "metric": "trigger-foods",
    "period_days": 30,
    "changes": ["food_123", "food_456"]
  }
}
```

#### flare_risk.elevated
Fired when predicted flare risk exceeds threshold (e.g., > 50%).

**Payload**:
```json
{
  "type": "flare_risk.elevated",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "risk_percentage": 65,
    "contributing_factors": [
      "high_fodmap_stacking",
      "high_stress_level",
      "recent_trigger_food"
    ],
    "recommendations": [
      "Reduce FODMAP intake",
      "Monitor stress levels"
    ]
  }
}
```

### System Events

#### webhook.test
Fired when you test a webhook connection.

**Payload**:
```json
{
  "type": "webhook.test",
  "timestamp": "2026-02-28T14:30:00Z",
  "data": {
    "message": "This is a test webhook event"
  }
}
```

---

## Webhook Payloads

### Payload Structure

All webhook payloads follow this structure:

```json
{
  "type": "event.type",
  "timestamp": "2026-02-28T14:30:00Z",
  "webhook_id": 1,
  "attempt": 1,
  "data": {
    // Event-specific data
  }
}
```

### Headers

Webhook requests include these headers:

```
POST /webhooks/events HTTP/1.1
Host: your-domain.com
User-Agent: GutHealthAPI/1.0
Content-Type: application/json
X-Gut-Health-Event-Type: meal.logged
X-Gut-Health-Timestamp: 2026-02-28T14:30:00Z
X-Gut-Health-Webhook-ID: 1
X-Gut-Health-Signature: sha256=abcdef1234567890...
X-Gut-Health-Attempt: 1
```

---

## Server-Sent Events (SSE)

### Connect to Event Stream

```bash
curl -N http://localhost:5000/api/v1/events/stream \
  -H "X-API-Key: YOUR_API_KEY"
```

The `-N` flag prevents curl from buffering so you see events in real-time.

### Example: Browser JavaScript

```javascript
const apiKey = 'YOUR_API_KEY';
const eventSource = new EventSource(
  'http://localhost:5000/api/v1/events/stream',
  {
    headers: { 'X-API-Key': apiKey }
  }
);

eventSource.addEventListener('meal.logged', (event) => {
  const data = JSON.parse(event.data);
  console.log('Meal logged:', data);
  updateUI(data);
});

eventSource.addEventListener('symptom.recorded', (event) => {
  const data = JSON.parse(event.data);
  console.log('Symptom recorded:', data);
});

eventSource.addEventListener('error', (event) => {
  if (event.readyState === EventSource.CLOSED) {
    console.log('Connection closed');
  }
});
```

### Example: Python

```python
import requests
import json

API_KEY = 'YOUR_API_KEY'

response = requests.get(
    'http://localhost:5000/api/v1/events/stream',
    headers={'X-API-Key': API_KEY},
    stream=True
)

for line in response.iter_lines():
    if line:
        line = line.decode('utf-8')
        if line.startswith('data:'):
            event_data = json.loads(line[5:])
            print(f"Event: {event_data['type']}")
            print(f"Data: {event_data['data']}")
```

### Event Stream Format

SSE events follow this format:

```
event: meal.logged
data: {"timestamp": "2026-02-28T14:30:00Z", "data": {...}}

event: symptom.recorded
data: {"timestamp": "2026-02-28T14:35:00Z", "data": {...}}
```

---

## Signature Verification

### HMAC-SHA256 Signature

Every webhook request includes an `X-Gut-Health-Signature` header containing an HMAC-SHA256 hash of the request body signed with your webhook secret.

### Python Example

```python
import hmac
import hashlib

def verify_webhook_signature(body, signature, secret):
    """Verify webhook signature"""
    expected = hmac.new(
        secret.encode(),
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)

# Usage
body = request.get_data()
signature = request.headers.get('X-Gut-Health-Signature')
secret = 'whsec_...'

if verify_webhook_signature(body, signature, secret):
    print("Signature is valid")
else:
    print("Signature is invalid - reject request")
```

### Node.js/JavaScript Example

```javascript
const crypto = require('crypto');

function verifyWebhookSignature(body, signature, secret) {
  const expectedSignature = crypto
    .createHmac('sha256', secret)
    .update(body)
    .digest('hex');

  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(expectedSignature)
  );
}

// Usage in Express
app.post('/webhooks/events', (req, res) => {
  const body = req.rawBody; // Make sure to capture raw body
  const signature = req.headers['x-gut-health-signature'];
  const secret = 'whsec_...';

  if (!verifyWebhookSignature(body, signature, secret)) {
    return res.status(401).json({ error: 'Invalid signature' });
  }

  // Process webhook
  res.json({ status: 'received' });
});
```

---

## Retry Logic

### Automatic Retries

If your webhook endpoint returns anything other than `2xx`, the API will retry:

- **Attempt 1**: Immediate
- **Attempt 2**: 5 minutes delay
- **Attempt 3**: 30 minutes delay
- **Attempt 4**: 2 hours delay
- **Attempt 5**: 24 hours delay

After 5 failed attempts, the webhook is disabled and you'll see `last_error` in webhook details.

### Idempotency

Since webhooks might be delivered multiple times, design your endpoints to be **idempotent**:

```python
# Bad: Creates duplicate if called twice
@app.route('/webhooks/meal', methods=['POST'])
def handle_meal():
    meal_id = request.json['data']['meal_id']
    create_notification(meal_id)  # Could duplicate!
    return {'status': 'ok'}, 200

# Good: Uses idempotency key
@app.route('/webhooks/meal', methods=['POST'])
def handle_meal():
    meal_id = request.json['data']['meal_id']

    # Check if already processed
    if Notification.query.filter_by(meal_id=meal_id).first():
        return {'status': 'already processed'}, 200

    create_notification(meal_id)
    return {'status': 'created'}, 200
```

---

## Best Practices

### 1. Respond Quickly

Return `200 OK` immediately, then process asynchronously:

```python
from threading import Thread

@app.route('/webhooks/events', methods=['POST'])
def handle_webhook():
    event = request.json

    # Return immediately
    Thread(
        target=process_event,
        args=(event,),
        daemon=True
    ).start()

    return {'status': 'received'}, 200

def process_event(event):
    # Heavy processing here - runs in background
    pass
```

### 2. Implement Proper Logging

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

@app.route('/webhooks/events', methods=['POST'])
def handle_webhook():
    event = request.json
    event_type = event['type']
    timestamp = event['timestamp']

    logger.info(f"Received webhook: {event_type} at {timestamp}")

    try:
        process_event(event)
        logger.info(f"Successfully processed: {event_type}")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {'error': str(e)}, 500

    return {'status': 'processed'}, 200
```

### 3. Use Event Filtering

Only subscribe to events you need:

```python
# Good: Only listen to what matters
webhook = {
    "url": "https://domain.com/webhooks",
    "events": ["meal.logged", "symptom.recorded"],  # Only these
    "active": True
}

# Less good: Listen to everything
webhook = {
    "url": "https://domain.com/webhooks",
    "events": ["*"],  # Too noisy
    "active": True
}
```

### 4. Handle Timestamps Correctly

Always use UTC timestamps and validate event freshness:

```python
from datetime import datetime, timedelta
import pytz

@app.route('/webhooks/events', methods=['POST'])
def handle_webhook():
    event = request.json
    event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
    now = datetime.now(pytz.UTC)

    # Reject events older than 5 minutes (replay attack prevention)
    if now - event_time > timedelta(minutes=5):
        logger.warning("Rejecting old webhook event")
        return {'error': 'Event too old'}, 400

    process_event(event)
    return {'status': 'ok'}, 200
```

### 5. Monitor Webhook Health

```python
# Check webhook status periodically
def check_webhook_health(api_key, webhook_id):
    response = requests.get(
        f'http://localhost:5000/api/v1/webhooks/{webhook_id}',
        headers={'X-API-Key': api_key}
    )
    webhook = response.json()['data']

    if webhook['last_error']:
        logger.error(f"Webhook {webhook_id} is failing: {webhook['last_error']}")
        alert_admin(f"Webhook {webhook_id} needs attention")
```

### 6. Test Webhooks Before Deployment

```bash
# Test webhook endpoint
curl -X POST https://your-domain.com/webhooks/test \
  -H "Content-Type: application/json" \
  -d '{
    "type": "webhook.test",
    "timestamp": "2026-02-28T14:30:00Z",
    "data": {"message": "Test event"}
  }'

# Also use the API test endpoint
curl -X POST http://localhost:5000/api/v1/webhooks/1/test \
  -H "X-API-Key: YOUR_API_KEY"
```

---

## Troubleshooting

### Webhook Not Triggering

**Check**:
1. Webhook is `active: true`
2. Event type is in webhook's `events` list
3. Webhook endpoint is reachable from API server
4. Response code is 2xx

### Signature Verification Fails

**Check**:
1. Using correct `secret` from webhook registration
2. Verifying signature of raw request body (not parsed JSON)
3. Secret is treated as string (not bytes)

### Events Appearing Duplicated

**Solution**: Implement idempotency keys or database constraints:

```python
# Add unique constraint
db.UniqueConstraint('meal_id', name='uq_meal_webhook_processed')
```

---

## Complete Webhook Example

```python
from flask import Flask, request
import hmac
import hashlib
import logging
from datetime import datetime, timedelta

app = Flask(__name__)
logger = logging.getLogger(__name__)

WEBHOOK_SECRET = 'whsec_...'
MAX_EVENT_AGE = timedelta(minutes=5)

def verify_signature(body, signature):
    """Verify webhook signature"""
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

def is_event_fresh(timestamp_str):
    """Check if event is recent"""
    event_time = datetime.fromisoformat(
        timestamp_str.replace('Z', '+00:00')
    )
    return datetime.now(timezone.utc) - event_time <= MAX_EVENT_AGE

@app.route('/webhooks/events', methods=['POST'])
def handle_webhook():
    # Verify signature
    body = request.get_data()
    signature = request.headers.get('X-Gut-Health-Signature')

    if not verify_signature(body, signature):
        logger.warning("Webhook signature verification failed")
        return {'error': 'Invalid signature'}, 401

    event = request.json

    # Verify freshness
    if not is_event_fresh(event['timestamp']):
        logger.warning("Webhook event is too old")
        return {'error': 'Event too old'}, 400

    # Log reception
    logger.info(f"Received webhook: {event['type']}")

    # Process asynchronously
    from threading import Thread
    Thread(
        target=process_event,
        args=(event,),
        daemon=True
    ).start()

    return {'status': 'received'}, 200

def process_event(event):
    """Process webhook event"""
    try:
        if event['type'] == 'meal.logged':
            handle_meal(event['data'])
        elif event['type'] == 'symptom.recorded':
            handle_symptom(event['data'])

        logger.info(f"Successfully processed: {event['type']}")
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")

def handle_meal(data):
    print(f"Meal logged: {data['meal_id']}")
    # Update your system

def handle_symptom(data):
    print(f"Symptom recorded: {data['symptom']}")
    # Update your system
```

---

**Last Updated**: February 28, 2026
**Version**: 1.0.0
