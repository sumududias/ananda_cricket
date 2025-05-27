#!/usr/bin/env python
"""
Script to mark all migrations as applied without actually running them
This is useful when the database schema is already correct but the migration records are out of sync
"""
import os
import django
import subprocess

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fake_all_migrations():
    """Mark all migrations as applied without actually running them"""
    print("Marking all migrations as applied...")
    
    # First, try to fake the initial migration for cricket_stats
    try:
        subprocess.run(
            ["python", "manage.py", "migrate", "cricket_stats", "0001_initial", "--fake"],
            check=True
        )
        print("Faked initial cricket_stats migration")
    except subprocess.CalledProcessError:
        print("Failed to fake initial cricket_stats migration")
    
    # Then, try to fake all migrations
    try:
        subprocess.run(
            ["python", "manage.py", "migrate", "--fake"],
            check=True
        )
        print("Faked all migrations")
    except subprocess.CalledProcessError:
        print("Failed to fake all migrations")
    
    print("Migration faking completed")

if __name__ == "__main__":
    fake_all_migrations()
