#!/usr/bin/env python
"""
Script to fix the migration order in the database
This script addresses the inconsistent migration history issue
"""
import os
import django
from django.db import connection
from django.utils import timezone

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_migration_order():
    """Fix the migration order in the database"""
    print("Starting migration order fix...")
    
    with connection.cursor() as cursor:
        # Get current migration records
        cursor.execute("SELECT id, app, name FROM django_migrations WHERE app = 'cricket_stats' ORDER BY id")
        migrations = cursor.fetchall()
        print(f"Found {len(migrations)} cricket_stats migrations:")
        for migration in migrations:
            print(f"  {migration[0]}: {migration[1]}.{migration[2]}")
        
        # Clear all cricket_stats migrations
        cursor.execute("DELETE FROM django_migrations WHERE app = 'cricket_stats'")
        print("Cleared all cricket_stats migrations")
        
        # Add migrations in the correct order
        now = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Define the correct migration order
        migration_order = [
            '0001_initial',
            '0002_add_match_formats',
            '0002_performance_indexes',
            '0003_add_college_name',
            '0003_remove_matchformat_days_match_match_days_and_more',
            '0004_add_tournament_model',
            '0004_alter_matchplayer_options_and_more',
            '0005_matchplayer_catches_matchplayer_direct_hits_and_more',
            '0005_update_tournament_fields',
            '0006_trainingsession_alter_playerattendance_options_and_more',
            '0007_fix_team_foreign_key',
            '0008_match_college_name_match_name_match_team_name_and_more',
            '0009_match_college_name_match_name',
            '0010_matchplayer_comments',
            '0011_merge_20250526_0556'
        ]
        
        print("\nAdding migrations in the correct order:")
        for i, migration_name in enumerate(migration_order):
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s)",
                ('cricket_stats', migration_name, now)
            )
            print(f"  {i+1}: cricket_stats.{migration_name}")
    
    print("\nMigration order fix completed.")
    print("Now try accessing your application.")

if __name__ == "__main__":
    fix_migration_order()
