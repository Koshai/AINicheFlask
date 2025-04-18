# reset_db.py
from app import create_app, db
import os

app = create_app()

with app.app_context():
    # Check if database file exists and delete it
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Create all tables
    db.create_all()
    print("✅ Database recreated with updated schema!")