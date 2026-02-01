# Gut Health Management App - Developer Guide

> **IMPORTANT**: This file displays and tracks all the updates that are made to the app. It must be updated whenever you make any changes. Include dates for version tracking.

---

## 🏗️ Application Structure

### Tech Stack
- **Backend**: Flask (Python)
- **Frontend**: HTML templates (Jinja2), Bootstrap, JavaScript
- **Database**: SQLite (assumed, standard for Flask apps)
- **Styling**: CSS with custom color scheme (sage green #8BA48B, gold #D6BD98, dark green #1A3636, white-ish)

### Page Architecture
All pages are in `templates/` folder organized by feature:

```
templates/
├── dashboard/          # Main landing page
├── foods/             # Food guide and management
├── diary/             # Symptom and meal logging
├── recipes/           # Recipe and meal management
├── education/         # Educational content
└── settings/          # App configuration
```

---

**Templates**:
- `templates/foods/index.html` - Main food guide page
- `templates/foods/search.html` - Category food lists
- `templates/foods/detail.html` - Individual food view
- `templates/foods/add-food.html` - Add new food form
- `templates/foods/edit-food.html` - Edit food form

---

## 🗓️ Version History

**Latest Updates: 2026-02-01 (Recipe Builder + AI Chat Integration)**

- **Recipe Builder to AI Chat Integration** (`templates/recipes/builder_preview.html`, `templates/recipes/chat.html`)
  - Added "Ask AI About This" button on Recipe Builder preview page
    - Formats recipe (name, ingredients, directions) and sends to AI Chat
    - Pre-populates chat with prompt asking AI to analyze recipe for gut health
    - Uses sessionStorage to pass recipe data between pages
  - Added "Copy for AI" button on Recipe Builder preview page
    - Copies formatted recipe text to clipboard
    - Visual feedback when copied
  - Added "Paste Recipe" button in AI Chat input area
    - Clipboard icon button next to Send button
    - Reads clipboard and pastes into message input
    - Visual feedback when pasted
  - AI Chat now shows toast notification when recipe is loaded from Recipe Builder
    - Auto-dismisses after 5 seconds
    - Message pre-populated and ready to send

---

**Previous Updates: 2026-02-01 (Recipe Builder Feature)**

- **Recipe Builder - External Recipe Search** (New Feature)
  - Added Recipe Builder feature to browse and search 2.15 million recipes from external dataset
  - New files created:
    - `utils/recipe_parser.py` - Parse recipe text into structured data (name, ingredients, directions)
    - `utils/recipe_search.py` - Polars-based search engine for parquet files
    - `routes/recipe_builder.py` - Blueprint with search, preview, archive, and save routes
    - `templates/recipes/builder.html` - Main search/browse interface
    - `templates/recipes/builder_preview.html` - Recipe preview with save options
    - `templates/recipes/builder_archived.html` - View and manage archived recipes
  - Features include:
    - Keyword search across recipe names and ingredients
    - Ingredient-based search (comma-separated list)
    - Random recipe suggestions for inspiration
    - Archive recipes you don't want to see again
    - Save recipes to your Recipe collection
    - Save recipes as Saved Meals
    - Shows total recipe count (2.15M) and archived count
  - Added `ArchivedExternalRecipe` model to track archived recipe hashes
  - Added `polars` and `pyarrow` dependencies to requirements.txt
  - Parquet data files stored in `data/recipes/external/`
  - Links added to Recipes & Meals index page and Quick Access sidebars

---

**Previous Updates: 2026-02-01 (AI Loading Progress Bar)**

- **AI Recipe Helper - Loading Progress Bar** (`templates/recipes/chat.html`)
  - Replaced text-based "Waiting for response..." message with animated loading indicator
  - Loading bar appears in chat area as an assistant message bubble while AI is processing
  - Shows animated progress bar with pulsing robot icon and "AI is thinking..." text
  - Displays which model and provider is being used (e.g., "Using llama3.2 via ollama")
  - Loading indicator is automatically removed when response arrives
  - Error messages now appear in chat area with styled error bubble instead of plain text

---

**Previous Updates: 2026-02-01 (Ollama Model Selector)**

- **AI Recipe Helper - Ollama Model Dropdown** (`templates/recipes/chat.html`)
  - Replaced text input for Ollama model with a dynamic dropdown selector
  - Automatically polls local Ollama installation to discover available models
  - Displays model names with file sizes (e.g., "llama3.2 (2.0 GB)")
  - Shows model count in connection status (e.g., "Ollama is running - 5 models available")
  - Added refresh button to re-fetch model list without page reload
  - Gracefully handles missing Ollama or no installed models with helpful messages
  - Text input remains available for OpenAI and Anthropic providers
  - Model selector switches appropriately when changing providers

---

**Previous Updates: 2026-02-01 (Recipe Context in AI Chat)**

- **AI Chat Recipe Context Feature** (`routes/api.py`, `templates/recipes/chat.html`)
  - Added ability to include saved recipes as context in AI chat conversations
  - New recipe selector UI: click "Add Recipe Context" button to search and select recipes
  - New @ mention autocomplete: type `@` followed by recipe name to quickly add recipe context
  - Selected recipes are displayed as tags above the chat input with remove buttons
  - AI receives full recipe details (ingredients, instructions, notes) when referenced
  - User messages show which recipes were used as context
  - New API endpoints:
    - `GET /api/recipes/search` - Search recipes by name for autocomplete
    - `GET /api/recipes/<id>/context` - Get formatted recipe details for AI
  - Modified chat endpoint to accept `recipe_ids` parameter and inject recipe context into AI prompts
  - Works with all LLM providers (Ollama, OpenAI, Anthropic)

---

**Previous Updates: 2026-02-01 (AI Chat Timeout Fix)**

- **AI Recipe Helper - Conversation Timeout Fix** (`routes/api.py`, `templates/recipes/chat.html`)
  - Fixed timeout error occurring on second message in AI chat conversations
  - Switched from Ollama's `/api/generate` endpoint to `/api/chat` endpoint for better conversation handling
  - Implemented conversation history limiting (max 10 messages) to prevent context explosion and timeouts
  - Increased timeout from 120 seconds to 300 seconds (5 minutes) for longer responses
  - Added specific error handling for timeout, connection, and HTTP errors
  - Improved response parsing with fallback support for different Ollama response formats
  - Added user feedback message indicating longer wait times for ongoing conversations
  - Enhanced error messages to provide clearer guidance when timeouts occur

**Updates: 2026-02-01 (Dashboard Date Format Update)**

- **Dashboard Date Display Enhancement** (`app.py`, `templates/dashboard/index.html`)
  - Added custom `ordinal` Jinja2 filter to format day numbers with ordinal suffixes (1st, 2nd, 3rd, etc.)
  - Updated dashboard date header to display day name on first line (larger, 1.7rem) and ordinal date on second line (smaller, 0.85rem), both in bold
  - Changed date color to dark blue (#005588) with !important to ensure override
  - New format: "Sunday" (large) / "1st February 2026" (small) - both bold, dark blue - instead of "Sunday, February 01, 2026"

**Updates: 2026-02-01 (AI Recipe Transfer to Forms)**

- **AI Recipe Transfer Feature** (`templates/recipes/chat.html`, `templates/recipes/create_recipe.html`, `templates/recipes/create_meal.html`)
  - Added "Add to Recipe" and "Add to Meal" buttons to chatbot-generated recipes
  - Implemented automatic form pre-filling from AI-generated recipe data
  - Enhanced recipe extraction to capture prep time, cook time, servings, notes, and description
  - Automatic ingredient matching: system attempts to match ingredient text to foods in database
  - Quantity extraction: automatically parses quantities from ingredient strings (e.g., "1 cup flour")
  - Pre-fills recipe form with: name, description, prep time, cook time, servings, instructions, notes, and ingredients
  - Pre-fills meal form with: name, description, and food items with portions
  - Shows success notification when AI recipe data is loaded
  - Uses sessionStorage for data transfer between pages
  - Intelligently clears sessionStorage after loading to prevent duplicate loads

**Previous Updates: 2026-02-01 (Recipe Chat Formatting & UI Improvements)**

- **Recipe Chat Formatting** (`templates/recipes/chat.html`)
  - Implemented markdown-style formatting for AI responses in chat
  - Recipes now display with proper headings (###), bullet lists, and bold text
  - Added CSS styling for h3 headers, lists, paragraphs, and strong tags in chat messages
  - Created `formatMessage()` function to convert markdown to HTML
  - Removed side panel dependency - recipes display directly in chat
  - Updated action buttons: "Copy Recipe" (inline) and "Create Recipe" (navigates to recipe creation)
  - Improved readability with color-coded headers (#D6BD98) and proper line spacing

**Previous Update: 2026-02-01 (AI Persona System)**

- **AI Persona System** (`models/chat.py`, `routes/api.py`, `migrations/add_chat_persona.py`)
  - Added `persona` field to ChatConversation model with 4 persona options:
    - **Nutritionist**: Gut health expert focused on FODMAP/histamine guidance
    - **Chef**: Creative chef specializing in gut-friendly cuisine
    - **Scientist**: Researcher providing evidence-based digestive health info
    - **Friendly**: Supportive friend with gut health knowledge
  - Created migration script to add persona field to existing database
  - Updated API endpoints to support persona-specific system prompts
  - Each persona has unique pre-prompt that shapes AI responses

- **Chat UI Enhancements** (`templates/recipes/chat.html`)
  - **Dark Green Color Scheme**:
    - Chat window background changed to dark green (#1A3636)
    - User messages: olive green (#40534C) with gold role labels (#D6BD98)
    - AI messages: deep green (#1A3636) with sage role labels (#8BA48B)
    - Improved text contrast with light text (#e0e7e1)
  - **Reduced Chat Window**:
    - Height reduced from 600px to 400px for better screen usage
    - Auto-scrolling scrollbar appears when messages exceed window height
  - **Persona Selector**:
    - Added persona dropdown in sidebar below Quick Access
    - Shows current persona for loaded conversations
    - Displays persona badge in chat history
    - Automatically applies selected persona to new conversations

**Previous Updates: 2026-02-01 (AI Recipe Helper Enhancement)**

- **AI Recipe Helper Page Complete Redesign** (`templates/recipes/chat.html`)
  - **LAYOUT UPDATES**:
    - Added standard sidebar navigation with all 7 nav links (Dashboard, Food Guide, Diary, Recipes, Education, Settings, Help & Support)
    - Fixed layout to match CLAUDE.md specifications (200px sidebar, max 880px main area, max 620px content column)
    - Changed from Bootstrap grid layout (col-lg-8/col-lg-4) to fixed-width layout
    - Restructured to single-column layout with collapsible chat history section
  - **NEW FEATURES**:
    - **Ollama Connection Status**: Auto-checks Ollama connection on page load, shows green/red status indicator
    - **Recipe Detection**: JavaScript automatically detects when AI generates a recipe (checks for "Ingredients:" and "Instructions:")
    - **Recipe Side Panel**: Slides in from right when recipe detected, allows preview, copy to clipboard, or create recipe
    - **Conversation Context**: AI now receives full conversation history for better context-aware responses
    - **Collapsible Chat History**: Chat history in accordion-style collapsible card with gold header
  - **CSS ENHANCEMENTS**:
    - Added recipe side panel styles (fixed position, slide animation, 500px width)
    - Added recipe panel overlay (semi-transparent background)
    - Chat message styling (user messages right-aligned blue, assistant left-aligned green)
    - Improved history item hover states and active states
- **API Enhancement** (`routes/api.py`)
  - Updated `call_ollama()` function to accept message array instead of single message
  - Modified `/api/chat` endpoint to load and send full conversation history for context
  - Improved conversation continuity and AI understanding
- **Configuration Update** (`config.py`)
  - Changed default Ollama model from `llama3.1:8b` to `hf.co/MaziyarPanahi/phi-4-GGUF:latest`
  - Uses local phi-4 model optimized for recipe and food advice

**Previous Updates: 2026-02-01 (Recipe View Page Layout Alignment Fix)**

- **Recipe View Page Layout Alignment**: Fixed container alignment on recipe detail page (`templates/recipes/view_recipe.html`) to match dashboard page
  - **STRUCTURE FIXES**:
    - Removed hard-coded spacer div, replaced with proper `padding-top: 40px` on main-content-area
    - Added `.recipe-detail-main-bg` class to `.main-content-area` div
    - Wrapped content column in `<div class="row">` for consistency with dashboard
    - Updated closing div structure to match new layout hierarchy
  - **CSS ENHANCEMENTS**:
    - Enhanced `.recipe-detail-main-bg` with full background styling (min-height, background-color, padding management)
    - Applied dark green background (`var(--bg-deep)`) without wallpaper image for clean appearance
    - Added footer spacing normalization
  - **RESULT**: Recipe detail containers and text now align to 620px max-width, matching dashboard and all other pages
  - **FILES MODIFIED**: `templates/recipes/view_recipe.html` (CSS and HTML structure)

**Previous Updates: 2026-02-01 (Recipe View Page Layout Redesign)**

- **Recipe View Page Layout Redesign**: Restructured recipe detail page to match new design specification
  - **NEW LAYOUT**:
    - Title and metadata at top with inline prep time, cook time, servings
    - Two-column layout: Image + Ingredients on left | Preparation/Method on right
    - Recipe image positioned at top-left (280px max-height, bordered with gold)
    - Ingredients list below image in same column
    - Preparation/instructions in right column
    - Additional info sections below: Recipe Info, Ingredient Analysis (FODMAP & Histamine), Notes
  - **STYLING**:
    - Cards use `--bg-elevated` (olive green) background
    - Headers use `--bg-deep` (dark green) with `--gold` text
    - Consistent padding (10px card body, 8px headers)
    - Typography tokens applied throughout (`--text-title`, `--text-body`, `--text-value`, `--text-label`)
    - Gold borders on title and image
  - **CONTENT IMPROVEMENTS**:
    - Ingredient analysis shows FODMAP/Histamine data for each ingredient individually
    - Consolidated allergen warnings with visual badges
    - Compact, single-page view with all info accessible without scrolling through large sections
    - Removed large icon displays, simplified metadata presentation
  - **TECHNICAL**:
    - Added `.recipe-detail-content-col` class to main.css (max-width: 620px)
    - Maintains proper container widths per CLAUDE.md specifications
    - Responsive column layout (col-md-5 for left, col-md-7 for right)
  - **FILES MODIFIED**:
    - `templates/recipes/view_recipe.html` - Complete layout restructure
    - `static/css/main.css` - Added `.recipe-detail-content-col` to width constraints

**2026-02-01 (Recipes Page Container Width Fix)**

- **Recipes & Meals Page Container Width (BUG FIX)**: Fixed containers extending too far to the right
  - **THE PROBLEM**:
    - Recipe index page containers were wider than intended, extending too far right
    - Missing Bootstrap `.row` wrapper around content column (unlike dashboard and food detail pages)
    - Without `.row`, the flexbox context needed for `.content-col` width constraints was missing
    - The `flex: 0 1 auto` property on `.content-col` requires a flex container parent to work
    - Dashboard structure: `.main-content-area` > `.row` > `.dashboard-content-col` ✓
    - Food detail structure: `.main-content-area` > `.food-detail-main-bg` > `.row` > `.food-detail-content-col` ✓
    - Recipes structure (broken): `.main-content-area` > `.content-col` (direct, no flex context) ✗
  - **THE SOLUTION**:
    - **Structure Fix** (`templates/recipes/index.html` lines 221-268):
      - Wrapped all content in `.row` > `.content-col` structure to match dashboard/food detail pattern
      - Before: `.main-content-area` directly contained h1 and multiple `.content-col` divs (siblings)
      - After: `.main-content-area` > `.row` > single `.content-col` containing all content
      - Moved h1 and all three feature cards inside the single `.content-col` wrapper
      - Removed `.content-col` from individual card wrappers (now just `<div class="mb-3">`)
    - **CSS Fix** (`templates/recipes/index.html` lines 30-35):
      - Added `box-sizing: border-box` to `.main-content-area` inline CSS
      - Added `background: transparent` to match food detail page pattern
  - **Why This Matters**:
    - Bootstrap's `.row` class provides `display: flex` context for child elements
    - `.content-col` has `flex: 0 1 auto` and `max-width: 620px` in global CSS (main.css lines 120-124)
    - Flex properties only work when element is a direct child of a flex container
    - Without `.row`, the flex property is ignored and width constraint cannot enforce the 620px limit
  - **Files Modified**:
    - `templates/recipes/index.html` - Restructured HTML hierarchy + updated inline CSS
  - **User Benefits**:
    - Recipe page containers now properly constrained to 620px width
    - Consistent width alignment with dashboard and food pages
    - Clean visual presentation matching the rest of the app

---

**Previous Updates: 2026-01-31 (Food Pages Width & Alignment Fixes)**

- **Food Detail Page Container Width & Alignment (BUG FIX)**: Fixed containers extending too far right and misaligned left edge
- **Add/Edit Food Pages - Additional Information Container Width (BUG FIX)**: Fixed "Additional Information" section being wider than Safe/Moderate/High serving sections
  - **THE PROBLEM**:
    - Food detail page containers were wider than intended and extending too far to the right
    - Container left edge didn't align with dashboard - started 15px further right
    - Inline CSS in template was overriding global width constraints from main.css
    - Nested div structure caused double left padding (30px instead of 15px)
  - **THE SOLUTION**:
    - **Width Fix** (`templates/foods/detail.html` lines 204-208):
      - Removed inline CSS override for `.food-detail-content-col` that set `width: 100% !important`
      - Removed padding overrides that prevented global max-width constraint from applying
      - Now properly inherits global CSS: `max-width: 620px` from `static/css/main.css`
    - **Alignment Fix** (`templates/foods/detail.html` line 200):
      - Changed `.food-detail-main-bg` padding-left from `15px` to `0`
      - Eliminated double padding from nested div structure
      - Dashboard uses combined classes on one element; detail page uses nested structure
  - **Global Width Specifications** (from `static/css/main.css`):
    - CSS Variables (lines 12-14):
      - `--layout-main-max: 880px` (main content area maximum width)
      - `--layout-content-max: 620px` (inner content column maximum width)
    - Global CSS Rules (lines 111-126):
      - `.main-content-area`: `max-width: 880px`
      - `.food-detail-content-col`: `max-width: 620px`
  - **Layout Specifications**:
    - Sidebar: 200px fixed width, `position: fixed`, `left: 0`
    - Main content: `margin-left: 200px`, `padding-left: 15px`
    - Content column: `max-width: 620px`
    - Total left offset: 215px (200px sidebar + 15px padding)
  - **Files Modified**:
    - `templates/foods/detail.html` - Removed width override CSS, fixed padding
- **User Benefits**:
    - Detail page containers now match dashboard width (620px max)
    - Consistent left alignment across all pages
    - Clean visual presentation without containers extending off-screen

- **Recipes & Meals Page - Width Alignment (UI CONSISTENCY)**: Matched main-body container widths to dashboard specs
  - Replaced Bootstrap `col-md-9` wrappers with `.content-col` (max-width 620px) for the three feature cards
  - Ensures Recipes & Meals content aligns with dashboard/food pages and no longer extends too wide
  - Files modified: `templates/recipes/index.html`

- **Recipe Detail Sidebar & Ingredients Cleanup (UI UPDATE)**: Reorganized sidebar actions and simplified ingredients list
  - Moved “Add to Diary” button into the sidebar above Quick Links, with larger spacing
  - Added “Quick Links” heading and thin divider line above the edit/navigation buttons
  - Removed the colored card background from the Ingredients section (now a plain list)
  - Files modified: `templates/recipes/view_recipe.html`

- **Recipe Detail Header & Tags Layout (UI UPDATE)**: Aligned header styling and moved tags into the sidebar
  - Added thick beige divider under the main recipe heading
  - Moved category badge inline with the recipe title and set it to beige
  - Moved tags to the sidebar with smaller font and a thin divider above them
  - Files modified: `templates/recipes/view_recipe.html`

- **Add/Edit Food Pages - Additional Information Container Width (BUG FIX)**: Fixed "Additional Information" section being wider than Safe/Moderate/High serving sections
  - **THE PROBLEM**:
    - On add-food.html and edit-food.html, the "Additional Information" and "Nutrition Information" collapsible sections were wider than the Safe/Moderate/High serving sections
    - Safe/Moderate/High sections are wrapped in `<div class="fodmap-section">` with `padding: 20px`, constraining their width
    - Additional Information sections were placed outside this container, extending to full card width
  - **THE SOLUTION**:
    - Wrapped both sections in `<div class="additional-section">` container
    - The `.additional-section` class already existed in CSS with same styling as `.fodmap-section`:
      - `border: var(--bevel)`
      - `border-radius: 16px`
      - `padding: 20px` (the key constraint)
      - `margin-bottom: 20px`
      - `background-color: var(--bg-deep)`
  - **Files Modified**:
    - `templates/foods/add-food.html` - Added `.additional-section` wrapper around Nutrition/Additional Information sections
    - `templates/foods/edit-food.html` - Added `.additional-section` wrapper around Nutrition/Additional Information sections
  - **User Benefits**:
    - All collapsible sections now have consistent width
    - Visual alignment matches throughout the form
    - Container styling (border, background) is now consistent

---

**Previous Updates: 2026-01-31 (Food Category Fixes & "View All" Enhancement)**

- **Food Category System Overhaul**: Fixed missing categories and standardized category names across the app
  - **THE PROBLEM**:
    - "Other" category existed in database (7 foods) but was missing from browse buttons on Food Guide page
    - "Herbs & Spices" category existed in database (5 foods) but was missing from browse buttons
    - "View All" link showed a search page instead of listing all foods alphabetically
    - Category names were inconsistent between browse buttons and add/edit food dropdowns:
      - "Grains & Cereals" (dropdown) vs "Grains" (database/browse)
      - "Proteins (Meat/Fish)" (dropdown) vs "Proteins" (database/browse)
      - "Dairy & Alternatives" (dropdown) vs "Dairy" (database/browse)
      - "Oils & Condiments" (browse) didn't exist in database
      - Dropdown had unused categories: "Condiments & Sauces", "Snacks", "Deli"
  - **THE SOLUTION**:
    - **Food Index Page** (`templates/foods/index.html`):
      - Added "Other" category browse button (icon: bi-three-dots)
      - Added "Herbs & Spices" category browse button (icon: bi-flower3)
      - Removed "Oils & Condiments" browse button (didn't exist in database)
      - Updated "View All" link to pass `view_all='1'` parameter
    - **Search Route** (`routes/foods.py`):
      - Added `view_all` parameter handling to show all foods alphabetically
    - **Search Template** (`templates/foods/search.html`):
      - Added support for `view_all` parameter to display all foods with heading "All Foods (X total)"
      - Updated sidebar title to show "All Foods" when viewing all
      - Updated page title to show "All Foods" with list icon
    - **Add Food Dropdown** (`templates/foods/add-food.html`):
      - Changed "Grains & Cereals" to "Grains"
      - Changed "Proteins (Meat/Fish)" to "Proteins"
      - Changed "Dairy & Alternatives" to "Dairy"
      - Removed "Condiments & Sauces", "Snacks", "Deli" (not in database)
      - Added "Herbs & Spices" option
    - **Edit Food Dropdown** (`templates/foods/edit-food.html`):
      - Applied same category dropdown changes as add-food form
  - **Database Categories** (11 total):
    - Beverages (5 foods)
    - Dairy (5 foods)
    - Fruits (11 foods)
    - Grains (8 foods)
    - Herbs & Spices (5 foods)
    - Nuts & Seeds (5 foods)
    - Other (7 foods)
    - Packaged Food (1 food)
    - Proteins (9 foods)
    - Spices (7 foods)
    - Vegetables (20 foods)
  - **User Benefits**:
    - Can now find and browse foods in "Other" category
    - All database categories are accessible from browse buttons
    - "View All" shows complete alphabetical food list instead of search page
    - Consistent category names prevent confusion when adding/editing foods

**Previous Updates: 2026-01-31 (Edit Food Page Layout Fix)**

- **Edit Food Page Layout (BUG FIX)**: Fixed container movement when browser width changes by converting from responsive to fixed layout
  - **THE PROBLEM**:
    - Edit Food page was using Bootstrap responsive column classes (`col-lg-2 col-md-3`, `col-lg-10 col-md-9`)
    - Sidebar was using `position: sticky` instead of `position: fixed`
    - Container would shift and move when browser window was resized
  - **THE SOLUTION** (Applied to `templates/foods/edit-food.html`):
    **CSS Changes**:
    ```css
    /* Sidebar - Changed from sticky to fixed positioning */
    .sidebar-column {
        position: fixed;           /* Was: min-height: 100% only */
        top: 50px;
        left: 0;
        width: 200px;
        height: calc(100vh - 50px);
        background: linear-gradient(135deg, #8BA48B, #677D6A);
        overflow-y: auto;
        z-index: 100;
    }

    .foods-sidebar {
        padding: 12px;
        padding-top: 40px;        /* Was: padding-top: 28px with position: sticky */
    }

    /* Main content - Updated to match add-food.html */
    .main-content-area {
        padding-left: 15px;        /* Was: padding-left: 30px */
        margin-left: 200px;        /* Added */
        /* Removed: border-left: 3px solid #8BA48B */
        /* Removed: min-height: 100% */
    }
    ```

    **HTML Structure Changes**:
    ```html
    <!-- BEFORE -->
    <div class="col-lg-2 col-md-3 sidebar-column">
    <div class="col-lg-10 col-md-9 main-content-area pt-2">

    <!-- AFTER (matches add-food.html) -->
    <div class="sidebar-column">
    <div class="main-content-area" style="padding-top: 40px;">
    ```

  - **RESULT**:
    - Sidebar now fixed, extends from header (50px) to bottom of viewport
    - Main content area matches add-food.html layout exactly
    - Container no longer moves when browser is resized
    - Consistent with all other fixed layout pages per CLAUDE.md
  - **Files changed**: `templates/foods/edit-food.html`, `Version_History.md`

---

**Previous Updates: 2026-01-30 (Edit Recipe Layout Consistency + Sidebar)**

- **Edit Recipe Layout Parity (UI CONSISTENCY)**: Brought `edit_recipe` in line with the create-recipe layout
  - Added the full fixed sidebar + quick access panel and matching styles
  - Matched the header row, content width, and main layout structure with create recipe page
  - Reorganized the top recipe meta fields to the same two-row layout (prep/cook/servings, then difficulty/source)
  - Aligned Recipe Classification columns to mirror create page (left: cuisine/prep/occasion, right: dietary needs)
- **Single-Select Prep/Occasion + Custom (FORM BEHAVIOR)**: Edit form now uses dropdowns with “Custom...” inputs like cuisine
  - Custom prep/occasion values persist and load back into the form when editing
  - Tag preview/removal logic updated to match single-select behavior
- **Files changed**: `templates/recipes/edit_recipe.html`, `routes/recipes.py`, `Version_History.md`

**Latest Updates: 2026-01-30 (Incomplete Foods To Do List)**

- **To Do List for Incomplete Foods (NEW FEATURE)**: Added tracking system for foods that were quickly added via recipe creation and need more information
  - **Database Changes**:
    - Added `is_complete` boolean field to Food model (default True)
    - Created migration script `migrations/add_food_is_complete.py` to add column to existing database
    - All existing foods automatically marked as complete (is_complete=True)
  - **Quick-Add API Updated** (`routes/api.py`):
    - Foods created via `/api/foods/quick-add` (from recipe creation) now marked as incomplete (is_complete=False)
    - These foods only have minimal information (name, category, basic FODMAP/histamine ratings)
  - **Food Creation Routes Updated** (`routes/foods.py`):
    - Foods created via full Add Food form (`/foods/add`) marked as complete (is_complete=True)
    - Foods edited via Edit Food form (`/foods/edit/<id>`) automatically marked as complete
  - **Dashboard To Do Section** (`templates/dashboard/index.html`):
    - Added new "To Do" watch list section below existing Watch List
    - Shows all incomplete foods with cyan/info color scheme (matching app palette)
    - Displays food name, category, date added, and "Edit" badge
    - Each item links directly to the edit page for that food
    - Shows success message when all foods are complete
  - **Dashboard Route Updated** (`routes/main.py`):
    - Queries for incomplete foods (is_complete=False) ordered by creation date
    - Passes incomplete_foods list to dashboard template
  - **Purpose**: Helps users keep track of foods that were quickly added during recipe creation and need to be filled out with complete FODMAP/histamine/nutrition information
  - **Files changed**: `models/food.py`, `routes/api.py`, `routes/foods.py`, `routes/main.py`, `templates/dashboard/index.html`, `migrations/add_food_is_complete.py`, `Version_History.md`

---

**Previous Updates: 2026-01-30 (Recipe Form Improvements + Multi-Select Fields)**

- **Recipe Form Layout Updates (UI IMPROVEMENTS)**: Reorganized the recipe form header to be more compact and efficient
  - Moved difficulty level to the same line as prep time, cook time, and servings (5 fields in one row)
  - Moved source URL field to the same line as well for better space utilization
  - Updated field widths: prep/cook/servings (col-md-2), difficulty (col-md-3), source URL (col-md-3)
  - Added icons to labels: clock for prep time, fire for cook time, people for servings, speedometer for difficulty, link for source URL
  - Shortened placeholder text to fit smaller fields (e.g., "15 min" instead of "15 minutes")

- **Multi-Select Preparation Methods (FEATURE ENHANCEMENT)**: Changed preparation method from single-select dropdown to multi-select checkboxes
  - Users can now select multiple preparation methods for one recipe (e.g., both "Baking" and "Roasting")
  - Checkboxes displayed in a vertical list (one per line) for better readability
  - Backend updated to store multiple methods as comma-separated values in `preparation_method` field
  - Updated `Recipe.get_all_tags()` method to properly expand comma-separated preparation methods

- **Multi-Select Occasions with Custom Input (FEATURE ENHANCEMENT)**: Changed occasion/holiday from single-select dropdown to multi-select checkboxes
  - Users can now select multiple occasions for one recipe (e.g., "Thanksgiving" and "Family Gatherings")
  - Checkboxes displayed in a vertical list (one per line)
  - Added always-visible custom occasion input field below checkboxes
  - Custom occasions are automatically saved to database for future use
  - Backend updated to store multiple occasions as comma-separated values in `occasion` field
  - Updated `Recipe.get_all_tags()` method to properly expand comma-separated occasions

- **Database Model Updates (SCHEMA CHANGES)**: Removed unnecessary field and updated column sizes
  - Removed `main_ingredient` field from Recipe model (was not being used in the UI)
  - Increased `preparation_method` column size from VARCHAR(100) to VARCHAR(200) to support multiple values
  - Increased `occasion` column size from VARCHAR(100) to VARCHAR(200) to support multiple values
  - Created migration script `migrations/update_recipe_fields.py` to safely update existing database
  - Updated `Recipe.get_all_tags()` to remove main_ingredient reference

- **JavaScript Updates (FUNCTIONALITY)**: Updated client-side code to handle new multi-select fields
  - Added `getPreparationMethodValues()` function to collect selected prep methods
  - Updated `getOccasionValues()` function to collect checkbox selections + custom input
  - Updated `updateSuggestedTags()` to properly display all selected prep methods and occasions
  - Updated `clearFormFieldForTag()` to handle unchecking prep method and occasion checkboxes
  - Updated event listeners to respond to checkbox changes and custom occasion input

- **Recipe Routes Updates (BACKEND)**: Updated create and edit recipe routes to handle multi-select fields
  - Both `create_recipe` and `edit_recipe` routes now use `request.form.getlist()` for preparation_methods and occasions
  - Custom occasion input is saved to `RecipeClassificationOption` table for future reuse
  - Multi-select values are joined as comma-separated strings before saving to database
  - Removed tags are properly filtered out from multi-select fields

**Note**: FODMAP Friendly option already exists in dietary needs list (was already implemented in recipe_categories.py). Source URL field already exists in both create and edit recipe forms.

---

**Previous Updates: 2026-01-30 (Create Recipe Layout + Custom Classification Options)**

- **Create Recipe Page Layout & Sidebar (UI IMPROVEMENTS)**: Reworked the create-recipe page to match the global fixed sidebar layout and reorganized the top form fields
  - Added full left sidebar navigation + quick access panel to `templates/recipes/create_recipe.html`
  - Moved recipe photo onto the same row as recipe name
  - Placed prep time, cook time, and servings on one line with icons and even spacing
  - Reorganized Recipe Classification so cuisine/origin, main ingredient, prep method, difficulty, and occasion stack on the left, with dietary needs on the right

- **Custom Cuisine/Main Ingredient Options (NEW FEATURE)**: Users can now select “Custom...” for cuisine/origin and main ingredient to add new values that persist for future use
  - Added `RecipeClassificationOption` model/table for custom recipe classification values
  - Added backend support to store custom cuisine and main ingredient values and merge them into dropdown lists
  - Added custom input UI + tag preview support to create and edit recipe forms
  - **Files changed**: `models/recipe.py`, `routes/recipes.py`, `templates/recipes/create_recipe.html`, `templates/recipes/edit_recipe.html`

**Latest Updates: 2026-01-29 (Add Food Page Layout & Typography Adjustments)**

- **Add Food Page Typography & Alignment (UI IMPROVEMENTS)**: Adjusted heading alignment, input sizes, and font sizes for consistency

  - **Changes Made**:
    1. **Page Heading Alignment**: Changed "Add Custom Food/Drink" heading from center to left-aligned to match container alignment
    2. **Input Height Consistency**: Removed `form-control-lg` from Food/Drink Name input and Category dropdown to ensure consistent heights
    3. **Serving Section Headings**: Reduced font size of "Safe Serving", "Moderate Serving", and "High Serving" from `var(--text-title)` (0.85rem) to `var(--text-body)` (0.70rem)
    4. **Section Headings**: Reduced font size of "Nutrition Information" and "Additional Information" headings to match serving sections

  - **CSS Changes**:
    ```css
    .collapsible-summary {
        font-size: var(--text-body);  /* Was: var(--text-title) */
    }
    ```

  - **HTML Changes**:
    ```html
    <!-- Heading alignment -->
    <div class="mb-4">  <!-- Was: <div class="text-center mb-4"> -->

    <!-- Input sizes -->
    <input type="text" class="form-control" ...>  <!-- Was: form-control-lg -->
    <select class="form-select" ...>  <!-- Was: form-select-lg -->
    ```

- **Add Food Page Layout (BUG FIX)**: Fixed layout to match dashboard structure

  - **THE PROBLEM**:
    - Add Food page layout was using outdated Bootstrap column structure
    - Sidebar was using `position: sticky` instead of `position: fixed`
    - Had a spacer div at the top that disrupted alignment
    - Sidebar didn't extend from header to bottom of page
    - Used Bootstrap columns (`col-lg-2`, `col-md-3`) instead of fixed sidebar

  - **THE SOLUTION** (Applied to `templates/foods/add-food.html`):

    **Removed**:
    - Spacer div: `<div style="height: 20px; margin-bottom: 5px;"></div>`
    - Bootstrap column classes from sidebar and main content area

    **CSS Changes**:
    ```css
    /* Sidebar - Changed from sticky to fixed positioning */
    .sidebar-column {
        position: fixed;           /* Was: position: sticky */
        top: 50px;
        left: 0;
        width: 200px;
        height: calc(100vh - 50px);
        background: linear-gradient(135deg, #8BA48B, #677D6A);
        overflow-y: auto;
        z-index: 100;
    }

    .foods-sidebar {
        padding: 12px;
        padding-top: 40px;        /* Was: padding-top: 28px */
    }

    /* Main content - Updated to match dashboard */
    .main-content-area {
        padding-left: 15px;        /* Was: padding-left: 30px */
        margin-left: 200px;
        /* Removed: border-left, min-height */
    }
    ```

    **HTML Structure Changes**:
    ```html
    <!-- BEFORE -->
    <div class="col-lg-2 col-md-3 sidebar-column">
    <div class="col-lg-10 col-md-9 main-content-area pt-2">

    <!-- AFTER (matches dashboard) -->
    <div class="sidebar-column">
    <div class="main-content-area" style="padding-top: 40px;">
    ```

  - **RESULT**:
    - Sidebar now fixed, extends from header (50px) to bottom of viewport
    - Main content area matches dashboard layout exactly
    - No spacer div needed - proper alignment with header
    - Maintains 750px content width constraint via `col-md-9` wrapper

---

**Previous Update: 2026-01-29 (Food Search Page Container Width Fix - CRITICAL LAYOUT REFERENCE)**

- **Food Search Container Width Mismatch (BUG FIX)**: Fixed container width not matching dashboard due to Bootstrap column padding being removed and duplicate padding from nesting

  - **THE PROBLEM**:
    - Food search page container was WIDER than dashboard container
    - When trying to adjust right edge to make container narrower, the entire container moved left instead
    - Only the left edge was changing, not the actual width

  - **ROOT CAUSE ANALYSIS**:
    1. **Dashboard Structure**: Uses single element with BOTH classes on same div
       - `<div class="main-content-area dashboard-main-bg">` (ONE element)
       - When both classes have `padding-left: 15px`, only ONE applies (no stacking)
       - Bootstrap `.dashboard-content-col` has default column padding (~15px each side)
       - Total horizontal padding: 15px left (container) + 15px left (column) + 15px right (column) = 30px left, 15px right

    2. **Search Page Structure**: Uses NESTED elements (stacking padding)
       - `<div class="main-content-area">` contains `<div class="food-search-main-bg">` (TWO elements)
       - Both have `padding-left: 15px` which STACKS: 15px + 15px = 30px left padding
       - `.food-search-content-col` had `padding-left: 0 !important; padding-right: 0 !important;`
       - This REMOVED Bootstrap's default column padding, making content stretch edge-to-edge
       - Total horizontal padding: 30px left (stacked containers) + 0px left (column override) + 0px right (column override) = 30px left, 0px right
       - Container was 15px WIDER on right side than dashboard due to missing column padding

  - **TROUBLESHOOTING PROCESS**:
    1. Initially tried removing duplicate left padding → moved left edge, didn't fix width
    2. Analyzed padding vs width separately → realized width is determined by RIGHT edge, not left
    3. Compared dashboard and search HTML structure → found single vs nested element difference
    4. Compared CSS classes → found `.food-search-content-col` was removing Bootstrap padding
    5. Traced exact padding calculations for both pages → identified missing right padding
    6. Solution: Remove padding overrides to restore Bootstrap column padding

  - **THE SOLUTION** (Applied to `templates/foods/search.html`):

    **CSS Changes**:
    ```css
    /* BEFORE (WRONG) */
    .main-content-area {
        padding-left: 15px;
        margin-left: 200px;
    }
    .food-search-main-bg {
        padding-left: 15px;
        padding-right: 15px;
    }
    .food-search-content-col {
        width: 100% !important;
        padding-left: 0 !important;    /* REMOVED Bootstrap padding */
        padding-right: 0 !important;   /* REMOVED Bootstrap padding */
    }

    /* AFTER (CORRECT) */
    .main-content-area {
        padding-left: 0;               /* Changed from 15px to 0 */
        margin-left: 200px;
    }
    .food-search-main-bg {
        padding-left: 15px;
        padding-right: 15px;
    }
    .food-search-content-col {
        width: 100% !important;        /* Removed padding overrides */
    }
    ```

    **HTML Changes**:
    ```html
    <!-- Updated h1 inline padding from 15px to 30px to align with content -->
    <h1 style="padding-left: 30px;">  <!-- Was 15px -->
    ```

  - **WHY THIS WORKS**:
    - **Dashboard total padding**: 15px left (container) + 15px left (Bootstrap column) = 30px left
    - **Search total padding**: 0px (container) + 15px (food-search-main-bg) + 15px (Bootstrap column) = 30px left
    - Both now have 30px left padding and 30px right padding (15px container + 15px Bootstrap column)
    - **Container width**: viewport - 200px (sidebar) - 30px (left) - 30px (right) = viewport - 260px
    - **H1 alignment**: 0px (container) + 30px (inline) = 30px from sidebar (matches content)

  - **REFERENCE FOR OTHER PAGES**:
    When fixing container width issues on other pages:
    1. Check if structure uses single element vs nested elements (affects padding stacking)
    2. Never remove Bootstrap column padding unless you compensate elsewhere
    3. Calculate total padding: LEFT = all containers + column padding, RIGHT = all containers + column padding
    4. Dashboard reference: 30px left + 30px right = viewport - 260px content width
    5. To match dashboard: ensure total horizontal padding = 60px (30px each side)

  - **Files changed**:
    - `templates/foods/search.html` (CSS: .main-content-area, .food-search-content-col, HTML: h1 inline padding)
    - `templates/foods/index.html` (earlier fix: same .main-content-area padding pattern)

---

**Latest Updates: 2026-01-29 (Food Guide Container Width Adjustment)**

- **Food Guide Main Container Width Pull-In**: Shifted the Food Guide right edge left by about 1 cm for a tighter alignment
  - Set Food Guide `.main-content-area` width/max-width to `calc(var(--layout-content-max) - 40px)`
  - **Files changed**: `templates/foods/index.html`

---

**Latest Updates: 2026-01-28 (Food Pages Background Cleanup)**

- **Removed Unwanted Olive Background (BUG FIX)**: Eliminated the large #40534C background block on Food Guide and Food Search pages while keeping existing card/container styling intact
  - Set `.food-guide-main-bg` and `.food-search-main-bg` backgrounds to transparent
  - Preserved all individual cards and containers that still use `var(--bg-elevated)` in the main content
  - **Files changed**: `templates/foods/index.html`, `templates/foods/search.html`

---

**Updates: 2026-01-28 (Food Detail Layout Fix)**

- **Food Detail Page Width Alignment (BUG FIX)**: Re-aligned the food detail page to the fixed-width layout system so the right edge no longer overflows the browser
  - Replaced Bootstrap column layout with the standard fixed sidebar + main content layout
  - Added inner padding wrapper to match dashboard container edges and prevent row overflow
  - Added fixed widths for main content (1000px) and content column (750px)
  - **Files changed**: `templates/foods/detail.html`

---

**Updates: 2026-01-28 (Food Search Actions Alignment)**

- **Food Search List Actions Reflow**: Moved the chevron and delete buttons into a fixed action block so the list row doesn’t push the right edge past the container
  - Added `.food-item-actions` to keep the chevron + delete aligned and contained
  - **Files changed**: `templates/foods/search.html`

---

**Updates: 2026-01-28 (Food Pages Width Fix)**

- **Food Search/Detail Width Overflow Fix**: Ensured the fixed 1000px main content width includes padding so it doesn't exceed the 1200px viewport
  - Added `box-sizing: border-box` to `.main-content-area` on Food Search and Food Detail pages
  - Reduced Food Search content column width to 750px to match dashboard container edge alignment
  - **Files changed**: `templates/foods/search.html`, `templates/foods/detail.html`

---

**Updates: 2026-01-28 (Food Search List Styling)**

- **Food Search Column Tuning**: Reduced food name font size, spaced serving columns evenly, aligned filter buttons, and refined action icons
  - Food name font reduced to `--text-micro`
  - Serving column width set to 100px with 8px gaps; filter columns matched
  - Serving column group moved right; chevron icon size reduced further; delete button border/padding tightened
  - **Files changed**: `templates/foods/search.html`

---

**Updates: 2026-01-28 (Food Guide/Search Container Width)**

- **Food Guide & Category Container Alignment**: Matched the visible container width to the dashboard content column
  - Set `.food-guide-main-bg` and `.food-search-main-bg` to 750px wide with border-box sizing
  - Adjusted content columns to 100% to avoid overflow inside the narrower containers
  - **Files changed**: `templates/foods/index.html`, `templates/foods/search.html`

---

**Updates: 2026-01-28 (Flexible Width Normalization)**

- **Global Layout Normalization**: Reverted all pages back to flexible widths while keeping a consistent max container size
  - `main-content-area` now fluid with `max-width: 1000px`
  - All content columns normalized to `max-width: 750px` with flexible width
  - Uses global overrides in `static/css/main.css` to avoid per-page fixed sizing
  - Removed per-template fixed width rules that enforced hard right edges
  - **Files changed**: `static/css/main.css`, `templates/dashboard/index.html`, `templates/foods/index.html`, `templates/foods/search.html`, `templates/foods/detail.html`, `templates/diary/calendar.html`, `templates/education/index.html`, `templates/recipes/index.html`, `templates/settings/index.html`, `templates/settings/help.html`

---

**Updates: 2026-01-28 (Food Guide Category Compaction)**

- **Food Guide Category Grid**: Tightened category tiles and pulled the right edge in for a more compact layout
  - Reduced tile padding and circle size; tightened label size
  - Set Food Guide container max width to 700px
  - **Files changed**: `templates/foods/index.html`

---

**Updates: 2026-01-28 (Layout Width Tightening)**

- **Container Edge Pull-In**: Reduced global layout max widths to bring right edges further left
  - Main container max width: 1000px → 950px → 880px
  - Content column max width: 750px → 700px → 620px
  - Food Guide main container max width: 700px → 650px → 600px
  - **Files changed**: `static/css/main.css`, `templates/foods/index.html`

---

**Updates: 2026-01-28 (Food Guide Width Alignment)**

- **Food Guide Container Edge Alignment**: Matched the Food Guide container edge to the dashboard content width
  - Set Food Guide main container max width to `var(--layout-content-max)`
  - **Files changed**: `templates/foods/index.html`

---

**Latest Updates: 2026-01-28 (MAJOR CSS CLEANUP & LAYOUT FIXES)**

- **CSS Layout System Overhaul (BUG FIX)**: Fixed major layout issues causing content to shift too far right and preventing layout changes from taking effect
  - **Root Cause**: `.container` class in base.html was applying Bootstrap's default centering logic, which conflicted with the custom `margin-left: 200px` sidebar offset. This created a CSS specificity battle where individual templates tried to override the centering with inline styles, creating an unmaintainable mess.

  - **Base Template Cleanup** (`templates/base.html`):
    - **REMOVED**: `.container` class from `<main>` wrapper (line 159) - now uses plain `<main>` tag
    - **REMOVED**: `my-4` margin class that was causing vertical spacing fights
    - **REMOVED**: Container max-width override (lines 103-105) - no longer needed
    - **UPDATED**: Flash messages container to use `margin-left: 200px` + padding instead of `.container` class
    - **Result**: No more Bootstrap centering conflicts, clean layout system

  - **Main CSS Cleanup** (`static/css/main.css`):
    - **REMOVED**: 78 lines of excessive media query bloat (lines 117-181) that forced desktop layout with redundant `!important` flags on every grid class
    - **REMOVED**: Container max-width overrides (lines 110-113) that conflicted with base.html
    - **CLEANED**: Body styles - removed 10 unnecessary `!important` declarations
    - **Result**: 88 fewer lines of CSS, cleaner codebase, no specificity wars

  - **Template Standardization** (All 8 main templates):
    - **REMOVED**: `margin-top: -1.5rem` hack from all templates (dashboard, foods, diary, recipes, education, settings, help, search)
    - **REMOVED**: `main.container` override from dashboard/index.html (lines 82-86)
    - **STANDARDIZED**: All `.main-content-area` styles across templates:
      - `margin-left: 200px` (sidebar offset)
      - `padding-left: 15px` (gap between sidebar and content, per CLAUDE.md)
      - `width: 1000px; max-width: 1000px;` (consistent content width)
    - **FIXED**: Footer styles - removed unnecessary `!important` flags

  - **Impact**:
    - ✅ Content now consistently aligns to the left across all pages
    - ✅ Layout changes now take effect immediately (no more caching confusion)
    - ✅ No more horizontal scrollbars or content overflow
    - ✅ Cleaner, more maintainable CSS without excessive `!important` usage
    - ✅ Consistent 15px gap between sidebar and content on all pages

  - **Files changed**:
    - `templates/base.html` (removed .container wrapper, cleaned flash messages)
    - `static/css/main.css` (removed 88 lines of bloat, cleaned body styles)
    - `templates/dashboard/index.html` (removed main.container override, margin-top hack, standardized layout)
    - `templates/foods/index.html` (removed margin-top hack, standardized layout)
    - `templates/foods/search.html` (removed margin-top hack, standardized layout)
    - `templates/diary/calendar.html` (removed margin-top hack, added width constraint)
    - `templates/recipes/index.html` (removed margin-top hack, added width constraint)
    - `templates/education/index.html` (removed margin-top hack, added width constraint)
    - `templates/settings/index.html` (removed margin-top hack, added width constraint)
    - `templates/settings/help.html` (removed margin-top hack, added width constraint)

---

**Earlier Updates: 2026-01-28**

- **Food Search Page - Filter Bar Styling & Layout**: Fixed filter bar alignment and compacted sizing to match olive container
  - Changed filter-header background from dark green (#1A3636) to olive green (var(--bg-elevated) #40534C)
  - Changed filter-header border to subtle white border (rgba(255, 255, 255, 0.08))
  - Reduced filter-header padding from 8px to 6px, margin-bottom from 8px to 6px
  - Reduced padding-top on food-search-main-bg from 15px to 8px (aligns filter with top edge of olive container)
  - Adjusted widths to prevent horizontal overflow:
    - main-content-area: 1000px → 950px (total with sidebar: 1150px)
    - food-search-content-col: 750px → 900px
  - Reduced traffic light circles from 14px to 12px (in both filter buttons and food list items)
  - Reduced filter buttons from 16px to 12px
  - Reduced filter-column border color to white semi-transparent (rgba(255, 255, 255, 0.2))
  - Reduced filter-label font from var(--text-micro) (0.62rem) to 0.58rem
  - Reduced serving-size-text font from var(--text-micro) to 0.58rem
  - Reduced filter-buttons gap from 4px to 3px
  - Filter bar now aligns with top edge of olive container, content fits viewport without horizontal overflow
  - **Files changed**: `templates/foods/search.html`

- **Food Guide & Search Pages - Fixed Width Layout**: Converted all food pages from responsive to fixed-width layout matching dashboard
  - **Main Content Area**: Set to fixed 1000px width starting at 200px (no extra padding), matching dashboard
  - **Background Wrapper**: Content wrapped in `.food-guide-main-bg` / `.food-search-main-bg` with:
    - Olive green background (var(--bg-elevated))
    - Rounded corners (border-radius: 10px) for chamfered appearance
    - Page headings positioned above the background container
  - **Fixed Content Column**: Changed from responsive `.col-md-9` to fixed width classes (750px)
  - **Overflow Prevention**: Added `overflow-x: hidden` on body to prevent horizontal scrolling
  - **Left Edge**: Container starts immediately at 200px from left edge (where sidebar ends), matching dashboard layout exactly

- **Food Search Page Compaction**: Made food list layout more compact to fit within fixed width
  - Reduced food name width from 240px to 200px
  - Reduced serving column width from 110px to 95px
  - Changed food names from `text-value` (0.76rem) to `text-label` (0.67rem) with font-weight: 500
  - Reduced list item padding from 6px to 4px vertical

- **Food Category Page Layout Overhaul**: Completely redesigned category/search page to match dashboard layout consistency
  - **Fixed Sidebar**: Matched sidebar to dashboard exactly - 200px width, fixed position, same padding (12px, 40px top)
  - **Fixed Main Content Width**: Set content area to 1000px with 750px content column (matching dashboard)
  - **Background Color**: Added olive green background (`--bg-elevated`) to main content area matching dashboard
  - **Font Size Reductions**:
    - Food item names reduced from `--text-value` (0.76rem) to `--text-label` (0.67rem)
    - Serving size text reduced from `--text-label` to `--text-micro` (0.62rem)
    - Filter labels reduced from `--text-label` to `--text-micro`
  - **Traffic Light Alignment**: Fixed vertical alignment of traffic lights in filter header and food items
    - Adjusted overall traffic light spacer from 25px to 20px
    - Adjusted food name spacer from 280px to 240px to match
    - Filter columns reduced from 130px to 110px to match serving columns
  - **Moved 'Found X foods' counter**: Relocated from main content to sidebar below search form (with white text color)
  - **Added Quick Links Section**: Added "Quick Links" heading with divider line above it in sidebar
  - **Removed Duplicate Button**: Removed "Back to Food Guide" button from sidebar (already in main navigation)
  - **Heading Alignment**: Category page heading now sits at same vertical level as sidebar heading (40px top padding)
  - **Files changed**: `templates/foods/search.html`

- **Deli Category Added**: Added new "Deli" category for deli meats, cheeses, and prepared deli items
  - **Food Guide Page**: Added Deli category tile with basket icon between Oils/Condiments and Packaged Food
    - Gold circular icon background (#D6BD98) with dark green basket icon (#1A3636)
    - Links to search page filtered by "Deli" category
  - **Add Food Form**: Added "Deli" option to category dropdown in add-food.html
    - Positioned before "Packaged Food" in dropdown list
  - **Edit Food Form**: Added "Deli" option to category dropdown in edit-food.html
    - Positioned before "Packaged Food" in dropdown list
    - Includes selected state condition for existing foods
  - **Purpose**: Enables tracking of deli meats (ham, salami, turkey), deli cheeses, and prepared deli items
  - **Files changed**: `templates/foods/index.html`, `templates/foods/add-food.html`, `templates/foods/edit-food.html`

- **Header Text Wrapping Fix (BUG FIX)**: Fixed app name and copyright text wrapping to next line when browser width is reduced
  - **Root Cause**: Header text elements lacked wrapping prevention, causing copyright text to wrap at narrow widths
  - **Solution**: Added `white-space: nowrap` to both app title and copyright text to prevent line breaks
  - Added `overflow: hidden` and `text-overflow: ellipsis` to copyright span for graceful truncation if needed
  - Added `flex-shrink: 0` to app title to prevent it from shrinking
  - Added `overflow: hidden` to header container to prevent overflow issues
  - Header text now stays on single line regardless of browser width
  - **Files changed**: `templates/base.html`

---

**Previous Updates: 2026-01-26**

- **Docker Line Ending Fix (BUG FIX)**: Fixed "exec /app/docker-entrypoint.sh: no such file or directory" error when running Docker on machines that clone with Windows line endings
  - **Root Cause**: Git on Windows converts LF (Unix) line endings to CRLF (Windows). The shebang `#!/bin/bash` becomes `#!/bin/bash\r`, causing Linux to look for `/bin/bash\r` which doesn't exist
  - **Solution 1**: Created `.gitattributes` file to force LF line endings for shell scripts, Dockerfile, and docker-compose files
  - **Solution 2**: Added `sed -i 's/\r$//'` command in Dockerfile to strip any CRLF line endings during build
  - **Files changed**: `.gitattributes` (new), `Dockerfile`

- **Diary Main Content Alignment**: Reduced the left gap and aligned the diary heading with the sidebar
  - Removed left padding on the main content area and adjusted the top offset to align the heading with the sidebar title
  - **Files changed**: `templates/diary/calendar.html`

- **Diary Sidebar Alignment**: Matched the diary calendar sidebar heading position to the dashboard
  - Increased the diary sidebar top padding to align with the dashboard sidebar
  - **Files changed**: `templates/diary/calendar.html`

- **Header Footer Text**: Moved the footer text into the header and right-aligned it on the same line as the app title
  - Kept the footer text at a small size and removed the footer block
  - **Files changed**: `templates/base.html`

- **Dashboard Sidebar Quick Add Buttons**: Matched dashboard sidebar quick add buttons to the diary calendar sidebar styling
  - Replaced the old quick actions section with the same stacked button block (colors, spacing, icon circles)
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Sidebar Quick Links**: Restored the quick links section under the quick add buttons
  - Added Trends and Weekly Summary links with the same sidebar link styling
  - **Files changed**: `templates/dashboard/index.html`

- **Food Guide Center Image**: Added a centered image below the category grid on the Food Guide page
  - Uses `static/images/wallpaper/image food page.png` with a capped width and soft shadow (now smaller)
  - **Files changed**: `templates/foods/index.html`

- **Food Guide Main Heading Alignment**: Aligned the main content heading with the sidebar heading
  - Adjusted the Food Guide page title top margin to match the sidebar heading position
  - **Files changed**: `templates/foods/index.html`

- **Food Guide Content Widening**: Reduced the left gap between the sidebar and main content
  - Decreased main content left padding so the Food Guide content aligns closer to the sidebar (now 0)
  - **Files changed**: `templates/foods/index.html`

- **Food Guide Sidebar Alignment**: Matched the sidebar heading vertical position to the dashboard
  - Increased the food guide sidebar top padding to align the heading with the dashboard sidebar
  - **Files changed**: `templates/foods/index.html`

- **Dashboard Fixed Layout**: Locked the dashboard background and content widths to prevent resizing with the browser
  - Set a fixed container width and fixed wallpaper render size so the layout stays static
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Wallpaper Lock**: Prevented the wallpaper from resizing with the browser
  - Set a fixed background render size so it stays consistent as the viewport changes
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Wallpaper Offset**: Extended the wallpaper under the sidebar without affecting layout width
  - Moved the background onto a pseudo-element that starts 200px left of the main content and fills the full height
  - Keeps a hard right edge while avoiding horizontal scroll on smaller windows
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Sidebar Alignment**: Shifted the sidebar content down to align with the date header
  - Increased the sidebar top padding so nav text no longer sits under the header
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Spacing Adjustment**: Increased top spacing for the date and content area
  - Moved the dashboard content down with a larger top padding and date margin
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Header Spacing + Horizontal Scroll Fix**: Added top spacing for the date and hid horizontal overflow on the dashboard
  - Added a small top margin to the date header and set `overflow-x: hidden` on the dashboard page
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Wallpaper Alignment Fix**: Fixed background image not butting up against sidebar and footer
  - Removed `padding-left: 15px` from `.main-content-area` so background starts at sidebar edge (200px)
  - Moved padding inside `.dashboard-main-bg` to preserve content spacing while background extends full width
  - Changed `background-position` from `left -20px bottom -20px` to `left bottom` for proper alignment
  - Added `main.container` overrides to remove margins/padding that created gaps
  - Added `footer { margin-top: 0 }` override so background meets footer edge
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Wallpaper Fit**: Forced the wallpaper to cover the full main-content height and reach the footer edge
  - Switched to `background-size: cover`, anchored to the left/bottom, and removed the main container bottom margin on the dashboard
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Wallpaper Positioning**: Shifted the dashboard wallpaper up and left to align with the sidebar edge
  - Adjusted background positioning to better frame the image behind the Watch List
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Wallpaper Coverage**: Extended the dashboard wallpaper to fill the entire main content area down to the footer
  - Set a minimum height for the dashboard background so it covers the full green space
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Wallpaper Background**: Added a dashboard-only wallpaper behind the main content area
  - Uses the image in `static/images/wallpaper/` with a subtle dark overlay for readability
  - **Files changed**: `templates/dashboard/index.html`

- **Global Sidebar Layout Overhaul**: Updated sidebar positioning and styling across all pages
  - **Sidebar now fixed position**: Stays in place when scrolling main content
  - **Key CSS changes for `.sidebar-column`**:
    - `position: fixed` (was sticky)
    - `top: 50px` (below header)
    - `left: 0`
    - `width: 200px` (fixed width)
    - `height: calc(100vh - 50px)` (extends from header to bottom)
    - `overflow-y: auto` (scrollable if content exceeds height)
    - `z-index: 100`
  - **Main content area changes**:
    - `margin-left: 200px` (matches sidebar width)
    - `padding-left: 15px` (gap between sidebar and content)
    - Removed `border-left` (no green separator line)
  - **Row container**: `margin-top: -1.5rem` (pulls content up to meet header)
  - **Removed spacer divs**: No longer needed for vertical alignment
  - **Removed Bootstrap column classes**: Sidebar and main content use custom CSS classes only
  - **Files changed**: `templates/dashboard/index.html`, `templates/foods/index.html`, `templates/diary/calendar.html`, `templates/recipes/index.html`, `templates/education/index.html`, `templates/settings/index.html`, `templates/settings/help.html`

---

**Previous Updates: 2026-01-25**

- **Diary Trends/Weekly - Sidebar + Width Alignment**: Applied the standard sidebar layout and constrained main content width to match the rest of the app
  - Added the green gradient sidebar with nav links, quick add buttons, and quick links
  - Wrapped content in the standard `row` + `col-md-9` container inside the main content area
  - **Files changed**: `templates/diary/trends.html`, `templates/diary/weekly.html`

- **Diary Calendar - Sidebar Quick Links**: Restored Trends and Weekly Summary links in the sidebar below the quick-entry buttons
  - Added a "Quick Links" subheading and two links matching the day-view sidebar styling
  - **Files changed**: `templates/diary/calendar.html`

- **Diary Calendar - Sidebar Quick Add Buttons**: Moved Quick Add Entry buttons from the main content into the sidebar to match the day-view diary styling exactly
  - Added the same dark green container, spacing, and button styles used on the day view
  - Removed the quick add card from the top of the diary calendar page
  - **Files changed**: `templates/diary/calendar.html`

- **Footer Updated for v1.0 Release**: Updated footer text to reflect the v1.0 milestone
  - New footer: "© 2026 Gut Health Management App | Your Personal Health Companion | By Sally - v1.0"
  - **Files changed**: `templates/base.html`

- **Database Backup Fix (BUG FIX)**: Fixed backup downloading empty database instead of the one with data
  - **Root Cause**: Backup route used relative paths (`gut_health.db` and `instance/gut_health.db`) which didn't resolve correctly
  - **Solution**: Changed to use Flask's `current_app.instance_path` for correct absolute path to database
  - Deleted orphan empty database files from root and database/ folders
  - **Files changed**: `routes/settings.py`

- **Docker Database Fix**: Fixed database not loading in Docker container
  - **Root Cause**: `.dockerignore` was excluding `*.db` and `instance/` folder, so database never got copied into image. Additionally, volume mount `./data:/app/instance` created an empty mount that overwrote any database.
  - **Solution**: Created entrypoint script (`docker-entrypoint.sh`) that copies initial database to volume on first run
  - Updated `.dockerignore` to allow `instance/` folder to be copied
  - Updated `Dockerfile` to save initial database to `/app/initial_data/` before volume mount overwrites it
  - Updated `docker-compose.yml` to use named volume `gut_health_data` for persistence
  - **Files changed**: `.dockerignore`, `Dockerfile`, `docker-compose.yml`, `docker-entrypoint.sh` (new)

- **Docker Support Added**: Made the app Docker-compatible for containerized deployment
  - Created `Dockerfile` with Python 3.12-slim base image
  - Created `.dockerignore` to exclude unnecessary files from image
  - Created `docker-compose.yml` for easy deployment with volume mounts
  - Added `watchdog==3.0.0` to requirements.txt (was missing, used by live reload)
  - Added `eventlet==0.33.3` to requirements.txt for better SocketIO production support
  - Configured persistent volumes for database and uploads
  - Health check endpoint configured
  - **Files changed**: `Dockerfile`, `.dockerignore`, `docker-compose.yml`, `requirements.txt`

- **v1.0.0 - GitHub Release Preparation**: Cleaned up project files for initial public release
  - Removed development docs: PHASE2_COMPLETE.md, PHASE3_PROGRESS.md, PHASE4_COMPLETE.md, CRUD_COMPLETION_SUMMARY.md, CRUD_IMPROVEMENT_PLAN.md, revised_app_development_plan.md, EDUCATION_MARKDOWN_GUIDE.md
  - Removed test files: test_add_food.py, test_kippers.py
  - Rewrote README.md with personal story and clean documentation
  - Updated QUICKSTART.md to be current and concise
  - Added .gitignore for Python/Flask projects
  - Created git repository with v1.0.0 tag
  - **Files changed**: README.md, QUICKSTART.md, .gitignore, Version_History.md

- **Settings - Section Order + Nutrition Info**: Reordered Settings page sections and added nutrition data tracking to App Information
  - Main section order now: Database Management, Tags Management, Database Integrity, Data Privacy & Security, Application Information
  - Added nutrition data list to Application Information table
  - **Files changed**: `templates/settings/index.html`

- **Settings - Remove Help & Support Card**: Removed the Help & Support container from the Settings main content area
  - **Files changed**: `templates/settings/index.html`

- **Diary Day View - Sidebar Alignment**: Aligned logging buttons and quick links with main navigation
  - Icons now use 24px circular containers matching main nav items
  - Text left-aligned to match main navigation styling
  - Dark green container extends closer to sidebar edges with negative margins
  - Shortened "Log Bowel Movement" to "Log Bowel" to fit on one line
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Food Info Button**: Added info button next to each food in meal cards
  - Small blue "i" button links to food detail page in new tab
  - Allows viewing full FODMAP, histamine, and nutrition information
  - **Files changed**: `templates/diary/day.html`

- **Diary - Nutrition Tracking for Logged Meals**: Calculate and store nutrition when logging foods
  - Added nutrition fields to MealFood model (energy_kj, protein_g, fat_g, carbs_g, sodium_mg, num_servings)
  - Parse portion size (e.g., "2 servings", "150g", "250ml") and calculate nutrition automatically
  - Display calculated nutrition badge in meal cards when available
  - **Files changed**: `models/diary.py`, `routes/diary.py`, `templates/diary/day.html`
  - **Migration**: `database/migrations/add_nutrition_to_meal_foods.py`

- **Food Detail - Nutrition Information Heading Match**: Matched Nutrition Information heading styling to "Browse by Category"
  - Switched heading class from `text-body` to `text-title` for consistent font size/weight
  - **Files changed**: `templates/foods/detail.html`

- **Diary Day View - Quick Links Cleanup**: Removed the Quick Links border and extra Food Guide link
  - Dropped the duplicate Food Guide button under Quick Links
  - Removed the dark green border from the remaining Quick Links button
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Sidebar Heading & Quick Links**: Updated diary sidebar heading alignment and quick-links spacing
  - Left-aligned and enlarged the "Diary" heading to match the main menu alignment
  - Increased spacing around divider lines above and below the log entry buttons
  - Added a "Quick Links" subheading with icon and extra spacing before the Food Guide/Back to Calendar buttons
  - **Files changed**: `templates/diary/day.html`

- **Diary Sidebar - Container Styling**: Added bordered containers for sidebar sections
  - Navigation menu wrapped in container with thin dark green border (1px solid #1A3636), 8px border-radius
  - Quick-add buttons in dark green container (#1A3636 background) with 8px border-radius, 12px padding
  - Quick-add buttons: 4px left border matching card colors, 25% opacity backgrounds, bold white text
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - UI Polish**: Fixed spacing, stress card layout, and divider styling
  - Reduced meal card bottom margin from 30px to 10px (accounts for timeline's 20px top padding)
  - Moved stress card time from left timeline column to header (matching symptom/bowel cards)
  - Added `stress-entry` class to hide timeline time and remove left padding
  - Changed severity column dividers from 2px dark green to 1px white (rgba 0.3)
  - Changed bowel card vertical separator from 2px gray to 1px white (rgba 0.3)
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Meal Spacing Alignment**: Matched meal card spacing to the timeline entry gaps
  - Replaced `mb-4` with a dedicated `meal-group-card` margin to align with 30px timeline spacing
  - Removed extra top margin on the "other entries" timeline so the gap under meals matches symptom/bowel spacing
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Other Entries Header Removal**: Removed the "Other Entries" heading and aligned timeline spacing to match entry card gaps
  - Added consistent top spacing before the other entries timeline to match symptom/bowel card separation
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Preserve Bowel Header**: Kept the bowel movement header using the original `bg-info` style while other entry types use tinted headers
  - Removed the bowel header override so it retains the brighter header look
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Header Styling Match**: Made all entry cards match the bowel card layout with tinted headers and gradients
  - Added per-entry header styling (meal, symptom, bowel, stress, note) with stronger borders/gradients
  - Added dedicated headers for stress and note cards and aligned their action buttons to the header style
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Entry Card Tinting CSS Fix**: Fixed two CSS issues preventing card backgrounds and borders from displaying
  - Issue 1: The `border-color` shorthand was overriding `border-left-color` - reordered properties correctly
  - Issue 2: The global `.card` style in main.css uses `background-color: var(--bg-elevated) !important` which overrode the tinted backgrounds - added `!important` to all timeline-card styles to ensure they take precedence
  - Now all card types (meal, symptom, bowel, stress, note) correctly show tinted backgrounds and matching borders
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Entry Card Tinting**: Matched day-view entry card backgrounds and borders to the calendar log button colors
  - Applied faint tinted backgrounds and matching border colors for meal, symptom, bowel, stress, and note cards
  - Ensures all entry types visually match their logging colors across the diary
  - **Files changed**: `templates/diary/day.html`

- **Diary Day View - Bowel Entry Width Alignment**: Matched bowel movement entry containers to the same left width as other entries in the day timeline
  - Added a dedicated `bowel-entry` timeline class to remove the extra left padding reserved for timestamps
  - Ensures bowel movement cards align with other entries that don’t show the timeline time column
  - **Files changed**: `templates/diary/day.html`

- **Diary Delete Modal Flashing Fix (BUG FIX)**: Fixed rapid flashing of delete confirmation modals when moving mouse over browser window
  - **Root Cause**: Delete modals were nested inside `.timeline-card` elements which have CSS hover effects (`transform: translateX(5px)`). Mouse movement caused the parent card's hover state to toggle, shifting the modal position and causing flashing.
  - **Solution**: Moved all delete modals outside of card elements to a dedicated section at the end of the content block
  - **Additional Changes**:
    - Converted stress entry and note entry delete buttons from inline JavaScript `confirm()` to Bootstrap modals for consistency
    - All entry types (meal, symptom, bowel, stress, note) now use the same modal-based delete confirmation
  - **Files changed**: `templates/diary/day.html`

- **Food Detail Vitamins Divider**: Added a second divider line under the Vitamins header
  - Matches the double-divider styling used in the other nutrition columns
  - **Files changed**: `templates/foods/detail.html`

- **Food Detail Minerals/Vitamins Cleanup**: Removed default mineral/vitamin rows when empty
  - Only renders Sodium/Potassium/Calcium/Phosphorus and core vitamins when data exists
  - Custom nutrient rows still display as before
  - **Files changed**: `templates/foods/detail.html`

- **Fixed Sodium Not Persisting in Edit Form (BUG FIX)**: Standard mineral fields (Sodium, Potassium, Calcium, Phosphorus) were missing from edit-food.html and add-food.html templates
  - Added static input fields for all four standard minerals in both forms
  - Mineral values now properly populate when editing a food item
  - Added same fields to add-food.html for consistency

- **Fixed Decimal Display Formatting**: Nutrition values showing unnecessary ".0" for whole numbers (e.g., "1010.0mg" instead of "1010mg")
  - Added custom Jinja filter `format_num` in app.py to remove trailing zeros
  - Applied filter to all nutrition values in detail.html (energy, protein, fat, carbs, cholesterol, minerals, vitamins)
  - Numbers display exactly as entered (e.g., "1010" stays "1010", "1.5" stays "1.5")

---

**Previous Updates: 2026-01-25**

- **Fixed Custom Nutrients Not Saving (CRITICAL BUG FIX)**: Custom vitamins and minerals RDI values were not saving due to form field name mismatches
  - Fixed field name discrepancy: Changed `custom_vitamin_rdi_percent_` to `custom_vitamin_rdi_` in add/edit forms
  - Fixed field name discrepancy: Changed `custom_mineral_rdi_percent_` to `custom_mineral_rdi_` in add/edit forms
  - Enhanced `parse_custom_nutrients()` function with robust error handling:
    - Added `safe_float()` helper to properly handle empty strings and invalid numeric inputs
    - Added `.strip()` to all text fields to remove whitespace
    - Improved ValueError/TypeError exception handling for invalid numeric conversions
  - **Root Cause**: Form fields used `_percent` suffix, but parser expected fields without suffix
  - **Impact**: Custom nutrients (vitamins/minerals) entered via "Add" buttons now save correctly
  - **Files changed**: `routes/foods.py`, `templates/foods/add-food.html`, `templates/foods/edit-food.html`

---

**Updates: 2026-01-24**

- **Edit Food Nutrition Section Layout Fixes**: Tightened minerals/vitamins widths and compacted inputs
  - Adjusted minerals/vitamins table column widths and enforced fixed table layout
  - Reduced input sizes and tightened padding/height for nutrition inputs
  - Updated custom nutrient row widths and smaller white delete buttons
  - **Files changed**: `templates/foods/edit-food.html`

- **Edit Food Form Sizing & Sidebar Actions**: Reduced form typography, widened serving inputs, and moved submit buttons to sidebar
  - Added smaller font sizing for edit form controls/labels
  - Increased serving size input widths for better visibility
  - Moved Cancel/Update buttons into sidebar with dark green styling
  - **Files changed**: `templates/foods/edit-food.html`

- **Food Detail Nutrition Table Font Size**: Reduced the nutrition table font further to prevent wrapping
  - Set nutrition cells to 0.55rem and headers to 0.5rem with tighter line-height
  - **Files changed**: `templates/foods/detail.html`

- **Food Detail Nutrition Table Font Size**: Reduced nutrition table font sizes to prevent wrapping
  - Set nutrition table cells and values to `--text-micro` with tighter line-height
  - **Files changed**: `templates/foods/detail.html`

- **Food Forms Collapsible Width Enforcement**: Forced collapsible sections to full-width block layout
  - Explicitly set `display: block` and `max-width: 100%` for consistent widths
  - **Files changed**: `templates/foods/add-food.html`, `templates/foods/edit-food.html`

- **Food Forms Collapsible Width Fix**: Matched Additional Information width to Nutrition section
  - Set collapsible section containers to full width with border-box sizing
  - **Files changed**: `templates/foods/add-food.html`, `templates/foods/edit-food.html`

- **Food Forms Collapsible Sections**: Made serving, nutrition, and additional info panels collapsible by default
  - Safe/Moderate/High serving sections now collapsed with summary rows
  - Nutrition information section collapsed with the same summary row style
  - Additional Information section moved to the bottom and collapsed by default
  - **Files changed**: `templates/foods/add-food.html`, `templates/foods/edit-food.html`

- **Food Forms Sidebar Cleanup**: Removed the FODMAP/histamine info blocks on add/edit pages
  - Deleted the informational container and educational resources section
  - Kept form content constrained to `row` + `col-md-9` per layout rules
  - **Files changed**: `templates/foods/add-food.html`, `templates/foods/edit-food.html`

- **Packaged Foods - Add to Diary Support**: Enabled adding packaged foods without serving types directly to diary
  - **Food Detail View** (`templates/foods/detail.html`):
    - Serving sections (Safe/Moderate/High) now hidden when no serving sizes exist (checks `food.safe_serving`, `food.moderate_serving`, `food.high_serving`)
    - "Add to Diary" UI added inside Nutrition Information header for packaged foods without serving data
    - Text input (150px width) for custom serving quantity (e.g., "2 servings", "150g") positioned left of button
    - "Add to Diary" button (green, btn-sm) positioned right side of header, aligned with section title
    - JavaScript transfers input value to modal's portion size field when modal opens
    - New modal `addToDiaryModalPackaged` for packaged food diary entry (same structure as existing serving modals)
    - Empty `serving_type` passed to existing `add_meal` route (no new route needed)
  - **Diary Route** (`routes/diary.py`):
    - Existing `add_meal` route already handles empty serving types correctly (converts to None)
    - No backend changes required
  - **Documentation** (`CLAUDE.md`):
    - Added Packaged Foods section under "Key Data Concepts" explaining the feature
  - **Purpose**: Allows tracking of pre-packaged supermarket foods and takeaway meals using only nutritional info without FODMAP/histamine serving data
  - **Files changed**: `templates/foods/detail.html`, `CLAUDE.md`, `Version_History.md`

- **Food Guide Sidebar Height**: Extended the green sidebar background to reach the footer
  - Set the sidebar column to `min-height: 100vh` so it spans full page height
  - **Files changed**: `templates/foods/index.html`

- **Food Guide Sidebar Cleanup**: Removed the database info container beneath the "View Safe Foods List" button
  - Simplified the sidebar by removing the informational box under the action buttons
  - **Files changed**: `templates/foods/index.html`

- **Food Guide Layout Fix**: Constrained main content width to match dashboard layout
  - Wrapped content in `row` + `col-md-9` per CLAUDE.md layout pattern
  - Restored expected width for "Browse by Category" container
  - **Files changed**: `templates/foods/index.html`

- **Food Guide Category Tiles**: Enlarged category tiles to fit 5 per row
  - Increased circle size and icon size
  - Set each tile to 20% width for consistent 5-column layout
  - **Files changed**: `templates/foods/index.html`

- **Dashboard Watch List Styling**: Darkened the High Risk section background slightly
  - Updated background opacity from `rgba(220, 53, 69, 0.08)` to `rgba(220, 53, 69, 0.16)`
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Watch List Styling**: Changed the Moderate Risk section background to a faint yellow
  - Updated background from dark green to `rgba(255, 193, 7, 0.06)` to match yellow risk palette
  - **Files changed**: `templates/dashboard/index.html`

- **Dashboard Cleanup**: Removed the "Getting Started" information section from the dashboard page
  - Simplified the main content area by removing the onboarding list
  - **Files changed**: `templates/dashboard/index.html`

- **Packaged Food Category Added**: Added new "Packaged Food" category for supermarket and restaurant/takeaway foods
  - **Food Guide Index**: Added new category tile with box-seam icon between "Oils & Condiments" and "View All"
    - Gold circular icon background (#D6BD98) with dark green icon (#1A3636)
    - Links to search page filtered by "Packaged Food" category
    - Compact 80px width matching existing category tiles
  - **Add Food Form**: Added "Packaged Food" option to category dropdown in add-food.html
    - Positioned before "Other" in dropdown list
  - **Edit Food Form**: Added "Packaged Food" option to category dropdown in edit-food.html
    - Positioned before "Other" in dropdown list
    - Includes selected state condition for existing foods
  - **Purpose**: Enables tracking of pre-prepared packaged foods from supermarkets and takeaway/restaurant meals
  - **Files changed**: `templates/foods/index.html`, `templates/foods/add-food.html`, `templates/foods/edit-food.html`

**Previous Updates: 2026-01-22**

- **Settings Page - Section Navigation**: Added quick navigation buttons in sidebar to jump to specific sections on the settings page
  - **Anchor IDs**: Added 7 anchor IDs to each section (`help-support`, `tags-management`, `typography-display`, `database-integrity`, `database-management`, `data-privacy`, `app-information`)
  - **Sidebar Buttons**: Added 7 section navigation buttons below separator in sidebar
    - Buttons styled with dark green background (#1A3636), gold text (#D6BD98), btn-sm, full width, text-start
    - Icons matching each section (question-circle, tags, eye, shield-check, database, shield-lock, info-square)
    - Positioned vertically below main navigation and separator line
  - **Smooth Scroll**: Implemented JavaScript smooth scroll functionality with 70px offset for sticky header
  - **Purpose**: Makes it easier for users to quickly navigate to specific settings sections without scrolling
  - **Files changed**: `templates/settings/index.html`

- **Help & Support System Added**: Created comprehensive help document management system in Settings
  - **New Database Model**: Added `HelpDocument` model in `models/education.py` for storing help content with markdown support
  - **New Routes**: Added 7 routes in `routes/settings.py` for help document CRUD operations (`/settings/help`, `/settings/help/<id>`, `/settings/help/upload`, `/settings/help/preview`, `/settings/help/edit/<id>`, `/settings/help/delete/<id>`, `/settings/help/preview_markdown`)
  - **New Templates**: Created 4 help templates in `templates/settings/`:
    - `help.html` - Main help documents list with category filtering, search, upload, edit/delete mode
    - `help_view.html` - Individual document view with in-document search and highlighting
    - `help_edit.html` - Edit document with live markdown preview
    - `help_preview.html` - Preview uploaded document before saving
  - **Settings Integration**: Added Help & Support card to `templates/settings/index.html`
  - **Features**: Markdown support, category organization, drag-and-drop upload, search, bulk edit/delete, live preview
  - **Purpose**: Centralized location for FAQs, tips, navigation guides, and scattered help information
  - **Files changed**: `models/education.py`, `routes/settings.py`, `templates/settings/index.html`, `templates/settings/help.html`, `templates/settings/help_view.html`, `templates/settings/help_edit.html`, `templates/settings/help_preview.html`, `CLAUDE.md`

- **Dashboard - Quick Actions & Watch List Styling**: Updated dashboard layout
  - **Add Recipe / Create Meal buttons**: Changed to outline style (transparent background, dark green border)
  - **Watch List container**: Added thin beige border (1px solid #D6BD98)
  - **Getting Started heading**: Changed to left-aligned, removed dividing lines above/below
  - **Files changed**: `templates/dashboard/index.html`

- **Recipes Page - Layout Fix**: Fixed layout issues on the Recipes index page
  - **Beige Border Container**: Added 2px solid beige border (#D6BD98) around all 3 feature cards (My Recipes, My Saved Meals, Recipe Helper AI)
    - Wrapper div with border-radius: 8px, padding: 15px
    - Individual cards no longer have separate beige borders
  - **Quick Tips Repositioned**: Moved Quick Tips card back below the 3 feature cards (was incorrectly placed above)
    - Order now: Page title → 3 Feature Cards (in beige container) → Quick Tips → Welcome Card
  - **Files changed**: `templates/recipes/index.html`

- **CLAUDE.md Compacted**: Reduced developer guide from 365 lines to 67 lines
  - Kept only essential information: app overview, structure, colors, layout pattern, typography tokens, data concepts, design rules
  - Removed verbose examples and redundant explanations
  - Added clear Development Checklist at bottom
  - **Files changed**: `CLAUDE.md`

**Previous Updates: 2026-01-20**

- **Education Page - Sub-Chapter Support**: Added support for hierarchical chapter numbering (e.g., 2.1, 2.2)
  - **Database Changes**:
    - Changed `chapter_number` field from Integer to String (VARCHAR) to support decimal numbering
    - Added natural sorting function to properly order chapters (1, 2, 2.1, 2.2, 3, 10)
    - Created migration script: `migrate_chapter_numbers.py` to convert existing data
  - **Chapter Display**:
    - Sub-chapters (chapters with "." in number) display with left indentation (40px)
    - Sub-chapters have distinct visual styling: info badge color, chevron icon, subtle left border
    - Main chapters continue to use secondary badge color
    - Proper sorting ensures sub-chapters appear directly after their parent chapter
  - **Edit Functionality**:
    - Chapter numbers are now editable in the edit form
    - Chapter number field moved to prominent position with helper text explaining sub-chapter format
    - Users can manually set/change chapter numbers (e.g., change "3" to "2.1" to make it a sub-chapter)
  - **Reorder Mode**:
    - Reorder functionality preserves chapter numbers (doesn't auto-renumber)
    - Alert message explains that chapter numbers are preserved after reordering
    - Users should manually edit chapter numbers after reordering if needed
  - **Filtering**:
    - Topic filters show sub-chapters when main chapter's topic matches
    - Search functionality searches across main and sub-chapters
  - **Files changed**:
    - `models/education.py` (database model)
    - `routes/education.py` (backend logic + natural_sort_key function)
    - `templates/education/index.html` (chapter list display)
    - `templates/education/edit.html` (editable chapter number field)
    - `templates/education/chapter.html` (sub-chapter badge display)

- **Education Page - Layout Reorganization**: Improved page layout for better space utilization
  - **Search Bar**: Moved from main content header into sidebar
    - Positioned at top of sidebar above navigation separator
    - Compact input-group-sm design with outline-light buttons
    - Maintains search and clear functionality
  - **Research Library**: Moved from middle column card into sidebar
    - Positioned at bottom of sidebar below final separator
    - Compact h6 heading (0.67rem) with file-earmark-text icon
    - Gold button (matching app color scheme) linking to research papers
    - Micro-sized helper text (0.62rem)
  - **Quick Topics Card**: Moved from left column to main content area
    - Narrower width (col-md-3 instead of col-md-4)
    - Topic filter buttons (FODMAPs, Histamine, Vagus Nerve, Stress & Gut)
  - **Chapter List**: Expanded to utilize freed space
    - Wider column (col-md-9 instead of col-md-8)
    - Removed compact TOC card (redundant with full chapter list)
    - More breathing room for chapter titles and metadata
  - **Header Simplification**: Removed search bar from header row
    - Header now only shows "Educational Booklet" title
    - Cleaner, less cluttered top section
  - **Result**: Sidebar now contains all tools (search, upload, reorder, research), main area focuses on content browsing

**Updates: 2026-01-19**

- **Food Detail & Category Pages - Sidebar Navigation**: Added consistent sidebar navigation to food detail and category list pages
  - **Food Detail Page** (`detail.html`):
    - Added green gradient sidebar with section title "Food Details"
    - 5 main navigation links (Dashboard, Food Guide, Diary, Recipes, Education, Settings)
    - Separator line below navigation
    - Action buttons: "Edit Food" (warning), "Back to [Category]", "Search Foods", "Delete Food"
    - Removed duplicate buttons from header (Edit/Delete) and footer (Back to Category/Search)
    - Header now only shows food name, category, and 1-serve traffic light indicator
    - Main content area: 3px sage green left border, 30px left padding
  - **Food Category/Search Page** (`search.html`):
    - Added green gradient sidebar with dynamic section title (category name or "Food Search")
    - 5 main navigation links (Dashboard, Food Guide, Diary, Recipes, Education, Settings)
    - Separator line below navigation
    - Action buttons: "Back to Food Guide" (if category), "Add Custom Food"
    - Removed duplicate buttons from top header area
    - Main content area: 3px sage green left border, 30px left padding
  - **Consistent Design**: Both pages use same sidebar pattern as other main pages
    - Sticky positioning: `top: 50px`, `padding-top: 28px` (via 30px spacer div)
    - Hover effects: slide right 3px + beige highlight background
    - All buttons: btn-sm, 0.7rem font, full width, vertically stacked
    - CSS class naming: `.food-detail-sidebar`, `.foods-sidebar`

- **Food Guide Main Page - Sidebar Consolidation**: Reorganized Food Guide page layout
  - Moved all functionality to sidebar under separator line
  - Search form in sidebar:
    - Compact search input with outline-light button
    - White text on semi-transparent background, 0.7rem font
  - Action buttons in sidebar:
    - "Add Custom Food" (green success button)
    - "View Safe Foods List" (outline-light button)
    - All buttons: btn-sm, 0.7rem font, full width, vertically stacked
  - Database info alert in sidebar (0.65rem font, compact design)
  - Browse by Category now uses full width (col-md-12)
  - Removed right column entirely
  - All functionality consolidated in sidebar for cleaner, more consistent interface

- **Add Food Page - FODMAP/Histamine Compact Layout**: Ultra-compact design to fit all three serving cards without wrapping
  - FODMAP grid: 85px min column width (down from 120px), 4px gap (down from 8px)
  - Histamine grid: 100px min column width (down from 150px), 4px gap (down from 8px)
  - FODMAP cards: 6px/4px padding (down from 12px/8px), 6px gap (down from 12px)
  - Section headers: 0.7rem font (down from 0.75rem), mt-2 mb-1 margins (down from mt-3 mb-2)
  - All labels: 0.65rem font (down from 0.7rem)
  - Serving cards: 220px min-width (down from 250px), 8px padding (down from 10px)
  - Container gap: 12px between cards (down from 20px)
  - Ensures all three serving cards fit side-by-side even with sidebar on smaller screens

- **Add Food Page - Sidebar Action Buttons**: Reorganized Add Food page layout
  - Moved all action buttons from top header to sidebar
  - Added separator line below Settings navigation (20px margins, 1px white semi-transparent)
  - Action buttons section in sidebar:
    - Primary: "Add Food to Library" (green) and "Cancel" (gray)
    - 10px spacer
    - Secondary: "Back to Food Guide" and "Add Another Food" (outline style)
    - All buttons: btn-sm, 0.7rem font, full width, vertically stacked
  - Simplified header to centered page title only: "Add Custom Food/Drink" (1.2rem)
  - Cleaner, less cluttered interface with better visual hierarchy

- **Food Forms - Sidebar Navigation**: Added sidebar navigation to Add Food and Edit Food form pages
  - Consistent green gradient sidebar matching all other main pages
  - Section title: "Food Guide" with egg-fried icon
  - 5 navigation links: Dashboard, Diary, Recipes, Education, Settings
  - Same styling as other sidebars: 24px circular icons, 0.7rem labels, hover effects
  - Main content area: 3px solid sage green left border, 30px left padding
  - 30px spacer div for vertical alignment consistency with other pages
  - Modals (Calculator, Conversion) positioned outside the sidebar/main-content structure

- **Settings Pages - Sidebar Navigation**: Added sidebar navigation to Settings pages (index.html and tags.html)
  - Consistent green gradient sidebar matching all other main pages
  - Section title: "Settings" with gear icon
  - 5 navigation links: Dashboard, Food Guide, Diary, Recipes, Education
  - Same styling as other sidebars: 24px circular icons, 0.7rem labels, hover effects
  - Main content area: 3px solid sage green left border, 30px left padding
  - Compact page headers: 1.2rem font size matching other pages
  - Compact buttons: btn-sm class with 0.7rem font size

- **Sidebar Vertical Alignment Fix**: Fixed sidebar positioning to match Dashboard across all pages
  - **Issue**: Dashboard had date header creating vertical spacing, other pages' sidebars appeared higher
  - **Solution**: Added 40px spacer div (`height: 30px; margin-bottom: 10px`) to all non-Dashboard pages
  - **Affected pages**: Food Guide, Diary, Recipes, Education, Settings (index & tags)
  - **Result**: All sidebars now align vertically at same height as Dashboard
  - Sticky positioning: `top: 50px`, `padding-top: 28px` (CONSISTENT across all pages)

**Updates: 2026-01-18**
- **Global Sidebar Navigation**: Added consistent sidebar navigation to Food Guide, Diary, Recipes, and Education pages
  - Green gradient sidebar (sage green #8BA48B to #677D6A) matching Dashboard design
  - Section title shows current page name with icon, white text, underline border
  - 5 navigation links: Dashboard, Food Guide, Diary, Recipes, Education, Settings
  - 24px circular icon containers with white semi-transparent background
  - 12px SVG icons in white, 0.7rem text labels with font-weight 500
  - Hover effects: slide right 3px + beige highlight background (rgba(214, 189, 152, 0.15))
  - Sticky positioning at top: 50px
  - Responsive layout: col-lg-2 col-md-3 for sidebar, col-lg-10 col-md-9 for content
  - Main content separated by 3px solid sage green left border with 30px left padding
  - Applied to: foods/index.html, diary/calendar.html, recipes/index.html, education/index.html

**2026-01-18**
- **Food Guide Sizing Consistency**: Made all Food Guide pages compact to match Dashboard and Diary at 100% zoom
  - All three food guide templates updated with consistent compact sizing
  - Page headers: 1.2rem (matching dashboard/diary)
  - Card padding: 10px consistent across all cards
  - Card headers: 6px/10px padding, 0.8rem font
  - Buttons: btn-sm class with 0.75rem font, 4px/10px padding
  - Body text: 0.7-0.75rem font sizes throughout
  - Category circles: 80px diameter (down from 120px), 2rem icons (down from 3rem)
  - Serving cards: 250px min-width (down from 280px), 10px padding, compact 0.7-0.8rem fonts
  - Traffic lights: 16px in lists, 20px in cards, 32px in headers (down from 24px/48px)
  - Nutrition panel: 0.7rem table font, 100x40px health star rating, 60px store logos
  - Margins: mb-3 (reduced from mb-4) for tighter spacing
  - Breadcrumbs: 0.75rem font, 6px padding
  - Files changed: `templates/foods/index.html`, `templates/foods/search.html`, `templates/foods/detail.html`
  - Updated CLAUDE.md with new "Compact Sizing" section documenting all sizing standards

- **Orphaned Diary Entry Cleanup**: Fixed calendar showing phantom entries after deletion
  - Calendar view now automatically detects and deletes orphaned DiaryEntry records (entries with no related content)
  - Day view also performs same cleanup when viewed
  - Issue: Deleted entries left empty DiaryEntry records in database showing dots on calendar
  - Solution: Both calendar and day views now filter and auto-delete orphaned entries on load
  - Ensures calendar dots only appear for entries with actual content
  - Files changed: `routes/diary.py`

- **Calendar View Sizing Consistency**: Made calendar view compact to match dashboard at 100% zoom
  - Reduced all font sizes: page title (1.2rem), buttons (0.65rem), headings (0.8rem-1rem)
  - Reduced spacing: card padding (10px), margins (mb-2/mb-3), calendar gaps (3px)
  - Reduced calendar elements: day cells (70px min-height), day numbers (0.75rem), dots (6px)
  - Stats section: compact 1.1rem numbers with 0.65rem labels
  - All sizing now consistent with dashboard's compact design
  - Files changed: `templates/diary/calendar.html`

- **Watch List Shows Both High and Moderate Risk**: Fixed watch list to show all concerning foods
  - Shows ALL foods logged in last 7 days that have amber/red ratings at moderate or high serving sizes
  - High Risk (red section): Foods with RED rating at high serving size
  - Moderate Risk (yellow section): Foods with AMBER at high serving, OR amber/red at moderate serving
  - Both sections display together, grouped by risk level then sorted by date
  - Files changed: `routes/main.py`

- **Watch List Diary Link Fix**: Fixed watch list items linking to food detail page instead of diary entry
  - Watch list now pulls foods from diary meal entries in the last 7 days
  - Clicking a food item now links to the diary day view where that food was logged
  - Added portion_size display from the actual MealFood entry (shows amount consumed)
  - Files changed: `routes/main.py`, `templates/dashboard/index.html`

- **Diary Serving Type Tracking Fix**: Fixed bug where serving type (safe/moderate/high) was not being recorded when adding food to diary from the food detail page
  - Added `serving_type` column to `meal_foods` database table
  - Updated MealFood model to include `serving_type` field
  - Added hidden `serving_types[]` input fields to all three "Add to Diary" modals (safe, moderate, high)
  - Updated diary route to capture and save `serving_type` with each food entry
  - Updated day view template to display correct FODMAP and histamine traffic lights based on the logged serving type
  - Previously, all foods showed as "safe" serving regardless of which button was clicked
  - Created migration script: `database/migrations/add_serving_type_to_meal_foods.py`
  - **Edit Meal Fix**: Fixed issue where editing a meal would reset serving type to "safe"
    - Updated diary route to include `serving_type` in `existing_meal_foods_dict` passed to template
    - Updated `entry-meal.html` to pass `serving_type` to `addFoodRow()` function
    - Added hidden `serving_types[]` input field to each food row in the meal edit form
    - Updated `updateFoodInfo()` function to accept and use existing serving type instead of always defaulting to "safe"
    - Serving button click now updates hidden input value so it's submitted with the form

- **Dashboard Watch List Redesign**: Improved Watch List with separate sections
  - Watch List heading now yellow (#ffc107) with thin 1px underline
  - Split foods into "High Risk" (red section) and "Moderate Risk" (amber section)
  - Each food item now shows serving size consumed
  - Section labels with matching color icons
  - Date moved to top of page, centered, larger (0.85rem), beige (#D6BD98)
  - Quick Actions separator line now thinner (1px) with wider gaps (25px margin)

- **Dashboard Spacing Improvements**: Added more breathing room between sections
  - Increased left padding from 20px to 30px for main content area
  - Flexbox layout with gap-5 for horizontal spacing
  - Watch List in beige bordered box, Quick Actions max-width 180px

- **Dashboard Styling Enhancements**: Updated sidebar and layout styling
  - Sidebar now has sage green gradient background (#8BA48B to #677D6A) matching Log Meal button
  - Sidebar text and icons changed to white for contrast on green background
  - Main content area has 3px solid sage green left border (full height separator)
  - All section title underlines increased to 3px thickness for visibility
  - All separator lines (dividers) increased to 3px thickness
  - Quick Actions now displayed vertically (stacked) instead of inline
  - 3px horizontal divider line added between diary logging and create actions

- **Dashboard Container Removal**: Removed all card containers for cleaner look
  - Sidebar now displays navigation links directly without card wrapper
  - Watch List and Quick Actions show content without card containers
  - Section titles use simple underline borders instead of card headers
  - Getting Started replaced alert box with simple numbered list
  - Overall much lighter, less chunky appearance

- **Compact UI Overhaul**: Reduced overall sizing for better display at 100% zoom
  - Base font size reduced to 0.875rem
  - Heading sizes reduced (h1: 1.25rem, h2: 1.1rem, h3: 1rem, h4: 0.95rem, h5: 0.875rem, h6: 0.8rem)
  - Compact navbar padding (0.35rem 1rem)
  - Compact cards (padding: 0.75rem body, 0.5rem header)
  - Compact form elements (font-size: 0.8rem, padding: 0.3rem 0.5rem)
  - Compact buttons (font-size: 0.8rem, padding: 0.3rem 0.6rem)
  - Container max-width reduced to 1100px

- **Dashboard Sidebar Improvements**: Skinnier sidebar with vertical separator
  - Sidebar now takes 2 cols on large screens, 3 cols on medium (was 3/4)
  - Gold vertical separator line (2px solid #D6BD98) between sidebar and main content
  - Compact icons: 28px circular containers, 14px SVG icons (was 45px/22px)
  - Compact text: 0.75rem labels (was 0.9rem)
  - Compact padding throughout all dashboard elements

- **Dashboard Sidebar Navigation**: Moved navigation to left sidebar
  - Navigation icons now in a vertical sidebar on the left side of the page
  - "Dashboard" heading at top of sidebar with dark green header
  - 5 navigation links (Food Guide, Diary, Recipes, Education, Settings) displayed vertically
  - Hover effect: slides right with shadow
  - Sticky sidebar stays visible when scrolling
  - Main content (Watch List, Quick Actions, Welcome Message) in right column

- **Previous Dashboard Layout Overhaul**: Major redesign of dashboard components
  - **Navigation Icons**: Reduced size to match quick action cards (60px circular icons, 28px SVG icons)
  - **Two-Column Layout**: Watch List (left, 7 cols) and Quick Actions (right, 5 cols) now side by side
  - **Watch List**: Compact vertical list with single-line items, color-coded left border
  - **Quick Actions**: 2x3 grid of gradient cards within a card container
  - Both sections have matching dark green headers with icons
  - Smaller, more compact quick action buttons (45px icons, 0.8rem text)
  - Consistent border-radius (16px for containers, 12px for action cards)

- **Quick Actions Redesign**: Complete visual overhaul of the Quick Actions section
  - Changed to vertical list layout with two sections separated by horizontal line
  - Top section: Diary logging (Log Meal, Log Symptoms, Log Bowel)
  - Bottom section: Create actions (Add Recipe, Create Saved Meal)
  - Removed Search Foods and View Diary from quick actions
  - Horizontal card layout with icon on left, text on right
  - Centered cards with max-width 280px
  - New gradient-based design with smooth color transitions using app color palette
  - Added hover effects (lift animation and enhanced shadow)

- **Dashboard Redesign**: Complete overhaul of dashboard layout
  - Removed tracking stats section (Symptom-Free Days, Meals Logged, Avg Symptom Level, Tracking Streak)
  - Added 5 large navigation icons with custom SVG symbols:
    - Food Guide (knife and fork icon)
    - Diary (book with lines icon)
    - Recipes (chef hat icon)
    - Education (graduation cap icon)
    - Settings (gear icon)
  - Navigation icons have hover effects (lift and shadow)
  - Added "Watch List" container showing foods logged in last 7 days that have moderate (amber) or high (red) FODMAP/histamine levels
  - Watch list shows food name, category, severity badge (Moderate/High), and date logged
  - Empty state displays when no concerning foods have been logged
  - Backend route (`routes/main.py`) updated with `get_traffic_light_color()` function to determine food severity

- **Custom Nutrients Feature**: Full implementation of custom nutrients system
  - Added `custom_nutrients` JSON field to Food model for storing custom vitamins, minerals, and macronutrients
  - Routes updated to parse and save custom nutrients from form submissions
  - Custom nutrients display on food detail view page with proper formatting
  - Pre-population of custom nutrients when editing existing foods
  - "Add Custom Vitamin/Mineral/Macronutrient" buttons in both add-food.html and edit-food.html
- **Drag-and-Drop Reordering**: Added JavaScript functionality for reordering nutrition rows in forms
  - Drag handles with grip icons on vitamin rows
  - Visual feedback during drag operations
  - Works within vitamins, minerals, and macronutrients containers
- **Decimal Precision**: Changed all nutrient input fields from `step="0.1"` or `step="0.01"` to `step="any"` for unlimited decimal precision
- **Form Parity**: Updated add-food.html to match edit-food.html with containers and custom nutrient functionality

**Updates: 2026-01-25**
- **Help Documents (File-Based Storage)**: Moved Help & Support documents from database to `data/help_docs`
  - Added `index.json` for metadata and `.md` files for content
  - Upload preview flow unchanged; save now writes markdown file + index entry
  - Edit/delete now updates/removes files and index entries
- **Help Page Display**: Help list now renders as collapsible, inline content blocks on the same page
  - Uses file-based markdown rendered to HTML in collapsible containers
  - Dates shown per document using file/index timestamps
- **Help List Styling**: Restyled Help list to match Education “CONTENTS” look (green panel, gold border, TOC-style typography)
- **Diary Meal Nutrition Tooltip**: Nutrition badge now shows a compact hover tooltip with serving size and per-serve nutrition values
- **Diary Nutrition Breakdown**: Tooltip now displays full per-serve breakdown (energy, macros, carbs, minerals, vitamins, custom nutrients) based on logged serving size
- **Diary Nutrition Tooltip Layout**: Added spacing before section headings and updated label to “Nutrition Information” with wider inline spacing
- **Diary Daily Nutrition Charts**: Added per-day doughnut charts grouped by nutrient unit (including custom nutrients) to the day view
- **Diary Chart Stability**: Fixed chart container sizing and initialization to prevent repeated growth
- **Diary Nutrition Pie Chart**: Switched to a single pie chart with all nutrients converted to grams
- **Diary Target Chart**: Added a bar + recommendation line chart comparing daily nutrient usage to targets
- **Diary Chart Layout**: Split charts into separate containers and enlarged chart sizing with smaller legend text
- **Diary Chart Collapsible Panels**: Made each chart section collapsible from its heading

**Previous Updates: 2026-01-17**
- **Nutrition Display - Show ALL Fields**: Complete overhaul of nutrition panel display in detail.html
  - ALL nutrition fields now ALWAYS display when the nutrition panel is shown (not just filled ones)
  - Empty/unfilled fields display "-" instead of being hidden
  - Consistent display across ALL food categories (Beverages, Fruits, Vegetables, Grains, etc.)
  - Expanded trigger conditions: panel shows if ANY nutrition-related field has data
  - Section dividers between Energy/Macros/Minerals/Vitamins are always present
  - RDI% column always shows (with "-" for empty values)
  - Allergens section (Contains/May Contain) always visible with "-" for empty
  - RDI% explanation footer always shown
- **Previous fix (earlier 2026-01-17)**: Changed conditionals from `{% if food.value %}` to `{% if food.value is not none %}`
- **Vitamin RDI % Indicator**: Added `<small class="text-muted">%</small>` below the RDI input field for all vitamins (A, B2, B12, D) in both add-food.html and edit-food.html
  - This matches the existing pattern used for Calcium and Phosphorus RDI fields

**Previous Updates: 2026-01-15**
- Fixed nutrition information display to show all fields filled in add/edit forms
- Added line separators above and below Cholesterol with "(mg)" label in muted color
- Added section dividers between Energy, Macronutrients, Minerals, and Vitamins sections
- Improved visual hierarchy matching the add/edit form structure
- **Nutrition Form Styling Updates** (edit-food.html):
  - Reduced delete button size to match food list page style (padding: 0.25rem 0.5rem, removed w-100)
  - Standardized all macronutrient input columns to col-md-4 width for vertical alignment
  - Updated Sodium and Potassium rows to col-md-4 for consistency
  - All nutrient text input fields now align vertically across the form

**Updates: 2026-01-14**
- Food detail view redesigned with side-by-side serving cards
- Traffic light moved to top-right of each serving card
- Nutrition information view updated to match add/edit form structure
- Added 4-column table layout with dedicated RDI% column
- Improved indentation for sub-nutrients (lactose/galactose under sugars)

---

## ⚠️ Important Notes

- **FODMAP Ratings**: Change based on serving size (not static per food)
- **Histamine Levels**: Also vary by serving size and preparation
- **Traffic Light Logic**: Calculated from worst rating across all FODMAP types and histamine markers
- **Monash Reference**: FODMAP ratings follow Monash University FODMAP app patterns
- **Custom Fields**: User can add/remove any nutrition data fields as needed

---

**Last Updated**: 2026-01-29
**Maintained By**: Claude (AI Assistant)
