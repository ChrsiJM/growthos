from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
import os

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'

    # Import models
    from models import user, daily_plan, lead, project, idea, event, reflection, finance
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.planner import planner_bp
    from routes.leads import leads_bp
    from routes.projects import projects_bp
    from routes.ideas import ideas_bp
    from routes.meetings import meetings_bp
    from routes.reflections import reflections_bp
    from routes.finance import finance_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/')
    app.register_blueprint(planner_bp, url_prefix='/planner')
    app.register_blueprint(leads_bp, url_prefix='/leads')
    app.register_blueprint(projects_bp, url_prefix='/projects')
    app.register_blueprint(ideas_bp, url_prefix='/ideas')
    app.register_blueprint(meetings_bp, url_prefix='/meetings')
    app.register_blueprint(reflections_bp, url_prefix='/reflections')
    app.register_blueprint(finance_bp, url_prefix='/finance')

    # Create tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"⚠️ Database tables may already exist: {e}")

    return app

# For production with gunicorn
app = create_app()
