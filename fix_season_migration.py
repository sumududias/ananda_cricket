#!/usr/bin/env python
"""
Script to directly fix the 'season' field issue in migration records
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_season_migration():
    """Fix the specific issue with the 'season' field in migration records"""
    print("Starting to fix the 'season' field migration issue...")
    
    with connection.cursor() as cursor:
        # First, let's check what migrations we have for cricket_stats
        cursor.execute("SELECT id, name FROM django_migrations WHERE app = 'cricket_stats' ORDER BY id")
        migrations = cursor.fetchall()
        print(f"Found {len(migrations)} cricket_stats migrations:")
        for migration_id, migration_name in migrations:
            print(f"  {migration_id}: {migration_name}")
        
        # Now let's find migrations that might be causing the issue
        print("\nLooking for problematic migrations...")
        cursor.execute("SELECT id, name FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%remove%season%'")
        season_migrations = cursor.fetchall()
        
        if season_migrations:
            print(f"Found {len(season_migrations)} migrations related to removing 'season':")
            for migration_id, migration_name in season_migrations:
                print(f"  {migration_id}: {migration_name}")
        else:
            print("No migrations found that remove 'season' field.")
            print("Adding a fake migration record to mark 'season' as removed...")
            
            # Get the highest migration ID to ensure we add our fake migration after all others
            cursor.execute("SELECT MAX(id) FROM django_migrations")
            max_id = cursor.fetchone()[0] or 0
            
            # Add a fake migration record
            from django.utils import timezone
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, %s)",
                (max_id + 1, 'cricket_stats', '0002_remove_tournament_season', now)
            )
            print("Added fake migration for removing 'season' field")
        
        # Let's also check if there's a migration that adds the 'season' field
        cursor.execute("SELECT id, name FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%add%season%'")
        add_season_migrations = cursor.fetchall()
        
        if add_season_migrations:
            print(f"\nFound {len(add_season_migrations)} migrations related to adding 'season':")
            for migration_id, migration_name in add_season_migrations:
                print(f"  {migration_id}: {migration_name}")
        else:
            print("\nNo migrations found that add 'season' field.")
        
        # Let's also check if there's a migration that adds the fields we need
        cursor.execute("SELECT id, name FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%add%location%'")
        location_migrations = cursor.fetchall()
        
        if not location_migrations:
            print("\nNo migrations found that add 'location' field.")
            print("Adding a fake migration record to mark 'location' and 'description' as added...")
            
            # Get the highest migration ID to ensure we add our fake migration after all others
            cursor.execute("SELECT MAX(id) FROM django_migrations")
            max_id = cursor.fetchone()[0] or 0
            
            # Add a fake migration record
            from django.utils import timezone
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, %s)",
                (max_id + 1, 'cricket_stats', '0003_tournament_location_tournament_description', now)
            )
            print("Added fake migration for adding 'location' and 'description' fields")
        
        # Let's also check if there's a migration that adds the match fields
        cursor.execute("SELECT id, name FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%match%college%'")
        match_migrations = cursor.fetchall()
        
        if not match_migrations:
            print("\nNo migrations found that add match fields.")
            print("Adding a fake migration record to mark match fields as added...")
            
            # Get the highest migration ID to ensure we add our fake migration after all others
            cursor.execute("SELECT MAX(id) FROM django_migrations")
            max_id = cursor.fetchone()[0] or 0
            
            # Add a fake migration record
            from django.utils import timezone
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, %s)",
                (max_id + 1, 'cricket_stats', '0004_match_college_name_match_team_name_match_name', now)
            )
            print("Added fake migration for adding match fields")
    
    print("\nMigration fix completed. Now try running 'python manage.py migrate --fake'")

if __name__ == "__main__":
    fix_season_migration()
