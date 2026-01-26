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

**Latest Updates: 2026-01-26**

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

**Last Updated**: 2026-01-25
**Maintained By**: Claude (AI Assistant)
