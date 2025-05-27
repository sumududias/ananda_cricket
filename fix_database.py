#!/usr/bin/env python
"""
Script to fix database issues on PythonAnywhere
This script will:
1. Create missing tables (django_session, cricket_stats_tournament)
2. Apply all migrations
3. Verify database integrity
"""
import os
import sys
import django
from django.db import connection
from django.core.management import call_command

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def check_table_exists(table_name):
    """Check if a table exists in the database"""
    with connection.cursor() as cursor:
        tables = connection.introspection.table_names()
        return table_name in tables

def main():
    print("Starting database fix script...")
    
    # Check for django_session table
    if not check_table_exists('django_session'):
        print("django_session table missing. Creating...")
        call_command('migrate', 'sessions', interactive=False)
    else:
        print("django_session table exists.")
    
    # Check for cricket_stats_tournament table
    if not check_table_exists('cricket_stats_tournament'):
        print("cricket_stats_tournament table missing. Creating...")
        # This will be created by the migrations
    else:
        print("cricket_stats_tournament table exists.")
    
    # Apply all migrations
    print("Applying all migrations...")
    call_command('migrate', interactive=False)
    
    # Verify database integrity
    print("Verifying database integrity...")
    call_command('check', '--database', 'default')
    
    print("Database fix complete!")

if __name__ == "__main__":
    main()
