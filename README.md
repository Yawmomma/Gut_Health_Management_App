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

### Daily Diary
- Log meals with specific foods and serving sizes
- Track symptoms with severity ratings
- Bristol Stool Chart for bowel movements
- Stress level monitoring
- General notes and observations
- Calendar view with daily summaries

### Recipes & Meals
- Save and organize gut-friendly recipes
- Create reusable meal templates
- Categorize by meal type and dietary requirements
- **Recipe Builder**: Search over 2 million recipes from an external database for inspiration
- **AI Recipe Helper**: Get AI-powered recipe suggestions tailored to your dietary needs (requires OpenAI API key)

### Educational Content
- Learn about FODMAPs, histamine, and gut health
- Markdown-supported articles
- Research paper references

### Settings & Data
- Backup and restore your data
- Customizable symptom tags
- Help documentation

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (local storage)
- **Frontend**: Jinja2 templates, Bootstrap 5, vanilla JavaScript
- **No external dependencies**: Everything runs locally

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

4. Run the application:
   ```bash
   python app.py
   ```

6. Open your browser and go to: **http://localhost:5000**

### Optional: AI Recipe Helper Setup

To use the AI Recipe Helper feature, you'll need an OpenAI API key:

1. Create a `.env` file in the project root
2. Add your API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

The AI helper will suggest recipes based on your dietary restrictions and available ingredients.

## Project Structure

```
Gut_Health_Management_App/
├── app.py                 # Main Flask application
├── config.py              # Configuration settings
├── models/                # Database models
├── routes/                # URL route handlers
│   └── recipe_builder.py  # Recipe Builder routes
├── templates/             # HTML templates
│   ├── dashboard/         # Main landing page
│   ├── foods/             # Food guide pages
│   ├── diary/             # Diary and tracking
│   ├── recipes/           # Recipe management (incl. builder)
│   ├── education/         # Educational content
│   └── settings/          # App settings & help
├── static/                # CSS, JavaScript, images
├── migrations/            # Database migration scripts
├── utils/                 # Utility modules
│   ├── recipe_parser.py   # Parse recipes from URLs
│   └── recipe_search.py   # External recipe database search
├── database/              # Database seeds
└── data/                  # User data storage
    └── recipes/external/  # External recipe database (download separately)
```

## Privacy

This app is designed for **local use only**. All your data stays on your computer in a SQLite database file. There are no accounts, no cloud sync, and no data collection.

To backup your data, simply copy the `gut_health.db` file from the `instance/` folder.

## License

This project is for personal use. Feel free to fork and modify for your own needs.

## Acknowledgments

Built with the help of Claude AI for code assistance and debugging.

---

## Changelog

### v1.1.0 (February 2026)
- **New**: Recipe Builder - search over 2 million external recipes for inspiration
- **New**: AI Recipe Helper - get personalized recipe suggestions (requires OpenAI API key)
- **New**: Recipe URL import - parse recipes from websites
- **New**: Chat persona support for AI helper
- **New**: Food completion tracking
- **Improved**: Recipes page redesigned with 2x2 grid layout
- **Improved**: UI improvements across all pages
- **Improved**: Help documentation with Quick Tips
- **Fixed**: Various bug fixes and styling updates

### v1.0.0 (Initial Release)
- Food Guide with FODMAP and histamine tracking
- Daily Diary for meals, symptoms, and observations
- Recipes & Meals management
- Educational content system
- Settings and backup functionality

---

**Version**: 1.1.0
