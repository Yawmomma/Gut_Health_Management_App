"""
Gamification Models
For challenges, badges, and engagement tracking
"""

from database import db
from datetime import datetime


class Challenge(db.Model):
    """Represents a user challenge"""
    __tablename__ = 'challenges'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))  # 'streak', 'variety', 'fodmap_free', etc.
    target = db.Column(db.Integer)  # e.g., 7 (days), 30 (unique plants)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    progress = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    badges = db.relationship('Badge', backref='challenge', cascade='all, delete-orphan')

    def to_dict(self):
        """Serialize challenge to dictionary"""
        pct_progress = 0
        if self.target and self.target > 0:
            pct_progress = min(100, int((self.progress / self.target) * 100))

        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'type': self.type,
            'target': self.target,
            'progress': self.progress,
            'progress_pct': pct_progress,
            'is_active': self.is_active,
            'completed': self.completed,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }


class Badge(db.Model):
    """Represents an earned badge/achievement"""
    __tablename__ = 'badges'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Bootstrap icon name, e.g., 'bi-star-fill'
    earned_at = db.Column(db.DateTime, nullable=False)
    challenge_id = db.Column(db.Integer, db.ForeignKey('challenges.id'), nullable=True)

    def to_dict(self):
        """Serialize badge to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'earned_at': self.earned_at.isoformat() if self.earned_at else None,
            'challenge_id': self.challenge_id
        }
