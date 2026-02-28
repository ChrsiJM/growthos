from app import db
from datetime import datetime


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.DateTime, nullable=False)
    reminder_note = db.Column(db.Text)
    linked_lead_id = db.Column(db.Integer, db.ForeignKey('leads.id'), nullable=True)
    linked_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    linked_lead = db.relationship('Lead', foreign_keys=[linked_lead_id])
    linked_project = db.relationship('Project', foreign_keys=[linked_project_id])

    @property
    def is_overdue( self ):
        return datetime.utcnow() > self.event_date

    def __repr__( self ):
        return f'<Event {self.title}>'