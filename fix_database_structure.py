#!/usr/bin/env python
"""
Script to fix database structure
This script creates missing tables and adds missing columns to existing tables
"""
import os
import django
from django.db import connection
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_database_structure():
    """Fix database structure by creating missing tables and columns"""
    print("Starting database structure fix...")
    
    with connection.cursor() as cursor:
        # First, check if cricket_stats_match table exists
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_match'")
        if not cursor.fetchone():
            print("ERROR: cricket_stats_match table doesn't exist. This is a critical table.")
            print("Please run Django migrations first: python manage.py migrate")
            return
        
        # Check and create django_session table
        cursor.execute("SHOW TABLES LIKE 'django_session'")
        if not cursor.fetchone():
            print("Creating django_session table...")
            cursor.execute("""
                CREATE TABLE `django_session` (
                    `session_key` varchar(40) NOT NULL,
                    `session_data` longtext NOT NULL,
                    `expire_date` datetime(6) NOT NULL,
                    PRIMARY KEY (`session_key`),
                    KEY `django_session_expire_date_a5c62663` (`expire_date`)
                )
            """)
            print("django_session table created.")
        
        # Check and create cricket_stats_tournament table
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_tournament'")
        if not cursor.fetchone():
            print("Creating cricket_stats_tournament table...")
            cursor.execute("""
                CREATE TABLE `cricket_stats_tournament` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `name` varchar(100) NOT NULL,
                    `start_date` date NOT NULL,
                    `end_date` date NOT NULL,
                    `location` varchar(100) NOT NULL DEFAULT 'Colombo',
                    `description` longtext NOT NULL DEFAULT '',
                    PRIMARY KEY (`id`)
                )
            """)
            print("cricket_stats_tournament table created.")
        
        # Add missing columns to cricket_stats_match table
        # Check for college_name column
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'college_name'")
        if not cursor.fetchone():
            print("Adding college_name column to cricket_stats_match table...")
            try:
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN college_name varchar(100) NOT NULL DEFAULT 'Ananda College'")
                print("college_name column added.")
            except Exception as e:
                print(f"Error adding college_name column: {e}")
        
        # Check for team_name column
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'team_name'")
        if not cursor.fetchone():
            print("Adding team_name column to cricket_stats_match table...")
            try:
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN team_name varchar(100) NOT NULL DEFAULT 'Ananda College'")
                print("team_name column added.")
            except Exception as e:
                print(f"Error adding team_name column: {e}")
        
        # Check for name column
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'name'")
        if not cursor.fetchone():
            print("Adding name column to cricket_stats_match table...")
            try:
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN name varchar(100) NOT NULL DEFAULT ''")
                print("name column added.")
            except Exception as e:
                print(f"Error adding name column: {e}")
        
        # Check for tournament_id column
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'tournament_id'")
        if not cursor.fetchone():
            print("Adding tournament_id column to cricket_stats_match table...")
            try:
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN tournament_id int(11) NULL")
                print("tournament_id column added.")
            except Exception as e:
                print(f"Error adding tournament_id column: {e}")
        
        # Create other Django tables if they don't exist
        django_tables = [
            "django_admin_log",
            "django_content_type",
            "django_migrations",
            "auth_group",
            "auth_group_permissions",
            "auth_permission",
            "auth_user",
            "auth_user_groups",
            "auth_user_user_permissions"
        ]
        
        for table in django_tables:
            cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if not cursor.fetchone():
                print(f"Table {table} doesn't exist. This might cause issues.")
        
        # Show all tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print("\nCurrent tables in the database:")
        for table in tables:
            print(f"  - {table[0]}")
        
        # Show columns in cricket_stats_match table
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match")
        columns = cursor.fetchall()
        print("\nColumns in cricket_stats_match table:")
        for column in columns:
            print(f"  - {column[0]}: {column[1]}")
    
    print("\nDatabase structure fix completed.")
    print("Now try accessing your application.")

if __name__ == "__main__":
    fix_database_structure()