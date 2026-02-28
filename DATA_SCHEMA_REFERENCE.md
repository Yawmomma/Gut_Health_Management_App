# Data Schema Reference

**Version**: 1.0.0
**Last Updated**: February 28, 2026

Complete field definitions and data types for all API request/response objects.

---

## Table of Contents

1. [Diary Objects](#diary-objects)
2. [Food Objects](#food-objects)
3. [Recipe Objects](#recipe-objects)
4. [Analytics Objects](#analytics-objects)
5. [User & Account Objects](#user--account-objects)
6. [Error Objects](#error-objects)
7. [Pagination Objects](#pagination-objects)

---

## Diary Objects

### Meal Object

Represents a single meal entry.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | — | Unique identifier (read-only) |
| date | string (date) | Yes | Entry date (YYYY-MM-DD) |
| meal_type | enum | Yes | One of: "breakfast", "lunch", "dinner", "snack" |
| foods | array[FoodInMeal] | Yes | Foods in this meal (min 1) |
| notes | string | No | Optional user notes (max 500 chars) |
| created_at | string (datetime) | — | Creation timestamp (read-only) |
| updated_at | string (datetime) | — | Last update timestamp (read-only) |
| nutrition | NutritionInfo | — | Aggregated nutrition (read-only) |

**Example**:
```json
{
  "id": 123,
  "date": "2026-02-28",
  "meal_type": "breakfast",
  "foods": [
    {
      "food_id": 456,
      "serving_size": "1 cup",
      "quantity": 1
    }
  ],
  "notes": "Felt great after",
  "nutrition": {
    "calories": 450,
    "protein_g": 15,
    "carbs_g": 65,
    "fat_g": 12,
    "fiber_g": 8
  },
  "created_at": "2026-02-28T12:00:00Z",
  "updated_at": "2026-02-28T12:00:00Z"
}
```

### FoodInMeal Object

A food within a meal, linking food + serving info.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| food_id | integer | Yes | Foreign key to Food |
| serving_size | string | Yes | Description like "1 cup", "150g" |
| quantity | number | Yes | Number of servings (e.g., 1.5) |
| custom_quantity | string | No | Free-text override (e.g., "handful") |
| notes | string | No | Food-specific notes |

**Example**:
```json
{
  "food_id": 456,
  "serving_size": "1 cup",
  "quantity": 1,
  "notes": "Extra virgin olive oil"
}
```

### Symptom Object

Represents a recorded symptom.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | — | Unique identifier (read-only) |
| date | string (date) | Yes | Symptom date (YYYY-MM-DD) |
| symptom | string | Yes | Symptom name (e.g., "Bloating", "Diarrhea") |
| severity | integer | Yes | 1-10 scale (1=mild, 10=severe) |
| notes | string | No | Additional context (max 500 chars) |
| related_meals | array[integer] | — | Meal IDs on same day (read-only, inferred) |
| created_at | string (datetime) | — | Creation timestamp (read-only) |

**Example**:
```json
{
  "id": 789,
  "date": "2026-02-28",
  "symptom": "Bloating",
  "severity": 6,
  "notes": "Started 2 hours after breakfast",
  "related_meals": [123, 124],
  "created_at": "2026-02-28T14:30:00Z"
}
```

### Bowel Entry Object

Bristol stool chart tracking.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | — | Unique identifier (read-only) |
| date | string (date) | Yes | Date (YYYY-MM-DD) |
| bristol_type | integer | Yes | 1-7 (see Bristol Stool Chart) |
| notes | string | No | Optional notes |
| created_at | string (datetime) | — | Creation timestamp (read-only) |

**Bristol Stool Types**:
- 1 = Separate hard lumps
- 2 = Lumpy and hard
- 3 = Lumpy and soft
- 4 = Smooth and soft (normal)
- 5 = Soft blobs
- 6 = Fluffy pieces
- 7 = Liquid with no solid (diarrhea)

**Example**:
```json
{
  "id": 101,
  "date": "2026-02-28",
  "bristol_type": 4,
  "notes": "Normal",
  "created_at": "2026-02-28T08:00:00Z"
}
```

---

## Food Objects

### Food (FODMAP) Object

Represents a food in the FODMAP database.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | — | Unique identifier (read-only) |
| name | string | Yes | Food name (max 100 chars) |
| category | string | Yes | Category (e.g., "Fruits", "Vegetables", "Grains") |
| description | string | No | Additional info about the food |
| traffic_light | enum | — | "green", "amber", "red" (computed from serving sizes) |
| serving_sizes | array[ServingSize] | Yes | Array of serving size definitions |
| histamine | object | Yes | Histamine information |
| usda_food_id | integer | No | Link to USDA food ID |
| ausnut_food_id | integer | No | Link to AusNut food ID |
| created_at | string (datetime) | — | Creation timestamp (read-only) |
| updated_at | string (datetime) | — | Last update timestamp (read-only) |

**Example**:
```json
{
  "id": 456,
  "name": "Apple",
  "category": "Fruits",
  "description": "Red delicious apple",
  "traffic_light": "amber",
  "serving_sizes": [
    {
      "size": "1 medium (182g)",
      "traffic_light": "green",
      "fructose": "low",
      "fructans": "moderate",
      "gos": "low",
      "lactose": "low",
      "polyols": "low",
      "sorbitol": "low",
      "mannitol": "low"
    }
  ],
  "histamine": {
    "level": "low",
    "dao_blocker": false,
    "liberator": false
  },
  "created_at": "2026-01-01T00:00:00Z"
}
```

### ServingSize Object

Defines FODMAP ratings for a specific serving size.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| size | string | Yes | Serving description (e.g., "1 cup", "150g") |
| traffic_light | enum | — | "green", "amber", "red" (worst rating of FODMAP types) |
| fructose | enum | Yes | "low", "moderate", "high" |
| fructans | enum | Yes | "low", "moderate", "high" |
| gos | enum | Yes | "low", "moderate", "high" |
| lactose | enum | Yes | "low", "moderate", "high" |
| polyols | enum | Yes | "low", "moderate", "high" |
| sorbitol | enum | Yes | "low", "moderate", "high" |
| mannitol | enum | Yes | "low", "moderate", "high" |

**Example**:
```json
{
  "size": "1 cup (150g)",
  "traffic_light": "green",
  "fructose": "low",
  "fructans": "low",
  "gos": "safe",
  "lactose": "low",
  "polyols": "low",
  "sorbitol": "low",
  "mannitol": "low"
}
```

### Histamine Object

Histamine level and enzyme info.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| level | enum | Yes | "low", "medium", "high" |
| dao_blocker | boolean | Yes | True if blocks DAO enzyme (e.g., alcohol, tomatoes) |
| liberator | boolean | Yes | True if releases histamine from mast cells |

**Example**:
```json
{
  "level": "low",
  "dao_blocker": false,
  "liberator": false
}
```

### USDA Food Object

Nutritional information from USDA FoodData Central.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | — | USDA FDC ID (read-only) |
| name | string | — | Food name |
| category | string | — | USDA category |
| nutrients | object | — | Nutrient values per 100g or per serving |
| serving_size | string | — | Standard serving size |
| data_type | string | — | "Foundation", "SR Legacy", etc. |

**Example**:
```json
{
  "id": 123456,
  "name": "Chicken breast, skinless",
  "category": "Poultry",
  "nutrients": {
    "energy_kcal": 165,
    "protein_g": 31,
    "fat_g": 3.6,
    "carbs_g": 0,
    "fiber_g": 0,
    "calcium_mg": 15,
    "iron_mg": 1.04
  },
  "serving_size": "100g"
}
```

---

## Recipe Objects

### Recipe Object

A saved recipe/meal template.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | — | Unique identifier (read-only) |
| name | string | Yes | Recipe name (max 100 chars) |
| ingredients | array[Ingredient] | Yes | Ingredients (min 1) |
| instructions | string | Yes | Preparation steps (markdown supported, max 2000 chars) |
| serving_size | string | No | Standard serving (e.g., "1 plate", "4 servings") |
| prep_time_min | integer | No | Preparation time in minutes |
| cook_time_min | integer | No | Cooking time in minutes |
| tags | array[string] | No | Tags like "low-fodmap", "quick", "vegan" |
| nutrition | NutritionInfo | — | Aggregated nutrition per serving (read-only) |
| fodmap_rating | enum | — | "green", "amber", "red" (worst ingredient) (read-only) |
| created_at | string (datetime) | — | Creation timestamp (read-only) |
| updated_at | string (datetime) | — | Last update timestamp (read-only) |

**Example**:
```json
{
  "id": 5,
  "name": "Grilled Salmon with Rice",
  "ingredients": [
    {
      "name": "Salmon fillet",
      "quantity": 1,
      "unit": "fillet (150g)",
      "food_id": 456
    },
    {
      "name": "White rice",
      "quantity": 0.75,
      "unit": "cups",
      "food_id": 789
    }
  ],
  "instructions": "1. Heat grill to 400F\n2. Grill salmon 4-5 min per side\n3. Serve with cooked rice",
  "serving_size": "1 plate",
  "prep_time_min": 10,
  "cook_time_min": 12,
  "tags": ["low-fodmap", "quick", "pescatarian"],
  "nutrition": {
    "calories": 450,
    "protein_g": 35,
    "carbs_g": 45,
    "fat_g": 15
  },
  "fodmap_rating": "green",
  "created_at": "2026-02-28T12:00:00Z"
}
```

### Ingredient Object

An ingredient in a recipe.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Ingredient name |
| quantity | number | Yes | Amount (e.g., 1, 0.5, 2.5) |
| unit | string | Yes | Unit (e.g., "cup", "g", "tbsp", "fillet") |
| food_id | integer | No | Link to Food object (for FODMAP lookup) |
| notes | string | No | Optional prep notes |

**Example**:
```json
{
  "name": "Olive oil",
  "quantity": 2,
  "unit": "tbsp",
  "notes": "Extra virgin, first cold pressed"
}
```

---

## Analytics Objects

### NutritionInfo Object

Aggregated nutritional information.

| Field | Type | Description |
|-------|------|-------------|
| calories | number | Energy (kcal) |
| protein_g | number | Protein (grams) |
| carbs_g | number | Carbohydrates (grams) |
| fat_g | number | Total fat (grams) |
| fiber_g | number | Dietary fiber (grams) |
| calcium_mg | number | Calcium (mg) |
| iron_mg | number | Iron (mg) |
| vitamin_d_ug | number | Vitamin D (micrograms) |
| sodium_mg | number | Sodium (mg) |

**Example**:
```json
{
  "calories": 450,
  "protein_g": 35,
  "carbs_g": 45,
  "fat_g": 15,
  "fiber_g": 8,
  "calcium_mg": 50,
  "iron_mg": 2.5
}
```

### SymptomTrend Object

Symptom data over time.

| Field | Type | Description |
|-------|------|-------------|
| name | string | Symptom name |
| trend | enum | "improving", "stable", "worsening" |
| daily_avg | number | Average severity (1-10) |
| values | array[number] | Daily severity values |
| dates | array[string] | Corresponding dates (YYYY-MM-DD) |

**Example**:
```json
{
  "name": "Bloating",
  "trend": "improving",
  "daily_avg": 3.2,
  "values": [4, 3.5, 3.2, 3.1, 3, 2.9],
  "dates": ["2026-02-23", "2026-02-24", "2026-02-25", "2026-02-26", "2026-02-27", "2026-02-28"]
}
```

### TriggerFood Object

A food that correlates with symptoms.

| Field | Type | Description |
|-------|------|-------------|
| food_id | integer | Food ID |
| name | string | Food name |
| symptom_rate | number | 0-1 (probability of triggering symptom) |
| avg_severity | number | Average symptom severity when triggered |
| times_triggered | integer | Count of symptom occurrences after eating this |
| last_triggered | string (date) | Last date this food caused symptoms |

**Example**:
```json
{
  "food_id": 101,
  "name": "Garlic",
  "symptom_rate": 0.92,
  "avg_severity": 7,
  "times_triggered": 8,
  "last_triggered": "2026-02-20"
}
```

---

## User & Account Objects

### API Key Object

Authentication key for programmatic access.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | integer | — | Unique identifier (read-only) |
| name | string | Yes | Human-readable name (max 100 chars) |
| key | string | Yes* | Full 64-char hex key (only shown once at creation) |
| key_prefix | string | — | First 8 chars for display (read-only) |
| scopes | array[string] | Yes | Granted scopes (e.g., ["read:diary", "write:recipes"]) |
| rate_limit | integer | Yes | Requests per minute (default: 120) |
| is_active | boolean | — | If false, key is revoked (default: true) |
| created_at | string (datetime) | — | Creation timestamp (read-only) |
| expires_at | string (datetime) | No | Expiration date (null = never expires) |
| last_used | string (datetime) | — | Last usage timestamp (read-only) |

*Only returned in creation response

**Example**:
```json
{
  "id": 5,
  "name": "APP2 Analytics",
  "key": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
  "key_prefix": "abcdef01",
  "scopes": ["read:diary", "read:analytics", "read:recipes"],
  "rate_limit": 200,
  "is_active": true,
  "created_at": "2026-02-28T12:00:00Z",
  "expires_at": "2027-02-28T23:59:59Z",
  "last_used": "2026-02-28T14:30:00Z"
}
```

### Access Log Object

Record of an API request.

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Unique identifier |
| key_id | integer | API key used (foreign key) |
| endpoint | string | API endpoint called (e.g., "/diary/entries") |
| method | string | HTTP method (GET, POST, PUT, DELETE) |
| status_code | integer | HTTP response code |
| ip_address | string | Client IP address |
| timestamp | string (datetime) | Request timestamp |

**Example**:
```json
{
  "id": 12345,
  "key_id": 5,
  "endpoint": "/diary/entries",
  "method": "GET",
  "status_code": 200,
  "ip_address": "192.168.1.100",
  "timestamp": "2026-02-28T14:30:00Z"
}
```

---

## Error Objects

### Error Response

All errors follow this structure.

| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Always false |
| error | object | Error details |
| error.code | string | Machine-readable error code |
| error.message | string | Human-readable error message |
| error.details | object | Additional context (varies by error type) |

**Example**:
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid serving size: must be positive",
    "details": {
      "field": "serving_size",
      "value": -10,
      "constraint": "must be positive"
    }
  }
}
```

### Standard Error Codes

| Code | HTTP Status | Meaning |
|------|-------------|---------|
| VALIDATION_ERROR | 400 | Invalid request data |
| MISSING_REQUIRED_FIELD | 400 | Required field missing |
| UNAUTHORIZED | 401 | Invalid/missing API key |
| FORBIDDEN | 403 | Insufficient scope |
| NOT_FOUND | 404 | Resource not found |
| ALREADY_EXISTS | 409 | Resource already exists |
| RATE_LIMIT_EXCEEDED | 429 | Rate limit exceeded |
| DATABASE_ERROR | 500 | Unexpected server error |
| NOT_IMPLEMENTED | 501 | Endpoint not yet implemented |

---

## Pagination Objects

### Pagination Metadata

Included in responses that return collections.

| Field | Type | Description |
|-------|------|-------------|
| page | integer | Current page (1-indexed) |
| per_page | integer | Items per page |
| total | integer | Total items across all pages |
| pages | integer | Total number of pages |
| has_next | boolean | If there's a next page |
| has_prev | boolean | If there's a previous page |

**Example**:
```json
{
  "page": 1,
  "per_page": 20,
  "total": 247,
  "pages": 13,
  "has_next": true,
  "has_prev": false
}
```

### Paginated Response

Collections return data nested in pagination.

**Example**:
```json
{
  "success": true,
  "data": {
    "data": [
      { "id": 1, "name": "Item 1" },
      { "id": 2, "name": "Item 2" }
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

---

## Common Enum Values

### FODMAP Levels
- "low" — Safe at listed serving
- "moderate" — Moderate amount
- "high" — High, may trigger symptoms

### Meal Types
- "breakfast"
- "lunch"
- "dinner"
- "snack"

### Traffic Light Status
- "green" — Safe
- "amber" — Moderate risk
- "red" — High risk

### Trend Direction
- "improving" — Getting better
- "stable" — No change
- "worsening" — Getting worse

### Histamine Levels
- "low" — Low histamine
- "medium" — Moderate histamine
- "high" — High histamine

---

**Last Updated**: February 28, 2026
**Version**: 1.0.0
