#!/usr/bin/env python
"""
Script to initialize database tables and columns
This script creates missing tables and adds missing columns to existing tables
"""
import os
import django
from django.db import connection
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def initialize_database_tables():
    """Initialize database tables and columns"""
    print("Starting database initialization...")
    
    with connection.cursor() as cursor:
        # Check if django_session table exists
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
        
        # Check if cricket_stats_tournament table exists
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
        
        # Check if cricket_stats_match table has college_name, team_name, and name columns
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'college_name'")
        if not cursor.fetchone():
            print("Adding college_name column to cricket_stats_match table...")
            cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN college_name varchar(100) NOT NULL DEFAULT 'Ananda College'")
            print("college_name column added.")
        
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'team_name'")
        if not cursor.fetchone():
            print("Adding team_name column to cricket_stats_match table...")
            cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN team_name varchar(100) NOT NULL DEFAULT 'Ananda College'")
            print("team_name column added.")
        
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'name'")
        if not cursor.fetchone():
            print("Adding name column to cricket_stats_match table...")
            cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN name varchar(100) NOT NULL DEFAULT ''")
            print("name column added.")
        
    print("Database initialization completed.")
    print("Now try accessing your application.")

if __name__ == "__main__":
    initialize_database_tables()