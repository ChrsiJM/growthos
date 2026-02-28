from app import db
from datetime import datetime


class WeeklyFinance(db.Model):
    __tablename__ = 'weekly_finances'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    week_start_date = db.Column(db.Date, nullable=False)
    week_end_date = db.Column(db.Date, nullable=False)
    income_source = db.Column(db.String(200))
    total_income = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    expense_description = db.Column(db.Text)
    review_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def remaining_balance( self ):
        return self.total_income - self.total_expenses

    def __repr__( self ):
        return f'<WeeklyFinance {self.week_start_date} - {self.week_end_date}>'