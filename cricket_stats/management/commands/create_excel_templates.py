from django.core.management.base import BaseCommand
import pandas as pd
import os
from datetime import datetime

class Command(BaseCommand):
    help = 'Create empty Excel templates for data import'

    def add_arguments(self, parser):
        parser.add_argument('--output-dir', type=str, default='excel_templates', help='Directory to save template files')

    def handle(self, *args, **options):
        # Create output directory if it doesn't exist
        output_dir = options['output_dir']
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.create_match_formats_template(output_dir)
        self.create_teams_template(output_dir)
        self.create_players_template(output_dir)
        self.create_matches_template(output_dir)
        self.create_match_players_template(output_dir)
        
        self.stdout.write(self.style.SUCCESS(f'Excel templates created in {output_dir}'))

    def create_match_formats_template(self, output_dir):
        # Create sample data
        data = {
            'name': ['Limited Over Match', '2 or 3 Day Match', 'Limited Over Practice Match', '2 or 3 Day Practice Match'],
            'short_name': ['LOM', '2-3D', 'LOPM', '2-3DPM'],
            'overs': [50, 0, 50, 0],
            'is_limited_overs': [True, False, True, False]
        }
        
        df = pd.DataFrame(data)
        filename = os.path.join(output_dir, 'match_formats_template.xlsx')
        df.to_excel(filename, index=False)
        self.stdout.write(self.style.SUCCESS(f'Created match formats template: {filename}'))

    def create_teams_template(self, output_dir):
        # Create sample data
        data = {
            'name': ['Ananda College First XI', 'Ananda College Second XI'],
            'season': ['2025', '2025'],
            'coach': ['John Smith', 'David Jones'],
            'captain_name': ['Saman Perera', '']  # Full name of captain (must match a player)
        }
        
        df = pd.DataFrame(data)
        filename = os.path.join(output_dir, 'teams_template.xlsx')
        df.to_excel(filename, index=False)
        self.stdout.write(self.style.SUCCESS(f'Created teams template: {filename}'))

    def create_players_template(self, output_dir):
        # Create sample data
        data = {
            'first_name': ['Saman', 'Kamal', 'Nimal'],
            'last_name': ['Perera', 'Fernando', 'Silva'],
            'dob': ['2000-01-15', '2001-03-22', '2000-11-05'],
            'role': ['BAT', 'BOWL', 'AR'],  # BAT, BOWL, AR (all-rounder), WK (wicket-keeper)
            'batting_style': ['RHB', 'LHB', 'RHB'],  # RHB (right-hand bat), LHB (left-hand bat)
            'bowling_style': ['', 'RFM', 'OB'],  # RFM (right-arm fast-medium), OB (off-break), etc.
            'is_active': [True, True, True]
        }
        
        df = pd.DataFrame(data)
        filename = os.path.join(output_dir, 'players_template.xlsx')
        df.to_excel(filename, index=False)
        self.stdout.write(self.style.SUCCESS(f'Created players template: {filename}'))

    def create_matches_template(self, output_dir):
        # Create sample data
        data = {
            'team_name': ['Ananda College First XI', 'Ananda College First XI'],
            'opponent': ['Royal College', 'Nalanda College'],
            'match_date': ['2025-01-15', '2025-02-10'],
            'venue': ['SSC Ground', 'P Sara Oval'],
            'format_name': ['Limited Over Match', '2 or 3 Day Match'],
            'result': ['WON', 'LOST'],  # WON, LOST, DRAW, TIE, ABANDONED
            'toss_winner': ['Ananda College', 'Nalanda College'],
            'toss_decision': ['BAT', 'BOWL'],  # BAT, BOWL
            'man_of_match_name': ['Saman Perera', '']  # Full name of player (must match a player)
        }
        
        df = pd.DataFrame(data)
        filename = os.path.join(output_dir, 'matches_template.xlsx')
        df.to_excel(filename, index=False)
        self.stdout.write(self.style.SUCCESS(f'Created matches template: {filename}'))

    def create_match_players_template(self, output_dir):
        # Create sample data
        data = {
            'match_date': ['2025-01-15', '2025-01-15', '2025-01-15'],
            'opponent': ['Royal College', 'Royal College', 'Royal College'],
            'player_name': ['Saman Perera', 'Kamal Fernando', 'Nimal Silva'],
            'innings_number': [1, 1, 1],
            'batting_order': [1, 2, 3],
            'runs_scored': [85, 45, 32],
            'balls_faced': [110, 60, 40],
            'fours': [10, 5, 3],
            'sixes': [2, 1, 0],
            'how_out': ['Caught', 'Bowled', 'Not Out'],
            'overs_bowled': [0, 10.0, 8.0],
            'maidens_bowled': [0, 2, 1],
            'runs_conceded': [0, 35, 28],
            'wickets_taken': [0, 3, 2],
            'wides': [0, 2, 1],
            'no_balls': [0, 0, 1]
        }
        
        df = pd.DataFrame(data)
        filename = os.path.join(output_dir, 'match_players_template.xlsx')
        df.to_excel(filename, index=False)
        self.stdout.write(self.style.SUCCESS(f'Created match players template: {filename}'))
