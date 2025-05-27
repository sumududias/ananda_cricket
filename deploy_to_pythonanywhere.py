#!/usr/bin/env python
"""
Safe deployment script for Ananda Cricket on PythonAnywhere.
Run this script on PythonAnywhere to safely update your application.
"""
import os
import sys
import subprocess
import datetime

def run_command(command):
    """Run a shell command and print output"""
    print(f"\n>>> Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(f"STDERR: {result.stderr}")
    if result.returncode != 0:
        print(f"WARNING: Command exited with code {result.returncode}")
    return result.returncode == 0

def main():
    """Main deployment function"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"Starting deployment at {timestamp}")
    
    # 1. Create backup using file system backup instead of database dump
    print("\n=== Creating backup ===")
    backup_dir = os.path.join("backups", f"backup_{timestamp}")
    if not os.path.exists("backups"):
        os.makedirs("backups")
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Backup media files
    media_backup = os.path.join(backup_dir, "media")
    if os.path.exists("media"):
        run_command(f"cp -r media {media_backup}")
    
    # Backup code files (excluding .git, __pycache__, etc.)
    run_command(f"find . -type f -not -path \"*/\.*\" -not -path \"*/venv/*\" -not -path \"*/__pycache__/*\" -not -path \"*/backups/*\" -exec cp --parents {{}} {backup_dir} \;")
    
    print(f"Backup created at {backup_dir}")
    
    
    # 2. Save local changes
    print("\n=== Saving local changes ===")
    run_command("git stash")
    
    # 3. Pull latest code
    print("\n=== Pulling latest code ===")
    run_command("git pull origin main")
    
    # 4. Restore local changes
    print("\n=== Restoring local changes ===")
    run_command("git stash pop")
    
    # 5. Restart web app
    print("\n=== Restarting web app ===")
    run_command("touch /var/www/anandacricket_pythonanywhere_com_wsgi.py")
    
    print("\n=== Deployment completed successfully ===")
    print("Your application should be updated now.")
    print("If you need to run migrations, do it manually with:")
    print("python manage.py migrate")

if __name__ == "__main__":
    main()
