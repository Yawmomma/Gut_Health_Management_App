# Gut Health Management App

A personal web application for tracking diet, symptoms, and identifying food triggers related to FODMAP sensitivity and histamine intolerance.

## Why I Built This

After years of struggling with unexplained digestive issues, I was finally diagnosed with FODMAP sensitivity and histamine intolerance. The journey to understanding my triggers was frustrating - existing apps were either too simplistic, too expensive, or didn't combine FODMAP and histamine tracking in one place.

I needed something that would:
- Track what I eat alongside my symptoms
- Understand which foods are safe at different serving sizes
- Learn about the science behind gut health
- Identify patterns I couldn't see on my own

So I built this app for myself. It's designed for personal use on a desktop/laptop - no cloud accounts, no subscriptions, no data leaving my computer. Just a straightforward tool to help manage gut health.

If you're dealing with similar issues, feel free to use it, fork it, or adapt it to your needs.

## Features

### Food Guide
- Comprehensive food database with FODMAP ratings (Fructans, GOS, Lactose, Fructose, Polyols)
- Histamine levels, DAO blockers, and liberator information
- Traffic light system (Green/Amber/Red) based on serving sizes
- Search and compare foods side-by-side

### USDA Food Database
I added the USDA FoodData Central database to provide comprehensive nutritional information without users having to manually enter it all themselves. This includes:
- **7,000+ foods** from USDA Foundation and SR Legacy datasets
- Complete nutritional profiles (calories, macros, vitamins, minerals, amino acids)
- Organized by food categories for easy browsing
- Multiple serving size options with gram weights
- Searchable by name, category, or data type

### Daily Diary
- Log meals with specific foods and serving sizes
- Track symptoms with severity ratings
- Bristol Stool Chart for bowel movements
- Stress level monitoring
- General notes and observations
- Calendar view with daily summaries

### My Recipe Book
- Save and organize gut-friendly recipes
- Create reusable meal templates
- Categorize by meal type and dietary requirements
- **Recipe Builder**: Search over 2 million recipes from an external database for inspiration
- **AI Recipe Helper**: Get AI-powered recipe suggestions tailored to your dietary needs (requires local Ollama LLM)

### Educational Content
- Learn about FODMAPs, histamine, and gut health
- Markdown-supported articles with rich formatting (tables, links, images, code blocks)
- Research paper references with clickable links

### Settings & Data
- Backup and restore your data
- Customizable symptom tags
- Help documentation

---

## REST API (137 Endpoints)

The app includes a comprehensive REST API at `/api/v1/` for programmatic access to all features. All endpoints are protected by API key authentication and scope-based authorization.

### API Documentation

**Interactive Documentation**: Access the complete API documentation via **Swagger UI** at `http://localhost:5000/api/docs`
- Full endpoint reference with all parameters and response schemas
- "Try it out" buttons to test endpoints directly in your browser
- X-API-Key authentication support in the UI
- OpenAPI spec JSON available at `/api/v1/apispec.json`

**Detailed Guides**:
- `api_endpoints.md` — Quick reference of all 137 endpoints by category
- `api_endpoint_full_documentation.md` — Comprehensive guide with examples, migration notes, and authentication details (for API consumers)

### Authentication & Authorization

Every API endpoint is secured with a two-layer system:

1. **API Key Authentication** — Pass your key via `X-API-Key` header or `Authorization: Bearer <key>`
2. **Scope-Based Authorization** — Each key is granted specific scopes (e.g., `read:diary`, `write:recipes`) that control what it can access

**Web browser bypass**: Requests without an API key header (i.e., normal browser usage) pass through unauthenticated, so the web UI works without any setup.

**Rate Limiting**: Each API key has a per-minute request limit (default: 120/min for standard keys, configurable down to 60/min for low-priority keys). Exceeding the limit returns `429 Too Many Requests` with a `Retry-After` header.

**Audit Logging**: All authenticated API requests are logged with key ID, endpoint, method, status code, IP address, and timestamp. Query the audit log via `GET /api/v1/auth/audit-log`.

**Creating an API Key**:
```bash
# Via the API (requires admin:security scope)
POST /api/v1/auth/api-keys
{
  "name": "My App",
  "scopes": ["read:diary", "read:analytics", "read:recipes"],
  "rate_limit": 120
}

# For APP2 integration, use the bootstrap script:
python scripts/create_app2_key.py            # Primary scopes (15)
python scripts/create_app2_key.py --secondary # + Secondary scopes (6)
```

The generated key is shown **once** and cannot be retrieved again. Store it securely.

### Diary (9 endpoints)
- `GET /diary/entries` — Get monthly diary entries grouped by date
- `GET /diary/day/{date}` — Get all entries for specific date with nutrition
- `GET /diary/trends` — Get symptom trends over time period
- `GET /diary/weekly` — Get weekly summary of entries
- `POST /diary/meals` — Create new meal entry
- `PUT /diary/meals/{id}` — Update existing meal entry
- `POST /diary/entries/bulk` — Create multiple entries in one call
- `POST /diary/meal-plan` — Save a 7-day meal plan
- `GET /diary/meal-plan/{id}` — Retrieve a saved meal plan

### Recipes & Meals (15 endpoints)
- `GET /recipes` — List all recipes (paginated)
- `GET /recipes/search` — Search recipes by name, category, cuisine, tags, ingredients
- `GET /recipes/category/{cat}` — Filter recipes by meal type
- `GET /recipes/{id}` — Get recipe details
- `POST /recipes` — Create new recipe
- `PUT /recipes/{id}` — Update recipe
- `DELETE /recipes/{id}` — Delete recipe
- `GET /recipes/{id}/context` — Get recipe formatted for AI context
- `POST /recipes/import` — Import recipe from external JSON
- `POST /recipes/{id}/transform` — Auto-substitute high-risk ingredients with safer alternatives
- `POST /recipes/share` — Export recipe as shareable JSON with unique token
- `GET /meals` — List all saved meals
- `POST /meals` — Create saved meal
- `PUT /meals/{id}` — Update saved meal
- `DELETE /meals/{id}` — Delete saved meal

### Foods & Compendium (14 endpoints)
- `GET /compendium/search` — Search FODMAP foods
- `GET /compendium/foods/{id}` — Get food details with usage stats
- `GET /compendium/compare` — Compare multiple foods side-by-side
- `POST /compendium/foods` — Create new food
- `PUT /compendium/foods/{id}` — Update food
- `DELETE /compendium/foods/{id}` — Delete food
- `POST /foods/quick-add` — Quick add incomplete food entry
- `POST /compendium/foods/{id}/link-ausnut` — Link food to AUSNUT database
- `POST /compendium/foods/{id}/link-usda` — Link food to USDA database
- `GET /foods/batch` — Get multiple foods in one call
- `GET /foods/substitutes` — Find safe FODMAP alternatives for a food
- `GET /foods/unified-search` — Search across FODMAP, USDA, and AUSNUT databases
- `POST /foods/scan-menu` — AI-powered menu scanning (stub)
- `GET /foods/nutrient-boosters` — Safe foods high in a specific nutrient

### Analytics & Dashboard (27 endpoints)
- `GET /dashboard` — Dashboard data (watch list, incomplete foods)
- `POST /foods/risk-rating` — Calculate traffic light for serving size
- `GET /analytics/symptom-patterns` — Correlate symptoms with meals
- `GET /analytics/food-reactions` — Identify food triggers
- `GET /analytics/symptom-trends` — Time-series symptom data
- `GET /analytics/food-frequency` — Most commonly eaten foods
- `GET /analytics/trigger-foods` — Foods on high-symptom days
- `GET /analytics/nutrition-summary` — Aggregated nutrition over date range
- `GET /analytics/fodmap-exposure` — Daily/weekly FODMAP exposure
- `GET /analytics/histamine-exposure` — Daily/weekly histamine exposure analysis
- `GET /analytics/fodmap-stacking` — Cumulative FODMAP load ("gas gauge")
- `GET /analytics/correlations` — Multi-variable food-symptom correlation with lag
- `GET /analytics/gut-stability-score` — 7-day rolling stability signal
- `GET /analytics/tolerance-curves` — Per-food tolerance by serving type
- `GET /analytics/nutrient-rdi-status` — Nutrients as % of RDI
- `GET /analytics/nutrient-gaps` — Nutrient deficits with food suggestions
- `GET /analytics/nutrient-heatmap` — 7-day x nutrient matrix
- `GET /analytics/nutrient-sources` — Food contribution to nutrients
- `GET /analytics/nutrient-symptom-correlation` — Statistical nutrient-symptom links
- `GET /analytics/correlation-matrix` — Food x symptom matrix
- `GET /analytics/bristol-trends` — Stool type time series with rolling average
- `GET /analytics/hydration` — Daily fluid intake vs target
- `GET /analytics/meal-timing` — When the user eats + late-meal analysis
- `GET /analytics/dietary-diversity` — Unique plant count + food groups
- `GET /analytics/flare-prediction` — Rule-based gut flare risk (0-100%)
- `GET /analytics/gut-health-score` — Composite 30-day wellness score
- `GET /analytics/interactions` — Nutrient interaction alerts

### USDA Database (4 endpoints)
- `GET /usda/search` — Search USDA FoodData Central
- `GET /usda/foods` — Browse/list all USDA foods (paginated)
- `GET /usda/foods/{id}` — Get USDA food with nutrients
- `GET /usda/categories` — List USDA categories with food counts

### AUSNUT Database (2 endpoints)
- `GET /ausnut/search` — Search AUSNUT 2023 Australian foods
- `GET /ausnut/foods/{id}` — Get AUSNUT food with nutrients

### Settings & Database (3 endpoints)
- `GET /settings/backup` — Download database backup
- `GET /settings/integrity-check` — Check database integrity
- `POST /settings/integrity-check/fix` — Auto-fix integrity issues

### Help Documents (7 endpoints)
- `GET /help` — List help documents
- `GET /help/{id}` — Get help document
- `POST /help/upload` — Upload markdown file
- `POST /help` — Save help document
- `PUT /help/{id}` — Update help document
- `DELETE /help/{id}` — Delete help document
- `POST /help/preview-markdown` — Convert markdown to HTML

### Education (9 endpoints)
- `GET /education` — List educational chapters
- `GET /education/{id}` — Get chapter details
- `POST /education/upload` — Upload chapter markdown
- `POST /education` — Save chapter
- `PUT /education/{id}` — Update chapter
- `DELETE /education/{id}` — Delete chapter
- `POST /education/reorder` — Update chapter order
- `POST /education/images` — Upload image for chapters
- `POST /education/preview-markdown` — Preview markdown as HTML

### AI Chat (5 endpoints)
- `POST /chat` — Send message to AI (Ollama/OpenAI/Anthropic)
- `GET /chat/conversations` — List all conversations
- `GET /chat/conversations/{id}` — Get conversation with messages
- `DELETE /chat/conversations/{id}` — Delete conversation
- `POST /chat/conversations/{id}/rename` — Rename conversation

### FODMAP Reference (2 endpoints)
- `GET /fodmap/categories` — Get FODMAP categories with counts
- `GET /fodmap/foods` — Get foods by category

### Search & Discovery (3 endpoints)
- `GET /search/global` — Search across all entities (foods, recipes, meals, help, education)
- `GET /foods/recommendations` — Get safe foods based on dietary restrictions
- `GET /recipes/suitable` — Get recipes matching dietary criteria

### Export & Reporting (3 endpoints)
- `GET /export/diary` — Export diary data (JSON or CSV)
- `GET /export/report/pdf` — Generate PDF health report
- `GET /export/shopping-list` — Generate shopping list from recipes

### Real-time & Webhooks (8 endpoints)
- `GET /events/stream` — Server-Sent Events stream for real-time updates
- `POST /webhooks/register` — Register a webhook URL
- `GET /webhooks` — List all registered webhooks
- `GET /webhooks/{id}` — Get webhook details
- `PUT /webhooks/{id}` — Update webhook configuration
- `DELETE /webhooks/{id}` — Delete webhook
- `POST /webhooks/{id}/test` — Test webhook with sample payload
- `POST /webhooks/external/receive` — Receive inbound webhook from external services (signature-verified, no API key)

### Gamification (3 endpoints)
- `GET /gamification/challenges` — List active challenges
- `POST /gamification/challenges` — Create a new challenge
- `GET /gamification/badges` — List earned badges

### Reintroduction Protocol (3 endpoints)
- `POST /reintroduction/protocol` — Start a FODMAP reintroduction protocol
- `GET /reintroduction/schedule` — Get reintroduction testing schedule
- `POST /reintroduction/evaluate` — Evaluate reintroduction test results

### Notifications (7 endpoints)
- `GET /notifications/settings` — Get notification preferences
- `POST /notifications/send` — Send a notification
- `POST /notifications/rules` — Create notification rule
- `GET /notifications/rules` — List notification rules
- `POST /notifications/schedule` — Schedule a notification
- `GET /notifications` — List all notifications
- `POST /notifications/{id}/mark-read` — Mark notification as read

### Security & Access Control (5 endpoints)
- `POST /auth/api-keys` — Generate API key (validates scopes, configurable rate limit)
- `GET /auth/api-keys` — List API keys (prefix only, never exposes full key)
- `DELETE /auth/api-keys/{key_id}` — Revoke API key (soft delete)
- `GET /auth/rate-limit` — Get per-key rate limit status (requests/min, remaining, reset time)
- `GET /auth/audit-log` — Query API access logs (filter by key, endpoint, method, date range)

### Integrations (3 endpoints)
- `POST /wearables/connect` — Connect wearable device (stub)
- `POST /wearables/sync` — Sync wearable data (stub)
- `POST /voice/log` — Voice-based diary logging (stub)

### Billing (2 endpoints)
- `GET /billing/status` — Get subscription/premium status (stub)
- `POST /billing/webhook` — Receive billing/subscription webhooks (signature-verified, no API key)

### Multi-User & Cohort Analysis (3 endpoints)
- `GET /users/cohort-analysis` — Cohort analysis (stub)
- `GET /users/compare` — Compare user data (stub)
- `GET /users/phenotypes` — User phenotype classification (stub)

---

## Database Migrations

The app uses **Flask-Migrate** (Alembic) for version-controlled database schema management. This allows safe, repeatable database updates across versions.

**For developers**: When you modify models, generate a migration and apply it:
```bash
flask db migrate -m "description of changes"
flask db upgrade
```

**For users**: Database updates are handled automatically. Your existing database is compatible with all new versions.

Old migration scripts (pre-Alembic) are preserved in `migrations_legacy/` for reference.

---

## Tech Stack

- **Backend**: Python Flask 3.0.0
- **Database**: SQLite 3 with Flask-Migrate/Alembic (version-controlled)
- **API Documentation**: Swagger/OpenAPI 2.0 with Flasgger
- **Frontend**: Jinja2 templates, Bootstrap 5, vanilla JavaScript
- **No external cloud services**: Everything runs locally

## Getting Started

### Prerequisites

- Python 3.10 or higher

### Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Gut_Health_Management_App.git
   cd Gut_Health_Management_App
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **(Optional) Download the Recipe Builder Database**:

   The Recipe Builder feature requires an external recipe database (~770MB). Download from Hugging Face:

   - Visit: https://huggingface.co/datasets/corbt/all-recipes
   - Download all 4 parquet files from the `data/` folder
   - Place them in: `data/recipes/external/`

   The app will work without this database, but the Recipe Builder search feature will be unavailable.

4. **(Optional) Import the USDA Food Database**:

   The USDA Foods feature provides comprehensive nutritional data for 7,000+ foods. **These large files are NOT included in this repository** — you must download them separately:

   - Download the USDA FoodData Central JSON files from [USDA FDC](https://fdc.nal.usda.gov/download-datasets.html)
   - Place them in `data/usda/` (the directory will be created automatically)
   - Run the import script: `python database/import_usda_foods.py`

   The app will work without this database, but the USDA Foods browsing feature will be unavailable.

5. **(Optional) Import the AusNut Food Database**:

   The AusNut Foods feature provides Australian food composition data. **These large files are NOT included in this repository** — you must download them separately:

   - Download from: [Food Standards Australia New Zealand](https://www.foodstandards.gov.au/science/monitoringnutrients/afcd)
   - Place the AUSNUT 2023 Excel file in `data/ausnut/`
   - Run the import script: `python database/import_ausnut_foods.py`

   The app will work without this database, but the AusNut Foods browsing feature will be unavailable.

5. Run the application:

   **Easy Launch (Recommended):**
   - Double-click `user_mode.vbs` - Starts the app invisibly (no terminal windows) and opens your browser
   - Double-click `start_admin.vbs` - Same as above, but with admin mode enabled for content editing

   **Alternative Launch Options:**
   - `user_mode.bat` - Starts with visible terminal (useful for debugging)
   - `start_admin.bat` - Admin mode with visible terminal
   - `python app.py` - Basic command-line launch

   **To Exit:** Click the "Exit" button in the top-right corner of the app header for a clean shutdown.

6. Your browser will open automatically to: **http://localhost:5000**

### Optional: AI Recipe Helper Setup

To use the AI Recipe Helper feature, you'll need a local Ollama LLM model on your pc. The AI helper will suggest recipes based on your dietary restrictions and available ingredients.

## Project Structure

```
Gut_Health_Management_App/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models/                # Database models
│   ├── food.py            # FODMAP food model
│   ├── usda.py            # USDA food database models
│   ├── ausnut.py          # AUSNUT food database models
│   ├── diary.py           # Diary entry models (7 models)
│   ├── recipe.py          # Recipe models (6 models)
│   ├── education.py       # Educational content models
│   ├── user.py            # User preference models
│   ├── chat.py            # Chat conversation models
│   ├── webhooks.py        # Webhook & event log models
│   ├── gamification.py    # Challenge & badge models
│   ├── reintroduction.py  # FODMAP reintroduction models
│   └── security.py        # API key, access log, and rate limit models
├── routes/                # URL route handlers
│   ├── api_v1/            # REST API v1 (137 endpoints across 20 modules)
│   ├── compendium.py      # Food Compendium web interface
│   ├── diary.py           # Diary web interface
│   ├── recipes.py         # Recipe web interface
│   ├── recipe_builder.py  # Recipe Builder routes
│   ├── usda_foods.py      # USDA Foods browsing routes
│   ├── ausnut_foods.py    # AUSNUT Foods browsing routes
│   ├── education.py       # Education web interface
│   ├── settings.py        # Settings web interface
│   └── main.py            # Dashboard
├── templates/             # HTML templates
│   ├── dashboard/         # Main landing page
│   ├── compendium/        # Food Compendium pages
│   ├── diary/             # Diary and tracking
│   ├── recipes/           # Recipe management (incl. builder)
│   ├── education/         # Educational content
│   ├── settings/          # App settings & help
│   └── usda_foods/        # USDA food database browsing
├── static/                # CSS, JavaScript, images
├── utils/                 # Utility modules
│   ├── auth.py            # API key authentication & scope authorization decorators
│   ├── validators.py      # Input validation (12 functions)
│   ├── pagination.py      # Paginated query helpers
│   ├── api_helpers.py     # Standardized API responses
│   ├── nutrition.py       # Nutrition calculation helpers
│   ├── recipe_parser.py   # Parse recipes from URLs
│   └── recipe_search.py   # External recipe database search
├── scripts/               # Management scripts
│   └── create_app2_key.py # Generate APP2 bootstrap API key
├── migrations/            # Database migration scripts
├── database/              # Database import scripts
│   └── import_usda_foods.py  # USDA data import script
└── data/                  # User data storage
    ├── recipes/external/  # External recipe database (download separately)
    └── usda/              # USDA FoodData Central JSON files
```

## Privacy

This app is designed for **local use only**. All your data stays on your computer in a SQLite database file. There are no accounts, no cloud sync, and no data collection.

To backup your data, simply copy the `gut_health.db` file from the `instance/` folder.

## License

This project is for personal use. Feel free to fork and modify for your own needs.

## Acknowledgments

Built with the help of Claude AI for code assistance and debugging.

---

**Version**: 1.4.0 (Swagger API Docs + Database Migrations)
