from app import db
from datetime import datetime


class Idea(db.Model):
    __tablename__ = 'ideas'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Business, Marketing, Product, Personal
    linked_project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    linked_project = db.relationship('Project', foreign_keys=[linked_project_id])

    def __repr__( self ):
        return f'<Idea {self.title}>'