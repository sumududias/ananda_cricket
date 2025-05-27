#!/usr/bin/env python
"""
Script to initialize the database with all required tables and columns
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def initialize_database():
    """Create all required tables in the database"""
    print("Starting database initialization...")
    
    with connection.cursor() as cursor:
        # Create django_session table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS django_session (
            session_key varchar(40) NOT NULL PRIMARY KEY,
            session_data longtext NOT NULL,
            expire_date datetime(6) NOT NULL,
            KEY django_session_expire_date_a5c62663 (expire_date)
        )
        """)
        print("django_session table created or already exists")
        
        # Create cricket_stats_tournament table if it doesn't exist
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cricket_stats_tournament (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            name varchar(100) NOT NULL,
            start_date date NOT NULL,
            end_date date,
            location varchar(100) NOT NULL DEFAULT 'Colombo',
            description text
        )
        """)
        print("cricket_stats_tournament table created or already exists")
        
        # Check if cricket_stats_match table exists and add missing columns
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_match'")
        if cursor.fetchone():
            # Add college_name column if it doesn't exist
            cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'college_name'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN college_name VARCHAR(100) NOT NULL DEFAULT 'Ananda College'")
                print("Added college_name column to cricket_stats_match")
            
            # Add team_name column if it doesn't exist
            cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'team_name'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN team_name VARCHAR(100) NOT NULL DEFAULT 'First XI'")
                print("Added team_name column to cricket_stats_match")
            
            # Add name column if it doesn't exist
            cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'name'")
            if not cursor.fetchone():
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT ''")
                print("Added name column to cricket_stats_match")
        else:
            print("cricket_stats_match table doesn't exist. Run Django migrations first.")
    
    print("Database initialization completed")

if __name__ == "__main__":
    initialize_database()