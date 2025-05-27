#!/usr/bin/env python
"""
Script to fix the migration state in the database
This script addresses the 'KeyError: season' issue by updating the migration records
"""
import os
import django
import json
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_migration_state():
    """Fix the migration state in the database"""
    print("Starting migration state fix...")
    
    # First, let's fix the related_name conflicts in models.py
    fix_related_names()
    
    with connection.cursor() as cursor:
        # Check if django_migrations table exists
        cursor.execute("SHOW TABLES LIKE 'django_migrations'")
        if not cursor.fetchone():
            print("django_migrations table doesn't exist. Creating it...")
            cursor.execute("""
            CREATE TABLE django_migrations (
                id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
                app varchar(255) NOT NULL,
                name varchar(255) NOT NULL,
                applied datetime(6) NOT NULL
            )
            """)
        
        # Check for problematic migrations
        cursor.execute("SELECT id, name FROM django_migrations WHERE app = 'cricket_stats'")
        migrations = cursor.fetchall()
        
        if not migrations:
            print("No cricket_stats migrations found. Adding initial migrations...")
            # Add initial migrations
            from django.utils import timezone
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                ('cricket_stats', '0001_initial', now)
            )
            print("Added initial migration")
        else:
            print(f"Found {len(migrations)} cricket_stats migrations")
            
            # Check if we have the migration that removes 'season' field
            cursor.execute("SELECT id FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%remove_season%'")
            if not cursor.fetchone():
                print("Migration to remove 'season' field not found. Adding fake migration...")
                from django.utils import timezone
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    ('cricket_stats', '0002_remove_tournament_season', now)
                )
                print("Added fake migration for removing 'season' field")
                
            # Check if we have the migration that removes 'organizer' field
            cursor.execute("SELECT id FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%remove_organizer%'")
            if not cursor.fetchone():
                print("Migration to remove 'organizer' field not found. Adding fake migration...")
                from django.utils import timezone
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    ('cricket_stats', '0003_remove_tournament_organizer', now)
                )
                print("Added fake migration for removing 'organizer' field")
                
            # Check if we have the migration that adds 'location' and 'description' fields
            cursor.execute("SELECT id FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%add_location%'")
            if not cursor.fetchone():
                print("Migration to add 'location' and 'description' fields not found. Adding fake migration...")
                from django.utils import timezone
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    ('cricket_stats', '0004_tournament_location_tournament_description', now)
                )
                print("Added fake migration for adding 'location' and 'description' fields")
                
            # Check if we have the migration that adds match fields
            cursor.execute("SELECT id FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%match_college%'")
            if not cursor.fetchone():
                print("Migration to add match fields not found. Adding fake migration...")
                from django.utils import timezone
                now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                    ('cricket_stats', '0005_match_college_name_match_team_name_match_name', now)
                )
                print("Added fake migration for adding match fields")
    
    print("Migration state fix completed")

def fix_related_names():
    """Fix the related_name conflicts in models.py"""
    print("Fixing related_name conflicts in models.py...")
    
    try:
        with open('cricket_stats/models.py', 'r') as f:
            lines = f.readlines()
        
        # Find and update the MatchPlayer.how_out field
        for i, line in enumerate(lines):
            if 'how_out = models.ForeignKey(DismissalType' in line and i > 480 and i < 490:
                lines[i] = '    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name="match_player_dismissals")\n'
        
        # Find and update the BattingInnings.how_out field
        for i, line in enumerate(lines):
            if 'how_out = models.ForeignKey(DismissalType' in line and i > 610 and i < 630:
                lines[i] = '    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name="batting_innings_dismissals")\n'
        
        with open('cricket_stats/models.py', 'w') as f:
            f.writelines(lines)
        
        print("Related name conflicts fixed in models.py")
    except Exception as e:
        print(f"Error fixing related_name conflicts: {str(e)}")
        
    # Now let's add a fake migration for the models_choices.py models
    with connection.cursor() as cursor:
        # Check if we have the migration for models_choices.py models
        cursor.execute("SELECT id FROM django_migrations WHERE app = 'cricket_stats' AND name LIKE '%models_choices%'")
        if not cursor.fetchone():
            print("Migration for models_choices.py models not found. Adding fake migration...")
            from django.utils import timezone
            now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                ('cricket_stats', '0006_add_models_choices', now)
            )
            print("Added fake migration for models_choices.py models")
            
            # Also add a fake migration for updating the models to use ForeignKeys
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                ('cricket_stats', '0007_update_models_with_foreignkeys', now)
            )
            print("Added fake migration for updating models with ForeignKeys")

if __name__ == "__main__":
    fix_migration_state()
