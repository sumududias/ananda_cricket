#!/usr/bin/env python
"""
Script to fix migration issues by creating a fake migration history
"""
import os
import django
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

def fix_migrations():
    """Fix migration issues by creating a fake migration history"""
    print("Starting migration fix...")
    
    # Create django_migrations table if it doesn't exist
    with connection.cursor() as cursor:
        # Check if django_migrations table exists
        cursor.execute("SHOW TABLES LIKE 'django_migrations'")
        if not cursor.fetchone():
            print("Creating django_migrations table...")
            cursor.execute("""
                CREATE TABLE `django_migrations` (
                    `id` int(11) NOT NULL AUTO_INCREMENT,
                    `app` varchar(255) NOT NULL,
                    `name` varchar(255) NOT NULL,
                    `applied` datetime(6) NOT NULL,
                    PRIMARY KEY (`id`)
                )
            """)
        
        # Clear existing migration records
        print("Clearing existing migration records...")
        cursor.execute("DELETE FROM django_migrations")
        
        # Insert records for all migrations except the problematic ones
        print("Creating fake migration history...")
        
        # Django core app migrations
        migrations = [
            ('contenttypes', '0001_initial'),
            ('contenttypes', '0002_remove_content_type_name'),
            ('auth', '0001_initial'),
            ('auth', '0002_alter_permission_name_max_length'),
            ('auth', '0003_alter_user_email_max_length'),
            ('auth', '0004_alter_user_username_opts'),
            ('auth', '0005_alter_user_last_login_null'),
            ('auth', '0006_require_contenttypes_0002'),
            ('auth', '0007_alter_validators_add_error_messages'),
            ('auth', '0008_alter_user_username_max_length'),
            ('auth', '0009_alter_user_last_name_max_length'),
            ('auth', '0010_alter_group_name_max_length'),
            ('auth', '0011_update_proxy_permissions'),
            ('auth', '0012_alter_user_first_name_max_length'),
            ('admin', '0001_initial'),
            ('admin', '0002_logentry_remove_auto_add'),
            ('admin', '0003_logentry_add_action_flag_choices'),
            ('sessions', '0001_initial'),
            # Cricket stats migrations (excluding the problematic one)
            ('cricket_stats', '0001_initial'),
            ('cricket_stats', '0002_add_match_formats'),
            ('cricket_stats', '0003_remove_matchformat_days_match_match_days_and_more'),
            ('cricket_stats', '0004_alter_matchplayer_options_and_more'),
            ('cricket_stats', '0005_matchplayer_catches_matchplayer_direct_hits_and_more'),
            ('cricket_stats', '0006_trainingsession_alter_playerattendance_options_and_more')
            # Deliberately excluding 0007_fix_team_foreign_key
        ]
        
        # Insert fake migration records with current timestamp
        for app, name in migrations:
            print(f"  - Marking {app}.{name} as applied")
            cursor.execute(
                "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, NOW())",
                [app, name]
            )
    
    print("\nMigration fix completed.")
    print("Now run the rebuild_database.py script again.")

if __name__ == "__main__":
    # Ask for confirmation
    print("WARNING: This will modify your migration history.")
    print("It will mark certain migrations as already applied.")
    response = input("Are you sure you want to proceed? (yes/no): ")
    
    if response.lower() == 'yes':
        fix_migrations()
    else:
        print("Migration fix cancelled.")
