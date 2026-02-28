# Gut Health Management App

> **MANDATORY**: Read this file before ANY changes. Update `Version_History.md` with dates for all changes.

## ⚠️ CRITICAL: Database & .gitignore Protection Rules

**🚨 NEVER DELETE FILES LISTED IN .gitignore**

Files in `.gitignore` are there for a reason - they are TOO LARGE or contain USER DATA that should NOT be version controlled:

### Absolute Rules:
1. **NEVER delete `instance/gut_health.db`**
   - This is the user's database containing all their health data
   - It's in .gitignore because it's 372+ MB (too large for GitHub)
   - Being in .gitignore does NOT mean it should be deleted
   - Being in .gitignore means it should STAY LOCAL ONLY

2. **NEVER delete any `data/usda/*.json` files**
   - These are large external data files (100-3000+ MB)
   - They are in .gitignore for the same reason
   - If they exist locally, they are intentional - LEAVE THEM ALONE

3. **NEVER delete any `data/ausnut/` files**
   - Same principle - they're big, they're local, they're intentional

### What .gitignore Actually Means:
- ✅ DO NOT track these files in git
- ✅ DO NOT push them to GitHub
- ✅ DO NOT include them in commits
- ❌ DO NOT delete them from the local filesystem
- ❌ DO NOT remove them from the working directory

### Before Making Changes Involving Files:
1. Check if the file is in `.gitignore`
2. If YES: Ask the user before touching it
3. If it's a database or user data: NEVER delete it
4. When in doubt: ASK THE USER FIRST

This is not optional. Databases are irreplaceable user data.

---

## App Overview
- **Stack**: Flask + SQLite + Jinja2 templates + Bootstrap
- **Purpose**: Track diet, symptoms, identify FODMAP/histamine food triggers
- **Launch**: `python app.py` (user mode), `start_admin.bat` (admin), or `.vbs` variants for hidden terminal
- **Exit**: Click "Exit" button in header (top-right) for graceful shutdown via `/shutdown` route

## Structure
```
templates/
├── dashboard/    # Main landing (/)
├── compendium/   # Food Compendium (/compendium) - index, search, detail, add-food, edit-food
├── diary/        # Logging (/diary) - calendar, day view, entry forms
├── recipes/      # My Recipe Book (/recipes)
├── education/    # Educational content (/education) - markdown support
└── settings/     # Config (/settings) - backup, tags, help documents
    └── help/     # Help & Support (/settings/help) - FAQs, tips, navigation guides

routes/
├── api_v1/       # REST API (137 endpoints, /api/v1/ prefix)
│   ├── analytics.py (27), diary.py (9), recipes.py (15), foods.py (14)
│   ├── usda.py (4), ausnut.py (2), chat.py (5), fodmap.py (2)
│   ├── search.py (3), export.py (3), realtime.py (8), settings.py (10), education.py (9)
│   ├── gamification.py (3), reintroduction.py (3), notifications.py (7)
│   ├── security.py (5), integrations.py (3), billing.py (2), multi_user.py (3)
│   └── __init__.py  # Blueprint registration
├── compendium.py, diary.py, recipes.py, education.py, settings.py
├── recipe_builder.py, usda_foods.py, ausnut_foods.py
└── main.py       # Dashboard

utils/
├── validators.py   # Input validation (12 functions)
├── pagination.py   # Paginated query helpers
├── api_helpers.py  # Standardized error/success responses
├── nutrition.py    # Nutrition calculation helpers
└── markdown_utils.py
```

## Color Scheme
| Color | Hex/Variable | Usage |
|-------|-------------|-------|
| Sage Green | #8BA48B | Primary, sidebar gradient start |
| Dark Green | #677D6A / `--sage` | Sidebar gradient end, muted text |
| Beige/Gold | #D6BD98 / `--gold` | Header, accents, links |
| Dark Green | #1A3636 / `--bg-deep` | Page background, text/emphasis |
| Olive Green | #40534C / `--bg-elevated` | Card backgrounds |
| White-ish | #e0e7e1 / `--white-ish` | Primary text color |
| Traffic Lights | #28a745 / #ffc107 / #dc3545 | Green/Amber/Red ratings |

## Layout (Fixed, No Responsive)
```
┌─────────────────────────────────────────────────────────┐
│  HEADER (fixed, 50px, z-index: 1000, #D6BD98)           │
├────────────┬────────────────────────────────────────────┤
│  SIDEBAR   │   MAIN CONTENT AREA (max 880px)           │
│  (200px)   │   ┌──────────────────────┐                │
│  fixed     │   │ CONTENT COL (620px)  │                │
│  z:100     │   │  max-width           │                │
│            │   └──────────────────────┘                │
└────────────┴────────────────────────────────────────────┘
```

**CSS Variables** (in `static/css/main.css`):
- `--layout-main-max: 880px` — Main content area max width
- `--layout-content-max: 620px` — Inner content column max width

**Key Rules**:
- Sidebar: `position: fixed`, 200px wide, green gradient
- Main content: `margin-left: 200px`, `padding-left: 15px`
- Content column classes: `.dashboard-content-col`, `.compendium-content-col`, `.content-col` etc.
- **CRITICAL**: Never override `.main-content-area` or content column classes with inline CSS
- **Never** use `width: 100vw` (use `right: 0`), `min-width` on containers, or Bootstrap `.navbar`
- `overflow-x: hidden` on html and body — no horizontal scrollbars

## Typography Tokens (in `static/css/main.css`)
```css
--text-micro:  0.62rem;   /* RDI%, footnotes */
--text-label:  0.67rem;   /* Labels, nav, form labels */
--text-body:   0.70rem;   /* Default body text, buttons */
--text-value:  0.76rem;   /* Numeric values, food names */
--text-title:  0.85rem;   /* Card headers */
--text-h2:     1.10rem;   /* Page titles */
```
**Rule**: Values (0.76rem, bold) > Labels (0.67rem, normal) for visual hierarchy

## Key Data Concepts
- **FODMAP Types**: Fructose, Sorbitol, Lactose, GOS, Fructans, Mannitol, Polyols
- **Serving Sizes**: Safe (green), Moderate (amber), High (red) — each has independent FODMAP/histamine ratings
- **Histamine**: Level (Low/Med/High), DAO Blocker (Y/N), Liberator (Y/N)
- **Traffic Light**: Calculated from worst rating across all types
- **Packaged Foods**: Foods with nutritional info but no serving sizes — "Add to Diary" via free-text quantity

## Design Rules
- Compact sizing: btn-sm, 10px card padding, mb-2/mb-3 margins
- Lists: Alphabetical, single-line
- Buttons in sidebar: Full width, vertically stacked, below separator line
- CSS/JS: Inline in templates (current pattern)
- Files: kebab-case; Python: snake_case

## Education System
- **Processor**: `markdown2` with extensions: `tables`, `fenced-code-blocks`, `header-ids`, `task-list`
- **Templates**: chapter.html (view), edit.html (edit), preview.html (upload preview)
- **Styling**: Inline CSS in education templates; links gold in chapter view, dark green in edit/preview
- **External links**: Auto-open in new tab with `rel="noopener noreferrer"`

## Development Checklist

### File Operations & Git Safety Checklist (DO THIS FIRST)
**BEFORE making ANY changes to files:**
- [ ] **Check `.gitignore` first** - Is this file listed in `.gitignore`?
- [ ] **If it's a database (.db) file:** STOP - Ask user before touching it
- [ ] **If it's in `.gitignore` for size reasons:** STOP - Ask user before deleting
- [ ] **If cleaning up git:** NEVER use `git rm` on ignored files without asking
- [ ] **When removing files:** Verify they are tracked in git FIRST (`git status`)
- [ ] **Large files:** If >100MB exists locally, it's intentional - LEAVE IT ALONE
- [ ] **User data:** NEVER delete databases, backups, or user-generated files

### General Development Rules
1. Read CLAUDE.md completely before ANY changes
2. Update `Version_History.md` with date and details
3. Follow color scheme and typography tokens
4. Keep all nav links in every sidebar
5. Test at 100% zoom for compact appearance

### API Endpoint Modification Checklist
When modifying ANY endpoint in `routes/api_v1/`:
- [ ] Update the route code itself
- [ ] Update `api_endpoint_full_documentation.md` with request/response examples
- [ ] Update the Postman collection (`postman_collection.json`)
- [ ] Update `api_endpoints.md` endpoint reference
- [ ] Update `Version_History.md` with date and change details

### Database Model/Schema Changes Checklist
When modifying ANY model in `models/`:
- [ ] Update the model code (add/remove/modify fields)
- [ ] Create a database migration: `flask db migrate -m "description"`
- [ ] Update `DATA_SCHEMA_REFERENCE.md` if schema changed
- [ ] Update `Version_History.md` with date and schema impact notes
- [ ] Run tests to verify serialization/deserialization still works
- [ ] Test API endpoints that use the modified model

### New Route File Checklist
When creating a NEW route file (especially in `routes/api_v1/`):
- [ ] Create the route file using kebab-case naming (e.g., `my_feature.py`)
- [ ] Register the blueprint in `routes/api_v1/__init__.py`
- [ ] Add endpoint count to Structure section in CLAUDE.md
- [ ] Update total endpoint count in TODO.md's "API Endpoints" section
- [ ] Document all endpoints in `api_endpoint_full_documentation.md`
- [ ] Add all requests to `postman_collection.json`
- [ ] Apply `@require_api_key` and `@require_scope()` decorators to all routes
- [ ] Update `Version_History.md` with date and new routes summary

### Template & UI Changes Checklist
When modifying templates or adding new UI elements:
- [ ] Use ONLY documented CSS color variables (--sage, --gold, --bg-deep, etc.)
- [ ] Use ONLY documented typography tokens (--text-micro, --text-body, --text-h2, etc.)
- [ ] Maintain sidebar fixed layout: 200px width, `position: fixed`, `z-index: 100`
- [ ] Maintain main content margin: `margin-left: 200px`, `padding-left: 15px`
- [ ] Never override `.main-content-area` or content column classes with inline CSS
- [ ] No `width: 100vw` or `min-width` on containers
- [ ] Test at 100% zoom for compact appearance
- [ ] Verify no horizontal scrollbars (ensure `overflow-x: hidden` on html/body)
- [ ] Update `Version_History.md` if layout/styling changed significantly

### Sidebar Navigation Checklist
When adding a new navigation link or changing navigation structure:
- [ ] Link appears in `/dashboard` page sidebar
- [ ] Link appears in `/diary` page sidebar
- [ ] Link appears in `/recipes` page sidebar
- [ ] Link appears in `/compendium` page sidebar
- [ ] Link appears in `/education` page sidebar
- [ ] Link appears in `/settings` page sidebar
- [ ] Navigation is consistent across all pages (maintain full link list)
- [ ] Update `Version_History.md` with navigation changes

### Help/Education Content Checklist
When adding new education modules or help documents:
- [ ] Add file to appropriate folder (`data/help_docs/` or education database)
- [ ] Follow markdown processor extensions: `tables`, `fenced-code-blocks`, `header-ids`, `task-list`
- [ ] Use correct color scheme in markdown:
  - Links gold (#D6BD98) in chapter view
  - Links dark green (#677D6A) in edit/preview
- [ ] Update education/help index or navigation references
- [ ] Test markdown rendering with `POST /api/v1/help/preview-markdown` or `POST /api/v1/education/preview-markdown`
- [ ] Update `Version_History.md` with date and content summary
- [ ] Verify external links open in new tab with `rel="noopener noreferrer"`

### Database Import/Food Data Changes Checklist
When running import scripts for USDA/AusNut/FODMAP foods:
- [ ] Document which import script was run and date in `Version_History.md`
- [ ] Record row count changes (before/after) in Version_History.md
- [ ] Update any cached food count fields (e.g., `USDAFoodCategory.food_count`)
- [ ] Re-run tests for food search/lookup endpoints (`/compendium/search`, `/usda/search`, `/ausnut/search`)
- [ ] Verify food-recipe linking still works if foreign keys changed
- [ ] Clear any caching layers if implemented
- [ ] Update `README.md` database statistics if public-facing

### Configuration & Environment Variables Reference
**Available environment variables** (set in `.env` or `config.py`):
- `FLASK_ENV` — `development` or `production`
- `DATABASE_URL` — SQLite path (default: `sqlite:///gut_health.db`)
- `SECRET_KEY` — Flask session encryption key
- `API_KEY_SALT` — Salt for hashing API keys in database
- `MAX_CONTENT_LENGTH` — Max upload size for files
- `FLASGGER_ENABLED` — Enable/disable Swagger UI (default: `True`)

**When adding new env vars:**
- [ ] Document in this section
- [ ] Add defaults to `config.py`
- [ ] Update `.env` template or `.flaskenv` example
- [ ] Document in `README.md` setup section if user-facing
- [ ] Update `Version_History.md` with what the var controls

### Error Code/Response Format Registry
**Standard API response format** (all endpoints use this):
```json
{
  "success": true|false,
  "message": "Human-readable message",
  "data": {...},
  "error_code": "OPTIONAL_ERROR_CODE",
  "timestamp": "2026-02-28T12:34:56Z"
}
```

**When adding new error codes:**
- [ ] Add to `utils/api_helpers.py` with clear name (e.g., `INVALID_FOOD_ID`)
- [ ] Document error code, HTTP status, and what triggers it
- [ ] Update `api_endpoint_full_documentation.md` error codes reference
- [ ] Add example error response to relevant endpoint documentation
- [ ] Update `DATA_SCHEMA_REFERENCE.md` if error object changes
- [ ] Ensure error messages are user-friendly and actionable
