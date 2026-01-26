# Gut Health Management App

> **MANDATORY**: Read this file before ANY changes. Update `Version_History.md` with dates for all changes.

## App Overview
- **Stack**: Flask + SQLite + Jinja2 templates + Bootstrap
- **Purpose**: Track diet, symptoms, identify FODMAP/histamine food triggers
- **Launch**: `python app.py`

## Structure
```
templates/
├── dashboard/    # Main landing (/)
├── foods/        # Food guide (/foods) - index, search, detail, add-food, edit-food
├── diary/        # Logging (/diary) - calendar, day view, entry forms
├── recipes/      # Recipes & meals (/recipes)
├── education/    # Educational content (/education) - markdown support
└── settings/     # Config (/settings) - backup, tags, help documents
    └── help/     # Help & Support (/settings/help) - FAQs, tips, navigation guides
```

## Color Scheme
| Color | Hex/Value | Usage |
|-------|-----------|-------|
| Sage Green | #8BA48B | Primary, sidebar gradient start |
| Dark Green | #677D6A | Sidebar gradient end |
| Beige/Gold | #D6BD98 | Secondary, header, accents |
| Dark Green | #1A3636 | Text/emphasis, Quick Actions buttons, moderate risk container bg |
| Olive Green | #40534C (`--bg-elevated`) | Card backgrounds, Watch List container bg |
| Traffic Lights | #28a745 / #ffc107 / #dc3545 | Green/Amber/Red ratings |

### CSS Variables (in `static/css/main.css`)
| Variable | Hex | Usage |
|----------|-----|-------|
| `--bg-deep` | #1A3636 | Page background, Quick Actions buttons |
| `--bg-elevated` | #40534C | Cards, elevated containers, Watch List box (olive green) |
| `--sage` | #677D6A | Muted text, sidebar gradient end |
| `--gold` | #D6BD98 | Accents, links, highlights, date header text |
| `--white-ish` | #e0e7e1 | Primary text color |

### Opacity Variations Used
| Base Color | RGBA | Usage |
|------------|------|-------|
| Gold (#D6BD98) | `rgba(214, 189, 152, 0.5)` | Section title borders |
| Gold (#D6BD98) | `rgba(214, 189, 152, 0.15)` | Sidebar nav hover |
| Gold (#D6BD98) | `rgba(214, 189, 152, 0.1)` | Watch item hover |
| White | `rgba(255, 255, 255, 0.5)` | Watch item row backgrounds |
| White | `rgba(255, 255, 255, 0.4)` | Sidebar section title border |
| White | `rgba(255, 255, 255, 0.3)` | Sidebar separator |
| White | `rgba(255, 255, 255, 0.25)` | Nav icon circles |
| White | `rgba(255, 255, 255, 0.2)` | Thin separator in Quick Actions |
| White | `rgba(255, 255, 255, 0.08)` | Watch list box border |
| Red (#dc3545) | `rgba(220, 53, 69, 0.16)` | High Risk container background |
| Red (#dc3545) | `rgba(220, 53, 69, 0.3)` | High Risk header border |
| Amber (#ffc107) | `rgba(255, 193, 7, 0.06)` | Moderate Risk container background |
| Amber (#ffc107) | `rgba(255, 193, 7, 0.3)` | Moderate Risk header border |
| Dark Green (#1A3636) | `rgba(26, 54, 54, 0.3)` | Outline button hover |

## Global Layout Pattern
All pages follow this structure:
- **Header**: Sticky beige bar (50px height), centered title
- **Sidebar** (fixed): Green gradient, `position: fixed`, `width: 200px`, `height: calc(100vh - 50px)`, `top: 50px`, `left: 0`, padding: 12px, 7 nav links (Dashboard, Food Guide, Diary, Recipes, Education, Settings, Help & Support), action buttons below separator
- **Main Content**: `margin-left: 200px`, `padding-left: 15px` (gap between sidebar and content)
- **Content Width Constraint** (col-md-9): Wrap main content in `<div class="row"><div class="col-md-9">` to match dashboard width (~75% of main area)
- **Row Container**: `margin-top: -1.5rem` pulls content up to meet header
- **No Spacer Divs**: Alignment handled by negative margin

### Sidebar CSS (`.sidebar-column`)
```css
position: fixed;
top: 50px;
left: 0;
width: 200px;
height: calc(100vh - 50px);
background: linear-gradient(135deg, #8BA48B, #677D6A);
overflow-y: auto;
z-index: 100;
```

### Main Content CSS (`.main-content-area`)
```css
padding-left: 15px;
margin-left: 200px;
```

### Layout Width Breakdown
```
Sidebar:        200px fixed width (no Bootstrap cols)
Main Area:      margin-left: 200px + 15px padding (no Bootstrap cols)
Content Width:  col-md-9 within main area (constrains content to ~75% width)
```

## 📐 Dashboard Reference Template
**USE THIS AS THE MASTER REFERENCE** for layout and styling. File: `templates/dashboard/index.html`

### Fixed Header (in base.html)
```html
<header style="position: fixed !important; top: 0 !important; left: 0 !important;
    right: 0 !important; height: 50px !important; min-height: 50px !important;
    z-index: 1000 !important; background-color: #D6BD98 !important;
    display: flex !important; align-items: center !important; padding: 0 1rem !important;">
    <a href="..." style="color: #1A3636 !important; font-size: 1.4rem !important;
        font-weight: 700; text-decoration: none;">
        <i class="bi bi-heart-pulse"></i> Gut Health App
    </a>
</header>
```
- **DO NOT** use Bootstrap `.navbar` class (causes conflicts)
- Body needs `padding-top: 50px` to account for fixed header

### Fixed Sidebar (200px)
```css
.sidebar-column {
    position: fixed;
    top: 50px;
    left: 0;
    width: 200px;
    height: calc(100vh - 50px);
    background: linear-gradient(135deg, #8BA48B, #677D6A);
    z-index: 100;
}
```

### Fixed Main Content Area (1000px)
```css
.main-content-area {
    margin-left: 200px;
    width: 1000px;
    max-width: 1000px;
}
```

### Fixed Content Column (750px)
```css
.dashboard-content-col {
    width: 750px !important;
    min-width: 750px !important;
    max-width: 750px !important;
    flex: 0 0 750px !important;
}
```

### Wallpaper Background
```css
.dashboard-main-bg::before {
    content: "";
    position: fixed;
    top: 50px;
    left: 0;
    right: 0;      /* NOT width: 100vw */
    bottom: 0;
    background-image: linear-gradient(rgba(26, 54, 54, 0.35), rgba(26, 54, 54, 0.35)),
        url("...");
    background-size: cover;
    background-position: right bottom;
    z-index: 0;
    pointer-events: none;
}
```

### Layout Dimensions Summary
```
┌─────────────────────────────────────────────────────────┐
│  HEADER (fixed, 50px height, z-index: 1000, beige)      │
├────────────┬────────────────────────────────────────────┤
│            │                                            │
│  SIDEBAR   │   MAIN CONTENT AREA (1000px)              │
│  (200px)   │   ┌──────────────────────┐                │
│  fixed     │   │ CONTENT COL (750px)  │  wallpaper     │
│  z:100     │   │                      │  shows here    │
│            │   └──────────────────────┘                │
│            │                                            │
└────────────┴────────────────────────────────────────────┘
```

## Fixed Layout Rules (No Responsive)
**IMPORTANT**: No horizontal scrollbars, no responsive breakpoints.

### Key Rules
- **No min-width constraints** - Never use `min-width` on html, body, main, or containers
- **No 100vw** - Never use `width: 100vw` (causes overflow). Use `right: 0` instead
- **overflow-x: hidden** - Set on both `html` and `body` in main.css
- **Fixed pixel widths** - Use exact pixel values, not percentages

### What NOT to Do
- ❌ `min-width: 1200px` on html/body/main
- ❌ `width: 100vw` (use `left: 0; right: 0` instead)
- ❌ `overflow-x: auto` (use `overflow-x: hidden`)
- ❌ Percentage-based column widths like `col-md-9` for main content
- ❌ Bootstrap `.navbar` class on the header (use plain `<header>` tag)

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
- **Serving Sizes**: Safe (green), Moderate (amber), High (red) - each has independent FODMAP/histamine ratings
- **Histamine**: Level (Low/Med/High), DAO Blocker (Y/N), Liberator (Y/N)
- **Traffic Light**: Calculated from worst rating across all types
- **Packaged Foods**: Foods with nutritional info but no serving sizes (safe/moderate/high)
  - Serving type sections hidden on detail page when no serving sizes exist
  - "Add to Diary" UI appears in Nutrition Information header (text input + button)
  - Custom serving quantity (e.g., "2 servings", "150g") entered as free text
  - Uses existing add_meal route with empty serving_type

## Design Rules
- Compact sizing: btn-sm, 10px card padding, mb-2/mb-3 margins
- Lists: Alphabetical, single-line
- Buttons in sidebar: Full width, vertically stacked, below separator line
- CSS/JS: Inline in templates (current pattern)
- Files: kebab-case; Python: snake_case

## Development Checklist
1. Read this file first
2. Update `Version_History.md` with date and details
3. Follow color scheme and typography tokens
4. Keep all 6 nav links in every sidebar
5. Test at 100% zoom for compact appearance


## 🗓️ New Chat Prompt
"Please read CLAUDE.md to understand my app fully before making changes. Update this file to reflect any changes so you can better understand my app next time."
