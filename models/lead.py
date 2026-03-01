from extensions import db
from datetime import datetime


class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    niche = db.Column(db.String(100))
    source = db.Column(db.String(50))  # Instagram, Cold DM, Referral, etc.
    feedback = db.Column(db.Text)
    interest_level = db.Column(db.String(20))  # Hot, Warm, Cold
    next_action = db.Column(db.String(200))
    expected_value = db.Column(db.Float, default=0.0)
    follow_up_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Negotiating')  # Negotiating, Closed, Not Interested
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__( self ):
        return f'<Lead {self.name}>'