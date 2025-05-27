#!/usr/bin/env python
"""
Script to fix the Tournament table schema directly using SQL
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_tournament_table():
    """Fix the Tournament table schema by adding the missing columns"""
    print("Starting Tournament table schema fix...")
    
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_tournament'")
        if not cursor.fetchone():
            print("Table cricket_stats_tournament doesn't exist. Nothing to fix.")
            return
        
        # Check if the location column exists
        cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'location'")
        if not cursor.fetchone():
            print("Adding 'location' column to cricket_stats_tournament...")
            cursor.execute("ALTER TABLE cricket_stats_tournament ADD COLUMN location VARCHAR(100) NOT NULL DEFAULT 'Colombo'")
        else:
            print("Column 'location' already exists.")
        
        # Check if the description column exists
        cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'description'")
        if not cursor.fetchone():
            print("Adding 'description' column to cricket_stats_tournament...")
            cursor.execute("ALTER TABLE cricket_stats_tournament ADD COLUMN description TEXT NULL")
        else:
            print("Column 'description' already exists.")
        
        # Check if the season column exists and remove it if it does
        cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'season'")
        if cursor.fetchone():
            print("Removing 'season' column from cricket_stats_tournament...")
            cursor.execute("ALTER TABLE cricket_stats_tournament DROP COLUMN season")
        else:
            print("Column 'season' doesn't exist.")
        
        # Check if the organizer column exists and remove it if it does
        cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'organizer'")
        if cursor.fetchone():
            print("Removing 'organizer' column from cricket_stats_tournament...")
            cursor.execute("ALTER TABLE cricket_stats_tournament DROP COLUMN organizer")
        else:
            print("Column 'organizer' doesn't exist.")
    
    print("Tournament table schema fix complete!")

if __name__ == "__main__":
    fix_tournament_table()
