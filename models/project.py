from extensions import db
from datetime import datetime


class Project(db.Model):
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))  # Startup, Client, Investment, Learning
    status = db.Column(db.String(20), default='Active')  # Active, Paused, Completed
    start_date = db.Column(db.Date)
    deadline = db.Column(db.Date)
    progress_percentage = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks = db.relationship('ProjectTask', backref='project', lazy='dynamic', cascade='all, delete-orphan')

    def update_progress( self ):
        total_tasks = self.tasks.count()
        if total_tasks > 0:
            completed_tasks = self.tasks.filter_by(status='Done').count()
            self.progress_percentage = int((completed_tasks / total_tasks) * 100)
        else:
            self.progress_percentage = 0
        db.session.commit()

    def __repr__( self ):
        return f'<Project {self.name}>'


class ProjectTask(db.Model):
    __tablename__ = 'project_tasks'

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='Pending')  # Pending, Done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__( self ):
        return f'<ProjectTask {self.title}>'