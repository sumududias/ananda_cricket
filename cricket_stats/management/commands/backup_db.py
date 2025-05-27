from django.core.management.base import BaseCommand
from django.core.management import call_command
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Backup database to JSON and Excel formats'

    def handle(self, *args, **options):
        # Create backup directory if it doesn't exist
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        # Generate timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # JSON backup
        json_file = f'{backup_dir}/backup_{timestamp}.json'
        call_command('dumpdata', '--exclude', 'auth.permission', 
                    '--exclude', 'contenttypes', 
                    '--indent', '2',
                    output=json_file)

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created backup at {json_file}')
        )