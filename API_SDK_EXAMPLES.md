# Gut Health Management App - SDK & Code Examples

**Version**: 1.0.0
**Last Updated**: February 28, 2026

Complete code examples for integrating with the Gut Health API in Python and JavaScript.

---

## Table of Contents

1. [Python SDK](#python-sdk)
2. [JavaScript SDK](#javascript-sdk)
3. [Common Patterns](#common-patterns)
4. [Error Handling](#error-handling)

---

## Python SDK

### Installation

```bash
pip install requests
```

### Basic Setup

```python
import requests
import json
from datetime import datetime, timedelta

class GutHealthAPI:
    """Simple wrapper for Gut Health Management API"""

    def __init__(self, base_url="http://localhost:5000", api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"X-API-Key": api_key})

    def _request(self, method, endpoint, **kwargs):
        """Make API request"""
        url = f"{self.base_url}/api/v1{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()

    def get(self, endpoint, **kwargs):
        return self._request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        return self._request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        return self._request("PUT", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        return self._request("DELETE", endpoint, **kwargs)

# Initialize
api = GutHealthAPI(api_key="your-api-key-here")
```

### Example 1: Log a Meal

```python
def log_meal(api, meal_data):
    """Log a meal with foods"""
    response = api.post("/diary/meals", json={
        "date": meal_data["date"],
        "meal_type": meal_data["meal_type"],
        "foods": meal_data["foods"],
        "notes": meal_data.get("notes", "")
    })
    return response["data"]["id"]

# Usage
meal_id = log_meal(api, {
    "date": "2026-02-28",
    "meal_type": "breakfast",
    "foods": [
        {"food_id": 123, "serving_size": "1 cup", "quantity": 1},
        {"food_id": 456, "serving_size": "2 slices", "quantity": 2}
    ],
    "notes": "Felt great after this meal"
})
print(f"Meal logged: {meal_id}")
```

### Example 2: Track Symptoms

```python
def log_symptoms(api, symptom_data):
    """Log one or more symptoms"""
    response = api.post("/diary/entries/bulk", json={
        "entries": [
            {
                "type": "symptom",
                "date": symptom_data["date"],
                "symptom": symptom_data["symptom"],
                "severity": symptom_data["severity"],  # 1-10
                "notes": symptom_data.get("notes", "")
            }
        ]
    })
    return response["data"]

# Usage
log_symptoms(api, {
    "date": "2026-02-28",
    "symptom": "Bloating",
    "severity": 5,
    "notes": "Started 2 hours after breakfast"
})
```

### Example 3: Search for Safe Foods

```python
def search_foods(api, query, limit=20):
    """Search for foods in database"""
    response = api.get("/compendium/search", params={
        "q": query,
        "page": 1,
        "per_page": limit
    })
    return response["data"]["data"]

def find_substitutes(api, food_id, limit=10):
    """Find safe alternatives for a food"""
    response = api.get("/foods/substitutes", params={
        "food_id": food_id,
        "limit": limit
    })
    return response["data"]["substitutes"]

# Usage
apples = search_foods(api, "apple")
print(f"Found {len(apples)} results for 'apple'")
for food in apples:
    print(f"- {food['name']}: {food['fodmap_rating']}")

# Find substitutes for high-FODMAP food
high_fodmap_id = 789
safer_options = find_substitutes(api, high_fodmap_id)
print(f"Safer alternatives to that food: {safer_options}")
```

### Example 4: Get Analytics & Trends

```python
def get_symptom_trends(api, days=30):
    """Get symptom trends over time"""
    response = api.get("/analytics/symptom-trends", params={
        "days": days,
        "granularity": "daily"
    })
    return response["data"]["symptoms"]

def get_trigger_foods(api, days=30):
    """Get foods that trigger symptoms"""
    response = api.get("/analytics/trigger-foods", params={
        "days": days,
        "symptom_threshold": 6
    })
    return response["data"]

def get_nutrition_summary(api, date_from, date_to):
    """Get aggregated nutrition over date range"""
    response = api.get("/analytics/nutrition-summary", params={
        "date_from": date_from,
        "date_to": date_to
    })
    return response["data"]

# Usage
trends = get_symptom_trends(api, days=30)
for symptom in trends:
    print(f"{symptom['name']}: {symptom['trend']}")
    print(f"  Daily average: {symptom['daily_avg']}")

triggers = get_trigger_foods(api, days=30)
print("\nFoods that trigger symptoms:")
for food in triggers:
    print(f"- {food['name']} ({food['symptom_rate']*100:.0f}% trigger rate)")

# Get last week's nutrition
today = datetime.now().date()
week_ago = today - timedelta(days=7)
nutrition = get_nutrition_summary(api, str(week_ago), str(today))
print(f"\nAverage daily calories: {nutrition['daily_avg']['calories']}")
```

### Example 5: Manage Recipes

```python
def create_recipe(api, recipe_data):
    """Create a new recipe"""
    response = api.post("/recipes", json={
        "name": recipe_data["name"],
        "ingredients": recipe_data["ingredients"],
        "instructions": recipe_data["instructions"],
        "serving_size": recipe_data.get("serving_size", "1 serving"),
        "prep_time_min": recipe_data.get("prep_time_min", 0),
        "cook_time_min": recipe_data.get("cook_time_min", 0),
        "tags": recipe_data.get("tags", [])
    })
    return response["data"]

def search_recipes(api, query):
    """Search recipes"""
    response = api.get("/recipes/search", params={"q": query})
    return response["data"]["data"]

def transform_recipe(api, recipe_id, replace_high_fodmap=True):
    """Auto-substitute high-FODMAP ingredients with safer ones"""
    response = api.post(f"/recipes/{recipe_id}/transform", json={
        "transformations": {
            "replace_high_fodmap": replace_high_fodmap
        }
    })
    return response["data"]

# Usage
new_recipe = create_recipe(api, {
    "name": "Grilled Salmon with Rice",
    "ingredients": [
        {"name": "Salmon fillet", "quantity": "150g"},
        {"name": "White rice", "quantity": "0.75 cups"}
    ],
    "instructions": "1. Heat grill to 400°F\n2. Grill salmon 4-5 min per side\n3. Serve with rice",
    "prep_time_min": 10,
    "cook_time_min": 12,
    "tags": ["low-fodmap", "quick", "pescatarian"]
})
print(f"Recipe created: {new_recipe['id']}")

# Search for safe recipes
safe_recipes = search_recipes(api, "low fodmap breakfast")
print(f"Found {len(safe_recipes)} safe recipes")

# Transform a high-FODMAP recipe
transformed = transform_recipe(api, recipe_id=5)
print(f"Changes made: {len(transformed['changes'])}")
for change in transformed['changes']:
    print(f"- {change['original']} → {change['replacement']}")
```

### Example 6: API Key Management

```python
def create_api_key(api, name, scopes, rate_limit=120, expires_in_days=365):
    """Create a new API key"""
    from datetime import datetime, timedelta

    expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat() + "Z"

    response = api.post("/auth/api-keys", json={
        "name": name,
        "scopes": scopes,
        "rate_limit": rate_limit,
        "expires_at": expires_at
    })
    return response["data"]

def list_api_keys(api):
    """List all API keys (shows prefix only, not full key)"""
    response = api.get("/auth/api-keys")
    return response["data"]["data"]

def revoke_api_key(api, key_id):
    """Revoke an API key"""
    response = api.delete(f"/auth/api-keys/{key_id}")
    return response["data"]

def check_rate_limit(api):
    """Check current rate limit status"""
    response = api.get("/auth/rate-limit")
    return response["data"]

# Usage
# Create key for APP2
app2_key = create_api_key(api,
    name="APP2 Analytics",
    scopes=[
        "read:diary", "read:analytics", "read:recipes",
        "read:compendium", "read:foods", "read:search",
        "write:diary", "write:webhooks"
    ],
    rate_limit=200
)
print(f"New API key created: {app2_key['key_prefix']}...")
print(f"Store this key securely: {app2_key['key']}")

# Check rate limit
rate_limit_status = check_rate_limit(api)
print(f"\nRate limit: {rate_limit_status['requests_this_minute']}/{rate_limit_status['limit']}")
print(f"Remaining: {rate_limit_status['remaining']}")
```

### Example 7: Bulk Operations

```python
def batch_get_foods(api, food_ids):
    """Efficiently fetch multiple foods at once"""
    ids_string = ",".join(str(id) for id in food_ids)
    response = api.get("/foods/batch", params={"ids": ids_string})
    return response["data"]

def bulk_log_entries(api, entries):
    """Log multiple diary entries at once"""
    response = api.post("/diary/entries/bulk", json={"entries": entries})
    return response["data"]

# Usage
# Get multiple foods efficiently
food_ids = [123, 456, 789, 101]
foods = batch_get_foods(api, food_ids)
print(f"Fetched {len(foods)} foods")

# Log multiple entries at once
entries = [
    {
        "type": "meal",
        "date": "2026-02-28",
        "meal_type": "breakfast",
        "foods": [{"food_id": 123, "serving_size": "1 cup", "quantity": 1}]
    },
    {
        "type": "symptom",
        "date": "2026-02-28",
        "symptom": "Bloating",
        "severity": 4
    },
    {
        "type": "bowel",
        "date": "2026-02-28",
        "bristol_type": 4
    }
]
results = bulk_log_entries(api, entries)
print(f"Logged {len(results)} entries")
```

### Example 8: Error Handling

```python
def safe_api_call(api, method, endpoint, **kwargs):
    """Make API call with error handling"""
    try:
        if method == "GET":
            return api.get(endpoint, **kwargs)
        elif method == "POST":
            return api.post(endpoint, **kwargs)
        elif method == "PUT":
            return api.put(endpoint, **kwargs)
        elif method == "DELETE":
            return api.delete(endpoint, **kwargs)

    except requests.exceptions.HTTPError as e:
        error_response = e.response.json()
        error_code = error_response.get("error", {}).get("code")
        error_message = error_response.get("error", {}).get("message")

        if e.response.status_code == 401:
            print("ERROR: Invalid or expired API key")
        elif e.response.status_code == 403:
            print(f"ERROR: Missing scope: {error_response.get('error', {}).get('details', {}).get('required_scope')}")
        elif e.response.status_code == 404:
            print("ERROR: Resource not found")
        elif e.response.status_code == 429:
            print(f"ERROR: Rate limited. Reset in {e.response.headers.get('Retry-After')} seconds")
        elif e.response.status_code == 400:
            print(f"ERROR: Validation failed - {error_message}")
        else:
            print(f"ERROR: {e.response.status_code} - {error_message}")
        return None

    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server")
        return None

    except Exception as e:
        print(f"ERROR: Unexpected error - {str(e)}")
        return None

# Usage
result = safe_api_call(api, "GET", "/diary/entries", params={"page": 1})
if result:
    print(f"Found {len(result['data']['data'])} entries")
```

---

## JavaScript SDK

### Installation

```bash
npm install axios
# or
yarn add axios
```

### Basic Setup

```javascript
import axios from 'axios';

class GutHealthAPI {
  constructor(baseURL = 'http://localhost:5000', apiKey = null) {
    this.baseURL = baseURL;
    this.client = axios.create({
      baseURL: `${baseURL}/api/v1`,
      headers: apiKey ? { 'X-API-Key': apiKey } : {}
    });
  }

  get(endpoint, params = {}) {
    return this.client.get(endpoint, { params });
  }

  post(endpoint, data = {}) {
    return this.client.post(endpoint, data);
  }

  put(endpoint, data = {}) {
    return this.client.put(endpoint, data);
  }

  delete(endpoint) {
    return this.client.delete(endpoint);
  }
}

// Initialize
const api = new GutHealthAPI('http://localhost:5000', 'your-api-key');
```

### Example 1: Log a Meal (async/await)

```javascript
async function logMeal(api, mealData) {
  try {
    const response = await api.post('/diary/meals', {
      date: mealData.date,
      meal_type: mealData.mealType,
      foods: mealData.foods,
      notes: mealData.notes || ''
    });
    return response.data.data.id;
  } catch (error) {
    console.error('Failed to log meal:', error.response?.data?.error?.message);
  }
}

// Usage
const mealId = await logMeal(api, {
  date: '2026-02-28',
  mealType: 'breakfast',
  foods: [
    { food_id: 123, serving_size: '1 cup', quantity: 1 },
    { food_id: 456, serving_size: '2 slices', quantity: 2 }
  ],
  notes: 'Felt great after this meal'
});
console.log('Meal logged:', mealId);
```

### Example 2: Search Foods

```javascript
async function searchFoods(api, query, limit = 20) {
  try {
    const response = await api.get('/compendium/search', {
      q: query,
      page: 1,
      per_page: limit
    });
    return response.data.data.data;
  } catch (error) {
    console.error('Search failed:', error.response?.data?.error?.message);
    return [];
  }
}

// Usage
const foods = await searchFoods(api, 'apple');
foods.forEach(food => {
  console.log(`${food.name}: ${food.fodmap_rating}`);
});
```

### Example 3: Get Analytics Data

```javascript
async function getSymptomTrends(api, days = 30) {
  try {
    const response = await api.get('/analytics/symptom-trends', {
      days,
      granularity: 'daily'
    });
    return response.data.data.symptoms;
  } catch (error) {
    console.error('Failed to get trends:', error.response?.data?.error?.message);
  }
}

async function getTriggerFoods(api, days = 30) {
  try {
    const response = await api.get('/analytics/trigger-foods', {
      days,
      symptom_threshold: 6
    });
    return response.data.data;
  } catch (error) {
    console.error('Failed to get triggers:', error.response?.data?.error?.message);
  }
}

// Usage
const symptoms = await getSymptomTrends(api, 30);
symptoms.forEach(symptom => {
  console.log(`${symptom.name}: ${symptom.trend}`);
  console.log(`  Average: ${symptom.daily_avg}`);
});

const triggers = await getTriggerFoods(api, 30);
triggers.forEach(food => {
  console.log(`${food.name} (${(food.symptom_rate * 100).toFixed(0)}% trigger rate)`);
});
```

### Example 4: Create Recipe

```javascript
async function createRecipe(api, recipeData) {
  try {
    const response = await api.post('/recipes', {
      name: recipeData.name,
      ingredients: recipeData.ingredients,
      instructions: recipeData.instructions,
      serving_size: recipeData.servingSize || '1 serving',
      prep_time_min: recipeData.prepTimeMin || 0,
      cook_time_min: recipeData.cookTimeMin || 0,
      tags: recipeData.tags || []
    });
    return response.data.data;
  } catch (error) {
    console.error('Failed to create recipe:', error.response?.data?.error?.message);
  }
}

// Usage
const recipe = await createRecipe(api, {
  name: 'Grilled Salmon with Rice',
  ingredients: [
    { name: 'Salmon fillet', quantity: '150g' },
    { name: 'White rice', quantity: '0.75 cups' }
  ],
  instructions: '1. Heat grill to 400°F\n2. Grill salmon 4-5 min per side\n3. Serve with rice',
  prepTimeMin: 10,
  cookTimeMin: 12,
  tags: ['low-fodmap', 'quick', 'pescatarian']
});
console.log('Recipe created:', recipe.id);
```

### Example 5: Error Handling (Promises)

```javascript
function handleApiError(error) {
  const status = error.response?.status;
  const errorCode = error.response?.data?.error?.code;
  const errorMessage = error.response?.data?.error?.message;

  switch (status) {
    case 401:
      console.error('Unauthorized: Check your API key');
      break;
    case 403:
      const requiredScope = error.response?.data?.error?.details?.required_scope;
      console.error(`Forbidden: Missing scope "${requiredScope}"`);
      break;
    case 404:
      console.error('Not found: Resource does not exist');
      break;
    case 429:
      const retryAfter = error.response?.headers['retry-after'];
      console.error(`Rate limited: Try again in ${retryAfter} seconds`);
      break;
    case 400:
      console.error(`Validation error: ${errorMessage}`);
      break;
    default:
      console.error(`API Error (${status}): ${errorMessage}`);
  }
}

// Usage
api.get('/diary/entries')
  .then(response => console.log(response.data))
  .catch(handleApiError);
```

### Example 6: Polling for Real-time Updates

```javascript
async function streamEvents(api, callback) {
  try {
    const response = await api.client.get('/events/stream', {
      responseType: 'stream'
    });

    response.data.on('data', (chunk) => {
      const line = chunk.toString().trim();
      if (line.startsWith('data:')) {
        const data = JSON.parse(line.substring(5));
        callback(data);
      }
    });

    response.data.on('error', (error) => {
      console.error('Stream error:', error);
    });
  } catch (error) {
    console.error('Failed to connect to stream:', error.message);
  }
}

// Usage
streamEvents(api, (event) => {
  console.log('New event:', event);
});
```

---

## Common Patterns

### Pattern 1: Retry with Exponential Backoff

```python
import time

def retry_api_call(api, method, endpoint, max_retries=3, **kwargs):
    """Retry failed API calls with exponential backoff"""
    for attempt in range(max_retries):
        try:
            if method == "GET":
                return api.get(endpoint, **kwargs)
            elif method == "POST":
                return api.post(endpoint, **kwargs)
        except requests.exceptions.ConnectionError:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

### Pattern 2: Rate Limit Handling

```javascript
async function respectRateLimit(api, callback) {
  try {
    const result = await callback();
    return result;
  } catch (error) {
    if (error.response?.status === 429) {
      const retryAfter = parseInt(error.response.headers['retry-after']) * 1000;
      console.log(`Rate limited. Waiting ${retryAfter}ms...`);
      await new Promise(resolve => setTimeout(resolve, retryAfter));
      return await callback(); // Retry
    }
    throw error;
  }
}

// Usage
const result = await respectRateLimit(api, () =>
  api.get('/diary/entries', { params: { page: 1 } })
);
```

### Pattern 3: Pagination Helper

```python
def paginate_all(api, endpoint, **kwargs):
    """Automatically paginate through all results"""
    page = 1
    all_data = []

    while True:
        response = api.get(endpoint, **kwargs, params={"page": page, "per_page": 50})
        items = response["data"]["data"]

        if not items:
            break

        all_data.extend(items)

        if not response["data"]["pagination"]["has_next"]:
            break

        page += 1

    return all_data

# Usage
all_diary_entries = paginate_all(api, "/diary/entries")
```

---

## Error Handling

### Expected Error Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| 400 | Bad Request | Fix request format/data |
| 401 | Unauthorized | Check API key validity |
| 403 | Forbidden | Request scope addition |
| 404 | Not Found | Verify resource ID |
| 429 | Rate Limited | Wait and retry |
| 500 | Server Error | Retry after delay |

### Error Response Structure

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid serving size",
    "details": {
      "field": "serving_size",
      "value": -5,
      "reason": "Must be positive"
    }
  }
}
```

---

## Testing Your Integration

```python
def test_api_connection(api):
    """Test if API is working"""
    try:
        # Test public endpoint (no auth required)
        response = api.get("/fodmap/categories")
        print("✓ API is accessible")

        # Test authenticated endpoint
        if api.api_key:
            response = api.get("/auth/rate-limit")
            print("✓ API key is valid")

        return True
    except Exception as e:
        print(f"✗ API connection failed: {e}")
        return False

# Usage
if test_api_connection(api):
    print("API integration is ready!")
```

---

**Last Updated**: February 28, 2026
**Version**: 1.0.0
