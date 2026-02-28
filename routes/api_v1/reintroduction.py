"""
Reintroduction Protocol API Endpoints
For FODMAP reintroduction testing and tolerance evaluation
"""

from flask import request, jsonify
from . import bp
from database import db
from models.reintroduction import ReintroductionProtocol, ReintroductionSchedule
from models.diary import DiaryEntry, Symptom
from utils.api_helpers import success_response, error_response, validation_error
from utils.auth import require_api_key, require_scope
from datetime import date, timedelta


@bp.route('/reintroduction/protocol', methods=['POST'])
@require_api_key
@require_scope('write:reintroduction')
def create_reintroduction_protocol():
    """
    Create a FODMAP reintroduction protocol
    Auto-generates standard schedule: days 1-3 (small), 4-6 (medium), 7-9 (large), 10-14 (washout)
    """
    data = request.get_json()
    if not data:
        return validation_error('Request body required')

    if not data.get('fodmap_category') or not data.get('start_date'):
        return validation_error('fodmap_category and start_date are required')

    try:
        start_date = date.fromisoformat(data['start_date']) if isinstance(data['start_date'], str) else data['start_date']

        # Create protocol
        protocol = ReintroductionProtocol(
            fodmap_category=data['fodmap_category'],
            status='active',
            start_date=start_date,
            notes=data.get('notes')
        )
        db.session.add(protocol)
        db.session.flush()  # Get the ID

        # Generate standard schedule
        schedules = []
        day_num = 1

        # Days 1-3: small dose
        for i in range(3):
            s = ReintroductionSchedule(
                protocol_id=protocol.id,
                day_number=day_num,
                scheduled_date=start_date + timedelta(days=i),
                dose_size='small',
                dose_description='Small test dose'
            )
            schedules.append(s)
            day_num += 1

        # Days 4-6: medium dose
        for i in range(3):
            s = ReintroductionSchedule(
                protocol_id=protocol.id,
                day_number=day_num,
                scheduled_date=start_date + timedelta(days=3+i),
                dose_size='medium',
                dose_description='Medium test dose'
            )
            schedules.append(s)
            day_num += 1

        # Days 7-9: large dose
        for i in range(3):
            s = ReintroductionSchedule(
                protocol_id=protocol.id,
                day_number=day_num,
                scheduled_date=start_date + timedelta(days=6+i),
                dose_size='large',
                dose_description='Large test dose'
            )
            schedules.append(s)
            day_num += 1

        # Days 10-14: washout period
        for i in range(5):
            s = ReintroductionSchedule(
                protocol_id=protocol.id,
                day_number=day_num,
                scheduled_date=start_date + timedelta(days=9+i),
                dose_size=None,
                dose_description='Washout period - avoid FODMAP category'
            )
            schedules.append(s)
            day_num += 1

        db.session.add_all(schedules)
        db.session.commit()

        return success_response({
            'protocol_id': protocol.id,
            'fodmap_category': protocol.fodmap_category,
            'status': protocol.status,
            'start_date': protocol.start_date.isoformat(),
            'schedule_count': len(schedules),
            'schedule': [s.to_dict() for s in schedules]
        }, message='Protocol created with auto-generated schedule', status=201)

    except ValueError as e:
        db.session.rollback()
        return validation_error(f'Invalid date format: {str(e)}')
    except Exception as e:
        db.session.rollback()
        return error_response(str(e))


@bp.route('/reintroduction/schedule', methods=['GET'])
@require_api_key
@require_scope('read:reintroduction')
def get_reintroduction_schedule():
    """Get reintroduction schedule for a protocol"""
    protocol_id = request.args.get('protocol_id', type=int)
    if not protocol_id:
        return validation_error('protocol_id is required')

    protocol = ReintroductionProtocol.query.get(protocol_id)
    if not protocol:
        return error_response(f'Protocol {protocol_id} not found', code='NOT_FOUND', status=404)

    schedules = protocol.schedules.order_by(ReintroductionSchedule.day_number).all()

    return success_response({
        'protocol_id': protocol.id,
        'fodmap_category': protocol.fodmap_category,
        'status': protocol.status,
        'start_date': protocol.start_date.isoformat(),
        'schedule': [s.to_dict() for s in schedules],
        'total_days': len(schedules)
    })


@bp.route('/reintroduction/evaluate', methods=['POST'])
@require_api_key
@require_scope('write:reintroduction')
def evaluate_reintroduction():
    """
    Evaluate reintroduction outcomes based on logged symptoms
    Classifies tolerance: no symptoms = 'tolerated', mild = 'partial', moderate/severe = 'avoid'
    """
    data = request.get_json()
    if not data:
        return validation_error('Request body required')

    protocol_id = data.get('protocol_id')
    if not protocol_id:
        return validation_error('protocol_id is required')

    protocol = ReintroductionProtocol.query.get(protocol_id)
    if not protocol:
        return error_response(f'Protocol {protocol_id} not found', code='NOT_FOUND', status=404)

    try:
        schedules = protocol.schedules.all()
        day_results = []
        symptom_count = 0

        for schedule in schedules:
            if schedule.diary_entry_id:
                entry = DiaryEntry.query.get(schedule.diary_entry_id)
                if entry:
                    symptoms = Symptom.query.filter_by(diary_entry_id=entry.id).first()
                    if symptoms:
                        total_score = sum([
                            getattr(symptoms, field, 0) or 0
                            for field in ['bloating', 'pain', 'wind', 'nausea', 'heartburn', 'headache', 'brain_fog', 'fatigue', 'sinus_issues']
                        ])
                        symptom_count += total_score

                        verdict = 'tolerated' if total_score == 0 else ('partial' if total_score <= 15 else 'avoid')
                        day_results.append({
                            'day_number': schedule.day_number,
                            'dose_size': schedule.dose_size,
                            'symptom_score': total_score,
                            'verdict': verdict
                        })

        # Overall verdict
        if symptom_count == 0:
            overall_verdict = 'tolerated'
            recommendation = f"Food containing {protocol.fodmap_category} appears to be well-tolerated."
        elif symptom_count <= 20:
            overall_verdict = 'partial'
            recommendation = f"Moderate reaction to {protocol.fodmap_category}. Consider limiting portions."
        else:
            overall_verdict = 'avoid'
            recommendation = f"Significant reaction to {protocol.fodmap_category}. Recommend avoidance."

        # Update protocol status
        protocol.status = 'completed'
        db.session.commit()

        return success_response({
            'protocol_id': protocol.id,
            'fodmap_category': protocol.fodmap_category,
            'overall_verdict': overall_verdict,
            'total_symptom_score': symptom_count,
            'day_results': day_results,
            'recommendation': recommendation
        }, message='Evaluation complete')

    except Exception as e:
        return error_response(str(e))
