#!/usr/bin/env python3

""" db_migrate.py
Generates the database schema for all db models
- Initializes Users, Sections, UserSections, and other defined tables.
- Imports data from the old database to the new database.

Usage: Run from the terminal as such:

Goto the scripts directory:
> cd scripts; ./db_migrate.py

Or run from the root of the project:
> scripts/db_migrate.py

For production databases install mysql:

brew install mysql

or

sudo apt-get install mysql-server

"""
import shutil
import sys
import os
import requests
import subprocess
import json
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# Add the directory containing main.py to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# Import application object
from main import app, db, initUsers

# Locations and credentials 
AUTH_URL = "https://flask2025.nighthawkcodingsociety.com/api/authenticate"
DATA_URL = "https://flask2025.nighthawkcodingsociety.com/api/user"
UID = app.config['DEFAULT_USER'] 
PASSWORD = app.config['DEFAULT_PASSWORD']

# Backup the old database
def backup_database(db_uri, backup_uri, db_string):
    """Backup the current database."""
    db_name = db_uri.split('/')[-1]
    backup_file = f"{db_name}_backup.sql"   
    if 'mysql' in db_string:
        os.environ['MYSQL_PWD'] = app.config["DB_PASSWORD"]
        try:
            subprocess.run([
                'mysqldump',
                '-h', app.config["DB_ENDPOINT"],
                '-u', app.config["DB_USERNAME"],
                f'-p{app.config["DB_PASSWORD"]}',
                db_name,
                '>', backup_file
            ], check=True, shell=True)
            print(f"MySQL database backed up to {backup_file}")
        except subprocess.CalledProcessError as e:
            print(f"Backup tool mysqldump not working or installed {e}")
        finally:
            del os.environ['MYSQL_PWD']
    elif 'sqlite' in db_string:
        # SQLite backup using shutil
        if backup_uri:
            db_path = db_uri.replace('sqlite:///', '')
            backup_path = backup_uri.replace('sqlite:///', '')
            shutil.copyfile(db_path, backup_path)
            print(f"SQLite database backed up to {backup_path}")
        else:
            print("Backup not supported for production database.")
    else:
        print("Unsupported database type for backup.")

# Create the database if it does not exist
def create_database(engine, db_name):
    """Create the database if it does not exist."""
    with engine.connect() as connection:
        result = connection.execute(text(f"SHOW DATABASES LIKE '{db_name}'"))
        if not result.fetchone():
            connection.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' created successfully.")
        else:
            print(f"Database '{db_name}' already exists.")

# Old data access        
def authenticate(uid, password):
    '''Authenticate and return the token'''
    auth_data = {
        "uid": uid,
        "password": password
    }
    headers = {
        "Content-Type": "application/json",
        "X-Origin": "client"
    }
    try:
        response = requests.post(AUTH_URL, json=auth_data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.cookies, None
    except requests.RequestException as e:
        return None, {'message': 'Failed to authenticate', 'code': response.status_code, 'error': str(e)}

# Old data JSON extraction
def extract_data(cookies):
    '''Extract data using the authentication cookies'''
    headers = {
        "Content-Type": "application/json",
        "X-Origin": "client"
    }
    try:
        response = requests.get(DATA_URL, headers=headers, cookies=cookies)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json(), None
    except requests.RequestException as e:
        return None, {'message': 'Failed to extract old data', 'code': response.status_code, 'error': str(e)}
    
# Write data to JSON file
def write_data_to_json(data, json_file):
    """Write data to JSON file and create a timestamped backup if the file exists."""
    if os.path.exists(json_file):
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_file = f"{json_file}.{timestamp}.bak"
        shutil.copyfile(json_file, backup_file)
        print(f"Existing JSON data backed up to {backup_file}")
    
    with open(json_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Data written to {json_file}")

# Read data from JSON file
def read_data_from_json(json_file):
    """Read data from JSON file."""
    if os.path.exists(json_file):
        with open(json_file, 'r') as f:
            return json.load(f), None
    else:
        return None, {'message': 'JSON data file not found', 'code': 404, 'error': 'File not found'}

# Main extraction and loading process
def main():
    
    # Step 0: Warning to the user and backup table
    with app.app_context():
        try:
            # Step 3: Build New schema
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
            backup_database(app.config['SQLALCHEMY_DATABASE_URI'], app.config['SQLALCHEMY_BACKUP_URI'], app.config['SQLALCHEMY_DATABASE_STRING'])  
                 
        except OperationalError as e:
            if "Unknown database" in str(e):
                # Create the database if it does not exist
                engine = create_engine(app.config['SQLALCHEMY_DATABASE_STRING'])
                create_database(engine, app.config['SQLALCHEMY_DATABASE_NAME'])
                # Retry the operation
                with app.app_context():
                    db.create_all()
                    print("All tables created after database creation.")
                    
            else:
                print(f"An error occurred: {e}")
                sys.exit(1) 
                
        except Exception as e:
            print(f"An error occurred: {e}")
            sys.exit(1)
        
    # Step 1: Authenticate to Old database
    cookies, error = authenticate(UID, PASSWORD)
    if error:
        print(error)
        print("Using local JSON data as fallback.")
        old_data, error = read_data_from_json(JSON_DATA)
        if error:
            print(error)
            sys.exit(1)
    else:
        # Step 2: Extract Old data 
        old_data, error = extract_data(cookies)
        if error:
            print(error)
            sys.exit(1)
        else:
            write_data_to_json(old_data, JSON_DATA)
    
    print("Old data extracted successfully.")
    
    # Step 3: Build New schema and load data 
    try:
        with app.app_context():
            # Drop all the tables defined in the project
            db.drop_all()
            print("All tables dropped.")
            
            # Create all tables
            db.create_all()
            print("All tables created.")
            
            # Add default test data 
            initUsers() # test data
            
            # Load data into the new database using Flask's test client
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
 
if __name__ == "__main__":
    main()