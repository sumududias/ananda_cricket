"""
Admin views for the cricket_stats app
"""
import os
import datetime
import subprocess
import zipfile
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
from django.contrib import messages
import glob

@staff_member_required
def backup_restore_view(request):
    """View for backup and restore functionality"""
    context = {}
    
    # Create backup directory if it doesn't exist
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Handle form submissions
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'backup':
            backup_type = request.POST.get('backup_type', 'full')
            result = create_backup(backup_type)
            
            if result['success']:
                messages.success(request, result['message'])
                context['message'] = result['message']
                context['message_type'] = 'success'
            else:
                messages.error(request, result['message'])
                context['message'] = result['message']
                context['message_type'] = 'error'
        
        elif action == 'restore':
            db_backup = request.POST.get('db_backup')
            media_backup = request.POST.get('media_backup')
            code_backup = request.POST.get('code_backup')
            
            result = restore_from_backup(db_backup, media_backup, code_backup)
            
            if result['success']:
                messages.success(request, result['message'])
                context['message'] = result['message']
                context['message_type'] = 'success'
            else:
                messages.error(request, result['message'])
                context['message'] = result['message']
                context['message_type'] = 'error'
        
        elif action == 'cleanup':
            days = int(request.POST.get('days', 30))
            result = cleanup_old_backups(days)
            
            if result['success']:
                messages.success(request, result['message'])
                context['message'] = result['message']
                context['message_type'] = 'success'
            else:
                messages.error(request, result['message'])
                context['message'] = result['message']
                context['message_type'] = 'error'
    
    # Get available backups
    backups = get_available_backups()
    context.update(backups)
    
    return render(request, 'admin/backup_restore.html', context)

def create_backup(backup_type):
    """Create a backup of the specified type"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if backup_type == 'db' or backup_type == 'full':
        # Database backup
        db_file = os.path.join(backup_dir, f'ananda_cricket_db_{timestamp}.sql')
        db_result = backup_mysql_database(db_file)
    
    if backup_type == 'media' or backup_type == 'full':
        # Media backup
        media_file = os.path.join(backup_dir, f'ananda_cricket_media_{timestamp}.zip')
        media_result = backup_media_files(media_file)
    
    if backup_type == 'code' or backup_type == 'full':
        # Code backup
        code_file = os.path.join(backup_dir, f'ananda_cricket_code_{timestamp}.zip')
        code_result = backup_code(code_file)
    
    # Create a manifest file for full backups
    if backup_type == 'full':
        manifest_file = os.path.join(backup_dir, f'backup_manifest_{timestamp}.txt')
        with open(manifest_file, 'w') as f:
            f.write(f"Ananda Cricket Full Backup - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Database Backup: {os.path.basename(db_file) if db_result['success'] else 'Failed'}\n")
            f.write(f"Media Backup: {os.path.basename(media_file) if media_result['success'] else 'Failed'}\n")
            f.write(f"Code Backup: {os.path.basename(code_file) if code_result['success'] else 'Failed'}\n")
        
        if db_result['success'] and media_result['success'] and code_result['success']:
            return {
                'success': True,
                'message': 'Full backup created successfully.'
            }
        else:
            return {
                'success': False,
                'message': 'Some parts of the backup failed. Check the manifest file for details.'
            }
    
    elif backup_type == 'db':
        return db_result
    elif backup_type == 'media':
        return media_result
    elif backup_type == 'code':
        return code_result
    else:
        return {
            'success': False,
            'message': f'Unknown backup type: {backup_type}'
        }

def backup_mysql_database(backup_file):
    """Backup MySQL database using mysqldump"""
    # Get database settings
    db_settings = settings.DATABASES['default']
    
    if db_settings['ENGINE'] != 'django.db.backends.mysql':
        return {
            'success': False,
            'message': 'This function only supports MySQL databases.'
        }
    
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
        return {
            'success': True,
            'message': f'Database backup created successfully.'
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'message': f'Error creating database backup: {str(e)}'
        }

def backup_media_files(backup_file):
    """Backup media files"""
    media_dir = settings.MEDIA_ROOT
    
    if not os.path.exists(media_dir):
        return {
            'success': False,
            'message': f'Media directory {media_dir} does not exist.'
        }
    
    try:
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(media_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(media_dir))
                    zipf.write(file_path, arcname)
        
        return {
            'success': True,
            'message': 'Media files backup created successfully.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error backing up media files: {str(e)}'
        }

def backup_code(backup_file):
    """Backup code using git"""
    try:
        # Create a zip of the entire codebase (excluding .git, __pycache__, etc.)
        with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(settings.BASE_DIR):
                # Skip directories
                dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'backups', 'media', 'env', 'venv', '.venv', 'ananda_cricket_env']]
                
                for file in files:
                    if file.endswith('.pyc') or file.endswith('.pyo'):
                        continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, settings.BASE_DIR)
                    zipf.write(file_path, arcname)
        
        return {
            'success': True,
            'message': 'Code backup created successfully.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error backing up code: {str(e)}'
        }

def restore_from_backup(db_backup=None, media_backup=None, code_backup=None):
    """Restore from backup files"""
    results = []
    success = True
    
    if db_backup:
        db_result = restore_database(db_backup)
        results.append(db_result['message'])
        if not db_result['success']:
            success = False
    
    if media_backup:
        media_result = restore_media_files(media_backup)
        results.append(media_result['message'])
        if not media_result['success']:
            success = False
    
    if code_backup:
        code_result = restore_code(code_backup)
        results.append(code_result['message'])
        if not code_result['success']:
            success = False
    
    if not (db_backup or media_backup or code_backup):
        return {
            'success': False,
            'message': 'No backup files selected for restore.'
        }
    
    return {
        'success': success,
        'message': '<br>'.join(results)
    }

def restore_database(backup_file):
    """Restore database from backup file"""
    if not os.path.exists(backup_file):
        return {
            'success': False,
            'message': f'Database backup file not found: {backup_file}'
        }
    
    # Get database settings
    db_settings = settings.DATABASES['default']
    
    if db_settings['ENGINE'] != 'django.db.backends.mysql':
        return {
            'success': False,
            'message': 'This function only supports MySQL databases.'
        }
    
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
        
        return {
            'success': True,
            'message': f'Database restored successfully from {os.path.basename(backup_file)}'
        }
    except subprocess.CalledProcessError as e:
        return {
            'success': False,
            'message': f'Error restoring database: {str(e)}'
        }

def restore_media_files(backup_file):
    """Restore media files from backup"""
    if not os.path.exists(backup_file):
        return {
            'success': False,
            'message': f'Media backup file not found: {backup_file}'
        }
    
    media_dir = settings.MEDIA_ROOT
    
    # Create media directory if it doesn't exist
    if not os.path.exists(media_dir):
        os.makedirs(media_dir)
    
    try:
        # Extract the zip file
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(os.path.dirname(media_dir))
        
        return {
            'success': True,
            'message': f'Media files restored successfully from {os.path.basename(backup_file)}'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'Error restoring media files: {str(e)}'
        }

def restore_code(backup_file):
    """Restore code from backup"""
    if not os.path.exists(backup_file):
        return {
            'success': False,
            'message': f'Code backup file not found: {backup_file}'
        }
    
    # Create a temporary directory for extraction
    temp_dir = os.path.join(settings.BASE_DIR, 'temp_restore')
    if os.path.exists(temp_dir):
        import shutil
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    try:
        # Extract the zip file
        with zipfile.ZipFile(backup_file, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Copy files from temp directory to project directory
        import shutil
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
        
        return {
            'success': True,
            'message': f'Code restored successfully from {os.path.basename(backup_file)}'
        }
    except Exception as e:
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)
        
        return {
            'success': False,
            'message': f'Error restoring code: {str(e)}'
        }

def get_available_backups():
    """Get available backups"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    if not os.path.exists(backup_dir):
        return {
            'backups': False
        }
    
    # Group backups by type
    db_backups_files = sorted(glob.glob(os.path.join(backup_dir, '*_db_*.sql')), reverse=True)
    media_backups_files = sorted(glob.glob(os.path.join(backup_dir, '*_media_*.zip')), reverse=True)
    code_backups_files = sorted(glob.glob(os.path.join(backup_dir, '*_code_*.zip')), reverse=True)
    
    db_backups = []
    for file_path in db_backups_files:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        db_backups.append({
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': f"{size_mb:.2f}",
            'date': date
        })
    
    media_backups = []
    for file_path in media_backups_files:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        media_backups.append({
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': f"{size_mb:.2f}",
            'date': date
        })
    
    code_backups = []
    for file_path in code_backups_files:
        size_mb = os.path.getsize(file_path) / (1024 * 1024)
        date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%Y-%m-%d %H:%M:%S')
        code_backups.append({
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': f"{size_mb:.2f}",
            'date': date
        })
    
    return {
        'backups': bool(db_backups or media_backups or code_backups),
        'db_backups': db_backups,
        'media_backups': media_backups,
        'code_backups': code_backups
    }

def cleanup_old_backups(max_age_days=30):
    """Remove backups older than max_age_days"""
    backup_dir = os.path.join(settings.BASE_DIR, 'backups')
    
    if not os.path.exists(backup_dir):
        return {
            'success': False,
            'message': 'Backup directory does not exist.'
        }
    
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
                return {
                    'success': False,
                    'message': f'Error deleting {file}: {str(e)}'
                }
    
    if deleted_count > 0:
        return {
            'success': True,
            'message': f'Cleaned up {deleted_count} backup files older than {max_age_days} days.'
        }
    else:
        return {
            'success': True,
            'message': f'No backup files older than {max_age_days} days found.'
        }
