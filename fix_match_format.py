#!/usr/bin/env python
"""
Script to fix the MatchFormat table structure and fake all migrations
"""
import os
import django
import subprocess
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_match_format_table():
    """Fix the MatchFormat table structure and fake all migrations"""
    print("Starting MatchFormat table fix...")
    
    with connection.cursor() as cursor:
        # Check if the MatchFormat table exists
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_matchformat'")
        if cursor.fetchone():
            print("MatchFormat table exists, checking columns...")
            
            # Check if days column exists
            cursor.execute("SHOW COLUMNS FROM cricket_stats_matchformat LIKE 'days'")
            if not cursor.fetchone():
                print("Adding 'days' column to MatchFormat table...")
                cursor.execute("ALTER TABLE cricket_stats_matchformat ADD COLUMN days INT NOT NULL DEFAULT 1")
                print("Added 'days' column to MatchFormat table")
            else:
                print("'days' column already exists in MatchFormat table")
                
            # Make sure we have the basic match formats
            print("\nEnsuring basic match formats exist...")
            cursor.execute("SELECT COUNT(*) FROM cricket_stats_matchformat")
            count = cursor.fetchone()[0]
            
            if count == 0:
                print("No match formats found, creating default ones...")
                cursor.execute("""
                INSERT INTO cricket_stats_matchformat (name, days, overs, description) 
                VALUES 
                ('Test', 5, 0, 'Test match format'),
                ('ODI', 1, 50, 'One Day International format'),
                ('T20', 1, 20, 'Twenty20 format'),
                ('T10', 1, 10, 'Ten10 format')
                """)
                print("Created default match formats")
            else:
                print(f"Found {count} existing match formats")
        else:
            print("MatchFormat table doesn't exist, creating it...")
            cursor.execute("""
            CREATE TABLE cricket_stats_matchformat (
                id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                name varchar(100) NOT NULL,
                days int NOT NULL DEFAULT 1,
                overs int NOT NULL DEFAULT 0,
                description text
            )
            """)
            print("Created MatchFormat table")
            
            # Insert default match formats
            print("Creating default match formats...")
            cursor.execute("""
            INSERT INTO cricket_stats_matchformat (name, days, overs, description) 
            VALUES 
            ('Test', 5, 0, 'Test match format'),
            ('ODI', 1, 50, 'One Day International format'),
            ('T20', 1, 20, 'Twenty20 format'),
            ('T10', 1, 10, 'Ten10 format')
            """)
            print("Created default match formats")
    
    # Now let's try to fake all migrations
    print("\nFaking all migrations...")
    try:
        # First mark all cricket_stats migrations as applied
        with connection.cursor() as cursor:
            # Get all migration files from the filesystem
            migrations_dir = os.path.join('cricket_stats', 'migrations')
            if os.path.exists(migrations_dir):
                migration_files = [f for f in os.listdir(migrations_dir) 
                                  if f.endswith('.py') and not f.startswith('__')]
                
                print(f"Found {len(migration_files)} migration files")
                
                # Clear existing cricket_stats migrations
                cursor.execute("DELETE FROM django_migrations WHERE app = 'cricket_stats'")
                print("Cleared existing cricket_stats migrations")
                
                # Add all migrations as applied
                from django.utils import timezone
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                
                for migration_file in migration_files:
                    migration_name = migration_file[:-3]  # Remove .py extension
                    if migration_name != '__init__':
                        cursor.execute(
                            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                            ('cricket_stats', migration_name, now)
                        )
                print(f"Marked {len(migration_files)} migrations as applied")
        
        # Now run migrate for other apps
        print("\nRunning migrate for other apps...")
        subprocess.run(
            ["python", "manage.py", "migrate", "admin", "--fake"],
            check=True
        )
        subprocess.run(
            ["python", "manage.py", "migrate", "auth", "--fake"],
            check=True
        )
        subprocess.run(
            ["python", "manage.py", "migrate", "contenttypes", "--fake"],
            check=True
        )
        subprocess.run(
            ["python", "manage.py", "migrate", "sessions", "--fake"],
            check=True
        )
        print("Migrations for other apps faked successfully")
        
    except Exception as e:
        print(f"Error during migration faking: {e}")
    
    print("\nMatchFormat table fix and migration faking completed.")
    print("Try accessing your application now.")

if __name__ == "__main__":
    fix_match_format_table()
