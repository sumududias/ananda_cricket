#!/usr/bin/env python
"""
Script to reset the migration state and create a fresh initial migration
"""
import os
import django
import shutil
import subprocess
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def reset_migrations():
    """Reset the migration state and create a fresh initial migration"""
    print("Starting migration reset process...")
    
    # Step 1: Clear the django_migrations table for cricket_stats
    with connection.cursor() as cursor:
        cursor.execute("DELETE FROM django_migrations WHERE app = 'cricket_stats'")
        print("Cleared cricket_stats migrations from database")
    
    # Step 2: Create a fake initial migration
    from django.utils import timezone
    now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            ('cricket_stats', '0001_initial', now)
        )
        print("Added fake initial migration record")
    
    # Step 3: Try to run migrate with --fake-initial
    try:
        print("\nRunning 'python manage.py migrate cricket_stats --fake-initial'...")
        result = subprocess.run(
            ["python", "manage.py", "migrate", "cricket_stats", "--fake-initial"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:")
            print(result.stderr)
    except Exception as e:
        print(f"Error running migrate: {e}")
    
    # Step 4: Add the match columns directly to the database if they don't exist
    with connection.cursor() as cursor:
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
            print("cricket_stats_match table doesn't exist.")
    
    print("\nMigration reset process completed. Try accessing your application now.")

if __name__ == "__main__":
    reset_migrations()
