#!/usr/bin/env python
"""
Script to replace the problematic migration file with an empty one
"""
import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def find_migration_file():
    """Find the problematic migration file"""
    from django.conf import settings
    
    # Get the app directory
    app_dir = os.path.join(settings.BASE_DIR, 'cricket_stats', 'migrations')
    
    # Look for the problematic migration file
    migration_file = os.path.join(app_dir, '0007_fix_team_foreign_key.py')
    
    if os.path.exists(migration_file):
        return migration_file
    else:
        # Try to find it by pattern matching if the exact name is different
        for filename in os.listdir(app_dir):
            if filename.startswith('0007_') and filename.endswith('.py'):
                return os.path.join(app_dir, filename)
    
    return None

def create_empty_migration(file_path):
    """Replace the migration file with an empty one"""
    if not file_path:
        print("Migration file path is empty")
        return False
    
    # Create a backup of the original file if it exists
    if os.path.exists(file_path):
        backup_path = file_path + '.bak'
        try:
            with open(file_path, 'r') as f:
                original_content = f.read()
            
            with open(backup_path, 'w') as f:
                f.write(original_content)
            
            print(f"Created backup at {backup_path}")
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
    
    # Create a simple empty migration
    content = """# Generated manually to fix migration issues

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0006_trainingsession_alter_playerattendance_options_and_more'),
    ]

    operations = [
        # Empty operations to skip the problematic SQL
    ]
"""
    
    try:
        with open(file_path, 'w') as f:
            f.write(content)
        print(f"Created empty migration file: {file_path}")
        return True
    except Exception as e:
        print(f"Error creating empty migration file: {e}")
        return False

if __name__ == "__main__":
    print("Looking for the problematic migration file...")
    migration_file = find_migration_file()
    
    if migration_file:
        print(f"Found migration file: {migration_file}")
        if create_empty_migration(migration_file):
            print("Successfully replaced the migration file with an empty one.")
            print("Now run the rebuild_database.py script again.")
        else:
            print("Failed to replace the migration file.")
    else:
        print("Could not find the problematic migration file.")
        app_dir = os.path.join(django.conf.settings.BASE_DIR, 'cricket_stats', 'migrations')
        new_file_path = os.path.join(app_dir, '0007_fix_team_foreign_key.py')
        print(f"Creating a new empty migration file at {new_file_path}")
        if create_empty_migration(new_file_path):
            print("Created a new empty migration file.")
            print("Now run the rebuild_database.py script again.")
        else:
            print("Failed to create a new migration file.")
