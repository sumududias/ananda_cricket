from django.core.management.base import BaseCommand
from django.db import connection
from cricket_stats.models import Match, Team

class Command(BaseCommand):
    help = 'Fix invalid team references in the Match model'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to fix invalid team references...'))
        
        # First, let's find matches with invalid team_id values
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, team_id, team_name, college_name 
                FROM cricket_stats_match 
                WHERE team_id IS NOT NULL AND team_id != ''
            """)
            matches = cursor.fetchall()
            
            fixed_count = 0
            skipped_count = 0
            
            for match_id, team_id, team_name, college_name in matches:
                try:
                    # Try to convert team_id to integer
                    int(team_id)
                    # If it succeeds, this is a valid team_id, so skip
                    skipped_count += 1
                    continue
                except (ValueError, TypeError):
                    # This is an invalid team_id (string instead of integer)
                    self.stdout.write(f"Found invalid team_id '{team_id}' for match {match_id}")
                    
                    # Check if there's a matching team by name
                    matching_team = None
                    if team_name:
                        matching_teams = Team.objects.filter(name__icontains=team_name)
                        if matching_teams.exists():
                            matching_team = matching_teams.first()
                    
                    # If no matching team found, try to find a default team or create one
                    if not matching_team:
                        # Try to find any team to use as a default
                        default_teams = Team.objects.all().order_by('id')
                        if default_teams.exists():
                            matching_team = default_teams.first()
                            self.stdout.write(self.style.WARNING(f"No matching team found for '{team_name}', using default team '{matching_team.name}'"))
                        else:
                            # Create a new team if none exists
                            team_name_to_use = team_name or team_id
                            matching_team = Team.objects.create(
                                name=team_name_to_use,
                                season="Unknown",
                                coach="Unknown"
                            )
                            self.stdout.write(self.style.WARNING(f"Created new team '{team_name_to_use}' as no teams exist"))
                    
                    # Update the match with the proper team ID
                    cursor.execute("""
                        UPDATE cricket_stats_match 
                        SET team_id = %s, team_name = %s 
                        WHERE id = %s
                    """, [
                        matching_team.id,  # Now we always have a valid team ID
                        team_name or team_id,  # Keep the original team_name or use team_id as fallback
                        match_id
                    ])
                    fixed_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Fixed {fixed_count} matches with invalid team references'))
        self.stdout.write(self.style.SUCCESS(f'Skipped {skipped_count} matches with valid team references'))
        
        # Verify the fix
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM cricket_stats_match 
                WHERE team_id IS NOT NULL AND team_id != '' AND team_id REGEXP '[^0-9]'
            """)
            invalid_count = cursor.fetchone()[0]
            
            if invalid_count > 0:
                self.stdout.write(self.style.WARNING(f'There are still {invalid_count} matches with invalid team references'))
            else:
                self.stdout.write(self.style.SUCCESS('All team references are now valid!'))
