# robust_reset_db.py
import os
import sys
import sqlite3
from pathlib import Path

# Get the absolute path to the database file
app_root = Path(__file__).parent
instance_dir = app_root / 'instance'
db_path = instance_dir / 'nichegen.db'
alt_db_path = app_root / 'nichegen.db'

# Check both possible database locations
potential_paths = [db_path, alt_db_path]
found_db = None

for path in potential_paths:
    if path.exists():
        found_db = path
        print(f"Found database at: {path}")
        
        # Remove the database file
        try:
            os.remove(path)
            print(f"Successfully deleted database: {path}")
        except Exception as e:
            print(f"Error deleting database {path}: {e}")
            sys.exit(1)

if not found_db:
    print("No existing database found. Will create new one on app startup.")

print("\nNow manually restart the Flask application to create a fresh database.")
print("Then try registering again.")