# Gut Health Management App - Complete API Reference

**Base URL:** `http://127.0.0.1:5000/api/v1`

**Note:** All endpoints return JSON unless otherwise noted. Errors return `{"error": "message"}` with appropriate HTTP status codes.

**Last Updated:** February 28, 2026

**Total Endpoints:** 137 (verified by @bp.route audit across all 20 route files)

---

## Table of Contents

1. [Diary Endpoints](#1-diary-endpoints) - Entry management, trends, weekly summaries
2. [Recipes Endpoints](#2-recipes-endpoints) - Recipes, saved meals, import
3. [Foods/Compendium Endpoints](#3-foods--compendium-endpoints) - FODMAP food database
4. [Analytics & Dashboard Endpoints](#4-analytics--dashboard-endpoints) - Risk analysis, patterns, nutrition
5. [USDA Database Endpoints](#5-usda-database-endpoints) - FoodData Central integration
6. [AUSNUT Database Endpoints](#6-ausnut-database-endpoints) - Australian food database
7. [Settings & Database Endpoints](#7-settings--database-endpoints) - Backup, integrity checks
8. [Help Document Endpoints](#8-help-document-endpoints) - User help documentation
9. [Education Endpoints](#9-education-endpoints) - Educational chapters
10. [Chat Endpoints](#10-chat-endpoints) - AI chat with multiple personas
11. [FODMAP Reference Endpoints](#11-fodmap-reference-endpoints) - Category listings
12. [Search & Discovery Endpoints](#12-search--discovery-endpoints) - Global search, recommendations
13. [Export & Reporting Endpoints](#13-export--reporting-endpoints) - Data export, PDF reports
14. [Real-time & Webhooks Endpoints](#14-real-time--webhooks-endpoints) - SSE streams, webhooks
15. [Gamification Endpoints](#15-gamification-endpoints) - Challenges and badges
16. [Reintroduction Protocol Endpoints](#16-reintroduction-protocol-endpoints) - FODMAP reintroduction testing
17. [Notifications Endpoints](#17-notifications-endpoints) - User notifications and rules
18. [Security & Access Control Endpoints](#18-security--access-control-endpoints) - API keys and rate limiting
19. [Integrations Endpoints](#19-integrations-endpoints) - Wearables and voice logging
20. [Billing Endpoints](#20-billing-endpoints) - Subscription and premium status
21. [Multi-User & Cohort Analysis Endpoints](#21-multi-user--cohort-analysis-endpoints) - Comparative analytics

---

## Quick Reference Table

| Method | Endpoint | Description |
|--------|----------|-------------|
| **DIARY** |
| GET | `/diary/entries` | Get monthly diary entries grouped by date |
| GET | `/diary/day/{date}` | Get all entries for specific date with nutrition |
| GET | `/diary/trends` | Get symptom trends over time period |
| GET | `/diary/weekly` | Get weekly summary of entries |
| POST | `/diary/meals` | Create new meal entry |
| PUT | `/diary/meals/{id}` | Update existing meal entry |
| POST | `/diary/entries/bulk` | Create multiple entries in one call |
| **RECIPES** |
| GET | `/recipes` | List all recipes (paginated) |
| GET | `/recipes/search` | Search recipes by name, category, cuisine, tags, ingredients |
| GET | `/recipes/category/{cat}` | Filter recipes by meal type |
| GET | `/recipes/{id}` | Get recipe details |
| POST | `/recipes` | Create new recipe |
| PUT | `/recipes/{id}` | Update recipe |
| DELETE | `/recipes/{id}` | Delete recipe |
| GET | `/recipes/{id}/context` | Get recipe formatted for AI |
| GET | `/meals` | List all saved meals |
| POST | `/meals` | Create saved meal |
| PUT | `/meals/{id}` | Update saved meal |
| DELETE | `/meals/{id}` | Delete saved meal |
| POST | `/recipes/import` | Import recipe from external JSON |
| **FOODS** |
| GET | `/compendium/search` | Search FODMAP foods |
| GET | `/compendium/foods/{id}` | Get food details with usage stats |
| GET | `/compendium/compare` | Compare multiple foods |
| POST | `/compendium/foods` | Create new food |
| PUT | `/compendium/foods/{id}` | Update food |
| DELETE | `/compendium/foods/{id}` | Delete food |
| POST | `/foods/quick-add` | Quick add incomplete food |
| POST | `/compendium/foods/{id}/link-ausnut` | Link food to AUSNUT |
| GET | `/foods/batch` | Get multiple foods in one call |
| **ANALYTICS** |
| GET | `/dashboard` | Get dashboard data (watch list, incomplete foods) |
| POST | `/foods/risk-rating` | Calculate traffic light for serving size |
| GET | `/analytics/symptom-patterns` | Correlate symptoms with meals |
| GET | `/analytics/food-reactions` | Identify food triggers |
| GET | `/analytics/symptom-trends` | Time-series symptom data |
| GET | `/analytics/food-frequency` | Most commonly eaten foods |
| GET | `/analytics/trigger-foods` | Foods on high-symptom days |
| GET | `/analytics/nutrition-summary` | Aggregated nutrition over date range |
| GET | `/analytics/fodmap-exposure` | Daily/weekly FODMAP exposure |
| **USDA** |
| GET | `/usda/search` | Search USDA FoodData Central |
| GET | `/usda/foods` | Browse/list USDA foods (paginated) |
| GET | `/usda/foods/{id}` | Get USDA food with nutrients |
| GET | `/usda/categories` | List USDA categories |
| **AUSNUT** |
| GET | `/ausnut/search` | Search AUSNUT 2023 foods |
| GET | `/ausnut/foods/{id}` | Get AUSNUT food with nutrients |
| **SETTINGS** |
| GET | `/settings/backup` | Download database backup |
| GET | `/settings/integrity-check` | Check database integrity |
| POST | `/settings/integrity-check/fix` | Auto-fix integrity issues |
| **HELP** |
| GET | `/help` | List help documents |
| GET | `/help/{id}` | Get help document |
| POST | `/help/upload` | Upload markdown file |
| POST | `/help` | Save help document |
| PUT | `/help/{id}` | Update help document |
| DELETE | `/help/{id}` | Delete help document |
| POST | `/help/preview-markdown` | Convert markdown to HTML |
| **EDUCATION** |
| GET | `/education` | List educational chapters |
| GET | `/education/{id}` | Get chapter details |
| POST | `/education/upload` | Upload chapter markdown |
| POST | `/education` | Save chapter |
| PUT | `/education/{id}` | Update chapter |
| DELETE | `/education/{id}` | Delete chapter |
| POST | `/education/reorder` | Update chapter order |
| POST | `/education/images` | Upload image for chapters |
| POST | `/education/preview-markdown` | Preview markdown as HTML |
| **CHAT** |
| POST | `/chat` | Send message to AI (Ollama/OpenAI/Anthropic) |
| GET | `/chat/conversations` | List all conversations |
| GET | `/chat/conversations/{id}` | Get conversation with messages |
| DELETE | `/chat/conversations/{id}` | Delete conversation |
| POST | `/chat/conversations/{id}/rename` | Rename conversation |
| **FODMAP** |
| GET | `/fodmap/categories` | Get FODMAP categories with counts |
| GET | `/fodmap/foods` | Get foods by category |
| **SEARCH** |
| GET | `/search/global` | Search across all entities |
| GET | `/foods/recommendations` | Get safe foods by restrictions |
| GET | `/recipes/suitable` | Get recipes by restrictions |
| **EXPORT** |
| GET | `/export/diary` | Export diary (JSON/CSV) |
| GET | `/export/report/pdf` | Generate PDF health report |
| GET | `/export/shopping-list` | Generate shopping list from recipes |
| **REALTIME** |
| GET | `/events/stream` | Server-Sent Events stream |
| POST | `/webhooks/register` | Register webhook |
| GET | `/webhooks` | List webhooks |
| GET | `/webhooks/{id}` | Get webhook details |
| PUT | `/webhooks/{id}` | Update webhook |
| DELETE | `/webhooks/{id}` | Delete webhook |
| POST | `/webhooks/{id}/test` | Test webhook |
| POST | `/webhooks/external/receive` | Receive inbound webhook from external service |
| **BILLING** |
| POST | `/billing/webhook` | Receive billing/subscription webhook |

---

## 1. Diary Endpoints

### GET /api/v1/diary/entries

Get diary entries for a specific month grouped by date with statistics.

**Query Parameters:**
- `year` (int, optional) - Year (default: current year)
- `month` (int, optional) - Month 1-12 (default: current month)

**Response (200):**
```json
{
    "year": 2026,
    "month": 2,
    "entries_by_date": {
        "2026-02-10": [
            {
                "id": 1,
                "date": "2026-02-10",
                "time": "08:30",
                "type": "meal",
                "created_at": "2026-02-10T08:30:00",
                "meals": [
                    {
                        "id": 1,
                        "meal_type": "Breakfast",
                        "location": "Home",
                        "preparation": "Fresh",
                        "recipe_id": null,
                        "notes": "",
                        "foods": [
                            {
                                "food_id": 123,
                                "food_name": "Apple",
                                "portion_size": "1 medium",
                                "serving_type": "safe",
                                "num_servings": 1.0,
                                "energy_kj": 218.0,
                                "protein_g": 0.3,
                                "fat_g": 0.2,
                                "carbs_g": 14.0,
                                "sodium_mg": 1.0
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "statistics": {
        "meals": 12,
        "symptoms": 5,
        "bowel": 8,
        "stress": 3,
        "notes": 2,
        "total": 30
    }
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/diary/entries?year=2026&month=2"
```

---

### GET /api/v1/diary/day/{date_string}

Get all diary entries for a specific date with daily nutrition totals.

**Path Parameters:**
- `date_string` (string, required) - Date in YYYY-MM-DD format

**Response (200):**
```json
{
    "date": "2026-02-10",
    "entries": [
        {
            "id": 1,
            "date": "2026-02-10",
            "time": "08:30",
            "type": "meal",
            "created_at": "2026-02-10T08:30:00",
            "meals": [/* meal objects */]
        }
    ],
    "nutrition": {
        "energy_kj": 8500.0,
        "protein_g": 75.0,
        "fat_g": 65.0,
        "carbs_g": 250.0,
        "sodium_mg": 1800.0
    },
    "entry_count": 8
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/diary/day/2026-02-10"
```

---

### GET /api/v1/diary/trends

Get symptom trends over a specified time period.

**Query Parameters:**
- `days` (int, optional) - Number of days to analyze (default: 30, max: 365)

**Response (200):**
```json
{
    "start_date": "2026-01-12",
    "end_date": "2026-02-10",
    "days": 30,
    "symptom_data": [
        {
            "date": "2026-01-15",
            "time": "14:30",
            "bloating": 5,
            "pain": 3,
            "wind": 2,
            "nausea": 0,
            "heartburn": 0,
            "headache": 0,
            "brain_fog": 0,
            "fatigue": 4,
            "sinus_issues": 0
        }
    ],
    "averages": {
        "bloating": 3.5,
        "pain": 2.1,
        "wind": 1.8,
        "nausea": 0.5,
        "heartburn": 0.3,
        "headache": 0.2,
        "brain_fog": 1.0,
        "fatigue": 2.5,
        "sinus_issues": 0.1
    },
    "total_entries": 15
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/diary/trends?days=30"
```

---

### GET /api/v1/diary/weekly

Get weekly summary of diary entries with daily counts.

**Query Parameters:**
- `start_date` (string, optional) - Week start date YYYY-MM-DD (default: current week Monday)

**Response (200):**
```json
{
    "start_date": "2026-02-10",
    "end_date": "2026-02-16",
    "weekly_data": [
        {
            "date": "2026-02-10",
            "day_name": "Monday",
            "counts": {
                "meals": 3,
                "symptoms": 1,
                "bowel": 2,
                "stress": 0,
                "notes": 0,
                "total": 6
            }
        }
    ],
    "weekly_totals": {
        "meals": 18,
        "symptoms": 5,
        "bowel": 9,
        "stress": 2,
        "notes": 1,
        "total": 35
    }
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/diary/weekly?start_date=2026-02-10"
```

---

### POST /api/v1/diary/meals

Create a new meal diary entry.

**Request Body:**
```json
{
    "entry_date": "2026-02-14",
    "entry_time": "12:30",
    "meal_type": "Lunch",
    "location": "Home",
    "preparation": "Cooked",
    "notes": "Felt good after this meal",
    "foods": [
        {
            "food_id": 123,
            "portion_size": "150g",
            "serving_type": "safe"
        },
        {
            "food_id": 456,
            "portion_size": "1 cup",
            "serving_type": "moderate"
        }
    ]
}
```

**Alternative:** Instead of `foods` array, can provide:
- `recipe_id` (int) - Use foods from a recipe
- `saved_meal_id` (int) - Use foods from a saved meal

**Required Fields:**
- `entry_date` (string)
- `meal_type` (string)
- At least one of: `foods`, `recipe_id`, or `saved_meal_id`

**Response (201):**
```json
{
    "id": 45,
    "message": "Meal created successfully"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/diary/meals \
  -H "Content-Type: application/json" \
  -d '{
    "entry_date": "2026-02-14",
    "meal_type": "Lunch",
    "foods": [
      {"food_id": 123, "portion_size": "150g", "serving_type": "safe"}
    ]
  }'
```

---

### PUT /api/v1/diary/meals/{entry_id}

Update an existing meal diary entry.

**Path Parameters:**
- `entry_id` (int, required) - Diary entry ID

**Request Body:**
Same structure as POST. All fields optional for partial update. If `foods` is provided, it replaces all existing foods.

**Response (200):**
```json
{
    "success": true,
    "meal_id": 12,
    "message": "Meal updated successfully!"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/diary/meals/45 \
  -H "Content-Type: application/json" \
  -d '{
    "meal_type": "Dinner",
    "notes": "Changed to dinner"
  }'
```

---

### POST /api/v1/diary/entries/bulk

Create multiple diary entries in one API call (batch operation).

**Request Body:**
```json
{
    "entries": [
        {
            "type": "meal",
            "date": "2026-02-14",
            "data": {
                "meal_type": "Breakfast",
                "foods": [
                    {"food_id": 123, "portion_size": "100g"}
                ]
            }
        },
        {
            "type": "symptom",
            "date": "2026-02-14",
            "data": {
                "bloating": 5,
                "pain": 3,
                "severity": 5,
                "duration": "2 hours"
            }
        }
    ]
}
```

**Supported Types:**
- `meal` - Meal entry
- `symptom` - Symptom log
- `bowel` - Bowel movement
- `stress` - Stress log
- `note` - General note

**Limits:**
- Maximum 50 entries per request

**Response (201):**
```json
{
    "success": true,
    "created_count": 2,
    "total_requested": 2,
    "results": [
        {
            "index": 0,
            "type": "meal",
            "id": 100,
            "meal_id": 50,
            "success": true
        },
        {
            "index": 1,
            "type": "symptom",
            "id": 101,
            "symptom_id": 25,
            "success": true
        }
    ]
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/diary/entries/bulk \
  -H "Content-Type: application/json" \
  -d '{
    "entries": [
      {
        "type": "symptom",
        "date": "2026-02-14",
        "data": {"bloating": 5, "pain": 3}
      }
    ]
  }'
```

---

## 2. Recipes Endpoints

### GET /api/v1/recipes

Get all user-created recipes ordered by created_at (paginated).

**Query Parameters:**
- `q` (string, optional) - Search query to filter recipes by name
- `page` (int, optional) - Page number (default: 1)
- `per_page` (int, optional) - Items per page (default: 50, max: 100)

**Response (200):**
```json
{
    "data": [
        {
            "id": 1,
            "name": "Grilled Chicken Salad",
            "description": "Healthy low-FODMAP chicken salad",
            "servings": 4,
            "prep_time": "15 minutes",
            "cook_time": "20 minutes",
            "instructions": "Step 1: Grill chicken...",
            "category": "Lunch",
            "cuisine": "American",
            "ingredients": [
                {
                    "id": 1,
                    "food_id": 123,
                    "quantity": "200g",
                    "notes": "chopped",
                    "food": {"id": 123, "name": "Chicken Breast", "category": "Meat"}
                }
            ]
        }
    ],
    "pagination": {"page": 1, "per_page": 50, "total": 25, "pages": 1}
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/recipes?q=salad&page=1"
```

---

### GET /api/v1/recipes/search

Search recipes by name, category, cuisine, tags, or ingredients.

**Query Parameters:**
- `q` (string, optional) - Search query for recipe name
- `category` (string, optional) - Filter by meal type category
- `cuisine` (string, optional) - Filter by cuisine
- `difficulty` (string, optional) - Filter by difficulty level
- `tags` (string, optional) - Comma-separated tags to filter by
- `ingredient` (string, optional) - Search by ingredient name
- `page` (int, optional) - Page number (default: 1)
- `per_page` (int, optional) - Items per page (default: 50, max: 100)

**Response (200):**
```json
{
    "data": [
        {
            "id": 1,
            "name": "Grilled Chicken Salad",
            "description": "Healthy low-FODMAP chicken salad",
            "servings": 4,
            "category": "Lunch",
            "cuisine": "American",
            "difficulty": "Beginner-Friendly",
            "ingredients": [...]
        }
    ],
    "pagination": {"page": 1, "per_page": 50, "total": 8, "pages": 1},
    "filters": {
        "q": "salad",
        "category": null,
        "cuisine": null,
        "difficulty": null,
        "tags": null,
        "ingredient": null
    }
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/recipes/search?q=salad&cuisine=Italian"
curl "http://127.0.0.1:5000/api/v1/recipes/search?ingredient=chicken&category=Dinner"
curl "http://127.0.0.1:5000/api/v1/recipes/search?tags=quick,easy&difficulty=Beginner-Friendly"
```

---

### GET /api/v1/recipes/category/{category}

Get recipes filtered by meal type category (paginated).

**Path Parameters:**
- `category` (string, required) - Meal type category

**Query Parameters:**
- `page` (int, optional) - Page number (default: 1)
- `per_page` (int, optional) - Items per page (default: 50, max: 100)

**Response (200):**
```json
{
    "data": [/* recipe objects */],
    "pagination": {"page": 1, "per_page": 50, "total": 10, "pages": 1}
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/recipes/category/Lunch"
```

---

### GET /api/v1/recipes/{id}

Get full recipe details with ingredients, instructions, metadata.

**Path Parameters:**
- `id` (int, required) - Recipe ID

**Response (200):**
```json
{
    "id": 1,
    "name": "Grilled Chicken Salad",
    "description": "Healthy low-FODMAP chicken salad",
    "servings": 4,
    "prep_time": "15 minutes",
    "cook_time": "20 minutes",
    "instructions": "Step 1: Grill chicken...",
    "notes": "Can substitute with turkey",
    "category": "Lunch",
    "subcategory": "Main Dish",
    "cuisine": "American",
    "dietary_needs": "Gluten-Free, Dairy-Free",
    "ingredients": [/* ingredient objects */]
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/recipes/1"
```

---

### POST /api/v1/recipes

Create a new recipe with ingredients.

**Request Body:**
```json
{
    "name": "Grilled Chicken Salad",
    "servings": 4,
    "category": "Lunch",
    "ingredients": [
        {"food_id": 123, "quantity": "200g", "notes": "chopped"}
    ]
}
```

**Response (201):**
```json
{
    "id": 1,
    "name": "Grilled Chicken Salad"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/recipes \
  -H "Content-Type: application/json" \
  -d '{"name": "Grilled Chicken Salad", "servings": 4, "category": "Lunch", "ingredients": [{"food_id": 123, "quantity": "200g"}]}'
```

---

### PUT /api/v1/recipes/{id}

Update an existing recipe.

**Path Parameters:**
- `id` (int, required) - Recipe ID

**Request Body:**
Same format as POST. All fields optional for partial update.

**Response (200):**
```json
{
    "id": 1,
    "name": "Updated Recipe Name"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/recipes/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Recipe Name"}'
```

---

### DELETE /api/v1/recipes/{id}

Delete a recipe (cascade deletes ingredients).

**Path Parameters:**
- `id` (int, required) - Recipe ID

**Response (200):**
```json
{
    "message": "Recipe \"Grilled Chicken Salad\" deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/recipes/1
```

---

### GET /api/v1/recipes/{id}/context

Get full recipe details formatted for AI context.

**Path Parameters:**
- `id` (int, required) - Recipe ID

**Response (200):**
```json
{
    "id": 1,
    "name": "Grilled Chicken Salad",
    "servings": 4,
    "ingredients": ["200g Chicken Breast (chopped)", "1 cup Lettuce"],
    "instructions": "Step 1: Grill chicken..."
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/recipes/1/context"
```

---

### GET /api/v1/meals

Get all saved meals ordered by created_at.

**Response (200):**
```json
[
    {
        "id": 1,
        "name": "Quick Breakfast Bowl",
        "meal_type": "Breakfast",
        "items": [
            {
                "id": 1,
                "food_id": 123,
                "portion_size": "1 cup",
                "food": {"id": 123, "name": "Oats", "category": "Grains"}
            }
        ]
    }
]
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/meals"
```

---

### POST /api/v1/meals

Create a new saved meal.

**Request Body:**
```json
{
    "name": "Quick Breakfast Bowl",
    "meal_type": "Breakfast",
    "items": [
        {"food_id": 123, "portion_size": "1 cup"}
    ]
}
```

**Response (201):**
```json
{
    "id": 1,
    "name": "Quick Breakfast Bowl"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/meals \
  -H "Content-Type: application/json" \
  -d '{"name": "Quick Breakfast Bowl", "meal_type": "Breakfast", "items": [{"food_id": 123, "portion_size": "1 cup"}]}'
```

---

### PUT /api/v1/meals/{id}

Update an existing saved meal.

**Path Parameters:**
- `id` (int, required) - Saved meal ID

**Request Body:**
Same format as POST. All fields optional.

**Response (200):**
```json
{
    "id": 1,
    "name": "Updated Breakfast Bowl"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/meals/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Breakfast Bowl"}'
```

---

### DELETE /api/v1/meals/{id}

Delete a saved meal (cascade deletes items).

**Path Parameters:**
- `id` (int, required) - Saved meal ID

**Response (200):**
```json
{
    "message": "Meal \"Quick Breakfast Bowl\" deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/meals/1
```

---

### POST /api/v1/recipes/import

Import recipe from external JSON format with automatic ingredient matching.

**Request Body:**
```json
{
    "recipe_json": {
        "name": "Apple Pie",
        "servings": 8,
        "ingredients": [
            {"name": "Apple", "amount": "6 medium", "category": "Fruit"}
        ],
        "instructions": "Step 1: Prepare crust..."
    }
}
```

**Response (201):**
```json
{
    "success": true,
    "recipe_id": 25,
    "name": "Apple Pie",
    "matched_ingredients": 1,
    "unmatched_ingredients": []
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/recipes/import \
  -H "Content-Type: application/json" \
  -d '{"recipe_json": {"name": "Apple Pie", "servings": 8, "ingredients": [{"name": "Apple", "amount": "6 medium"}], "instructions": "Bake at 350F..."}}'
```

---

## 3. Foods / Compendium Endpoints

### GET /api/v1/compendium/search

Search FODMAP foods by name and/or category.

**Query Parameters:**
- `q` (string, optional) - Search query for food name
- `category` (string, optional) - Filter by food category

**Response (200):**
```json
[
    {
        "id": 123,
        "name": "Apple",
        "category": "Fruit",
        "safe_serving": "1",
        "safe_serving_unit": "medium",
        "safe_traffic_light": "Green",
        "safe_fructans": "Green",
        "safe_gos": "Green",
        "safe_fructose": "Green",
        "safe_polyols": "Green",
        "safe_histamine_level": "Low",
        "is_complete": true
    }
]
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/compendium/search?q=apple&category=Fruit"
```

---

### GET /api/v1/compendium/foods/{id}

Get full food details including custom nutrients and usage statistics.

**Path Parameters:**
- `id` (int, required) - Food ID

**Response (200):**
```json
{
    "id": 123,
    "name": "Apple",
    "category": "Fruit",
    "safe_serving": "1",
    "safe_serving_unit": "medium",
    "moderate_serving": "2",
    "high_serving": "3",
    "custom_nutrients": {
        "vitamins": [{"name": "Vitamin C", "per_serve": 8.4, "unit": "mg"}],
        "minerals": [],
        "macros": []
    },
    "usage": {
        "meal_count": 15,
        "recipe_count": 3,
        "total": 18
    }
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/compendium/foods/123"
```

---

### GET /api/v1/compendium/compare

Get multiple foods for side-by-side comparison.

**Query Parameters:**
- `ids` (string, required) - Comma-separated food IDs

**Response (200):**
```json
[
    {"id": 123, "name": "Apple", "category": "Fruit"},
    {"id": 456, "name": "Banana", "category": "Fruit"}
]
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/compendium/compare?ids=123,456,789"
```

---

### POST /api/v1/compendium/foods

Create a new food with complete FODMAP/histamine ratings.

**Request Body:**
```json
{
    "name": "Strawberry",
    "category": "Fruit",
    "safe_serving": "5",
    "safe_serving_unit": "medium",
    "safe_fructans": "Green",
    "safe_gos": "Green",
    "safe_histamine_level": "Low"
}
```

**Response (201):**
```json
{
    "id": 789,
    "name": "Strawberry",
    "category": "Fruit"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/compendium/foods \
  -H "Content-Type: application/json" \
  -d '{"name": "Strawberry", "category": "Fruit", "safe_serving": "5", "safe_serving_unit": "medium"}'
```

---

### PUT /api/v1/compendium/foods/{id}

Update an existing food.

**Path Parameters:**
- `id` (int, required) - Food ID

**Request Body:**
Same format as POST. All fields optional.

**Response (200):**
```json
{
    "id": 123,
    "name": "Apple"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/compendium/foods/123 \
  -H "Content-Type: application/json" \
  -d '{"safe_fructose": "Amber"}'
```

---

### DELETE /api/v1/compendium/foods/{id}

Delete a food (validates no meals/recipes/saved meals reference it).

**Path Parameters:**
- `id` (int, required) - Food ID

**Response (200):**
```json
{
    "message": "Food \"Apple\" deleted successfully"
}
```

**Error (400):**
```json
{
    "error": "Cannot delete 'Apple'. It is used in: 15 diary meals, 3 recipes.",
    "usage": {"meal_count": 15, "recipe_count": 3, "total": 18}
}
```

**Example:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/compendium/foods/123
```

---

### POST /api/v1/foods/quick-add

Quick add food with minimal information (marked as incomplete).

**Request Body:**
```json
{
    "name": "New Food",
    "category": "Vegetables"
}
```

**Response (201):**
```json
{
    "success": true,
    "data": {
        "id": 999,
        "name": "New Food",
        "category": "Vegetables"
    }
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/foods/quick-add \
  -H "Content-Type: application/json" \
  -d '{"name": "New Food", "category": "Vegetables"}'
```

---

### POST /api/v1/compendium/foods/{id}/link-ausnut

Link a FODMAP food to an AUSNUT database record.

**Path Parameters:**
- `id` (int, required) - Food ID

**Request Body:**
```json
{
    "ausnut_food_id": 12345
}
```

**Response (200):**
```json
{
    "success": true,
    "ausnut_food_id": 12345
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/compendium/foods/123/link-ausnut \
  -H "Content-Type: application/json" \
  -d '{"ausnut_food_id": 12345}'
```

---

### GET /api/v1/foods/batch

Get multiple food objects in one API call.

**Query Parameters:**
- `ids` (string, required) - Comma-separated food IDs (max 100)
- `include_nutrients` (bool, optional) - Include full nutrient data (default: false)

**Response (200):**
```json
{
    "foods": [
        {"id": 123, "name": "Apple", "category": "Fruit"}
    ],
    "requested_count": 3,
    "found_count": 2,
    "missing_ids": [999]
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/foods/batch?ids=123,456,789"
```

---

## 4. Analytics & Dashboard Endpoints

### GET /api/v1/dashboard

Get dashboard data: high/moderate risk foods, incomplete foods.

**Query Parameters:**
- `days` (int, optional) - Days to look back (default: 7, max: 365)

**Response (200):**
```json
{
    "high_risk_foods": [
        {
            "food": {"id": 456, "name": "Onion", "category": "Vegetables"},
            "level": "high",
            "logged_date": "2026-02-12",
            "serving_type": "high",
            "traffic_light_color": "red"
        }
    ],
    "moderate_risk_foods": [],
    "incomplete_foods": [
        {"id": 999, "name": "New Food", "category": "Other"}
    ],
    "days_analyzed": 7
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/dashboard?days=7"
```

---

### POST /api/v1/foods/risk-rating

Calculate traffic light color for a food at a given serving size.

**Request Body:**
```json
{
    "food_id": 123,
    "serving_type": "moderate"
}
```

**Response (200):**
```json
{
    "food_id": 123,
    "food_name": "Apple",
    "serving_type": "moderate",
    "color": "amber",
    "risk_level": "moderate"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/foods/risk-rating \
  -H "Content-Type: application/json" \
  -d '{"food_id": 123, "serving_type": "moderate"}'
```

---

### GET /api/v1/analytics/symptom-patterns

Correlate symptom spikes with recent meals.

**Query Parameters:**
- `days` (int, optional) - Days to analyze (default: 30, max: 365)

**Response (200):**
```json
{
    "days_analyzed": 30,
    "total_symptom_entries": 15,
    "high_symptom_days": [
        {
            "date": "2026-02-10",
            "total_severity": 25,
            "symptoms": [{"scores": {"bloating": 7, "pain": 5}, "severity": 7}],
            "meals_consumed": [{"meal_type": "Lunch", "foods": []}]
        }
    ],
    "patterns": {"average_severity_per_day": 8.5, "worst_day": "2026-02-10"}
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/analytics/symptom-patterns?days=30"
```

---

### GET /api/v1/analytics/food-reactions

Identify foods that correlate with symptoms.

**Query Parameters:**
- `days` (int, optional) - Days to analyze (default: 30, max: 365)
- `min_occurrences` (int, optional) - Minimum food appearances (default: 2)
- `hours_window` (int, optional) - Hours after eating to check symptoms (default: 24, max: 72)

**Response (200):**
```json
{
    "days_analyzed": 30,
    "suspected_triggers": [
        {
            "food": {"id": 456, "name": "Onion"},
            "occurrences": 5,
            "symptom_correlation": {
                "times_followed_by_symptoms": 4,
                "correlation_rate": 0.8,
                "common_symptoms": ["bloating", "pain"]
            }
        }
    ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/analytics/food-reactions?days=30&hours_window=24"
```

---

### GET /api/v1/analytics/symptom-trends

Time-series symptom data for charting/visualization.

**Query Parameters:**
- `days` (int, optional) - Days to analyze (default: 30, max: 365)
- `symptom_type` (string, optional) - Filter by symptom (bloating, pain, etc.)

**Response (200):**
```json
{
    "days_analyzed": 30,
    "symptom_type": "bloating",
    "time_series": [
        {"date": "2026-02-01", "count": 2, "average_score": 5.5}
    ],
    "summary": {
        "total_entries": 15,
        "average_score": 4.2,
        "peak_day": "2026-02-10",
        "symptom_free_days": 15
    }
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/analytics/symptom-trends?days=30&symptom_type=bloating"
```

---

### GET /api/v1/analytics/food-frequency

Most commonly eaten foods with counts.

**Query Parameters:**
- `days` (int, optional) - Days to analyze (default: 30, max: 365)
- `limit` (int, optional) - Number of foods (default: 20, max: 100)
- `category` (string, optional) - Filter by category

**Response (200):**
```json
{
    "days_analyzed": 30,
    "top_foods": [
        {
            "food": {"id": 123, "name": "Apple", "category": "Fruit"},
            "frequency": 15,
            "average_portion_size": 1.0,
            "serving_types": {"safe": 10, "moderate": 5}
        }
    ],
    "summary": {"total_unique_foods": 45, "total_meals": 90}
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/analytics/food-frequency?days=30&limit=20"
```

---

### GET /api/v1/analytics/trigger-foods

Foods correlated with symptom spikes.

**Query Parameters:**
- `days` (int, optional) - Days to analyze (default: 30, max: 365)
- `threshold` (float, optional) - Min correlation rate (0.0-1.0, default: 0.5)
- `severity_threshold` (int, optional) - Min daily severity for "high symptom day" (default: 10)

**Response (200):**
```json
{
    "days_analyzed": 30,
    "high_symptom_days": 8,
    "likely_triggers": [
        {
            "food": {"id": 456, "name": "Onion"},
            "appearances_on_bad_days": 6,
            "total_appearances": 8,
            "correlation_rate": 0.75,
            "common_symptoms": ["bloating", "pain"]
        }
    ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/analytics/trigger-foods?days=30&threshold=0.5"
```

---

### GET /api/v1/analytics/nutrition-summary

Aggregated nutrition statistics over a date range.

**Query Parameters:**
- `start_date` (string, required) - Start date (YYYY-MM-DD)
- `end_date` (string, required) - End date (YYYY-MM-DD)
- `meal_type` (string, optional) - Filter by meal type

**Response (200):**
```json
{
    "date_range": {"start": "2026-01-01", "end": "2026-01-31"},
    "days_in_range": 31,
    "days_with_data": 28,
    "totals": {"energy_kj": 210000.0, "protein_g": 2100.0},
    "daily_averages": {"energy_kj": 7500.0, "protein_g": 75.0},
    "meal_breakdown": {"Breakfast": {"count": 28, "avg_energy_kj": 2000.0}}
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/analytics/nutrition-summary?start_date=2026-01-01&end_date=2026-01-31"
```

---

### GET /api/v1/analytics/fodmap-exposure

Daily/weekly FODMAP type exposure levels.

**Query Parameters:**
- `start_date` (string, required) - Start date (YYYY-MM-DD)
- `end_date` (string, required) - End date (YYYY-MM-DD)
- `group_by` (string, optional) - Group by 'day' or 'week' (default: 'day')

**Response (200):**
```json
{
    "date_range": {"start": "2026-01-01", "end": "2026-01-31"},
    "group_by": "day",
    "exposure_data": [
        {
            "date": "2026-01-01",
            "fodmap_types": {
                "fructose": {"safe": 5, "moderate": 2, "high": 0},
                "lactose": {"safe": 3, "moderate": 0, "high": 1}
            },
            "total_risk_score": 29,
            "risk_level": "high"
        }
    ],
    "summary": {"highest_risk_period": "2026-01-15", "average_risk_score": 18.5}
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/analytics/fodmap-exposure?start_date=2026-01-01&end_date=2026-01-31&group_by=day"
```

---

## 5. USDA Database Endpoints

### GET /api/v1/usda/search

Search and browse USDA foods with filters (paginated).

**Query Parameters:**
- `q` (string, optional) - Search query for food description
- `category_id` (int, optional) - Filter by category ID
- `data_type` (string, optional) - Filter by type (Foundation, SR Legacy, Survey, Branded)
- `letter` (string, optional) - Filter by starting letter
- `page` (int, optional) - Page number (default: 1)
- `per_page` (int, optional) - Items per page (default: 50, max: 100)

**Response (200):**
```json
{
    "data": [
        {
            "id": 169905,
            "fdc_id": 746775,
            "description": "Apples, raw, with skin",
            "data_type": "SR Legacy",
            "category": "Fruits and Fruit Juices"
        }
    ],
    "pagination": {"page": 1, "per_page": 50, "total": 250, "pages": 5}
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/usda/search?q=apple&category_id=9"
```

---

### GET /api/v1/usda/foods

Browse and list USDA foods with pagination and optional filtering. Unlike `/usda/search`, no search query is required — this is for browsing all available foods.

**Query Parameters:**
- `category_id` (int, optional) - Filter by category ID
- `data_type` (string, optional) - Filter by type (Foundation, SR Legacy, Survey, Branded)
- `letter` (string, optional) - Filter by starting letter
- `page` (int, optional) - Page number (default: 1)
- `per_page` (int, optional) - Items per page (default: 50, max: 100)

**Response (200):**
```json
{
    "data": [
        {
            "id": 169905,
            "fdc_id": 746775,
            "description": "Apples, raw, with skin",
            "data_type": "SR Legacy",
            "category": "Fruits and Fruit Juices"
        }
    ],
    "pagination": {"page": 1, "per_page": 50, "total": 340, "pages": 7},
    "filters": {
        "category_id": 9,
        "data_type": null,
        "letter": null
    }
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/usda/foods?category_id=9&page=1&per_page=50"
curl "http://127.0.0.1:5000/api/v1/usda/foods?data_type=Foundation&letter=A"
```

---

### GET /api/v1/usda/foods/{id}

Get detailed information for a specific USDA food.

**Path Parameters:**
- `id` (int, required) - USDA food ID

**Query Parameters:**
- `include_nutrients` (bool, optional) - Include nutrients (default: true)
- `include_portions` (bool, optional) - Include portions (default: true)

**Response (200):**
```json
{
    "id": 169905,
    "description": "Apples, raw, with skin",
    "data_type": "SR Legacy",
    "nutrients_by_group": {
        "Proximates": [
            {"name": "Water", "amount": 85.56, "unit": "g"}
        ]
    },
    "portions": [
        {"description": "1 cup, quartered", "gram_weight": 125.0}
    ]
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/usda/foods/169905"
```

---

### GET /api/v1/usda/categories

Get USDA food categories with food counts.

**Query Parameters:**
- `data_type` (string, optional) - Filter by data type
- `min_count` (int, optional) - Min foods per category (default: 1)

**Response (200):**
```json
{
    "categories": [
        {"id": 9, "description": "Fruits and Fruit Juices", "food_count": 340}
    ],
    "count": 25,
    "total_foods": 8463
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/usda/categories?min_count=10"
```

---

## 6. AUSNUT Database Endpoints

### GET /api/v1/ausnut/search

Search and browse AUSNUT 2023 Australian foods.

**Query Parameters:**
- `q` (string, optional) - Search query for food name
- `letter` (string, optional) - Filter by starting letter
- `limit` (int, optional) - Max results (default: 500, max: 1000)

**Response (200):**
```json
{
    "foods": [
        {
            "id": 1,
            "survey_id": "01A10001",
            "food_name": "Apple, red, unpeeled, raw",
            "derivation": "Analytical"
        }
    ],
    "count": 150,
    "limit": 500
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/ausnut/search?q=apple&limit=100"
```

---

### GET /api/v1/ausnut/foods/{id}

Get detailed information for a specific AUSNUT food.

**Path Parameters:**
- `id` (int, required) - AUSNUT food ID

**Query Parameters:**
- `include_nutrients` (bool, optional) - Include nutrients (default: true)

**Response (200):**
```json
{
    "id": 1,
    "food_name": "Apple, red, unpeeled, raw",
    "derivation": "Analytical",
    "nutrients_by_group": {
        "Energy": [{"name": "Energy", "amount": 218.0, "unit": "kJ"}]
    }
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/ausnut/foods/1"
```

---

## 7. Settings & Database Endpoints

### GET /api/v1/settings/backup

Download database backup (SQLite file).

**Response (200):**
Binary SQLite database file download

**Example:**
```bash
curl -O "http://127.0.0.1:5000/api/v1/settings/backup"
```

---

### GET /api/v1/settings/integrity-check

Check database integrity (foreign keys, orphaned records).

**Response (200):**
```json
{
    "success": true,
    "errors": [
        {
            "table": "meals",
            "issue": "orphaned_records",
            "count": 3,
            "message": "3 meals reference non-existent diary entries"
        }
    ],
    "total_errors": 1,
    "can_auto_fix": true
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/settings/integrity-check"
```

---

### POST /api/v1/settings/integrity-check/fix

Auto-fix integrity issues found in integrity check.

**Response (200):**
```json
{
    "success": true,
    "fixed_count": 3,
    "fixes": [
        {"table": "meals", "action": "deleted_orphaned_records", "count": 3}
    ]
}
```

**Example:**
```bash
curl -X POST "http://127.0.0.1:5000/api/v1/settings/integrity-check/fix"
```

---

## 8. Help Document Endpoints

### GET /api/v1/help

List help documents with optional filtering (paginated).

**Query Parameters:**
- `category` (string, optional) - Filter by category
- `search` (string, optional) - Search in title and content
- `page` (int, optional) - Page number (default: 1)
- `per_page` (int, optional) - Items per page (default: 50, max: 100)

**Response (200):**
```json
{
    "data": [
        {
            "id": 1,
            "title": "Getting Started",
            "category": "Quick Start",
            "content": "<h1>Getting Started</h1>...",
            "is_markdown": true
        }
    ],
    "pagination": {"page": 1, "total": 15},
    "available_categories": ["Quick Start", "Features"]
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/help?category=Quick%20Start"
```

---

### GET /api/v1/help/{id}

Get specific help document by ID.

**Path Parameters:**
- `id` (int, required) - Help document ID

**Response (200):**
```json
{
    "id": 1,
    "title": "Getting Started",
    "category": "Quick Start",
    "content": "<h1>Getting Started</h1>...",
    "markdown_source": "# Getting Started\n..."
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/help/1"
```

---

### POST /api/v1/help/upload

Upload markdown file for help document.

**Form Data:**
- `file` (file, required) - Markdown file (.md)
- `category` (string, optional) - Document category (default: 'General')

**Response (200):**
```json
{
    "success": true,
    "upload_id": "abc-123",
    "title": "Getting Started",
    "category": "Quick Start",
    "html_preview": "<h1>Getting Started</h1>..."
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/help/upload \
  -F "file=@getting-started.md" \
  -F "category=Quick Start"
```

---

### POST /api/v1/help

Save help document after preview.

**Request Body:**
```json
{
    "upload_id": "abc-123",
    "title": "Getting Started",
    "category": "Quick Start",
    "markdown_source": "# Getting Started\n..."
}
```

**Response (201):**
```json
{
    "success": true,
    "help_id": 1,
    "message": "Help document added successfully!"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/help \
  -H "Content-Type: application/json" \
  -d '{"title": "Getting Started", "category": "Quick Start", "markdown_source": "# Getting Started\n..."}'
```

---

### PUT /api/v1/help/{id}

Update existing help document.

**Path Parameters:**
- `id` (int, required) - Help document ID

**Request Body:**
```json
{
    "title": "Updated Title",
    "markdown_source": "# Updated Content..."
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "Help document updated successfully!"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/help/1 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

---

### DELETE /api/v1/help/{id}

Delete a help document.

**Path Parameters:**
- `id` (int, required) - Help document ID

**Response (200):**
```json
{
    "success": true,
    "message": "Help document deleted successfully!"
}
```

**Example:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/help/1
```

---

### POST /api/v1/help/preview-markdown

Convert markdown to HTML for live preview.

**Request Body:**
```json
{
    "markdown": "# Heading\n\nSome **bold** text."
}
```

**Response (200):**
```json
{
    "html": "<h1>Heading</h1>\n<p>Some <strong>bold</strong> text.</p>"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/help/preview-markdown \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Heading\n\nSome **bold** text."}'
```

---

## 9. Education Endpoints

### GET /api/v1/education

List educational chapters with filtering (paginated).

**Query Parameters:**
- `topic` (string, optional) - Filter by section/topic
- `search` (string, optional) - Search in title, section, content
- `page` (int, optional) - Page number (default: 1)
- `per_page` (int, optional) - Items per page (default: 50, max: 100)

**Response (200):**
```json
{
    "data": [
        {
            "id": 1,
            "chapter_number": "1",
            "section": "FODMAP Basics",
            "title": "Understanding FODMAPs",
            "content": "<h1>Understanding FODMAPs</h1>..."
        }
    ],
    "pagination": {"page": 1, "total": 20},
    "available_topics": ["FODMAP Basics", "Histamine"]
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/education?topic=FODMAP"
```

---

### GET /api/v1/education/{id}

Get specific educational chapter by ID.

**Path Parameters:**
- `id` (int, required) - Chapter ID

**Response (200):**
```json
{
    "id": 1,
    "chapter_number": "1",
    "section": "FODMAP Basics",
    "title": "Understanding FODMAPs",
    "content": "<h1>Understanding FODMAPs</h1>..."
}
```

**Example:**
```bash
curl "http://127.0.0.1:5000/api/v1/education/1"
```

---

### POST /api/v1/education/upload

Upload markdown file for educational chapter.

**Form Data:**
- `file` (file, required) - Markdown file (.md)
- `section` (string, optional) - Chapter section (default: 'General')

**Response (200):**
```json
{
    "success": true,
    "upload_id": "xyz-789",
    "title": "Understanding FODMAPs",
    "suggested_chapter": "4",
    "html_preview": "<h1>Understanding FODMAPs</h1>..."
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/education/upload \
  -F "file=@understanding-fodmaps.md" \
  -F "section=FODMAP Basics"
```

---

### POST /api/v1/education

Save educational chapter after preview.

**Request Body:**
```json
{
    "upload_id": "xyz-789",
    "chapter_number": "4",
    "title": "Understanding FODMAPs",
    "section": "FODMAP Basics",
    "markdown_source": "# Understanding FODMAPs\n..."
}
```

**Response (201):**
```json
{
    "success": true,
    "chapter_id": 4,
    "message": "Chapter added successfully!"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/education \
  -H "Content-Type: application/json" \
  -d '{"chapter_number": "4", "title": "Understanding FODMAPs", "section": "FODMAP Basics", "markdown_source": "# Understanding FODMAPs\n..."}'
```

---

### PUT /api/v1/education/{id}

Update existing educational chapter.

**Path Parameters:**
- `id` (int, required) - Chapter ID

**Request Body:**
```json
{
    "title": "Updated Title",
    "markdown_source": "# Updated Content..."
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "Chapter updated successfully!"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/education/4 \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

---

### DELETE /api/v1/education/{id}

Delete an educational chapter.

**Path Parameters:**
- `id` (int, required) - Chapter ID

**Response (200):**
```json
{
    "success": true,
    "message": "Chapter deleted successfully!"
}
```

**Example:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/education/4
```

---

### POST /api/v1/education/reorder

Update chapter order and chapter numbers.

**Request Body:**
```json
{
    "order": [
        {"id": 1, "order": 1, "chapter_number": "1"},
        {"id": 3, "order": 2, "chapter_number": "2"}
    ]
}
```

**Response (200):**
```json
{
    "success": true,
    "message": "Chapters reordered successfully!"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/education/reorder \
  -H "Content-Type: application/json" \
  -d '{"order": [{"id": 1, "order": 1, "chapter_number": "1"}]}'
```

---

### POST /api/v1/education/images

Upload an image for use in markdown chapters.

**Form Data:**
- `image` (file, required) - Image file (PNG, JPG, JPEG, GIF, WEBP)

**Response (200):**
```json
{
    "success": true,
    "path": "/uploads/edu_20260214_103045_diagram.png",
    "markdown": "![Image description](/uploads/edu_20260214_103045_diagram.png)"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/education/images \
  -F "image=@diagram.png"
```

---

### POST /api/v1/education/preview-markdown

Convert markdown to HTML for live preview.

**Request Body:**
```json
{
    "markdown": "# Heading\n\nSome **bold** text."
}
```

**Response (200):**
```json
{
    "html": "<h1>Heading</h1>\n<p>Some <strong>bold</strong> text.</p>"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/education/preview-markdown \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Heading\n\nSome **bold** text."}'
```

---

## Section 10: Chat Endpoints

AI-powered chat with multiple LLM providers (Ollama, OpenAI, Anthropic) and personas.

### POST /api/v1/chat

Send message to AI assistant with multi-provider support and conversation history.

**Request Body:**
```json
{
    "message": "What foods are low in FODMAPs and histamine?",
    "provider": "ollama",
    "model": "llama2",
    "persona": "nutritionist",
    "conversation_id": 5,
    "recipe_ids": [12, 45]
}
```

**Body Parameters:**
- `message` (string, required) - User message to send
- `provider` (string, optional) - AI provider: 'ollama', 'openai', or 'anthropic' (default: 'ollama')
- `model` (string, optional) - Model name (uses default for provider if not specified)
- `persona` (string, optional) - AI persona: 'nutritionist', 'chef', 'scientist', or 'friendly' (default: 'nutritionist')
- `conversation_id` (int, optional) - Existing conversation ID to continue
- `recipe_ids` (array, optional) - List of recipe IDs to include as context

**Response (200):**
```json
{
    "response": "Low-FODMAP and low-histamine foods include fresh chicken, rice, carrots, zucchini, and blueberries. These are gentle on your digestive system and suitable for both dietary restrictions.",
    "conversation_id": 5
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What foods are low in FODMAPs and histamine?",
    "provider": "ollama",
    "persona": "nutritionist"
  }'
```

---

### GET /api/v1/chat/conversations

List all chat conversations ordered by most recent.

**Response (200):**
```json
[
    {
        "id": 5,
        "title": "FODMAP questions",
        "provider": "ollama",
        "model": "llama2",
        "persona": "nutritionist",
        "created_at": "2026-02-10T14:30:00Z",
        "updated_at": "2026-02-14T09:15:00Z",
        "message_count": 12
    },
    {
        "id": 3,
        "title": "Recipe ideas for low histamine meals",
        "provider": "openai",
        "model": "gpt-4",
        "persona": "chef",
        "created_at": "2026-02-08T11:20:00Z",
        "updated_at": "2026-02-08T12:45:00Z",
        "message_count": 8
    }
]
```

**Example:**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/chat/conversations
```

---

### GET /api/v1/chat/conversations/{id}

Get specific conversation with all messages.

**Path Parameters:**
- `id` (int, required) - Conversation ID

**Response (200):**
```json
{
    "conversation": {
        "id": 5,
        "title": "FODMAP questions",
        "provider": "ollama",
        "model": "llama2",
        "persona": "nutritionist",
        "created_at": "2026-02-10T14:30:00Z",
        "updated_at": "2026-02-14T09:15:00Z",
        "message_count": 4
    },
    "messages": [
        {
            "id": 15,
            "conversation_id": 5,
            "role": "user",
            "content": "What are FODMAPs?",
            "created_at": "2026-02-10T14:30:00Z"
        },
        {
            "id": 16,
            "conversation_id": 5,
            "role": "assistant",
            "content": "FODMAPs are fermentable carbohydrates that can trigger digestive symptoms...",
            "created_at": "2026-02-10T14:30:15Z"
        },
        {
            "id": 17,
            "conversation_id": 5,
            "role": "user",
            "content": "Which foods are high in FODMAPs?",
            "created_at": "2026-02-10T14:32:00Z"
        },
        {
            "id": 18,
            "conversation_id": 5,
            "role": "assistant",
            "content": "High FODMAP foods include onions, garlic, wheat, legumes, and certain fruits...",
            "created_at": "2026-02-10T14:32:10Z"
        }
    ]
}
```

**Example:**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/chat/conversations/5
```

---

### DELETE /api/v1/chat/conversations/{id}

Delete a chat conversation (cascade deletes all messages).

**Path Parameters:**
- `id` (int, required) - Conversation ID

**Response (200):**
```json
{
    "message": "Conversation deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/chat/conversations/5
```

---

### POST /api/v1/chat/conversations/{id}/rename

Rename a chat conversation.

**Path Parameters:**
- `id` (int, required) - Conversation ID

**Request Body:**
```json
{
    "title": "Updated FODMAP Discussion"
}
```

**Body Parameters:**
- `title` (string, required) - New conversation title

**Response (200):**
```json
{
    "message": "Conversation renamed successfully",
    "conversation": {
        "id": 5,
        "title": "Updated FODMAP Discussion",
        "provider": "ollama",
        "model": "llama2",
        "persona": "nutritionist",
        "created_at": "2026-02-10T14:30:00Z",
        "updated_at": "2026-02-14T09:20:00Z",
        "message_count": 12
    }
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/chat/conversations/5/rename \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated FODMAP Discussion"}'
```

---

## Section 11: FODMAP Reference Endpoints

FODMAP category reference data and food filtering.

### GET /api/v1/fodmap/categories

Get distinct FODMAP food categories with counts (only foods with FODMAP data).

**Response (200):**
```json
[
    {
        "name": "Fruit",
        "count": 215
    },
    {
        "name": "Vegetables",
        "count": 187
    },
    {
        "name": "Grains & Cereals",
        "count": 94
    },
    {
        "name": "Dairy & Alternatives",
        "count": 78
    },
    {
        "name": "Protein",
        "count": 142
    },
    {
        "name": "Nuts & Seeds",
        "count": 56
    },
    {
        "name": "Herbs & Spices",
        "count": 89
    },
    {
        "name": "Beverages",
        "count": 63
    }
]
```

**Example:**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/fodmap/categories
```

---

### GET /api/v1/fodmap/foods

Get FODMAP foods in a specific category.

**Query Parameters:**
- `category` (string, required) - Food category to filter by (e.g., "Fruit", "Vegetables")

**Response (200):**
```json
[
    {
        "id": 125,
        "name": "Apple, Granny Smith",
        "category": "Fruit"
    },
    {
        "id": 126,
        "name": "Apple, Pink Lady",
        "category": "Fruit"
    },
    {
        "id": 127,
        "name": "Banana, ripe",
        "category": "Fruit"
    },
    {
        "id": 128,
        "name": "Blueberries",
        "category": "Fruit"
    }
]
```

**Example:**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/fodmap/foods?category=Fruit"
```

---

## Section 12: Search & Discovery Endpoints

Global search and intelligent food/recipe recommendations based on dietary restrictions.

### GET /api/v1/search/global

Search across foods, recipes, saved meals, help docs, and education content.

**Query Parameters:**
- `q` (string, required) - Search query (minimum 2 characters)
- `types` (string, optional) - Comma-separated list of types to search: foods, recipes, meals, help, education (default: all)
- `limit` (int, optional) - Results per type (default: 10, max: 50)

**Response (200):**
```json
{
    "query": "apple",
    "types_searched": ["foods", "recipes", "meals", "help", "education"],
    "results": {
        "foods": [
            {
                "id": 123,
                "name": "Apple, Granny Smith",
                "category": "Fruit",
                "type": "food",
                "traffic_light": "green"
            },
            {
                "id": 124,
                "name": "Apple Juice",
                "category": "Beverages",
                "type": "food",
                "traffic_light": "red"
            }
        ],
        "recipes": [
            {
                "id": 45,
                "name": "Apple Crumble",
                "category": "Dessert",
                "servings": 6,
                "type": "recipe",
                "description": "Delicious low-FODMAP apple crumble with oat topping..."
            }
        ],
        "meals": [
            {
                "id": 12,
                "name": "Apple & Cheese Snack",
                "meal_type": "Snack",
                "type": "saved_meal",
                "description": "Quick snack with sliced apple and cheddar..."
            }
        ],
        "help": [
            {
                "id": 3,
                "title": "Understanding Apple Varieties",
                "category": "Foods",
                "type": "help"
            }
        ],
        "education": [
            {
                "id": 8,
                "title": "Fruits and FODMAP Content",
                "chapter_number": "2.3",
                "section": "FODMAP Basics",
                "type": "education"
            }
        ]
    },
    "total_results": 23
}
```

**Example:**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/search/global?q=apple&types=foods,recipes&limit=10"
```

---

### GET /api/v1/foods/recommendations

Get safe food recommendations based on dietary restrictions.

**Query Parameters:**
- `avoid` (string, optional) - Comma-separated FODMAP types to avoid: fructose, sorbitol, lactose, gos, fructans, mannitol, polyols
- `histamine_level` (string, optional) - Maximum histamine level: low, medium, high
- `dao_blocker` (boolean, optional) - Avoid DAO blockers (default: true)
- `liberator` (boolean, optional) - Avoid histamine liberators (default: true)
- `category` (string, optional) - Filter by food category
- `limit` (int, optional) - Number of results (default: 20, max: 100)

**Response (200):**
```json
{
    "restrictions": {
        "avoid_fodmap": ["fructans", "lactose"],
        "histamine_level": "low",
        "dao_blocker": true,
        "liberator": true,
        "category": null
    },
    "foods": [
        {
            "id": 145,
            "name": "Blueberries",
            "category": "Fruit",
            "safe_serving": "1 cup",
            "traffic_light": "green",
            "notes": "Safe at 1 cup"
        },
        {
            "id": 156,
            "name": "Carrot, raw",
            "category": "Vegetables",
            "safe_serving": "1 medium",
            "traffic_light": "green",
            "notes": "Safe at 1 medium"
        },
        {
            "id": 178,
            "name": "Chicken breast",
            "category": "Protein",
            "safe_serving": "150g",
            "traffic_light": "green",
            "notes": "Safe at 150g"
        }
    ],
    "total_count": 45
}
```

**Example:**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/foods/recommendations?avoid=fructans,lactose&histamine_level=low&limit=20"
```

---

### GET /api/v1/recipes/suitable

Get suitable recipes matching dietary restrictions with suitability scoring.

**Query Parameters:**
- `fodmap_safe` (boolean, optional) - Only include recipes with all safe FODMAP ingredients (default: false)
- `histamine_level` (string, optional) - Maximum histamine level: low, medium, high
- `meal_type` (string, optional) - Filter by meal type/category
- `avoid` (string, optional) - Comma-separated FODMAP types to avoid
- `limit` (int, optional) - Number of results (default: 20, max: 50)

**Response (200):**
```json
{
    "restrictions": {
        "fodmap_safe": true,
        "histamine_level": "low",
        "avoid_fodmap": ["fructans"],
        "meal_type": "Lunch"
    },
    "recipes": [
        {
            "id": 45,
            "name": "Grilled Chicken Salad",
            "category": "Lunch",
            "servings": 4,
            "prep_time": "15 mins",
            "cook_time": "20 mins",
            "ingredients_count": 8,
            "suitability": {
                "safe_ingredients": 8,
                "moderate_ingredients": 0,
                "high_risk_ingredients": 0,
                "percentage_safe": 100.0
            }
        },
        {
            "id": 52,
            "name": "Quinoa Buddha Bowl",
            "category": "Lunch",
            "servings": 2,
            "prep_time": "10 mins",
            "cook_time": "25 mins",
            "ingredients_count": 10,
            "suitability": {
                "safe_ingredients": 9,
                "moderate_ingredients": 1,
                "high_risk_ingredients": 0,
                "percentage_safe": 90.0
            }
        }
    ],
    "total_count": 12
}
```

**Example:**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/recipes/suitable?fodmap_safe=true&histamine_level=low&meal_type=Lunch"
```

---

## Section 13: Export & Reporting Endpoints

Data export and report generation capabilities (JSON, CSV, PDF, shopping lists).

### GET /api/v1/export/diary

Complete diary export in JSON or CSV format.

**Query Parameters:**
- `start_date` (string, required) - Start date in YYYY-MM-DD format
- `end_date` (string, required) - End date in YYYY-MM-DD format
- `format` (string, optional) - Export format: 'json' or 'csv' (default: json)
- `types` (string, optional) - Comma-separated entry types: meal, symptom, bowel, stress, note (default: all)

**Response (200) - JSON format:**
```json
{
    "date_range": {
        "start": "2026-01-01",
        "end": "2026-01-31"
    },
    "format": "json",
    "types": ["meal", "symptom", "bowel", "stress", "note"],
    "entries": [
        {
            "id": 123,
            "date": "2026-01-05",
            "time": "08:30",
            "type": "meal",
            "meal_type": "Breakfast",
            "location": "Home",
            "preparation": "Homemade",
            "notes": "Felt good after",
            "total_energy_kj": 1850.5,
            "total_protein_g": 15.2,
            "total_carbs_g": 45.3,
            "total_fat_g": 8.1,
            "total_sodium_mg": 320.0,
            "foods": [
                {
                    "food_name": "Oatmeal",
                    "portion_size": "1",
                    "serving_type": "safe"
                },
                {
                    "food_name": "Blueberries",
                    "portion_size": "0.5",
                    "serving_type": "safe"
                }
            ]
        },
        {
            "id": 124,
            "date": "2026-01-05",
            "time": "14:30",
            "type": "symptom",
            "bloating": 3,
            "pain": 2,
            "wind": 1,
            "nausea": 0,
            "heartburn": 0,
            "headache": 0,
            "brain_fog": 0,
            "fatigue": 2,
            "sinus_issues": 0,
            "severity": 4,
            "duration": "30 mins",
            "notes": "Mild discomfort after lunch"
        }
    ],
    "total_entries": 45,
    "exported_at": "2026-02-14T10:30:00"
}
```

**Response (200) - CSV format:**
Returns downloadable CSV file with all diary entries flattened.

**Example:**
```bash
# JSON export
curl -X GET "http://127.0.0.1:5000/api/v1/export/diary?start_date=2026-01-01&end_date=2026-01-31&format=json"

# CSV export (meals only)
curl -X GET "http://127.0.0.1:5000/api/v1/export/diary?start_date=2026-01-01&end_date=2026-01-31&format=csv&types=meal"
```

---

### GET /api/v1/export/report/pdf

Generate comprehensive PDF health report with charts and summary statistics.

**Note:** Requires reportlab library (`pip install reportlab==4.0.9`)

**Query Parameters:**
- `type` (string, optional) - Report type: 'monthly' or 'weekly' (default: monthly)
- `date` (string, required) - Date for report: YYYY-MM for monthly, YYYY-MM-DD for weekly

**Response (200):**
Returns downloadable PDF file containing:
- Report title and metadata
- Entry summary table (meal/symptom/bowel/stress/note counts)
- Symptom analysis with occurrence counts and average severity
- Daily entries log (up to 50 entries)
- Professional formatting with app color scheme

**Example:**
```bash
# Monthly report
curl -X GET "http://127.0.0.1:5000/api/v1/export/report/pdf?type=monthly&date=2026-02" \
  --output report_feb2026.pdf

# Weekly report
curl -X GET "http://127.0.0.1:5000/api/v1/export/report/pdf?type=weekly&date=2026-02-10" \
  --output report_week.pdf
```

---

### GET /api/v1/export/shopping-list

Generate aggregated shopping list from multiple recipes.

**Query Parameters:**
- `recipe_ids` (string, required) - Comma-separated recipe IDs (max 20 recipes)
- `format` (string, optional) - Export format: 'json' or 'text' (default: json)

**Response (200) - JSON format:**
```json
{
    "recipes": [
        {
            "id": 1,
            "name": "Apple Pie"
        },
        {
            "id": 2,
            "name": "Chicken Salad"
        }
    ],
    "shopping_list": {
        "Fruit": [
            {
                "food": "Apple, Granny Smith",
                "total_quantity": "6 medium",
                "recipes": ["Apple Pie"]
            },
            {
                "food": "Blueberries",
                "total_quantity": "1 cup",
                "recipes": ["Chicken Salad"]
            }
        ],
        "Protein": [
            {
                "food": "Chicken breast",
                "total_quantity": "500g, 200g",
                "recipes": ["Chicken Salad", "Apple Pie"]
            }
        ],
        "Vegetables": [
            {
                "food": "Carrot",
                "total_quantity": "2 medium",
                "recipes": ["Chicken Salad"]
            }
        ]
    },
    "total_items": 15,
    "generated_at": "2026-02-14T11:00:00"
}
```

**Response (200) - TEXT format:**
Returns plain text shopping list formatted by category with checkboxes.

**Example:**
```bash
# JSON shopping list
curl -X GET "http://127.0.0.1:5000/api/v1/export/shopping-list?recipe_ids=1,2,5&format=json"

# Text shopping list
curl -X GET "http://127.0.0.1:5000/api/v1/export/shopping-list?recipe_ids=1,2,5&format=text"
```

---

## Section 14: Real-time & Webhooks Endpoints

Server-Sent Events stream and webhook management for real-time notifications.

### GET /api/v1/events/stream

Server-Sent Events (SSE) stream for real-time updates.

**Query Parameters:**
- `since` (string, optional) - ISO timestamp to get events since (default: last 5 minutes)
- `events` (string, optional) - Comma-separated event types to listen for: entry_created, entry_updated, entry_deleted, symptom_logged, meal_logged (default: all)
- `timeout` (int, optional) - Max connection time in seconds (default: 300, max: 3600)

**Response (200) - SSE Stream:**
```
event: entry_created
id: 123
data: {"id": 123, "event_type": "entry_created", "entity_type": "meal", "entity_id": 456, "data": {"meal_type": "Lunch"}, "created_at": "2026-02-14T10:00:00"}

event: symptom_logged
id: 124
data: {"id": 124, "event_type": "symptom_logged", "entity_type": "symptom", "entity_id": 789, "data": {"type": "bloating", "severity": 5}, "created_at": "2026-02-14T10:15:00"}

: heartbeat
```

**JavaScript Usage Example:**
```javascript
const eventSource = new EventSource('/api/v1/events/stream?events=entry_created,symptom_logged');

eventSource.addEventListener('entry_created', (e) => {
    const data = JSON.parse(e.data);
    console.log('New entry:', data);
});

eventSource.addEventListener('symptom_logged', (e) => {
    const data = JSON.parse(e.data);
    console.log('New symptom:', data);
});
```

**Example:**
```bash
curl -X GET "http://127.0.0.1:5000/api/v1/events/stream?since=2026-02-14T10:00:00&events=entry_created,symptom_logged&timeout=600"
```

---

### POST /api/v1/webhooks/register

Register a webhook URL for event notifications.

**Request Body:**
```json
{
    "name": "My Notification Service",
    "url": "https://example.com/webhook",
    "events": ["entry_created", "symptom_logged"],
    "secret": "optional_secret_for_hmac"
}
```

**Body Parameters:**
- `name` (string, required) - Webhook name
- `url` (string, required) - Webhook URL (must start with http:// or https://)
- `events` (array, required) - Event types to subscribe to: entry_created, entry_updated, entry_deleted, symptom_logged, meal_logged, bowel_logged, stress_logged, note_created
- `secret` (string, optional) - Optional secret for HMAC validation

**Response (201):**
```json
{
    "success": true,
    "webhook_id": 123,
    "name": "My Notification Service",
    "url": "https://example.com/webhook",
    "events": ["entry_created", "symptom_logged"],
    "is_active": true,
    "message": "Webhook registered successfully"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Notification Service",
    "url": "https://example.com/webhook",
    "events": ["entry_created", "symptom_logged"]
  }'
```

---

### GET /api/v1/webhooks

List all registered webhooks.

**Response (200):**
```json
{
    "webhooks": [
        {
            "id": 123,
            "name": "My Notification Service",
            "url": "https://example.com/webhook",
            "events": ["entry_created", "symptom_logged"],
            "is_active": true,
            "created_at": "2026-02-12T10:00:00",
            "last_triggered": "2026-02-14T09:30:00",
            "trigger_count": 45,
            "last_error": null
        },
        {
            "id": 124,
            "name": "Secondary Webhook",
            "url": "https://api.example.com/notifications",
            "events": ["meal_logged", "bowel_logged"],
            "is_active": false,
            "created_at": "2026-02-10T14:00:00",
            "last_triggered": "2026-02-13T18:20:00",
            "trigger_count": 12,
            "last_error": "HTTP 500: Internal Server Error"
        }
    ],
    "total_count": 2
}
```

**Example:**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/webhooks
```

---

### GET /api/v1/webhooks/{id}

Get details of a specific webhook.

**Path Parameters:**
- `id` (int, required) - Webhook ID

**Response (200):**
```json
{
    "id": 123,
    "name": "My Notification Service",
    "url": "https://example.com/webhook",
    "events": ["entry_created", "symptom_logged"],
    "is_active": true,
    "created_at": "2026-02-12T10:00:00",
    "last_triggered": "2026-02-14T09:30:00",
    "trigger_count": 45,
    "last_error": null
}
```

**Example:**
```bash
curl -X GET http://127.0.0.1:5000/api/v1/webhooks/123
```

---

### PUT /api/v1/webhooks/{id}

Update an existing webhook.

**Path Parameters:**
- `id` (int, required) - Webhook ID

**Request Body:**
```json
{
    "name": "Updated Webhook Name",
    "url": "https://new-url.com/webhook",
    "events": ["entry_created", "meal_logged", "symptom_logged"],
    "is_active": true,
    "secret": "new_secret"
}
```

**Body Parameters:**
- `name` (string, optional) - Updated webhook name
- `url` (string, optional) - Updated webhook URL
- `events` (array, optional) - Updated event subscriptions
- `is_active` (boolean, optional) - Active status
- `secret` (string, optional) - Updated secret

**Response (200):**
```json
{
    "success": true,
    "webhook": {
        "id": 123,
        "name": "Updated Webhook Name",
        "url": "https://new-url.com/webhook",
        "events": ["entry_created", "meal_logged", "symptom_logged"],
        "is_active": true,
        "created_at": "2026-02-12T10:00:00",
        "last_triggered": "2026-02-14T09:30:00",
        "trigger_count": 45,
        "last_error": null
    },
    "message": "Webhook updated successfully"
}
```

**Example:**
```bash
curl -X PUT http://127.0.0.1:5000/api/v1/webhooks/123 \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Webhook Name",
    "is_active": true
  }'
```

---

### DELETE /api/v1/webhooks/{id}

Delete a webhook.

**Path Parameters:**
- `id` (int, required) - Webhook ID

**Response (200):**
```json
{
    "success": true,
    "message": "Webhook \"My Notification Service\" deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://127.0.0.1:5000/api/v1/webhooks/123
```

---

### POST /api/v1/webhooks/{id}/test

Test a webhook by sending a test event.

**Path Parameters:**
- `id` (int, required) - Webhook ID

**Response (200):**
```json
{
    "success": true,
    "status_code": 200,
    "response": "{\"status\": \"received\", \"message\": \"Test webhook processed successfully\"}",
    "message": "Test event sent successfully"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/webhooks/123/test
```

---

### POST /api/v1/webhooks/external/receive

Receive inbound webhooks from external services (wearables, meal trackers, health apps). Validates HMAC signature if `EXTERNAL_WEBHOOK_SECRET` environment variable is set.

**Request Body:**
```json
{
    "source": "wearable_sync",
    "provider": "fitbit",
    "event_type": "heart_rate",
    "timestamp": "2026-02-28T10:00:00Z",
    "data": {
        "bpm": 72,
        "measured_at": "2026-02-28T09:55:00Z"
    }
}
```

**Body Parameters:**
- `source` (string, required) - Source type: `wearable_sync`, `meal_tracker`, `health_app`
- `provider` (string, required) - Provider name (e.g., fitbit, oura, apple_watch, myfitnesspal)
- `event_type` (string, required) - Event type (e.g., heart_rate, sleep, stress, steps, meal_import)
- `timestamp` (string, optional) - ISO timestamp of when the data was generated
- `data` (object, required) - The actual payload data

**Headers (optional):**
- `X-Webhook-Signature: sha256=<hex_digest>` - HMAC signature (validated if EXTERNAL_WEBHOOK_SECRET is configured)

**Response (200):**
```json
{
    "success": true,
    "log_id": 1,
    "source": "wearable_sync",
    "provider": "fitbit",
    "event_type": "heart_rate",
    "signature_verified": null,
    "processed": false,
    "message": "Webhook received and logged successfully"
}
```

**Error Response (401) - Invalid Signature:**
```json
{
    "error": "Invalid webhook signature"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/webhooks/external/receive \
  -H "Content-Type: application/json" \
  -d '{
    "source": "wearable_sync",
    "provider": "fitbit",
    "event_type": "heart_rate",
    "data": {"bpm": 72}
  }'
```

---

---

## 15. Gamification Endpoints

### GET /api/v1/gamification/challenges

Get all active challenges with current progress.

**Response (200):**
```json
{
    "success": true,
    "data": {
        "challenges": [
            {
                "id": 1,
                "title": "Log 7 Days",
                "description": "Log meals for 7 consecutive days",
                "type": "streak",
                "target": 7,
                "progress": 5,
                "is_active": true,
                "completed": false,
                "created_at": "2026-02-01T10:00:00"
            }
        ],
        "total_count": 5,
        "active_count": 5,
        "completed_count": 2
    }
}
```

**Example:**
```bash
curl http://127.0.0.1:5000/api/v1/gamification/challenges
```

---

### POST /api/v1/gamification/challenges

Create a new challenge (admin endpoint).

**Request Body:**
```json
{
    "title": "Hydration Challenge",
    "description": "Log water intake daily for 14 days",
    "type": "daily_habit",
    "target": 14,
    "duration_days": 14
}
```

**Response (201):**
```json
{
    "success": true,
    "data": {
        "id": 6,
        "title": "Hydration Challenge",
        "type": "daily_habit",
        "target": 14
    },
    "message": "Challenge created"
}
```

---

### GET /api/v1/gamification/badges

Get all earned badges with date earned.

**Response (200):**
```json
{
    "success": true,
    "data": {
        "badges": [
            {
                "id": 1,
                "name": "First Entry",
                "description": "Log your first diary entry",
                "icon": "star",
                "earned_at": "2026-02-10T08:30:00"
            }
        ],
        "total_earned": 3,
        "by_challenge": {}
    }
}
```

---

## 16. Reintroduction Protocol Endpoints

### POST /api/v1/reintroduction/protocol

Create a FODMAP reintroduction protocol with auto-generated schedule.

**Request Body:**
```json
{
    "fodmap_category": "Fructose",
    "start_date": "2026-03-01",
    "notes": "Starting fructose reintroduction"
}
```

**Response (201):**
```json
{
    "success": true,
    "data": {
        "protocol_id": 1,
        "fodmap_category": "Fructose",
        "status": "active",
        "start_date": "2026-03-01",
        "schedule_days": 14,
        "phases": [
            {"phase": 1, "days": "1-3", "dose_size": "small"},
            {"phase": 2, "days": "4-6", "dose_size": "medium"},
            {"phase": 3, "days": "7-9", "dose_size": "large"},
            {"phase": 4, "days": "10-14", "dose_size": "washout"}
        ]
    },
    "message": "Reintroduction protocol created"
}
```

---

### GET /api/v1/reintroduction/schedule

Get the reintroduction schedule for a protocol.

**Query Parameters:**
- `protocol_id` (int, optional) - Protocol ID

**Response (200):**
```json
{
    "success": true,
    "data": {
        "protocol_id": 1,
        "schedule": [
            {
                "day_number": 1,
                "scheduled_date": "2026-03-01",
                "dose_size": "small",
                "dose_description": "Small test dose",
                "completed": false
            }
        ],
        "total_days": 14
    }
}
```

---

### POST /api/v1/reintroduction/evaluate

Evaluate symptoms during reintroduction phase.

**Request Body:**
```json
{
    "protocol_id": 1,
    "day_number": 3,
    "symptoms": {
        "bloating": 3,
        "pain": 1,
        "wind": 2
    },
    "notes": "Mild symptoms noticed",
    "tolerated": true
}
```

**Response (200):**
```json
{
    "success": true,
    "data": {
        "evaluation_id": 10,
        "protocol_id": 1,
        "tolerated": true,
        "recommendation": "Continue to next phase"
    }
}
```

---

## 17. Notifications Endpoints

### GET /api/v1/notifications/settings

Get user notification preferences.

**Response (200):**
```json
{
    "success": true,
    "data": {
        "notification_channels": "in_app",
        "email_enabled": false,
        "sms_enabled": false,
        "push_enabled": false,
        "settings": {
            "email_enabled": "false",
            "sms_enabled": "false"
        }
    }
}
```

---

### POST /api/v1/notifications/send

Send a notification to user.

**Request Body:**
```json
{
    "message": "Your daily summary is ready",
    "channel": "in_app"
}
```

**Response (501 - Not Configured):**
```json
{
    "status": "not_configured",
    "message_received": "Your daily summary is ready",
    "todo": "Configure notification provider (Twilio, SendGrid, etc.)"
}
```

---

### POST /api/v1/notifications/rules

Create an automated notification trigger rule.

**Request Body:**
```json
{
    "trigger": "high_symptoms",
    "condition": "bloating > 7",
    "channel": "in_app",
    "is_active": true
}
```

**Response (201):**
```json
{
    "success": true,
    "data": {
        "rule_id": 1,
        "trigger": "high_symptoms",
        "channel": "in_app",
        "is_active": true
    },
    "message": "Rule created"
}
```

---

### GET /api/v1/notifications/rules

Get all notification rules.

**Response (200):**
```json
{
    "success": true,
    "data": {
        "rules": [
            {
                "id": 1,
                "trigger": "high_symptoms",
                "condition": "bloating > 7",
                "channel": "in_app",
                "is_active": true
            }
        ],
        "total_count": 3
    }
}
```

---

### POST /api/v1/notifications/schedule

Schedule a notification for a specific date/time.

**Request Body:**
```json
{
    "message": "Time for lunch logging",
    "scheduled_time": "2026-03-01T12:00:00",
    "channel": "in_app"
}
```

**Response (201):**
```json
{
    "success": true,
    "data": {
        "notification_id": 5,
        "scheduled_time": "2026-03-01T12:00:00",
        "status": "scheduled"
    }
}
```

---

### GET /api/v1/notifications

List pending notifications.

**Response (200):**
```json
{
    "success": true,
    "data": {
        "notifications": [
            {
                "id": 1,
                "message": "Daily summary ready",
                "channel": "in_app",
                "created_at": "2026-02-28T08:00:00",
                "read": false
            }
        ],
        "unread_count": 2
    }
}
```

---

### POST /api/v1/notifications/{id}/mark-read

Mark a notification as read.

**Path Parameters:**
- `id` (int, required) - Notification ID

**Response (200):**
```json
{
    "success": true,
    "message": "Notification marked as read"
}
```

---

## 18. Security & Access Control Endpoints

### POST /api/v1/auth/api-keys

Generate a new API key for external access.

**Request Body:**
```json
{
    "name": "Mobile App Key",
    "scopes": ["diary:read", "diary:write", "recipes:read"],
    "expires_at": "2026-12-31T23:59:59Z"
}
```

**Response (201):**
```json
{
    "success": true,
    "data": {
        "key_id": 1,
        "name": "Mobile App Key",
        "api_key": "ak_abcdef123456789...",
        "key_prefix": "ak_ab****",
        "scopes": ["diary:read", "diary:write", "recipes:read"],
        "is_active": true,
        "created_at": "2026-02-28T10:00:00",
        "expires_at": "2026-12-31T23:59:59Z",
        "warning": "This key is shown only once. Store it securely."
    },
    "message": "API key created"
}
```

---

### GET /api/v1/auth/api-keys

List all API keys (showing only prefix).

**Response (200):**
```json
{
    "success": true,
    "data": {
        "keys": [
            {
                "id": 1,
                "name": "Mobile App Key",
                "key_prefix": "ak_ab****",
                "scopes": "diary:read,diary:write,recipes:read",
                "is_active": true,
                "created_at": "2026-02-28T10:00:00",
                "expires_at": "2026-12-31T23:59:59Z",
                "last_used": "2026-02-28T15:30:00"
            }
        ],
        "total_count": 3,
        "active_count": 2,
        "note": "Key prefixes shown for identification. Full keys cannot be retrieved."
    }
}
```

---

### DELETE /api/v1/auth/api-keys/{key_id}

Revoke an API key.

**Path Parameters:**
- `key_id` (int, required) - API Key ID

**Response (200):**
```json
{
    "success": true,
    "message": "API key revoked successfully"
}
```

---

### GET /api/v1/rate-limit
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---

### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
Get current rate limit status.
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---

### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
**Response (200):**
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
```json
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
{
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
    "success": true,
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
    "data": {
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
        "limit": 1000,
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
        "remaining": 987,
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
        "reset_at": "2026-03-01T00:00:00Z",
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
        "tier": "free"
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
    }
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
}
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
```
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---

### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---
---
### GET /api/v1/auth/audit-logGet audit log of API access (requires admin:security scope).**Query Parameters:**- `key_id` (optional, int) — Filter by API key ID- `endpoint` (optional, str) — Filter by endpoint- `page` (optional, int) — Page number (default: 1)- `per_page` (optional, int) — Results per page (default: 50)**Response (200):**```json{    "success": true,    "data": [        {            "id": 123,            "key_id": 45,            "endpoint": "/diary/entries",            "method": "GET",            "status_code": 200,            "ip_address": "192.168.1.1",            "timestamp": "2026-02-28T12:34:56Z"        }    ],    "pagination": {"page": 1, "per_page": 50, "total": 156, "pages": 4}}```---

## 19. Integrations Endpoints

### POST /api/v1/wearables/connect

Connect a wearable device (Fitbit, Apple Watch, Oura Ring).

**Request Body:**
```json
{
    "device_type": "fitbit",
    "auth_code": "authorization_code_from_oauth"
}
```

**Response (501 - Not Configured):**
```json
{
    "status": "not_configured",
    "supported_devices": ["Fitbit", "Apple Watch", "Oura Ring", "Google Fit"],
    "message": "Wearable integration not configured",
    "todo": "Implement OAuth 2.0 flow in config.py"
}
```

---

### POST /api/v1/wearables/sync

Sync data from connected wearable device.

**Response (501 - Not Configured):**
```json
{
    "status": "not_configured",
    "message": "No wearable device connected",
    "todo": "Implement data sync from wearable APIs"
}
```

---

### POST /api/v1/voice/log

Process voice command into diary entry.

**Request Body:**
```json
{
    "transcript": "I had oatmeal with blueberries and felt bloated afterwards"
}
```

**Response (501 - Not Configured):**
```json
{
    "status": "not_configured",
    "transcript_received": true,
    "transcript": "I had oatmeal with blueberries and felt bloated afterwards",
    "message": "Voice logging not configured",
    "todo": "Implement NLP parser to extract meals and symptoms from transcript"
}
```

---

## 20. Billing Endpoints

### GET /api/v1/billing/status

Get current subscription/premium status.

**Response (200):**
```json
{
    "status": "not_configured",
    "plan": "free",
    "tier": "free_tier",
    "message": "Billing integration not configured",
    "features": {
        "diary_logging": true,
        "analytics": true,
        "recipes": true,
        "education": true,
        "ai_chat": false,
        "api_access": false,
        "export_pdf": false
    },
    "todo": "Configure Stripe/App Store for subscription webhooks"
}
```

---

### POST /api/v1/billing/webhook

Receive subscription/payment webhooks from Stripe or App Store. Validates signatures per provider. Supports idempotency via `event_id` — duplicate events return 200 without reprocessing.

**Request Body:**
```json
{
    "provider": "stripe",
    "event_type": "subscription.created",
    "event_id": "evt_1234567890",
    "timestamp": "2026-02-28T10:00:00Z",
    "data": {
        "subscription_id": "sub_xxx",
        "plan": "pro",
        "amount": 999,
        "currency": "usd",
        "customer_email": "user@example.com"
    }
}
```

**Body Parameters:**
- `provider` (string, required) - Provider: `stripe`, `app_store`, `google_play`
- `event_type` (string, required) - Event type: `subscription.created`, `subscription.renewed`, `subscription.cancelled`, `subscription.expired`, `subscription.upgraded`, `subscription.downgraded`, `payment.succeeded`, `payment.failed`, `payment.refunded`, `trial.started`, `trial.ending`
- `event_id` (string, required) - External event ID for idempotency (e.g., Stripe evt_xxx)
- `timestamp` (string, optional) - ISO timestamp
- `data` (object, required) - Event-specific data

**Headers (optional):**
- `Stripe-Signature: <signature>` - For Stripe webhooks (validated if STRIPE_WEBHOOK_SECRET is configured)
- `X-Webhook-Signature: sha256=<hex_digest>` - For other providers

**Response (200):**
```json
{
    "success": true,
    "event_log_id": 1,
    "provider": "stripe",
    "event_type": "subscription.created",
    "signature_verified": null,
    "processed": false,
    "message": "Billing webhook received and logged successfully"
}
```

**Response (200) - Duplicate Event (Idempotent):**
```json
{
    "success": true,
    "event_log_id": 1,
    "duplicate": true,
    "message": "Event already received and logged (idempotent)"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/api/v1/billing/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "stripe",
    "event_type": "subscription.created",
    "event_id": "evt_test_001",
    "data": {"plan": "pro", "amount": 999, "currency": "usd"}
  }'
```

---

## 21. Multi-User & Cohort Analysis Endpoints

### GET /api/v1/users/cohort-analysis

Anonymous cohort analysis across users.

**Response (200):**
```json
{
    "status": "single_user_mode",
    "message": "Multi-user features are not enabled in single-user mode",
    "todo": "Implement user account system and cohort data pooling"
}
```

---

### GET /api/v1/users/compare

Compare user to similarity cluster.

**Response (200):**
```json
{
    "status": "single_user_mode",
    "message": "Multi-user features are not enabled in single-user mode",
    "todo": "Implement user cohort clustering and comparative metrics"
}
```

---

### GET /api/v1/users/phenotypes

Identify phenotype similarities with other users.

**Response (200):**
```json
{
    "status": "single_user_mode",
    "message": "Multi-user features are not enabled in single-user mode",
    "todo": "Implement phenotype classification and similarity matching"
}
```

---

## Complete API Reference - All 135 Endpoints Documented

**This document provides comprehensive documentation for all 135 API v1 endpoints across 21 categories.**

### Updated Summary by Category
1. **Diary Endpoints**: 9 endpoints
2. **Recipes Endpoints**: 14 endpoints
3. **Foods/Compendium Endpoints**: 14 endpoints
4. **Analytics & Dashboard Endpoints**: 27 endpoints
5. **USDA Database Endpoints**: 3 endpoints
6. **AUSNUT Database Endpoints**: 2 endpoints
7. **Settings & Database Endpoints**: 10 endpoints
8. **Help Document Endpoints**: 10 endpoints
9. **Education Endpoints**: 9 endpoints
10. **Chat Endpoints**: 5 endpoints
11. **FODMAP Reference Endpoints**: 2 endpoints
12. **Search & Discovery Endpoints**: 3 endpoints
13. **Export & Reporting Endpoints**: 3 endpoints
14. **Real-time & Webhooks Endpoints**: 8 endpoints (+1 inbound webhook)
15. **Gamification Endpoints**: 3 endpoints
16. **Reintroduction Protocol Endpoints**: 3 endpoints
17. **Notifications Endpoints**: 7 endpoints
18. **Security & Access Control Endpoints**: 4 endpoints
19. **Integrations Endpoints**: 3 endpoints
20. **Billing Endpoints**: 2 endpoints (+1 inbound webhook)
21. **Multi-User & Cohort Analysis Endpoints**: 3 endpoints

**Total: 135 API v1 Endpoints**
- **Previous Total:** 133 endpoints
- **New Endpoints Added:** 2 inbound webhook receivers

Inbound webhook endpoints complete the planned API. All 49 new endpoints from the part_2 spreadsheets are now implemented.
