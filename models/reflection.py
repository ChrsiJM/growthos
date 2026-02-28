from app import db
from datetime import datetime


class Reflection(db.Model):
    __tablename__ = 'reflections'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(20))  # Weekly, Monthly
    wins = db.Column(db.Text)
    failures = db.Column(db.Text)
    lessons = db.Column(db.Text)
    next_focus = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__( self ):
        return f'<Reflection {self.type} {self.created_at.date()}>'