#!/usr/bin/env python
"""
Script to create a backup of the MySQL database on PythonAnywhere
"""
import os
import sys
import django
import datetime
import subprocess
import shutil
import zipfile
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def create_backup_directory():
    """Create backup directory if it doesn't exist"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    return backup_dir

def backup_mysql_database():
    """Backup MySQL database using mysqldump"""
    backup_dir = create_backup_directory()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(backup_dir, f'ananda_cricket_backup_{timestamp}.sql')
    
    # Get database settings
    db_settings = settings.DATABASES['default']
    
    if db_settings['ENGINE'] != 'django.db.backends.mysql':
        print("This script is intended for MySQL databases only.")
        return None
    
    # Construct mysqldump command
    cmd = [
        'mysqldump',
        '-u', db_settings['USER'],
        f"--password={db_settings['PASSWORD']}",
        '-h', db_settings.get('HOST', 'localhost'),
        '--databases', db_settings['NAME'],
        '-r', backup_file
    ]
    
    try:
        # Execute the command
        subprocess.run(cmd, check=True)
        print(f"MySQL database backup created at {backup_file}")
        return backup_file
    except subprocess.CalledProcessError as e:
        print(f"Error creating backup: {str(e)}")
        return None

def backup_media_files():
    """Backup media files"""
    backup_dir = create_backup_directory()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_file = os.path.join(backup_dir, f'media_backup_{timestamp}.zip')
    
    media_dir = settings.MEDIA_ROOT
    
    if not os.path.exists(media_dir):
        print(f"Media directory {media_dir} does not exist.")
        return None
    
    try:
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(media_dir))
                    zipf.write(file_path, arcname)
        
        print(f"Media files backup created at {zip_file}")
        return zip_file
    except Exception as e:
        print(f"Error backing up media files: {str(e)}")
        return None

def download_backups():
    """Create a message with instructions to download backups"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    if not os.path.exists(backup_dir) or not os.listdir(backup_dir):
        print("No backups found.")
        return
    
    print("\nTo download backups from PythonAnywhere:")
    print("1. Go to the PythonAnywhere Files tab")
    print(f"2. Navigate to {backup_dir}")
    print("3. Select the backup files you want to download")
    print("4. Click the 'Download' button\n")
    
    print("Available backup files:")
    for file in sorted(os.listdir(backup_dir), reverse=True):
        file_path = os.path.join(backup_dir, file)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        print(f"- {file} ({size_mb:.2f} MB)")

def cleanup_old_backups(max_age_days=30):
    """Remove backups older than max_age_days"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    if not os.path.exists(backup_dir):
        return
    
    now = datetime.datetime.now()
    deleted_count = 0
    
    for file in os.listdir(backup_dir):
        file_path = os.path.join(backup_dir, file)
        
        # Skip if not a file
        if not os.path.isfile(file_path):
            continue
        
        # Get file modification time
        mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        age_days = (now - mod_time).days
        
        # Delete if older than max_age_days
        if age_days > max_age_days:
            try:
                os.remove(file_path)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {file}: {str(e)}")
    
    if deleted_count > 0:
        print(f"Cleaned up {deleted_count} backup files older than {max_age_days} days.")

def main():
    """Main function to create backups"""
    print("Starting Ananda Cricket backup process...")
    
    # Backup database
    db_backup = backup_mysql_database()
    
    # Backup media files
    media_backup = backup_media_files()
    
    # Clean up old backups
    cleanup_old_backups()
    
    # Show download instructions
    download_backups()
    
    print("\nBackup process completed.")

if __name__ == "__main__":
    main()
