# Gut Health Management App - Complete API Documentation

**Version**: 1.0.0 (February 28, 2026)
**API Prefix**: `/api/v1`
**Total Endpoints**: 136 across 20 endpoint categories

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Authentication & Authorization](#authentication--authorization)
3. [Response Format & Error Handling](#response-format--error-handling)
4. [Rate Limiting](#rate-limiting)
5. [Scopes Reference](#scopes-reference)
6. [Migration Notes](#migration-notes)
7. [All Endpoints by Category](#all-endpoints-by-category)
8. [Common Use Cases](#common-use-cases)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### 1. Get an API Key

Generate an API key with the scopes you need:

```bash
# Option A: Via the API (requires admin:security scope)
curl -X POST http://localhost:5000/api/v1/auth/api-keys \
  -H "X-API-Key: YOUR_EXISTING_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Integration",
    "scopes": ["read:diary", "read:analytics", "read:recipes"],
    "rate_limit": 120
  }'

# Option B: Using the bootstrap script (for APP2)
python scripts/create_app2_key.py              # Primary features (15 scopes)
python scripts/create_app2_key.py --secondary  # + Secondary features (6 more scopes)
```

**Important**: The API key is shown **only once**. Store it securely.

### 2. Make Your First Request

```bash
# Use X-API-Key header
curl -X GET http://localhost:5000/api/v1/fodmap/categories \
  -H "X-API-Key: YOUR_API_KEY"

# Or use Authorization Bearer header
curl -X GET http://localhost:5000/api/v1/fodmap/categories \
  -H "Authorization: Bearer YOUR_API_KEY"
```

### 3. Check the Interactive Documentation

Visit **http://localhost:5000/api/docs** in your browser for:
- Full Swagger UI with all endpoints listed
- Request/response examples
- "Try it out" buttons to test live
- Authentication configuration
- Parameter validation

---

## Authentication & Authorization

### Two-Layer Security Model

Every API request is validated through two independent checks:

#### 1. API Key Authentication
- **Header**: `X-API-Key: <your-64-char-hex-key>`
- **Alternative**: `Authorization: Bearer <your-64-char-hex-key>`
- **Validation**:
  - Key must exist in database (SHA-256 hashed)
  - Key must be `is_active = true`
  - Key must not be expired (`expires_at` must be in future or null)
- **Response on failure**: `401 Unauthorized`

#### 2. Scope-Based Authorization
- Each API key is granted specific **scopes** (e.g., `read:diary`, `write:recipes`)
- Each endpoint requires specific scope(s) to access
- Multi-scope endpoints require **at least one** matching scope
- **Response on failure**: `403 Forbidden` with `required_scope` in response

#### 3. Browser Bypass
Web browser requests (no API key header) pass through unauthenticated. This allows:
- Normal web UI usage without configuration
- No need to expose API key in browser code
- API key auth is only enforced for programmatic access

### Example: Authentication Flow

```
Request: GET /api/v1/diary/entries
Header: X-API-Key: abc123...xyz

Step 1: Hash the key → lookup in api_keys table
  ✓ Key found, is_active=true, expires_at=null → Continue
  ✗ Key not found or expired → Return 401

Step 2: Check required scope (read:diary)
  ✓ Key has scope "read:diary" → Allow request
  ✗ Key missing scope → Return 403 with required_scope

Step 3: Log the request (for audit trail)
  - api_key_id, endpoint, method, status_code, ip_address, timestamp

Step 4: Execute endpoint and return data
```

### Creating API Keys Programmatically

**Endpoint**: `POST /api/v1/auth/api-keys`
**Required Scope**: `admin:security`
**Rate Limit**: Standard (120/min)

**Request Body**:
```json
{
  "name": "My App Integration",
  "scopes": ["read:diary", "read:analytics", "write:diary"],
  "rate_limit": 120,
  "expires_at": "2027-02-28T23:59:59Z"
}
```

**Response** (201 Created):
```json
{
  "success": true,
  "data": {
    "id": 5,
    "name": "My App Integration",
    "key": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
    "key_prefix": "abcdef01",
    "scopes": ["read:diary", "read:analytics", "write:diary"],
    "rate_limit": 120,
    "created_at": "2026-02-28T12:00:00Z",
    "expires_at": "2027-02-28T23:59:59Z"
  },
  "message": "API key created. Store it securely — it will never be displayed again."
}
```

### Listing and Revoking Keys

```bash
# List all API keys (returns prefix only, never full key)
curl http://localhost:5000/api/v1/auth/api-keys \
  -H "X-API-Key: YOUR_KEY"

# Revoke a key
curl -X DELETE http://localhost:5000/api/v1/auth/api-keys/{key_id} \
  -H "X-API-Key: YOUR_KEY"
```

---

## Response Format & Error Handling

### Success Response (2xx)

All successful responses follow this structure:

```json
{
  "success": true,
  "data": {
    "id": 123,
    "name": "Apple",
    "fodmap_status": "green",
    "serving_sizes": [...]
  },
  "message": "Optional message"
}
```

**Status Codes**:
- `200 OK` — Standard successful GET, PUT
- `201 Created` — Successful POST
- `204 No Content` — DELETE, no response body

### Error Response (4xx, 5xx)

All error responses follow this structure:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input: 'serving_size' must be a positive number",
    "details": {
      "field": "serving_size",
      "value": -10,
      "reason": "Must be positive"
    }
  }
}
```

### Standard Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `VALIDATION_ERROR` | 400 | Invalid request data (bad format, missing fields, out-of-range values) |
| `MISSING_REQUIRED_FIELD` | 400 | Required field is missing from request |
| `UNAUTHORIZED` | 401 | API key invalid, expired, or missing |
| `FORBIDDEN` | 403 | Key lacks required scope for endpoint |
| `NOT_FOUND` | 404 | Requested resource not found |
| `ALREADY_EXISTS` | 409 | Resource already exists (duplicate name, etc.) |
| `DATABASE_ERROR` | 500 | Unexpected database error |
| `NOT_IMPLEMENTED` | 501 | Endpoint not yet implemented |

### Paginated Response

Some GET endpoints return paginated data:

```json
{
  "success": true,
  "data": {
    "data": [
      { "id": 1, "name": "Item 1" },
      { "id": 2, "name": "Item 2" },
      { "id": 3, "name": "Item 3" }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 247,
      "pages": 13,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

**Query Parameters** (for paginated endpoints):
- `page` (default: 1) — Page number (1-indexed)
- `per_page` (default: 20) — Items per page (max: 100)

---

## Rate Limiting

### How It Works

Each API key has a **per-minute request limit** (default: 120 requests/minute). This is checked on every request:

1. Count requests in the past 60 seconds from this key
2. If count >= limit → reject with `429 Too Many Requests`
3. If count < limit → allow request and increment counter

### Response Headers

Successful requests include rate limit info:

```
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1645877460
```

### Rate Limit Exceeded Response

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Remaining: 0
Retry-After: 45

{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Max 120 requests per minute.",
    "details": {
      "limit": 120,
      "remaining": 0,
      "reset_in_seconds": 45
    }
  }
}
```

### Checking Your Rate Limit Status

```bash
curl http://localhost:5000/api/v1/auth/rate-limit \
  -H "X-API-Key: YOUR_KEY"
```

Response:
```json
{
  "success": true,
  "data": {
    "limit": 120,
    "requests_this_minute": 23,
    "remaining": 97,
    "reset_at": "2026-02-28T17:15:30Z"
  }
}
```

### Rate Limit Tiers

| Tier | Limit | Use Case |
|------|-------|----------|
| Standard | 120/min | Most integrations |
| High | 180/min | Bulk operations |
| Low | 60/min | Demo/trial keys |

Custom limits can be set when creating a key.

---

## Scopes Reference

### What Are Scopes?

Scopes control what data an API key can access. A key can have multiple scopes (comma-separated).

### All Available Scopes

**Read Scopes** (22 total):
| Scope | Endpoints | Description |
|-------|-----------|-------------|
| `read:diary` | GET /diary/* | Read diary entries, trends, meals |
| `read:analytics` | GET /analytics/* | Read all analytics endpoints |
| `read:export` | GET /export/* | Export diary, PDF, shopping lists |
| `read:chat` | GET /chat/* | Read chat conversations |
| `read:compendium` | GET /compendium/search, /compendium/foods/{id} | Search and view foods |
| `read:foods` | GET /foods/* | Food utilities (batch, substitutes, boosters) |
| `read:recipes` | GET /recipes/*, GET /meals | List, search, view recipes and meals |
| `read:search` | GET /search/* | Global search endpoints |
| `read:fodmap` | GET /fodmap/* | FODMAP categories and foods |
| `read:usda` | GET /usda/* | USDA food database |
| `read:ausnut` | GET /ausnut/* | AUSNUT food database |
| `read:education` | GET /education/* | Educational content |
| `read:help` | GET /help/* | Help documents and FAQs |
| `read:webhooks` | GET /webhooks/* | List and view webhooks |
| `read:gamification` | GET /gamification/* | Challenges and badges |
| `read:reintroduction` | GET /reintroduction/* | Reintroduction protocol |
| `read:notifications` | GET /notifications/* | Notification settings and rules |
| `read:integrations` | (none yet) | Reserved for wearable integrations |
| `read:billing` | GET /billing/status | Billing and subscription status |
| `read:security` | GET /auth/rate-limit | Rate limit status (read-only) |

**Write Scopes** (13 total):
| Scope | Endpoints | Description |
|-------|-----------|-------------|
| `write:diary` | POST /diary/*, PUT /diary/* | Create and update diary entries |
| `write:foods` | POST /compendium/foods, PUT /compendium/foods/{id}, DELETE /compendium/foods/{id} | Create, update, delete foods |
| `write:recipes` | POST /recipes, PUT /recipes/{id}, DELETE /recipes/{id}, POST /recipes/import, POST /recipes/share | Recipe management |
| `write:chat` | POST /chat, DELETE /chat/conversations/{id} | Chat messages and cleanup |
| `write:webhooks` | POST /webhooks/*, PUT /webhooks/{id}, DELETE /webhooks/{id} | Webhook management |
| `write:help` | POST /help, PUT /help/{id}, DELETE /help/{id} | Help document management |
| `write:education` | POST /education, PUT /education/{id}, DELETE /education/{id}, POST /education/reorder | Educational content management |
| `write:gamification` | POST /gamification/challenges | Create challenges |
| `write:reintroduction` | POST /reintroduction/* | Start and evaluate protocols |
| `write:notifications` | POST /notifications/*, PUT /notifications/*, DELETE /notifications/* | Notification rules and scheduling |
| `write:integrations` | POST /wearables/*, POST /voice/* | Wearable and voice logging |

**Special Scopes** (5 total):
| Scope | Endpoints | Description |
|-------|-----------|-------------|
| `stream:realtime` | GET /events/stream | Server-Sent Events stream |
| `admin:backup` | GET /settings/backup | Database backup |
| `admin:settings` | GET /settings/integrity-check, POST /settings/integrity-check/fix | Database maintenance |
| `admin:security` | POST /auth/api-keys, GET /auth/api-keys, DELETE /auth/api-keys/{id} | API key management |
| `admin:users` | GET /users/* | Multi-user admin operations |

### Typical Scope Combinations

**For APP2 (Analytics Dashboard)** — Primary:
```
read:diary,read:analytics,read:export,read:recipes,read:compendium,read:foods,read:search,read:fodmap,read:usda,read:chat,read:webhooks,write:diary,write:webhooks,stream:realtime
```

**For APP2 (Analytics Dashboard)** — Secondary (add to primary):
```
read:gamification,read:reintroduction,read:notifications,read:billing,read:education,read:help
```

**For Mobile App** (Limited set):
```
read:diary,read:recipes,read:compendium,write:diary
```

**For Integration Partner**:
```
read:analytics,read:diary,read:foods,read:recipes
```

---

## Migration Notes

### For Users Upgrading from v1.3.x to v1.4.0

#### New Features
1. **Swagger API Documentation** — Interactive API docs now available at `/api/docs`
   - Full endpoint reference
   - Parameter validation
   - "Try it out" buttons in browser

2. **Database Migrations (Alembic)** — Formal schema versioning
   - All future database updates will be managed through migrations
   - Your existing database is automatically compatible
   - No action required on your part

#### Backward Compatibility
- ✅ All existing endpoints work identically
- ✅ API key authentication unchanged
- ✅ Response formats unchanged
- ✅ Database file (gut_health.db) fully compatible
- ✅ Old API (`/api/*`) still works (deprecated, will remove in v2.0)

#### What's Deprecated (Will Remove in v2.0)
The old API routes (`/api/...` without `/v1`) are deprecated. **Migrate to `/api/v1/` endpoints if you have any integrations using the old paths.**

Before:
```
GET /api/foods/search
GET /api/diary/entries
```

After:
```
GET /api/v1/foods/unified-search (or /api/v1/compendium/search)
GET /api/v1/diary/entries
```

### For API Consumers & Integrations

#### If You Built Something with the Old API
- All endpoints migrated to `/api/v1/` with updated paths
- Add the `/v1` segment to your requests
- Update your scope requirements (new 40-scope system)
- Create a new API key with correct scopes

#### Example Migration

Old code:
```python
import requests
response = requests.get('http://localhost:5000/api/foods/search',
                       params={'q': 'apple'})
```

Updated code:
```python
import requests
response = requests.get('http://localhost:5000/api/v1/compendium/search',
                       params={'q': 'apple'},
                       headers={'X-API-Key': 'your-api-key'})
```

---

## All Endpoints by Category

### Diary (9 endpoints)

#### GET /diary/entries
Get diary entries (meals, symptoms, bowel, stress, notes) within a date range.

**Scopes**: `read:diary`
**Parameters**:
- `date_from` (string, YYYY-MM-DD) — Start date
- `date_to` (string, YYYY-MM-DD) — End date
- `page` (integer, default: 1)
- `per_page` (integer, default: 20, max: 100)

**Response**:
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": 1,
        "date": "2026-02-28",
        "meals": [...],
        "symptoms": [...],
        "bowel": {...},
        "stress": {...},
        "notes": "String"
      }
    ],
    "pagination": {...}
  }
}
```

#### GET /diary/day/{date}
Get all entries for a specific day with detailed nutrition.

**Scopes**: `read:diary`
**Parameters**:
- `date` (path parameter, YYYY-MM-DD) — Target date

**Response**:
```json
{
  "success": true,
  "data": {
    "date": "2026-02-28",
    "meals": [
      {
        "id": 5,
        "meal_type": "breakfast",
        "foods": [...],
        "nutrition": {
          "calories": 450,
          "protein_g": 15,
          "carbs_g": 65,
          "fat_g": 12,
          "fiber_g": 8,
          "fodmap_level": "green",
          "histamine_level": "low"
        }
      }
    ],
    "symptoms": [...],
    "daily_totals": {...}
  }
}
```

#### GET /diary/trends
Get symptom trends over a time period (default 30 days).

**Scopes**: `read:diary`
**Parameters**:
- `days` (integer, default: 30) — Look back period
- `symptom_type` (string, optional) — Filter by symptom type

**Response**:
```json
{
  "success": true,
  "data": {
    "period_days": 30,
    "symptoms": [
      {
        "name": "Bloating",
        "daily_avg": 3.2,
        "trend": "improving",
        "data_points": [...]
      }
    ],
    "correlations": [...]
  }
}
```

#### GET /diary/weekly
Get weekly summaries for better long-term trends.

**Scopes**: `read:diary`
**Parameters**:
- `weeks` (integer, default: 4) — Number of weeks to show

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "week": "2026-02-23 to 2026-03-01",
      "meals_logged": 18,
      "symptom_avg": 2.5,
      "foods_eaten": 32,
      "trigger_foods": ["Garlic", "Wheat"],
      "nutrition_summary": {}
    }
  ]
}
```

#### POST /diary/meals
Create a new meal entry.

**Scopes**: `write:diary`
**Request Body**:
```json
{
  "date": "2026-02-28",
  "meal_type": "breakfast",
  "foods": [
    {
      "food_id": 123,
      "serving_size": "1 cup",
      "quantity": 1
    },
    {
      "food_id": 456,
      "custom_quantity": "250g"
    }
  ],
  "notes": "Optional meal notes"
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 78,
    "date": "2026-02-28",
    "meal_type": "breakfast",
    "foods": [...],
    "created_at": "2026-02-28T12:00:00Z"
  },
  "message": "Meal entry created successfully"
}
```

#### PUT /diary/meals/{id}
Update an existing meal entry.

**Scopes**: `write:diary`
**Parameters**:
- `id` (path parameter, integer) — Meal ID

**Request Body**: Same as POST

**Response**: 200 OK with updated meal data

#### POST /diary/entries/bulk
Create multiple diary entries at once (meals, symptoms, etc.).

**Scopes**: `write:diary`
**Request Body**:
```json
{
  "entries": [
    {
      "type": "meal",
      "date": "2026-02-28",
      "meal_type": "breakfast",
      "foods": [...]
    },
    {
      "type": "symptom",
      "date": "2026-02-28",
      "symptom": "Bloating",
      "severity": 4,
      "notes": "After eating wheat"
    },
    {
      "type": "bowel",
      "date": "2026-02-28",
      "bristol_type": 4,
      "notes": "Normal"
    }
  ]
}
```

**Response**: 201 Created with array of created entries

#### POST /diary/meal-plan
Save a meal plan (typically 7 days).

**Scopes**: `write:diary`
**Request Body**:
```json
{
  "name": "Low FODMAP Week 1",
  "description": "Initial elimination diet",
  "days": [
    {
      "date": "2026-03-01",
      "meals": [
        {
          "meal_type": "breakfast",
          "foods": [...]
        }
      ]
    }
  ]
}
```

**Response**: 201 Created with meal plan ID

#### GET /diary/meal-plan/{id}
Retrieve a saved meal plan.

**Scopes**: `read:diary`
**Parameters**:
- `id` (path parameter, integer) — Meal plan ID

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Low FODMAP Week 1",
    "created_at": "2026-02-28T12:00:00Z",
    "days": [...]
  }
}
```

---

### Analytics (27 endpoints)

All analytics endpoints return time-series data, trends, and correlations. Most support date range filtering.

#### GET /analytics/dashboard
Get personalized dashboard data (watch list, incomplete foods, recent triggers).

**Scopes**: `read:analytics`

**Response**:
```json
{
  "success": true,
  "data": {
    "watch_list": [...],
    "incomplete_foods": [...],
    "recent_triggers": [...],
    "symptom_streak": 5,
    "flare_risk": 25
  }
}
```

#### POST /foods/risk-rating
Calculate traffic light rating for a specific serving size.

**Scopes**: `read:analytics`
**Request Body**:
```json
{
  "food_id": 123,
  "serving_size": "1 cup",
  "quantity": 1
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "traffic_light": "amber",
    "fodmap_types": {
      "fructans": "safe",
      "gos": "moderate",
      "lactose": "safe",
      "fructose": "safe",
      "polyols": "safe",
      "sorbitol": "safe",
      "mannitol": "safe"
    },
    "histamine": "low",
    "safe_quantity": "0.5 cups",
    "notes": "High GOS at this serving size"
  }
}
```

#### GET /analytics/symptom-patterns
Find correlations between foods and symptoms.

**Scopes**: `read:analytics`
**Parameters**:
- `days` (integer, default: 30)
- `min_confidence` (float, 0-1, default: 0.7)

**Response**:
```json
{
  "success": true,
  "data": {
    "patterns": [
      {
        "symptom": "Bloating",
        "trigger_foods": [
          {
            "food_name": "Garlic",
            "confidence": 0.92,
            "lag_hours": 2,
            "occurrences": 8
          }
        ]
      }
    ]
  }
}
```

#### GET /analytics/food-reactions
Get foods that have historically triggered symptoms.

**Scopes**: `read:analytics`

**Response**:
```json
{
  "success": true,
  "data": {
    "high_risk_foods": [
      {
        "food_id": 123,
        "name": "Garlic",
        "symptom_rate": 0.67,
        "avg_severity": 5,
        "times_triggered": 8,
        "last_triggered": "2026-02-20"
      }
    ]
  }
}
```

#### GET /analytics/symptom-trends
Time-series data for all symptoms.

**Scopes**: `read:analytics`
**Parameters**:
- `days` (integer, default: 30)
- `granularity` (string: "daily" or "weekly", default: "daily")

**Response**:
```json
{
  "success": true,
  "data": {
    "period": "30 days",
    "symptoms": [
      {
        "name": "Bloating",
        "trend": "improving",
        "values": [4, 3.5, 3.2, 3.1, ...],
        "dates": ["2026-01-29", "2026-01-30", ...]
      }
    ]
  }
}
```

#### GET /analytics/food-frequency
Most-eaten foods during period.

**Scopes**: `read:analytics`
**Parameters**:
- `days` (integer, default: 30)
- `limit` (integer, default: 20, max: 100)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "food_id": 456,
      "name": "Rice",
      "times_eaten": 18,
      "avg_serving": "1 cup",
      "traffic_light": "green"
    }
  ]
}
```

#### GET /analytics/trigger-foods
Foods eaten on high-symptom days.

**Scopes**: `read:analytics`
**Parameters**:
- `days` (integer, default: 30)
- `symptom_threshold` (float, 1-10, default: 6)

**Response**: List of foods strongly associated with high-symptom days

#### GET /analytics/nutrition-summary
Aggregated nutrition over date range.

**Scopes**: `read:analytics`
**Parameters**:
- `date_from` (string, YYYY-MM-DD)
- `date_to` (string, YYYY-MM-DD)

**Response**:
```json
{
  "success": true,
  "data": {
    "period": "7 days",
    "daily_avg": {
      "calories": 1850,
      "protein_g": 65,
      "carbs_g": 200,
      "fat_g": 50,
      "fiber_g": 25
    },
    "weekly_totals": {...},
    "nutrient_gaps": [...]
  }
}
```

#### GET /analytics/fodmap-exposure
FODMAP load over time.

**Scopes**: `read:analytics`

**Response**:
```json
{
  "success": true,
  "data": {
    "current_load": "moderate",
    "daily_trend": [...],
    "by_fodmap_type": {
      "fructans": 8,
      "gos": 3,
      "lactose": 0,
      ...
    }
  }
}
```

#### GET /analytics/histamine-exposure
Histamine load (similar structure to FODMAP exposure).

#### GET /analytics/fodmap-stacking
Cumulative FODMAP load across the day (useful for understanding why someone had a reaction).

#### GET /analytics/correlations
Multi-variable correlations (foods, nutrients, stress, sleep affecting symptoms).

#### GET /analytics/gut-stability-score
7-day rolling "stability" metric (inverse of symptom variability).

#### GET /analytics/tolerance-curves
Per-food tolerance curves (how much of each food is tolerable).

#### GET /analytics/nutrient-rdi-status
Nutrients as % of RDA/RDI.

#### GET /analytics/nutrient-gaps
Nutrients below target with food suggestions to boost them.

#### GET /analytics/nutrient-heatmap
7-day × nutrient grid showing daily values.

#### GET /analytics/nutrient-sources
Which foods contribute most to each nutrient.

#### GET /analytics/nutrient-symptom-correlation
Statistical correlation between nutrient levels and symptoms.

#### GET /analytics/correlation-matrix
Food × symptom correlation matrix for visualization.

#### GET /analytics/bristol-trends
Stool consistency time series with rolling average.

#### GET /analytics/hydration
Daily fluid intake vs target.

#### GET /analytics/meal-timing
When meals are eaten + analysis of late meals.

#### GET /analytics/dietary-diversity
Unique plant foods eaten + diversity score.

#### GET /analytics/flare-prediction
Rule-based prediction of gut flare risk (0-100%).

#### GET /analytics/gut-health-score
Composite 30-day wellness metric (0-100).

#### GET /analytics/interactions
Nutrient/medication interaction alerts.

---

### Recipes & Meals (15 endpoints)

#### GET /recipes
List all recipes (paginated).

**Scopes**: `read:recipes`
**Parameters**: `page`, `per_page`

**Response**: Paginated recipe list

#### GET /recipes/search
Search recipes by name, ingredients, cuisine, etc.

**Scopes**: `read:recipes`
**Parameters**:
- `q` (string, required) — Search query
- `page` (integer, default: 1)

**Response**: Matching recipes

#### GET /recipes/category/{category}
Filter recipes by meal type.

**Scopes**: `read:recipes`
**Parameters**:
- `category` (path parameter) — "breakfast", "lunch", "dinner", "snack", "dessert"

**Response**: Recipes in category

#### GET /recipes/{id}
Get full recipe details.

**Scopes**: `read:recipes`
**Parameters**: `id` (path)

**Response**:
```json
{
  "success": true,
  "data": {
    "id": 5,
    "name": "Grilled Salmon with Rice",
    "ingredients": [...],
    "instructions": "String (markdown supported)",
    "serving_size": "1 plate",
    "prep_time_min": 10,
    "cook_time_min": 15,
    "nutrition": {...},
    "fodmap_rating": "green",
    "tags": ["low-fodmap", "quick", "pescatarian"],
    "created_at": "2026-02-28T12:00:00Z"
  }
}
```

#### GET /recipes/{id}/context
Get recipe formatted for AI context (used by AI helper).

**Scopes**: `read:recipes`

**Response**: Simplified recipe format for AI processing

#### POST /recipes
Create a new recipe.

**Scopes**: `write:recipes`
**Request Body**:
```json
{
  "name": "Grilled Salmon with Rice",
  "ingredients": [
    {"name": "Salmon fillet", "quantity": "150g"},
    {"name": "White rice", "quantity": "0.75 cups"}
  ],
  "instructions": "1. Heat grill to 400°F...",
  "serving_size": "1 plate",
  "prep_time_min": 10,
  "cook_time_min": 15,
  "tags": ["low-fodmap", "quick"]
}
```

**Response**: 201 Created with new recipe

#### PUT /recipes/{id}
Update a recipe.

**Scopes**: `write:recipes`
**Request Body**: Same as POST

**Response**: 200 OK with updated recipe

#### DELETE /recipes/{id}
Delete a recipe.

**Scopes**: `write:recipes`
**Parameters**: `id` (path)

**Response**: 200 OK

#### POST /recipes/import
Import a recipe from external JSON/URL.

**Scopes**: `write:recipes`
**Request Body**:
```json
{
  "name": "Imported Recipe",
  "url": "https://example.com/recipes/123",
  "source_data": {...}
}
```

**Response**: 201 Created with imported recipe

#### POST /recipes/{id}/transform
Auto-substitute high-risk ingredients with safer alternatives.

**Scopes**: `write:recipes`
**Parameters**:
- `id` (path) — Recipe ID

**Request Body**:
```json
{
  "transformations": {
    "replace_high_fodmap": true,
    "reduce_histamine": false
  }
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "original_recipe": {...},
    "transformed_recipe": {...},
    "changes": [
      {
        "original": "Garlic (2 cloves)",
        "replacement": "Garlic-infused oil (1 tsp)",
        "reason": "High FODMAP"
      }
    ]
  }
}
```

#### POST /recipes/share
Export recipe as shareable JSON with unique token.

**Scopes**: `write:recipes`
**Parameters**:
- `id` (path or body) — Recipe ID

**Response**:
```json
{
  "success": true,
  "data": {
    "share_token": "abc123def456",
    "recipe_json": {...},
    "share_url": "http://localhost:5000/api/v1/recipes/shared/abc123def456"
  }
}
```

#### GET /meals
List all saved meals (templates).

**Scopes**: `read:recipes`

**Response**: Paginated meal list

#### POST /meals
Create a saved meal (template for recurring meals).

**Scopes**: `write:recipes`
**Request Body**:
```json
{
  "name": "Typical Breakfast",
  "meal_type": "breakfast",
  "foods": [...]
}
```

**Response**: 201 Created

#### PUT /meals/{id}
Update a saved meal.

**Scopes**: `write:recipes`

#### DELETE /meals/{id}
Delete a saved meal.

**Scopes**: `write:recipes`

---

### Foods & Compendium (14 endpoints)

#### GET /compendium/search
Search FODMAP food database.

**Scopes**: `read:compendium` (no auth required for public searches)
**Parameters**:
- `q` (string, required) — Search term
- `page` (integer, default: 1)

**Response**:
```json
{
  "success": true,
  "data": {
    "data": [
      {
        "id": 123,
        "name": "Apple",
        "category": "Fruits",
        "fodmap_rating": "amber",
        "serving_sizes": [
          {
            "size": "1 medium (182g)",
            "traffic_light": "green",
            "fodmap_notes": "Fructose: low, Sorbitol: moderate"
          }
        ]
      }
    ],
    "pagination": {...}
  }
}
```

#### GET /compendium/foods/{id}
Get food details with all serving sizes.

**Scopes**: `read:compendium`

**Response**: Full food data with nutrition and FODMAP info for each serving size

#### GET /compendium/compare
Compare multiple foods side-by-side.

**Scopes**: `read:compendium`
**Parameters**:
- `ids` (string) — Comma-separated food IDs (e.g., "123,456,789")

**Response**:
```json
{
  "success": true,
  "data": {
    "foods": [...],
    "comparison": {
      "serving_sizes": {...},
      "fodmap_types": {...},
      "histamine_levels": {...},
      "safest": "Apple"
    }
  }
}
```

#### POST /compendium/foods
Create a new food entry.

**Scopes**: `write:foods`
**Request Body**:
```json
{
  "name": "Custom Food Name",
  "category": "Vegetables",
  "serving_sizes": [
    {
      "size": "1 cup (150g)",
      "fructose": "low",
      "fructans": "low",
      "gos": "moderate",
      "lactose": "low",
      "polyols": "safe",
      "sorbitol": "safe",
      "mannitol": "safe",
      "histamine": "low",
      "dao_blocker": false,
      "liberator": false
    }
  ]
}
```

**Response**: 201 Created

#### PUT /compendium/foods/{id}
Update a food entry.

**Scopes**: `write:foods`

#### DELETE /compendium/foods/{id}
Delete a food entry.

**Scopes**: `write:foods`

#### POST /foods/quick-add
Quick add incomplete food entry (for diary logging).

**Scopes**: `write:foods`
**Request Body**:
```json
{
  "name": "Custom food",
  "quantity": "1 cup",
  "date": "2026-02-28",
  "meal_type": "breakfast"
}
```

**Response**: 201 Created with diary entry ID

#### POST /compendium/foods/{id}/link-ausnut
Link FODMAP food to AUSNUT database.

**Scopes**: `write:foods`

#### POST /compendium/foods/{id}/link-usda
Link FODMAP food to USDA database.

**Scopes**: `write:foods`

#### GET /foods/batch
Get multiple foods in one call (efficient for bulk operations).

**Scopes**: `read:foods`
**Parameters**:
- `ids` (string) — Comma-separated food IDs

**Response**: Array of food objects

#### GET /foods/substitutes
Find safe FODMAP alternatives for a food.

**Scopes**: `read:foods`
**Parameters**:
- `food_id` (integer, required) — Food to find substitutes for
- `limit` (integer, default: 10)

**Response**:
```json
{
  "success": true,
  "data": {
    "original_food": {...},
    "substitutes": [
      {
        "id": 456,
        "name": "White rice",
        "traffic_light": "green",
        "similarity": 0.85
      }
    ]
  }
}
```

#### GET /foods/unified-search
Search across FODMAP, USDA, and AUSNUT databases.

**Scopes**: `read:foods`
**Parameters**:
- `q` (string, required)

**Response**:
```json
{
  "success": true,
  "data": {
    "fodmap_results": [...],
    "usda_results": [...],
    "ausnut_results": [...]
  }
}
```

#### POST /foods/scan-menu
AI-powered menu scanning (returns safe/unsafe items).

**Scopes**: `write:foods`
**Request Body**:
```json
{
  "menu_text": "BREAKFAST\nEggs with toast\nOrange juice\n...",
  "dietary_restrictions": ["low-fodmap"]
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "safe_items": [...],
    "unsafe_items": [...],
    "uncertain_items": [...]
  }
}
```

#### GET /foods/nutrient-boosters
Find safe foods high in a specific nutrient.

**Scopes**: `read:foods`
**Parameters**:
- `nutrient` (string, required) — e.g., "iron", "calcium", "vitamin-d"
- `limit` (integer, default: 10)

**Response**:
```json
{
  "success": true,
  "data": [
    {
      "id": 789,
      "name": "Fortified rice",
      "nutrient_level": 15,
      "unit": "mg",
      "traffic_light": "green"
    }
  ]
}
```

---

### Other Endpoint Categories

For complete documentation of all remaining endpoints (USDA, AusNut, FODMAP, Search, Export, Chat, Education, Settings, Realtime, Security, Gamification, Notifications, Integrations, Billing, Users, Reintroduction), please refer to:

1. **Interactive Swagger UI**: http://localhost:5000/api/docs
2. **Quick Reference**: `api_endpoints.md`
3. **Endpoint Source Code**: `routes/api_v1/`

---

## Common Use Cases

### Use Case 1: Log a Meal and Track Symptoms

```python
import requests

API_KEY = "your-api-key"
BASE_URL = "http://localhost:5000/api/v1"
headers = {"X-API-Key": API_KEY}

# 1. Create a meal entry
meal_response = requests.post(
    f"{BASE_URL}/diary/meals",
    json={
        "date": "2026-02-28",
        "meal_type": "breakfast",
        "foods": [
            {"food_id": 123, "serving_size": "1 cup", "quantity": 1}
        ]
    },
    headers=headers
)
meal_id = meal_response.json()["data"]["id"]

# 2. Log symptoms 4 hours later
requests.post(
    f"{BASE_URL}/diary/entries/bulk",
    json={
        "entries": [
            {
                "type": "symptom",
                "date": "2026-02-28",
                "symptom": "Bloating",
                "severity": 5,
                "notes": "After breakfast"
            }
        ]
    },
    headers=headers
)

# 3. Check correlation
correlation_response = requests.get(
    f"{BASE_URL}/analytics/symptom-patterns",
    params={"days": 30, "min_confidence": 0.7},
    headers=headers
)
patterns = correlation_response.json()["data"]["patterns"]
```

### Use Case 2: Build a Shopping List from Recipes

```python
# 1. Get recipes I can eat (by FODMAP status)
recipes_response = requests.get(
    f"{BASE_URL}/recipes",
    params={"page": 1, "per_page": 10},
    headers=headers
)

# 2. Get shopping list
shopping_response = requests.get(
    f"{BASE_URL}/export/shopping-list",
    json={"recipe_ids": [1, 2, 3]},
    headers=headers
)

shopping_list = shopping_response.json()["data"]
print("Items to buy:")
for item in shopping_list:
    print(f"- {item['name']} ({item['quantity']})")
```

### Use Case 3: Analyze Food Triggers

```python
# 1. Get foods that trigger symptoms
triggers_response = requests.get(
    f"{BASE_URL}/analytics/trigger-foods",
    params={"days": 30, "symptom_threshold": 6},
    headers=headers
)

triggers = triggers_response.json()["data"]

# 2. Check safe substitutes for top trigger
top_trigger = triggers[0]
substitutes_response = requests.get(
    f"{BASE_URL}/foods/substitutes",
    params={"food_id": top_trigger["food_id"], "limit": 5},
    headers=headers
)

substitutes = substitutes_response.json()["data"]["substitutes"]
print(f"Found {len(substitutes)} safer alternatives to {top_trigger['name']}")
```

### Use Case 4: Create a Reusable Meal Plan

```python
# 1. Get recipes suitable for your dietary needs
suitable_response = requests.get(
    f"{BASE_URL}/recipes/suitable",
    params={"dietary_restrictions": ["low-fodmap", "dairy-free"]},
    headers=headers
)
recipes = suitable_response.json()["data"]

# 2. Create a 7-day meal plan
meal_plan_response = requests.post(
    f"{BASE_URL}/diary/meal-plan",
    json={
        "name": "Low FODMAP Week",
        "description": "Safe recipes for elimination diet",
        "days": [
            {
                "date": "2026-03-01",
                "meals": [
                    {
                        "meal_type": "breakfast",
                        "foods": [{"food_id": recipes[0]["id"], ...}]
                    }
                ]
            }
            # ... repeat for 7 days
        ]
    },
    headers=headers
)

# 3. Reuse the plan later
plan_id = meal_plan_response.json()["data"]["id"]
saved_plan = requests.get(
    f"{BASE_URL}/diary/meal-plan/{plan_id}",
    headers=headers
)
```

---

## Troubleshooting

### "401 Unauthorized"
**Cause**: API key invalid, missing, or expired
**Solutions**:
- Verify you're passing the key in `X-API-Key` header
- Check key hasn't expired (`GET /auth/api-keys`)
- Ensure key is still active (not revoked)
- Generate a new key if needed

### "403 Forbidden"
**Cause**: API key lacks required scope
**Solutions**:
- Check endpoint documentation for required scope
- Verify your key has the scope: `GET /auth/api-keys`
- Generate a new key with broader scopes
- Example: To access `read:diary`, your key must have `read:diary` in its scopes

### "429 Too Many Requests"
**Cause**: Exceeded rate limit
**Solutions**:
- Wait for rate limit window to reset (shown in `Retry-After` header)
- Check current rate limit: `GET /auth/rate-limit`
- Reduce request frequency
- Request higher rate limit when creating key (if appropriate use case)

### "404 Not Found"
**Cause**: Resource doesn't exist
**Solutions**:
- Verify the ID is correct
- Check resource hasn't been deleted
- Use search endpoints to find resource ID

### "400 Validation Error"
**Cause**: Invalid request data
**Solutions**:
- Check parameter types (integer, string, date format)
- Verify required fields are present
- Review error `details` field for specific issue
- Example: `date_from` must be "YYYY-MM-DD" format

### API Works in Swagger UI but Not in Code
**Cause**: Headers or parameters not formatted correctly
**Solutions**:
- Check you're using `X-API-Key` (exact case)
- Verify parameters are in correct location (path vs query vs body)
- Use Swagger "Try it out" to see exact request format
- Check response status code (may be success even if data looks wrong)

### "Database Error" (500)
**Cause**: Unexpected server error
**Solutions**:
- Try request again (transient issue)
- Check server logs (if running locally)
- Report bug with request details if reproducible
- Use database integrity check: `GET /settings/integrity-check`

---

## Additional Resources

- **Interactive API Docs**: http://localhost:5000/api/docs
- **OpenAPI Spec**: http://localhost:5000/api/v1/apispec.json
- **Quick Reference**: See `api_endpoints.md`
- **Source Code**: `routes/api_v1/` (each file documents its endpoints)
- **Settings**: `config.py` (API configuration)

---

**Last Updated**: February 28, 2026
**Version**: 1.0.0
