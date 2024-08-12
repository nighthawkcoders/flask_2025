#!/usr/bin/env python3


#
# WARNING:This script is deprecated.
#


""" db_init.py
Generates the database schema for all db models
- Initializes Users, Sections, and UserSections tables.
- Imports data from the old database to the new database.

Usage: Run from the terminal as such:

Goto the scripts directory:
> cd scriipts; ./db_init.py

Or run from the root of the project:
> scripts/db_init.py

Process outline:

1. New schema.  The schema is created in "this" new database.
2. Old data extraction.  An API has been created in the old project ...
  - Extract Data: retrieves data from the specified tables in the old database.
  - Transform Data: the API to JSON format understood by the new project.
3. Load Data: The bulk load API in "this" project inserts the data using required business logic.

"""
import shutil
import sys
import os
import requests

# Add the directory containing main.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the app and db objects
from main import app, db, initUsers

# Backup the old database
def backup_database(db_uri, backup_uri):
    """Backup the current database."""
    if backup_uri:
        db_path = db_uri.replace('sqlite:///', 'instance/')
        backup_path = backup_uri.replace('sqlite:///', 'instance/')
        shutil.copyfile(db_path, backup_path)
        print(f"Database backed up to {backup_path}")
    else:
        print("Backup not supported for production database.")

# Obtain the app context 
with app.app_context():
    try:
        
        # Step 1: New schema
        # Check if the database has any tables
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if tables:
            print("Warning, you are about to lose all data in the database!")
            print("Do you want to continue? (y/n)")
            response = input()
            if response.lower() != 'y':
                print("Exiting without making changes.")
                sys.exit(0)
        
        # Backup the old database
        backup_database(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_BACKUP_URI'])
        
        # Drop all tables defined in the project
        db.drop_all()
        print("All tables dropped.")
        
        # Create all tables
        db.create_all()
        print("All tables created.")
        
        # Add default test data 
        initUsers() # test data
        
        # Step 3: Load data into the new database using Flask's test client
        with app.test_client() as client:
            post_response = client.post('/api/users', json=old_data)
            if post_response.status_code == 200:
                print("Data loaded into the new database successfully.")
            else:
                print(f"Failed to load data into the new database. Status code: {post_response.status_code}")
                sys.exit(1)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)
    
    # Log success 
    print("Database initialized!")