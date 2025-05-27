#!/usr/bin/env python
"""
Script to completely rebuild the database tables from Django models
"""
import os
import django
import sys
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def rebuild_database():
    """Completely rebuild the database by dropping and recreating all tables"""
    print("Starting complete database rebuild...")
    
    # Disable foreign key checks to allow dropping tables in any order
    with connection.cursor() as cursor:
        print("Disabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        
        # Get list of all tables in the database
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        # Drop all existing tables
        print("Dropping all existing tables...")
        for table in tables:
            table_name = table[0]
            print(f"  - Dropping table: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
        
        # Re-enable foreign key checks
        print("Re-enabling foreign key checks...")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        print("All tables dropped successfully.")
    
    # Run Django migrations to recreate all tables properly
    print("\nRecreating all tables using Django migrations...")
    from django.core.management import call_command
    call_command('migrate', interactive=False)
    
    # Create a superuser if needed
    try:
        from django.contrib.auth.models import User
        if not User.objects.filter(is_superuser=True).exists():
            print("\nCreating a superuser account...")
            User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123'
            )
            print("Superuser created with username: 'admin' and password: 'admin123'")
            print("IMPORTANT: Please change this password immediately after logging in!")
    except Exception as e:
        print(f"Could not create superuser: {e}")
    
    print("\nDatabase rebuild completed successfully.")
    print("Now try accessing your application.")
    print("Remember to restart your web application:")
    print("touch /var/www/anandacricket_pythonanywhere_com_wsgi.py")

if __name__ == "__main__":
    # Ask for confirmation
    print("WARNING: This will DELETE ALL DATA in your database.")
    print("All existing tables will be dropped and recreated.")
    response = input("Are you sure you want to proceed? (yes/no): ")
    
    if response.lower() == 'yes':
        rebuild_database()
    else:
        print("Database rebuild cancelled.")
