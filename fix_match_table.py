#!/usr/bin/env python
"""
Script to fix the Match table schema directly using SQL
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_match_table():
    """Fix the Match table schema by adding the missing columns"""
    print("Starting Match table schema fix...")
    
    with connection.cursor() as cursor:
        # Check if the table exists
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_match'")
        if not cursor.fetchone():
            print("Table cricket_stats_match doesn't exist. Nothing to fix.")
            return
        
        # Check if the college_name column exists
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'college_name'")
        if not cursor.fetchone():
            print("Adding 'college_name' column to cricket_stats_match...")
            cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN college_name VARCHAR(100) NOT NULL DEFAULT 'Ananda College'")
        else:
            print("Column 'college_name' already exists.")
        
        # Check if the team_name column exists
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'team_name'")
        if not cursor.fetchone():
            print("Adding 'team_name' column to cricket_stats_match...")
            cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN team_name VARCHAR(100) NULL DEFAULT ''")
        else:
            print("Column 'team_name' already exists.")
        
        # Check if the name column exists
        cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'name'")
        if not cursor.fetchone():
            print("Adding 'name' column to cricket_stats_match...")
            cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN name VARCHAR(100) NULL DEFAULT ''")
        else:
            print("Column 'name' already exists.")
    
    print("Match table schema fix complete!")

if __name__ == "__main__":
    fix_match_table()
