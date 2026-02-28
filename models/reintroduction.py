"""
Reintroduction Protocol Models
For managing FODMAP reintroduction protocols and schedules
"""

from database import db
from datetime import datetime, date


class ReintroductionProtocol(db.Model):
    """Represents a FODMAP reintroduction protocol"""
    __tablename__ = 'reintroduction_protocols'

    id = db.Column(db.Integer, primary_key=True)
    fodmap_category = db.Column(db.String(50), nullable=False)  # e.g., 'Fructans', 'Lactose'
    status = db.Column(db.String(20), default='active')  # 'active', 'completed', 'paused'
    start_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    schedules = db.relationship('ReintroductionSchedule', backref='protocol',
                                cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        """Serialize protocol to dictionary"""
        return {
            'id': self.id,
            'fodmap_category': self.fodmap_category,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'schedule_count': self.schedules.count()
        }


class ReintroductionSchedule(db.Model):
    """Represents a day in a reintroduction schedule"""
    __tablename__ = 'reintroduction_schedules'

    id = db.Column(db.Integer, primary_key=True)
    protocol_id = db.Column(db.Integer, db.ForeignKey('reintroduction_protocols.id'), nullable=False)
    day_number = db.Column(db.Integer)  # Day 1, 2, 3...
    scheduled_date = db.Column(db.Date, nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey('foods.id'), nullable=True)
    dose_description = db.Column(db.String(200))  # e.g., "1/2 cup milk"
    dose_size = db.Column(db.String(50))  # 'small', 'medium', 'large'
    diary_entry_id = db.Column(db.Integer, db.ForeignKey('diary_entries.id'), nullable=True)
    reaction_noted = db.Column(db.Boolean, default=False)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    food = db.relationship('Food', backref='reintroduction_schedules')
    diary_entry = db.relationship('DiaryEntry', backref='reintroduction_schedules')

    def to_dict(self):
        """Serialize schedule to dictionary"""
        return {
            'id': self.id,
            'protocol_id': self.protocol_id,
            'day_number': self.day_number,
            'scheduled_date': self.scheduled_date.isoformat() if self.scheduled_date else None,
            'food_id': self.food_id,
            'food_name': self.food.name if self.food else None,
            'dose_description': self.dose_description,
            'dose_size': self.dose_size,
            'diary_entry_id': self.diary_entry_id,
            'reaction_noted': self.reaction_noted,
            'completed': self.completed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
