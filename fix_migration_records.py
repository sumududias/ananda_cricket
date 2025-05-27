#!/usr/bin/env python
"""
Script to fix Django migration records in the database
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_migration_records():
    """Fix the Django migration records to match the current database state"""
    print("Starting migration records fix...")
    
    with connection.cursor() as cursor:
        # Check if the django_migrations table exists
        cursor.execute("SHOW TABLES LIKE 'django_migrations'")
        if not cursor.fetchone():
            print("Table django_migrations doesn't exist. Nothing to fix.")
            return
        
        # Get current migration records for cricket_stats app
        cursor.execute("SELECT name FROM django_migrations WHERE app = 'cricket_stats'")
        applied_migrations = [row[0] for row in cursor.fetchall()]
        print(f"Current applied migrations: {applied_migrations}")
        
        # Migrations we want to mark as applied
        migrations_to_apply = [
            '0001_initial',
            '0002_performance_indexes',
            '0003_add_college_name',
            '0004_add_tournament_model',
            '0005_update_tournament_fields',
            '0011_merge_20250526_0556'
        ]
        
        # Add missing migrations
        for migration in migrations_to_apply:
            if migration not in applied_migrations:
                print(f"Marking migration {migration} as applied...")
                cursor.execute(
                    "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                    ['cricket_stats', migration]
                )
    
    print("Migration records fix complete!")

if __name__ == "__main__":
    fix_migration_records()
