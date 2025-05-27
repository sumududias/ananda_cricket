from django.core.management.base import BaseCommand
import pandas as pd
import os
from datetime import datetime
from cricket_stats.models import MatchFormat, Team, Player, Match, MatchPlayer

class Command(BaseCommand):
    help = 'Export data to Excel files for backup or sharing'

    def add_arguments(self, parser):
        parser.add_argument('--output-dir', type=str, default='exports', help='Directory to save exported files')
        parser.add_argument('--formats', action='store_true', help='Export match formats')
        parser.add_argument('--teams', action='store_true', help='Export teams')
        parser.add_argument('--players', action='store_true', help='Export players')
        parser.add_argument('--matches', action='store_true', help='Export matches')
        parser.add_argument('--match-players', action='store_true', help='Export match players')
        parser.add_argument('--all', action='store_true', help='Export all data')

    def handle(self, *args, **options):
        # Create output directory if it doesn't exist
        output_dir = options['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if options['all'] or options['formats']:
            self.export_formats(output_dir, timestamp)
        
        if options['all'] or options['teams']:
            self.export_teams(output_dir, timestamp)
        
        if options['all'] or options['players']:
            self.export_players(output_dir, timestamp)
        
        if options['all'] or options['matches']:
            self.export_matches(output_dir, timestamp)
        
        if options['all'] or options['match_players']:
            self.export_match_players(output_dir, timestamp)
        
        self.stdout.write(self.style.SUCCESS(f'Data exported to {output_dir}'))

    def export_formats(self, output_dir, timestamp):
        self.stdout.write('Exporting match formats...')
        formats = MatchFormat.objects.all()
        
        data = []
        for format_obj in formats:
            data.append({
                'name': format_obj.name,
                'short_name': format_obj.short_name,
                'overs': format_obj.overs,
                'is_limited_overs': format_obj.is_limited_overs
            })
        
        if data:
            df = pd.DataFrame(data)
            filename = os.path.join(output_dir, f'match_formats_{timestamp}.xlsx')
            df.to_excel(filename, index=False)
            self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} match formats to {filename}'))
        else:
            self.stdout.write(self.style.WARNING('No match formats to export'))

    def export_teams(self, output_dir, timestamp):
        self.stdout.write('Exporting teams...')
        teams = Team.objects.all()
        
        data = []
        for team in teams:
            captain_name = f"{team.captain.first_name} {team.captain.last_name}" if team.captain else ""
            data.append({
                'name': team.name,
                'season': team.season,
                'coach': team.coach,
                'captain_name': captain_name
            })
        
        if data:
            df = pd.DataFrame(data)
            filename = os.path.join(output_dir, f'teams_{timestamp}.xlsx')
            df.to_excel(filename, index=False)
            self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} teams to {filename}'))
        else:
            self.stdout.write(self.style.WARNING('No teams to export'))

    def export_players(self, output_dir, timestamp):
        self.stdout.write('Exporting players...')
        players = Player.objects.all()
        
        data = []
        for player in players:
            data.append({
                'first_name': player.first_name,
                'last_name': player.last_name,
                'dob': player.dob.strftime('%Y-%m-%d') if player.dob else '',
                'role': player.role,
                'batting_style': player.batting_style,
                'bowling_style': player.bowling_style,
                'is_active': player.is_active
            })
        
        if data:
            df = pd.DataFrame(data)
            filename = os.path.join(output_dir, f'players_{timestamp}.xlsx')
            df.to_excel(filename, index=False)
            self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} players to {filename}'))
        else:
            self.stdout.write(self.style.WARNING('No players to export'))

    def export_matches(self, output_dir, timestamp):
        self.stdout.write('Exporting matches...')
        matches = Match.objects.all()
        
        data = []
        for match in matches:
            man_of_match_name = f"{match.man_of_match.first_name} {match.man_of_match.last_name}" if match.man_of_match else ""
            data.append({
                'name': match.name,
                'team_name': match.team.name,
                'opponent': match.opponent,
                'match_date': match.match_date.strftime('%Y-%m-%d'),
                'venue': match.venue,
                'format_name': match.format.name,
                'result': match.result,
                'toss_winner': match.toss_winner,
                'toss_decision': match.toss_decision,
                'man_of_match_name': man_of_match_name
            })
        
        if data:
            df = pd.DataFrame(data)
            filename = os.path.join(output_dir, f'matches_{timestamp}.xlsx')
            df.to_excel(filename, index=False)
            self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} matches to {filename}'))
        else:
            self.stdout.write(self.style.WARNING('No matches to export'))

    def export_match_players(self, output_dir, timestamp):
        self.stdout.write('Exporting match players...')
        match_players = MatchPlayer.objects.all()
        
        data = []
        for mp in match_players:
            data.append({
                'match_date': mp.match.match_date.strftime('%Y-%m-%d'),
                'opponent': mp.match.opponent,
                'player_name': f"{mp.player.first_name} {mp.player.last_name}",
                'innings_number': mp.innings_number,
                'batting_order': mp.batting_order,
                'runs_scored': mp.runs_scored,
                'balls_faced': mp.balls_faced,
                'fours': mp.fours,
                'sixes': mp.sixes,
                'how_out': mp.how_out,
                'overs_bowled': mp.overs_bowled,
                'maidens_bowled': mp.maidens_bowled,
                'runs_conceded': mp.runs_conceded,
                'wickets_taken': mp.wickets_taken,
                'wides': mp.wides,
                'no_balls': mp.no_balls
            })
        
        if data:
            df = pd.DataFrame(data)
            filename = os.path.join(output_dir, f'match_players_{timestamp}.xlsx')
            df.to_excel(filename, index=False)
            self.stdout.write(self.style.SUCCESS(f'Exported {len(data)} match players to {filename}'))
        else:
            self.stdout.write(self.style.WARNING('No match players to export'))
