from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session
from config import Config
import os

db = SQLAlchemy()
bcrypt = Bcrypt()
session = Session()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    session.init_app(app)
    
    # Configure CORS for production
    if os.environ.get('RAILWAY_ENVIRONMENT'):
        # Production CORS - will update this after deploying Blazor app
        CORS(app, origins=[
            "https://*.up.railway.app",  # Allow Railway subdomains
            "http://localhost:5152",     # Keep for local Blazor testing
            "https://localhost:7046"     # Keep for local Blazor testing
        ])
    else:
        # Development CORS
        CORS(app)
    
    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    with app.app_context():
        # Import middleware
        from .middleware import auth_middleware
        
        # Register blueprints
        from .routes import auth, generate
        app.register_blueprint(auth.bp)
        app.register_blueprint(generate.bp)
        
        # Register middleware
        app.before_request(auth_middleware.load_logged_in_user)

        # Import models and create tables
        from . import models
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")

    return app