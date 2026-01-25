# Quick Start Guide

## Installation

### 1. Check Python
```bash
python --version
```
Requires Python 3.10 or higher.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the App
```bash
python app.py
```

### 4. Open Browser
Go to: **http://localhost:5000**

## Using the App

### Navigation
- **Dashboard** - Overview and quick actions
- **Food Guide** - Search foods, view FODMAP/histamine ratings
- **Diary** - Log meals, symptoms, and daily tracking
- **Recipes** - Save and manage gut-friendly recipes
- **Education** - Learn about gut health topics
- **Settings** - Backup data, manage tags, get help

### Daily Workflow
1. Log your meals in the **Diary** section
2. Record any symptoms throughout the day
3. Check the **Food Guide** before trying new foods
4. Review your patterns in the weekly/monthly views

## Common Tasks

### Search for a Food
1. Go to **Food Guide**
2. Type the food name in the search box
3. Click on a food to see full FODMAP and histamine details

### Log a Meal
1. Go to **Diary**
2. Click **Add Meal**
3. Select foods and serving sizes
4. Save the entry

### Backup Your Data
1. Go to **Settings**
2. Click **Backup Database**
3. Your data is saved to the `backups/` folder

## Troubleshooting

### Port Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, port=5001)
```

### Database Reset
Delete `instance/gut_health.db` and restart the app. A fresh database will be created.

### Missing Module Error
```bash
pip install -r requirements.txt
```

## Stopping the App
Press `Ctrl+C` in the terminal.
