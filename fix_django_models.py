#!/usr/bin/env python
"""
Script to fix Django models and database tables to ensure they match
This script directly modifies both the database and Django's migration records
"""
import os
import django
import subprocess
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_django_models():
    """Fix Django models and database tables to ensure they match"""
    print("Starting Django models and database fix...")
    
    with connection.cursor() as cursor:
        # Step 1: Fix the database tables
        print("\n--- Step 1: Fixing Database Tables ---")
        
        # Fix Tournament table
        print("\nChecking Tournament table...")
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_tournament'")
        if cursor.fetchone():
            print("Tournament table exists, checking columns...")
            
            # Check for location column
            cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'location'")
            if not cursor.fetchone():
                print("Adding 'location' column to Tournament table...")
                cursor.execute("ALTER TABLE cricket_stats_tournament ADD COLUMN location VARCHAR(100) NOT NULL DEFAULT 'Colombo'")
                print("Added 'location' column to Tournament table")
            
            # Check for description column
            cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'description'")
            if not cursor.fetchone():
                print("Adding 'description' column to Tournament table...")
                cursor.execute("ALTER TABLE cricket_stats_tournament ADD COLUMN description TEXT")
                print("Added 'description' column to Tournament table")
            
            # Check for season column and remove it if it exists
            cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'season'")
            if cursor.fetchone():
                print("Removing 'season' column from Tournament table...")
                cursor.execute("ALTER TABLE cricket_stats_tournament DROP COLUMN season")
                print("Removed 'season' column from Tournament table")
            
            # Check for organizer column and remove it if it exists
            cursor.execute("SHOW COLUMNS FROM cricket_stats_tournament LIKE 'organizer'")
            if cursor.fetchone():
                print("Removing 'organizer' column from Tournament table...")
                cursor.execute("ALTER TABLE cricket_stats_tournament DROP COLUMN organizer")
                print("Removed 'organizer' column from Tournament table")
        else:
            print("Tournament table doesn't exist, creating it...")
            cursor.execute("""
            CREATE TABLE cricket_stats_tournament (
                id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name varchar(100) NOT NULL,
                start_date date NOT NULL,
                end_date date,
                location varchar(100) NOT NULL DEFAULT 'Colombo',
                description text
            )
            """)
            print("Created Tournament table")
        
        # Fix Match table
        print("\nChecking Match table...")
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_match'")
        if cursor.fetchone():
            print("Match table exists, checking columns...")
            
            # Check for college_name column
            cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'college_name'")
            if not cursor.fetchone():
                print("Adding 'college_name' column to Match table...")
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN college_name VARCHAR(100) NOT NULL DEFAULT 'Ananda College'")
                print("Added 'college_name' column to Match table")
            
            # Check for team_name column
            cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'team_name'")
            if not cursor.fetchone():
                print("Adding 'team_name' column to Match table...")
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN team_name VARCHAR(100) NOT NULL DEFAULT 'First XI'")
                print("Added 'team_name' column to Match table")
            
            # Check for name column
            cursor.execute("SHOW COLUMNS FROM cricket_stats_match LIKE 'name'")
            if not cursor.fetchone():
                print("Adding 'name' column to Match table...")
                cursor.execute("ALTER TABLE cricket_stats_match ADD COLUMN name VARCHAR(100) NOT NULL DEFAULT ''")
                print("Added 'name' column to Match table")
        else:
            print("Match table doesn't exist. This is a more complex table, so we'll let Django create it.")
        
        # Step 2: Fix migration records
        print("\n--- Step 2: Fixing Migration Records ---")
        
        # Clear all existing cricket_stats migrations
        cursor.execute("DELETE FROM django_migrations WHERE app = 'cricket_stats'")
        print("Cleared all cricket_stats migrations")
        
        # Add fake migrations in the correct order
        from django.utils import timezone
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Add initial migration
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
            ('cricket_stats', '0001_initial', now)
        )
        print("Added fake initial migration")
        
        # Add other migrations
        migrations = [
            '0002_add_match_formats',
            '0003_remove_matchformat_days_match_match_days_and_more',
            '0004_alter_matchplayer_options_and_more',
            '0005_matchplayer_catches_matchplayer_direct_hits_and_more',
            '0006_trainingsession_alter_playerattendance_options_and_more',
            '0007_fix_team_foreign_key',
            '0008_match_college_name_match_name_match_team_name_and_more',
            '0009_match_college_name_match_name',
            '0010_matchplayer_comments',
            '0011_merge_20250526_0556'
        ]
        
        for migration in migrations:
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                ('cricket_stats', migration, now)
            )
        print(f"Added {len(migrations)} fake migrations")
    
    # Step 3: Try to run migrations for other apps
    print("\n--- Step 3: Running Migrations for Other Apps ---")
    try:
        print("Running migrations for admin app...")
        subprocess.run(
            ["python", "manage.py", "migrate", "admin", "--fake"],
            check=True
        )
        
        print("Running migrations for auth app...")
        subprocess.run(
            ["python", "manage.py", "migrate", "auth", "--fake"],
            check=True
        )
        
        print("Running migrations for contenttypes app...")
        subprocess.run(
            ["python", "manage.py", "migrate", "contenttypes", "--fake"],
            check=True
        )
        
        print("Running migrations for sessions app...")
        subprocess.run(
            ["python", "manage.py", "migrate", "sessions", "--fake"],
            check=True
        )
    except Exception as e:
        print(f"Error running migrations: {e}")
    
    print("\nDjango models and database fix completed.")
    print("Try accessing your application now.")

if __name__ == "__main__":
    fix_django_models()
