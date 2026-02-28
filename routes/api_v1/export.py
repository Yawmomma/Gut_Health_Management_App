"""
Export & Reporting API v1 Endpoints
Provides data export and report generation capabilities
"""

from flask import request, jsonify, Response
from datetime import datetime, timedelta
from . import bp
from database import db
from models.diary import DiaryEntry, Meal, Symptom, BowelMovement, StressLog, Note, MealFood
from models.recipe import Recipe, RecipeIngredient
from collections import defaultdict
from utils.validators import validate_date_range, validate_optional_enum, ValidationError
from utils.auth import require_api_key, require_scope
from sqlalchemy.orm import joinedload
import csv
import io


# =============================================================================
# PHASE 3: EXPORT & REPORTING ENDPOINTS
# =============================================================================

@bp.route('/export/diary', methods=['GET'])
@require_api_key
@require_scope('read:export')
def export_diary():
    """
    GET /api/v1/export/diary?start_date=2026-01-01&end_date=2026-01-31&format=json
    Complete diary export in JSON or CSV format

    Query Parameters:
    - start_date: Start date (YYYY-MM-DD, required)
    - end_date: End date (YYYY-MM-DD, required)
    - format: Export format (json or csv, default: json)
    - types: Comma-separated entry types (optional, default: all)
      Options: meal, symptom, bowel, stress, note

    Returns (JSON):
    {
        "date_range": {"start": "2026-01-01", "end": "2026-01-31"},
        "format": "json",
        "entries": [
            {
                "date": "2026-01-01",
                "type": "meal",
                "data": {...}
            },
            ...
        ],
        "total_entries": 45,
        "exported_at": "2026-02-12T10:30:00"
    }

    Returns (CSV):
    CSV file download with all diary entries flattened
    """
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        types_str = request.args.get('types', '').strip()

        # Validate date range
        if not start_date_str or not end_date_str:
            return jsonify({'error': 'start_date and end_date are required (YYYY-MM-DD)'}), 400

        try:
            start_date_str, end_date_str = validate_date_range(start_date_str, end_date_str)
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Validate format
        try:
            export_format = validate_optional_enum(
                request.args.get('format'),
                ['json', 'csv'],
                field_name='format',
                default='json'
            )
        except ValidationError as e:
            return jsonify({'error': str(e)}), 400

        # Parse types to export
        all_types = ['meal', 'symptom', 'bowel', 'stress', 'note']
        if types_str:
            types_to_export = [t.strip() for t in types_str.split(',') if t.strip() in all_types]
        else:
            types_to_export = all_types

        # Get all diary entries in date range (with eager loading to prevent N+1 queries)
        query = DiaryEntry.query.options(
            joinedload(DiaryEntry.meals).joinedload(Meal.meal_foods).joinedload(MealFood.food),
            joinedload(DiaryEntry.symptoms),
            joinedload(DiaryEntry.bowel_movements),
            joinedload(DiaryEntry.stress_logs),
            joinedload(DiaryEntry.notes)
        ).filter(
            DiaryEntry.entry_date >= start_date,
            DiaryEntry.entry_date <= end_date
        )

        if types_to_export != all_types:
            query = query.filter(DiaryEntry.entry_type.in_(types_to_export))

        entries = query.order_by(DiaryEntry.entry_date, DiaryEntry.entry_time).all()

        # Build export data
        export_data = []

        for entry in entries:
            entry_dict = {
                'id': entry.id,
                'date': entry.entry_date.isoformat(),
                'time': entry.entry_time.strftime('%H:%M') if entry.entry_time else None,
                'type': entry.entry_type
            }

            # Add type-specific data
            if entry.entry_type == 'meal' and entry.meals:
                for meal in entry.meals:
                    meal_dict = entry_dict.copy()
                    meal_dict['meal_type'] = meal.meal_type
                    meal_dict['location'] = meal.location
                    meal_dict['preparation'] = meal.preparation
                    meal_dict['notes'] = meal.notes
                    # Sum nutrition from meal_foods (Meal has no nutrition fields)
                    meal_dict['total_energy_kj'] = round(sum(mf.energy_kj or 0 for mf in meal.meal_foods), 1)
                    meal_dict['total_protein_g'] = round(sum(mf.protein_g or 0 for mf in meal.meal_foods), 1)
                    meal_dict['total_carbs_g'] = round(sum(mf.carbs_g or 0 for mf in meal.meal_foods), 1)
                    meal_dict['total_fat_g'] = round(sum(mf.fat_g or 0 for mf in meal.meal_foods), 1)
                    meal_dict['total_sodium_mg'] = round(sum(mf.sodium_mg or 0 for mf in meal.meal_foods), 1)

                    # Add foods
                    foods_list = []
                    for mf in meal.meal_foods:
                        if mf.food:
                            foods_list.append({
                                'food_name': mf.food.name,
                                'portion_size': mf.portion_size,
                                'serving_type': mf.serving_type
                            })
                    meal_dict['foods'] = foods_list
                    export_data.append(meal_dict)

            elif entry.entry_type == 'symptom' and entry.symptoms:
                for symptom in entry.symptoms:
                    symptom_dict = entry_dict.copy()
                    symptom_dict['bloating'] = symptom.bloating
                    symptom_dict['pain'] = symptom.pain
                    symptom_dict['wind'] = symptom.wind
                    symptom_dict['nausea'] = symptom.nausea
                    symptom_dict['heartburn'] = symptom.heartburn
                    symptom_dict['headache'] = symptom.headache
                    symptom_dict['brain_fog'] = symptom.brain_fog
                    symptom_dict['fatigue'] = symptom.fatigue
                    symptom_dict['sinus_issues'] = symptom.sinus_issues
                    symptom_dict['severity'] = symptom.severity
                    symptom_dict['duration'] = symptom.duration
                    symptom_dict['notes'] = symptom.notes
                    export_data.append(symptom_dict)

            elif entry.entry_type == 'bowel' and entry.bowel_movements:
                for bowel in entry.bowel_movements:
                    bowel_dict = entry_dict.copy()
                    bowel_dict['bristol_type'] = bowel.bristol_type
                    bowel_dict['urgency'] = bowel.urgency
                    bowel_dict['completeness'] = bowel.completeness
                    bowel_dict['straining'] = bowel.straining
                    bowel_dict['blood_present'] = bowel.blood_present
                    bowel_dict['mucus_present'] = bowel.mucus_present
                    bowel_dict['color'] = bowel.color
                    bowel_dict['notes'] = bowel.notes
                    export_data.append(bowel_dict)

            elif entry.entry_type == 'stress' and entry.stress_logs:
                for stress in entry.stress_logs:
                    stress_dict = entry_dict.copy()
                    stress_dict['stress_level'] = stress.stress_level
                    stress_dict['stress_types'] = stress.stress_types
                    stress_dict['physical_symptoms'] = stress.physical_symptoms
                    stress_dict['management_actions'] = stress.management_actions
                    stress_dict['duration_status'] = stress.duration_status
                    stress_dict['notes'] = stress.notes
                    export_data.append(stress_dict)

            elif entry.entry_type == 'note' and entry.notes:
                for note in entry.notes:
                    note_dict = entry_dict.copy()
                    note_dict['title'] = note.title
                    note_dict['content'] = note.content
                    export_data.append(note_dict)

        # Export based on format
        if export_format == 'json':
            return jsonify({
                'date_range': {
                    'start': start_date_str,
                    'end': end_date_str
                },
                'format': 'json',
                'types': types_to_export,
                'entries': export_data,
                'total_entries': len(export_data),
                'exported_at': datetime.now().isoformat()
            })

        else:  # CSV format
            # Create CSV
            output = io.StringIO()

            if len(export_data) > 0:
                # Get all unique keys for CSV columns
                all_keys = set()
                for item in export_data:
                    # Flatten foods list if present
                    if 'foods' in item and isinstance(item['foods'], list):
                        item['foods'] = '; '.join([f"{f['food_name']} ({f['portion_size']})" for f in item['foods']])
                    all_keys.update(item.keys())

                writer = csv.DictWriter(output, fieldnames=sorted(all_keys))
                writer.writeheader()
                writer.writerows(export_data)

            csv_content = output.getvalue()
            output.close()

            # Return as downloadable file
            filename = f"diary_export_{start_date_str}_to_{end_date_str}.csv"
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment;filename={filename}'}
            )

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/export/report/pdf', methods=['GET'])
@require_api_key
@require_scope('read:export')
def export_pdf_report():
    """
    GET /api/v1/export/report/pdf?type=monthly&date=2026-02
    Generate PDF report with charts and summary

    NOTE: This endpoint requires additional libraries (reportlab or weasyprint)
    which are not currently installed. This is a placeholder implementation.

    Query Parameters:
    - type: Report type (monthly or weekly, default: monthly)
    - date: Date for report (YYYY-MM for monthly, YYYY-MM-DD for weekly)

    Returns:
    PDF file download with:
    - Summary statistics
    - Charts (symptom trends, nutrition breakdown, etc.)
    - Entry listings

    Status: NOT IMPLEMENTED (501)
    Reason: Requires reportlab/weasyprint library installation
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
        from reportlab.lib.enums import TA_CENTER

        report_type = request.args.get('type', 'monthly').lower()
        date_str = request.args.get('date', '').strip()

        if not date_str:
            return jsonify({'error': 'date parameter is required'}), 400

        if report_type not in ['monthly', 'weekly']:
            return jsonify({'error': 'type must be "monthly" or "weekly"'}), 400

        # Parse date
        try:
            if report_type == 'monthly':
                date_obj = datetime.strptime(date_str, '%Y-%m')
                start_date = date_obj.replace(day=1).date()
                # Get last day of month
                if date_obj.month == 12:
                    end_date = date_obj.replace(year=date_obj.year + 1, month=1, day=1).date() - timedelta(days=1)
                else:
                    end_date = date_obj.replace(month=date_obj.month + 1, day=1).date() - timedelta(days=1)
                report_title = f"Monthly Health Report - {date_obj.strftime('%B %Y')}"
            else:  # weekly
                start_date = datetime.strptime(date_str, '%Y-%m-%d').date()
                end_date = start_date + timedelta(days=6)
                report_title = f"Weekly Health Report - {start_date.isoformat()} to {end_date.isoformat()}"
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM for monthly or YYYY-MM-DD for weekly'}), 400

        # Get all entries in date range
        entries = DiaryEntry.query.filter(
            DiaryEntry.entry_date >= start_date,
            DiaryEntry.entry_date <= end_date
        ).order_by(DiaryEntry.entry_date, DiaryEntry.entry_time).all()

        # Create PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

        # Container for PDF elements
        elements = []
        styles = getSampleStyleSheet()

        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1A3636'),
            spaceAfter=30,
            alignment=TA_CENTER
        )

        # Add title
        elements.append(Paragraph(report_title, title_style))
        elements.append(Spacer(1, 0.2*inch))

        # Add metadata
        elements.append(Paragraph(f"<b>Report Period:</b> {start_date.isoformat()} to {end_date.isoformat()}", styles['Normal']))
        elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
        elements.append(Spacer(1, 0.3*inch))

        # Summary statistics
        meal_count = sum(1 for e in entries if e.entry_type == 'meal')
        symptom_count = sum(1 for e in entries if e.entry_type == 'symptom')
        bowel_count = sum(1 for e in entries if e.entry_type == 'bowel')
        stress_count = sum(1 for e in entries if e.entry_type == 'stress')
        note_count = sum(1 for e in entries if e.entry_type == 'note')

        # Summary section
        elements.append(Paragraph("<b>Entry Summary</b>", styles['Heading2']))
        summary_data = [
            ['Entry Type', 'Count'],
            ['Meals Logged', str(meal_count)],
            ['Symptoms', str(symptom_count)],
            ['Bowel Movements', str(bowel_count)],
            ['Stress Logs', str(stress_count)],
            ['Notes', str(note_count)],
            ['<b>Total Entries</b>', f'<b>{len(entries)}</b>']
        ]

        summary_table = Table(summary_data, colWidths=[3.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A3636')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#D6BD98')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -2), colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#E8E8E8')),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey)
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.4*inch))

        # Symptom summary
        if symptom_count > 0:
            elements.append(Paragraph("<b>Symptom Analysis</b>", styles['Heading2']))
            symptom_field_names = ['bloating', 'pain', 'wind', 'nausea', 'heartburn',
                                   'headache', 'brain_fog', 'fatigue', 'sinus_issues']
            symptom_types = defaultdict(int)
            total_severity = 0
            severity_count = 0

            for entry in entries:
                if entry.entry_type == 'symptom' and entry.symptoms:
                    for symptom in entry.symptoms:
                        # Count which symptom fields were elevated (>0)
                        for field in symptom_field_names:
                            val = getattr(symptom, field, 0) or 0
                            if val > 0:
                                symptom_types[field] += 1
                                total_severity += val
                                severity_count += 1

            symptom_data = [['Symptom Type', 'Occurrences']]
            for symptom_type, count in sorted(symptom_types.items(), key=lambda x: x[1], reverse=True):
                symptom_data.append([symptom_type.replace('_', ' ').capitalize(), str(count)])

            if severity_count > 0:
                avg_severity = round(total_severity / severity_count, 1)
                symptom_data.append(['<b>Average Severity</b>', f'<b>{avg_severity}/10</b>'])

            symptom_table = Table(symptom_data, colWidths=[3.5*inch, 1.5*inch])
            symptom_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1A3636')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#D6BD98')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey)
            ]))
            elements.append(symptom_table)
            elements.append(Spacer(1, 0.3*inch))

        # Daily entries (show up to 50)
        if len(entries) > 0:
            elements.append(PageBreak())
            elements.append(Paragraph("<b>Daily Entries Log</b>", styles['Heading2']))
            elements.append(Spacer(1, 0.2*inch))

            entries_to_show = entries[:50]
            for entry in entries_to_show:
                date_text = f"<b>{entry.entry_date.strftime('%Y-%m-%d')}</b>"
                if entry.entry_time:
                    date_text += f" at {entry.entry_time.strftime('%H:%M')}"

                elements.append(Paragraph(f"{date_text} - {entry.entry_type.capitalize()}", styles['Heading3']))

                # Entry details
                if entry.entry_type == 'meal' and entry.meals:
                    for meal in entry.meals:
                        meal_text = f"<b>{meal.meal_type}</b>"
                        if meal.meal_foods:
                            foods_list = ', '.join([mf.food.name for mf in meal.meal_foods[:5] if mf.food])
                            if len(meal.meal_foods) > 5:
                                foods_list += f" (+{len(meal.meal_foods) - 5} more)"
                            meal_text += f": {foods_list}"
                        elements.append(Paragraph(meal_text, styles['Normal']))

                elif entry.entry_type == 'symptom' and entry.symptoms:
                    for symptom in entry.symptoms:
                        # Build text from elevated symptom fields
                        elevated = []
                        for field in symptom_field_names:
                            val = getattr(symptom, field, 0) or 0
                            if val > 0:
                                elevated.append(f"{field.replace('_', ' ')}: {val}/10")
                        symptom_text = ', '.join(elevated) if elevated else 'No symptoms recorded'
                        if symptom.severity:
                            symptom_text += f" (Overall: {symptom.severity})"
                        elements.append(Paragraph(symptom_text, styles['Normal']))

                elements.append(Spacer(1, 0.15*inch))

            if len(entries) > 50:
                elements.append(Paragraph(f"<i>Showing first 50 of {len(entries)} total entries. Use diary export for complete data.</i>", styles['Italic']))

        # Build PDF
        doc.build(elements)

        # Return PDF
        buffer.seek(0)
        filename = f"gut_health_report_{report_type}_{date_str.replace('-', '')}.pdf"

        return Response(
            buffer.getvalue(),
            mimetype='application/pdf',
            headers={'Content-Disposition': f'attachment;filename={filename}'}
        )

    except ImportError:
        return jsonify({
            'error': 'PDF generation library not available',
            'message': 'reportlab is not installed',
            'instructions': 'Install with: pip install reportlab==4.0.9'
        }), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/export/shopping-list', methods=['GET'])
@require_api_key
@require_scope('read:export')
def export_shopping_list():
    """
    GET /api/v1/export/shopping-list?recipe_ids=1,2,3&format=json
    Generate aggregated shopping list from recipes

    Query Parameters:
    - recipe_ids: Comma-separated recipe IDs (required)
    - format: Export format (json or text, default: json)

    Returns (JSON):
    {
        "recipes": [
            {"id": 1, "name": "Apple Pie"},
            {"id": 2, "name": "Chicken Salad"}
        ],
        "shopping_list": {
            "Fruit": [
                {"food": "Apple", "total_quantity": "6 medium", "recipes": ["Apple Pie"]},
                ...
            ],
            "Vegetables": [...],
            ...
        },
        "total_items": 15
    }

    Returns (TEXT):
    Plain text shopping list formatted by category
    """
    try:
        recipe_ids_str = request.args.get('recipe_ids', '').strip()
        export_format = request.args.get('format', 'json').lower()

        if not recipe_ids_str:
            return jsonify({'error': 'recipe_ids parameter is required (comma-separated list)'}), 400

        if export_format not in ['json', 'text']:
            return jsonify({'error': 'format must be "json" or "text"'}), 400

        # Parse recipe IDs
        try:
            recipe_ids = [int(id_str.strip()) for id_str in recipe_ids_str.split(',') if id_str.strip()]
        except ValueError:
            return jsonify({'error': 'Invalid recipe ID format. IDs must be integers'}), 400

        if len(recipe_ids) == 0:
            return jsonify({'error': 'At least one recipe ID must be provided'}), 400

        if len(recipe_ids) > 20:
            return jsonify({'error': 'Maximum 20 recipes per shopping list'}), 400

        # Get recipes
        recipes = Recipe.query.filter(Recipe.id.in_(recipe_ids)).all()
        if len(recipes) == 0:
            return jsonify({'error': 'No recipes found with provided IDs'}), 404

        # Build shopping list
        shopping_list = defaultdict(list)
        food_tracker = defaultdict(lambda: {
            'quantity_entries': [],
            'recipes': set()
        })

        recipe_info = []
        for recipe in recipes:
            recipe_info.append({
                'id': recipe.id,
                'name': recipe.name
            })

            # Get ingredients
            ingredients = RecipeIngredient.query.filter_by(recipe_id=recipe.id).all()

            for ingredient in ingredients:
                if not ingredient.food:
                    continue

                food = ingredient.food
                food_id = food.id

                # Track this food
                food_tracker[food_id]['name'] = food.name
                food_tracker[food_id]['category'] = food.category
                food_tracker[food_id]['quantity_entries'].append(ingredient.quantity)
                food_tracker[food_id]['recipes'].add(recipe.name)

        # Build organized shopping list by category
        for food_id, data in food_tracker.items():
            category = data['category']

            # Combine quantities (simple text concatenation for now)
            combined_quantity = ', '.join(data['quantity_entries'])

            shopping_list[category].append({
                'food': data['name'],
                'total_quantity': combined_quantity,
                'recipes': sorted(list(data['recipes']))
            })

        # Sort items within each category
        for category in shopping_list:
            shopping_list[category].sort(key=lambda x: x['food'])

        # Count total items
        total_items = sum(len(items) for items in shopping_list.values())

        # Export based on format
        if export_format == 'json':
            return jsonify({
                'recipes': recipe_info,
                'shopping_list': dict(shopping_list),
                'total_items': total_items,
                'generated_at': datetime.now().isoformat()
            })

        else:  # Text format
            text_lines = []
            text_lines.append('SHOPPING LIST')
            text_lines.append('=' * 50)
            text_lines.append('')
            text_lines.append(f'For recipes: {", ".join([r["name"] for r in recipe_info])}')
            text_lines.append('')

            for category in sorted(shopping_list.keys()):
                text_lines.append(f'\n{category.upper()}:')
                text_lines.append('-' * 50)
                for item in shopping_list[category]:
                    text_lines.append(f'  ☐ {item["food"]} - {item["total_quantity"]}')
                    if len(item['recipes']) > 1:
                        text_lines.append(f'     (used in: {", ".join(item["recipes"])})')

            text_lines.append('')
            text_lines.append(f'\nTotal items: {total_items}')
            text_lines.append(f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')

            text_content = '\n'.join(text_lines)

            return Response(
                text_content,
                mimetype='text/plain',
                headers={'Content-Disposition': 'attachment;filename=shopping_list.txt'}
            )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
