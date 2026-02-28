from database import db
from datetime import datetime

class UserPreference(db.Model):
    """User preferences and settings"""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<UserPreference {self.key}>'

    def to_dict(self):
        """Convert user preference to dictionary"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class SavedRecipe(db.Model):
    """Saved recipes from LLM chat"""
    __tablename__ = 'saved_recipes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)

    notes = db.Column(db.Text)
    tags = db.Column(db.String(500))  # Comma-separated

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<SavedRecipe {self.title}>'

    def to_dict(self):
        """Convert saved recipe to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'ingredients': self.ingredients,
            'instructions': self.instructions,
            'notes': self.notes,
            'tags': [t.strip() for t in self.tags.split(',') if t.strip()] if self.tags else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class NotificationRule(db.Model):
    """Automated notification trigger rules"""
    __tablename__ = 'notification_rules'

    id = db.Column(db.Integer, primary_key=True)
    trigger = db.Column(db.String(50), nullable=False)  # 'no_log_by_time', 'high_symptom', etc.
    condition = db.Column(db.JSON)  # JSON dict: {"time": "20:00", "days": ["Mon","Tue",...]}
    channel = db.Column(db.String(20))  # 'in_app', 'email', 'sms', 'push'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<NotificationRule {self.trigger}>'

    def to_dict(self):
        """Convert notification rule to dictionary"""
        return {
            'id': self.id,
            'trigger': self.trigger,
            'condition': self.condition,
            'channel': self.channel,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
