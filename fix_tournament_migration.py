#!/usr/bin/env python
"""
Script to fix the tournament table migration issue
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
    migration_file = os.path.join(app_dir, '0004_add_tournament_model.py')
    
    if os.path.exists(migration_file):
        return migration_file
    else:
        # Try to find it by pattern matching if the exact name is different
        for filename in os.listdir(app_dir):
            if 'add_tournament_model' in filename and filename.endswith('.py'):
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
        ('cricket_stats', '0003_add_college_name'),
    ]

    operations = [
        # Empty operations to skip the problematic table creation
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

def fix_migration_dependencies():
    """Fix any migration dependencies that might be affected"""
    from django.conf import settings
    
    app_dir = os.path.join(settings.BASE_DIR, 'cricket_stats', 'migrations')
    
    # List all migration files
    migration_files = [f for f in os.listdir(app_dir) if f.endswith('.py') and not f.startswith('__')]
    
    for filename in migration_files:
        file_path = os.path.join(app_dir, filename)
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Skip if this is the file we just modified
            if '0004_add_tournament_model' in filename:
                continue
                
            # Check if this migration depends on the one we modified
            if "'cricket_stats', '0004_add_tournament_model'" in content:
                print(f"Found dependency in {filename}, but we'll leave it as is since the migration still exists")
        except Exception as e:
            print(f"Error checking file {filename}: {e}")
    
    return True

if __name__ == "__main__":
    print("Looking for the problematic tournament migration file...")
    migration_file = find_migration_file()
    
    if migration_file:
        print(f"Found migration file: {migration_file}")
        if create_empty_migration(migration_file):
            print("Successfully replaced the migration file with an empty one.")
            fix_migration_dependencies()
            print("Now run the rebuild_database.py script again.")
        else:
            print("Failed to replace the migration file.")
    else:
        print("Could not find the problematic migration file.")
        print("Please check the migrations directory manually.")
