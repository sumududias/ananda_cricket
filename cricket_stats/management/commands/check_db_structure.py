from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Check database structure of the Match table'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            # For MySQL
            cursor.execute("DESCRIBE cricket_stats_match")
            rows = cursor.fetchall()
            self.stdout.write(self.style.SUCCESS('Match table structure:'))
            for row in rows:
                self.stdout.write(f"Field: {row[0]}, Type: {row[1]}, Null: {row[2]}, Key: {row[3]}, Default: {row[4]}, Extra: {row[5]}")
