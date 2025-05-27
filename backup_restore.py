#!/usr/bin/env python
"""
Script to backup and restore the Ananda Cricket system
Handles database, media files, and code backup
"""
import os
import sys
import django
import datetime
import subprocess
import shutil
import zipfile
import argparse
import glob
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
    backup_file = os.path.join(backup_dir, f'ananda_cricket_db_{timestamp}.sql')
    
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
        print(f"Error creating database backup: {str(e)}")
        return None

def backup_media_files():
    """Backup media files"""
    backup_dir = create_backup_directory()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_file = os.path.join(backup_dir, f'ananda_cricket_media_{timestamp}.zip')
    
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

def backup_code():
    """Backup code using git"""
    backup_dir = create_backup_directory()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_file = os.path.join(backup_dir, f'ananda_cricket_code_{timestamp}.zip')
    
    try:
        # Get git status
        result = subprocess.run(['git', 'status', '--porcelain'], 
                               cwd=settings.BASE_DIR,
                               capture_output=True, 
                               text=True)
        
        # Check if there are uncommitted changes
        if result.stdout.strip():
            print("Warning: There are uncommitted changes in your repository.")
            print("Consider committing your changes before backing up.")
        
        # Create a zip of the entire codebase (excluding .git, __pycache__, etc.)
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(settings.BASE_DIR):
                # Skip directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'backups', 'media', 'env', 'venv', '.venv', 'ananda_cricket_env']]
                
                for file in files:
                    if file.endswith('.pyc') or file.endswith('.pyo'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, settings.BASE_DIR)
                    zipf.write(file_path, arcname)
        
        print(f"Code backup created at {zip_file}")
        return zip_file
    except Exception as e:
        print(f"Error backing up code: {str(e)}")
        return None

def create_full_backup():
    """Create a full backup of database, media files, and code"""
    print("Starting full backup process...")
    
    # Backup database
    db_backup = backup_mysql_database()
    
    # Backup media files
    media_backup = backup_media_files()
    
    # Backup code
    code_backup = backup_code()
    
    # Create a manifest file
    backup_dir = create_backup_directory()
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    manifest_file = os.path.join(backup_dir, f'backup_manifest_{timestamp}.txt')
    
    with open(manifest_file, 'w') as f:
        f.write(f"Ananda Cricket Full Backup - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Database Backup: {os.path.basename(db_backup) if db_backup else 'Failed'}\n")
        f.write(f"Media Backup: {os.path.basename(media_backup) if media_backup else 'Failed'}\n")
        f.write(f"Code Backup: {os.path.basename(code_backup) if code_backup else 'Failed'}\n")
    
    print(f"Backup manifest created at {manifest_file}")
    print("Full backup completed.")

def restore_database(backup_file):
    """Restore database from backup file"""
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    # Get database settings
    db_settings = settings.DATABASES['default']
    
    if db_settings['ENGINE'] != 'django.db.backends.mysql':
        print("This script is intended for MySQL databases only.")
        return False
    
    try:
        # Construct mysql command
        cmd = [
            'mysql',
            '-u', db_settings['USER'],
            f"--password={db_settings['PASSWORD']}",
            '-h', db_settings.get('HOST', 'localhost'),
        ]
        
        # Execute the command
        with open(backup_file, 'r') as f:
            process = subprocess.run(cmd, stdin=f, check=True)
        
        print(f"Database restored from {backup_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error restoring database: {str(e)}")
        return False

def restore_media_files(backup_file):
    """Restore media files from backup"""
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    media_dir = settings.MEDIA_ROOT
    
    # Create media directory if it doesn't exist
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    try:
        # Extract the zip file
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(os.path.dirname(media_dir))
        
        print(f"Media files restored from {backup_file}")
        return True
    except Exception as e:
        print(f"Error restoring media files: {str(e)}")
        return False

def restore_code(backup_file):
    """Restore code from backup"""
    if not os.path.exists(backup_file):
        print(f"Backup file not found: {backup_file}")
        return False
    
    # Create a temporary directory for extraction
    temp_dir = os.path.join(settings.BASE_DIR, 'temp_restore')
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        # Extract the zip file
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Ask for confirmation
        print(f"Code will be restored from {backup_file}")
        print("WARNING: This will overwrite your current code!")
        confirm = input("Are you sure you want to proceed? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("Code restore cancelled.")
            shutil.rmtree(temp_dir)
            return False
        
        # Copy files from temp directory to project directory
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                src_path = os.path.join(root, file)
                rel_path = os.path.relpath(src_path, temp_dir)
                dst_path = os.path.join(settings.BASE_DIR, rel_path)
                
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                
                # Copy file
                shutil.copy2(src_path, dst_path)
        
        # Clean up
        shutil.rmtree(temp_dir)
        
        print(f"Code restored from {backup_file}")
        return True
    except Exception as e:
        print(f"Error restoring code: {str(e)}")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        return False

def list_backups():
    """List available backups"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    if not os.path.exists(backup_dir) or not os.listdir(backup_dir):
        print("No backups found.")
        return
    
    # Group backups by type
    db_backups = sorted(glob.glob(os.path.join(backup_dir, '*_db_*.sql')), reverse=True)
    media_backups = sorted(glob.glob(os.path.join(backup_dir, '*_media_*.zip')), reverse=True)
    code_backups = sorted(glob.glob(os.path.join(backup_dir, '*_code_*.zip')), reverse=True)
    
    print("\nAvailable Database Backups:")
    for i, file_path in enumerate(db_backups):
        file = os.path.basename(file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. {file} ({size_mb:.2f} MB) - {date}")
    
    print("\nAvailable Media Backups:")
    for i, file_path in enumerate(media_backups):
        file = os.path.basename(file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. {file} ({size_mb:.2f} MB) - {date}")
    
    print("\nAvailable Code Backups:")
    for i, file_path in enumerate(code_backups):
        file = os.path.basename(file_path)
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. {file} ({size_mb:.2f} MB) - {date}")
    
    return {
        'db': db_backups,
        'media': media_backups,
        'code': code_backups
    }

def restore_interactive():
    """Interactive restore process"""
    print("Starting interactive restore process...")
    
    # List available backups
    backups = list_backups()
    
    if not backups:
        return
    
    # Select database backup
    db_choice = None
    if backups['db']:
        db_choice = input("\nEnter the number of the database backup to restore (or 0 to skip): ")
        if db_choice.isdigit() and 1 <= int(db_choice) <= len(backups['db']):
            db_file = backups['db'][int(db_choice) - 1]
        else:
            db_file = None
            print("Skipping database restore.")
    else:
        db_file = None
        print("No database backups found.")
    
    # Select media backup
    media_choice = None
    if backups['media']:
        media_choice = input("\nEnter the number of the media backup to restore (or 0 to skip): ")
        if media_choice.isdigit() and 1 <= int(media_choice) <= len(backups['media']):
            media_file = backups['media'][int(media_choice) - 1]
        else:
            media_file = None
            print("Skipping media restore.")
    else:
        media_file = None
        print("No media backups found.")
    
    # Select code backup
    code_choice = None
    if backups['code']:
        code_choice = input("\nEnter the number of the code backup to restore (or 0 to skip): ")
        if code_choice.isdigit() and 1 <= int(code_choice) <= len(backups['code']):
            code_file = backups['code'][int(code_choice) - 1]
        else:
            code_file = None
            print("Skipping code restore.")
    else:
        code_file = None
        print("No code backups found.")
    
    # Confirm restore
    print("\nRestore Summary:")
    print(f"Database: {os.path.basename(db_file) if db_file else 'Skip'}")
    print(f"Media: {os.path.basename(media_file) if media_file else 'Skip'}")
    print(f"Code: {os.path.basename(code_file) if code_file else 'Skip'}")
    
    confirm = input("\nAre you sure you want to proceed with the restore? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Restore cancelled.")
        return
    
    # Perform restore
    success = True
    
    if db_file:
        print("\nRestoring database...")
        if not restore_database(db_file):
            success = False
    
    if media_file:
        print("\nRestoring media files...")
        if not restore_media_files(media_file):
            success = False
    
    if code_file:
        print("\nRestoring code...")
        if not restore_code(code_file):
            success = False
    
    if success:
        print("\nRestore completed successfully.")
    else:
        print("\nRestore completed with errors. Please check the output above.")

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
    """Main function"""
    parser = argparse.ArgumentParser(description='Ananda Cricket Backup and Restore Tool')
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Backup command
    backup_parser = subparsers.add_parser('backup', help='Create a backup')
    backup_parser.add_argument('--type', choices=['db', 'media', 'code', 'full'], default='full',
                              help='Type of backup to create (default: full)')
    
    # Restore command
    restore_parser = subparsers.add_parser('restore', help='Restore from a backup')
    restore_parser.add_argument('--db', help='Database backup file to restore')
    restore_parser.add_argument('--media', help='Media backup file to restore')
    restore_parser.add_argument('--code', help='Code backup file to restore')
    restore_parser.add_argument('--interactive', action='store_true', help='Interactive restore mode')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List available backups')
    
    # Cleanup command
    cleanup_parser = subparsers.add_parser('cleanup', help='Clean up old backups')
    cleanup_parser.add_argument('--days', type=int, default=30,
                               help='Remove backups older than this many days (default: 30)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == 'backup':
        if args.type == 'db':
            backup_mysql_database()
        elif args.type == 'media':
            backup_media_files()
        elif args.type == 'code':
            backup_code()
        else:  # full
            create_full_backup()
    
    elif args.command == 'restore':
        if args.interactive:
            restore_interactive()
        else:
            success = True
            if args.db:
                print(f"Restoring database from {args.db}...")
                if not restore_database(args.db):
                    success = False
            
            if args.media:
                print(f"Restoring media files from {args.media}...")
                if not restore_media_files(args.media):
                    success = False
            
            if args.code:
                print(f"Restoring code from {args.code}...")
                if not restore_code(args.code):
                    success = False
            
            if not (args.db or args.media or args.code):
                print("No restore options specified. Use --db, --media, --code, or --interactive")
                parser.print_help()
            elif success:
                print("Restore completed successfully.")
            else:
                print("Restore completed with errors. Please check the output above.")
    
    elif args.command == 'list':
        list_backups()
    
    elif args.command == 'cleanup':
        cleanup_old_backups(args.days)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
