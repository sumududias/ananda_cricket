#!/usr/bin/env python
"""
Script to inspect the database structure and show all tables and columns
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def inspect_database():
    """Inspect the database structure and show all tables and columns"""
    print("Starting database inspection...")
    
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        
        print(f"Found {len(tables)} tables in the database:")
        for table in tables:
            table_name = table[0]
            print(f"\n{table_name}:")
            
            # Get columns for this table
            cursor.execute(f"DESCRIBE {table_name}")
            columns = cursor.fetchall()
            
            print(f"  Columns ({len(columns)}):")
            for column in columns:
                column_name = column[0]
                column_type = column[1]
                column_null = column[2]
                column_key = column[3]
                column_default = column[4]
                print(f"    {column_name}: {column_type}, Null: {column_null}, Key: {column_key}, Default: {column_default}")
        
        # Check specifically for the Tournament table and its columns
        print("\n--- Checking Tournament Table ---")
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_tournament'")
        if cursor.fetchone():
            print("Tournament table exists, checking columns...")
            cursor.execute("DESCRIBE cricket_stats_tournament")
            columns = cursor.fetchall()
            print(f"Tournament table has {len(columns)} columns:")
            for column in columns:
                print(f"  {column[0]}: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}")
        else:
            print("Tournament table does not exist!")
        
        # Check specifically for the Match table and its columns
        print("\n--- Checking Match Table ---")
        cursor.execute("SHOW TABLES LIKE 'cricket_stats_match'")
        if cursor.fetchone():
            print("Match table exists, checking columns...")
            cursor.execute("DESCRIBE cricket_stats_match")
            columns = cursor.fetchall()
            print(f"Match table has {len(columns)} columns:")
            for column in columns:
                print(f"  {column[0]}: {column[1]}, Null: {column[2]}, Key: {column[3]}, Default: {column[4]}")
        else:
            print("Match table does not exist!")
        
        # Check migration records
        print("\n--- Checking Migration Records ---")
        cursor.execute("SELECT id, app, name FROM django_migrations WHERE app = 'cricket_stats' ORDER BY id")
        migrations = cursor.fetchall()
        print(f"Found {len(migrations)} cricket_stats migrations:")
        for migration in migrations:
            print(f"  {migration[0]}: {migration[1]}.{migration[2]}")
    
    print("\nDatabase inspection completed.")

if __name__ == "__main__":
    inspect_database()
