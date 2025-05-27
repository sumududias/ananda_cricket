from django.core.management.base import BaseCommand
import pandas as pd
from cricket_stats.models import MatchFormat, Team, Player, Match, MatchPlayer
from django.contrib.auth.models import User
from datetime import datetime
import os

class Command(BaseCommand):
    help = 'Import data from Excel files'

    def add_arguments(self, parser):
        parser.add_argument('--formats', type=str, help='Path to match formats Excel')
        parser.add_argument('--teams', type=str, help='Path to teams Excel')
        parser.add_argument('--players', type=str, help='Path to players Excel')
        parser.add_argument('--matches', type=str, help='Path to matches Excel')
        parser.add_argument('--match-players', type=str, help='Path to match players Excel')

    def handle(self, *args, **options):
        if options['formats']:
            self.import_formats(options['formats'])
        if options['teams']:
            self.import_teams(options['teams'])
        if options['players']:
            self.import_players(options['players'])
        if options['matches']:
            self.import_matches(options['matches'])
        if options['match_players']:
            self.import_match_players(options['match_players'])

    def import_formats(self, file_path):
        df = pd.read_excel(file_path)
        count = 0
        for _, row in df.iterrows():
            try:
                format_obj, created = MatchFormat.objects.get_or_create(
                    name=row['name'],
                    defaults={
                        'short_name': row['short_name'],
                        'overs': row['overs'],
                        'is_limited_overs': row['is_limited_overs']
                    }
                )
                if created:
                    count += 1
                else:
                    # Update existing format
                    format_obj.short_name = row['short_name']
                    format_obj.overs = row['overs']
                    format_obj.is_limited_overs = row['is_limited_overs']
                    format_obj.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing format {row["name"]}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} match formats'))

    def import_teams(self, file_path):
        df = pd.read_excel(file_path)
        count = 0
        for _, row in df.iterrows():
            try:
                # Handle captain reference
                captain = None
                if 'captain_name' in row and pd.notna(row['captain_name']):
                    captain_parts = row['captain_name'].split()
                    if len(captain_parts) > 1:
                        first_name = ' '.join(captain_parts[:-1])
                        last_name = captain_parts[-1]
                        captain = Player.objects.filter(first_name=first_name, last_name=last_name).first()
                
                team_obj, created = Team.objects.get_or_create(
                    name=row['name'],
                    season=row['season'],
                    defaults={
                        'coach': row['coach'] if 'coach' in row and pd.notna(row['coach']) else '',
                        'captain': captain
                    }
                )
                
                if created:
                    count += 1
                else:
                    # Update existing team
                    if 'coach' in row and pd.notna(row['coach']):
                        team_obj.coach = row['coach']
                    if captain:
                        team_obj.captain = captain
                    team_obj.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing team {row["name"]}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} teams'))

    def import_players(self, file_path):
        df = pd.read_excel(file_path)
        count = 0
        for _, row in df.iterrows():
            try:
                # Parse date of birth
                dob = None
                if 'dob' in row and pd.notna(row['dob']):
                    if isinstance(row['dob'], str):
                        try:
                            dob = datetime.strptime(row['dob'], '%Y-%m-%d').date()
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f'Invalid date format for {row["first_name"]} {row["last_name"]}: {row["dob"]}'))
                    else:
                        dob = row['dob']
                
                player_obj, created = Player.objects.get_or_create(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    defaults={
                        'dob': dob,
                        'role': row['role'] if 'role' in row and pd.notna(row['role']) else 'BAT',
                        'batting_style': row['batting_style'] if 'batting_style' in row and pd.notna(row['batting_style']) else 'RHB',
                        'bowling_style': row['bowling_style'] if 'bowling_style' in row and pd.notna(row['bowling_style']) else '',
                        'is_active': row['is_active'] if 'is_active' in row and pd.notna(row['is_active']) else True
                    }
                )
                
                if created:
                    count += 1
                else:
                    # Update existing player
                    if dob:
                        player_obj.dob = dob
                    if 'role' in row and pd.notna(row['role']):
                        player_obj.role = row['role']
                    if 'batting_style' in row and pd.notna(row['batting_style']):
                        player_obj.batting_style = row['batting_style']
                    if 'bowling_style' in row and pd.notna(row['bowling_style']):
                        player_obj.bowling_style = row['bowling_style']
                    if 'is_active' in row and pd.notna(row['is_active']):
                        player_obj.is_active = row['is_active']
                    player_obj.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing player {row["first_name"]} {row["last_name"]}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} players'))

    def import_matches(self, file_path):
        df = pd.read_excel(file_path)
        count = 0
        for _, row in df.iterrows():
            try:
                # Get related objects
                team = Team.objects.filter(name=row['team_name']).first()
                if not team:
                    self.stdout.write(self.style.WARNING(f'Team not found: {row["team_name"]}'))
                    continue
                
                format_obj = MatchFormat.objects.filter(name=row['format_name']).first()
                if not format_obj:
                    self.stdout.write(self.style.WARNING(f'Match format not found: {row["format_name"]}'))
                    continue
                
                # Parse match date
                match_date = None
                if 'match_date' in row and pd.notna(row['match_date']):
                    if isinstance(row['match_date'], str):
                        try:
                            match_date = datetime.strptime(row['match_date'], '%Y-%m-%d').date()
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f'Invalid date format for match: {row["match_date"]}'))
                            continue
                    else:
                        match_date = row['match_date']
                else:
                    self.stdout.write(self.style.WARNING('Match date is required'))
                    continue
                
                # Handle man of the match
                man_of_match = None
                if 'man_of_match_name' in row and pd.notna(row['man_of_match_name']):
                    mom_parts = row['man_of_match_name'].split()
                    if len(mom_parts) > 1:
                        first_name = ' '.join(mom_parts[:-1])
                        last_name = mom_parts[-1]
                        man_of_match = Player.objects.filter(first_name=first_name, last_name=last_name).first()
                
                # Generate a unique name if not provided
                match_name = row['name'] if 'name' in row and pd.notna(row['name']) else f"{team.name} vs {row['opponent']} - {match_date}"
                
                match_obj, created = Match.objects.get_or_create(
                    team=team,
                    opponent=row['opponent'],
                    match_date=match_date,
                    defaults={
                        'name': match_name,
                        'venue': row['venue'] if 'venue' in row and pd.notna(row['venue']) else '',
                        'format': format_obj,
                        'result': row['result'] if 'result' in row and pd.notna(row['result']) else '',
                        'team_name': team.name,
                        'college_name': 'Ananda College',
                        'toss_winner': row['toss_winner'] if 'toss_winner' in row and pd.notna(row['toss_winner']) else '',
                        'toss_decision': row['toss_decision'] if 'toss_decision' in row and pd.notna(row['toss_decision']) else '',
                        'man_of_match': man_of_match
                    }
                )
                
                if created:
                    count += 1
                else:
                    # Update existing match
                    match_obj.name = match_name
                    if 'venue' in row and pd.notna(row['venue']):
                        match_obj.venue = row['venue']
                    match_obj.format = format_obj
                    if 'result' in row and pd.notna(row['result']):
                        match_obj.result = row['result']
                    if 'toss_winner' in row and pd.notna(row['toss_winner']):
                        match_obj.toss_winner = row['toss_winner']
                    if 'toss_decision' in row and pd.notna(row['toss_decision']):
                        match_obj.toss_decision = row['toss_decision']
                    if man_of_match:
                        match_obj.man_of_match = man_of_match
                    match_obj.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing match {row.get("name", "unknown")}: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} matches'))

    def import_match_players(self, file_path):
        df = pd.read_excel(file_path)
        count = 0
        for _, row in df.iterrows():
            try:
                # Find the match
                match_date = None
                if 'match_date' in row and pd.notna(row['match_date']):
                    if isinstance(row['match_date'], str):
                        try:
                            match_date = datetime.strptime(row['match_date'], '%Y-%m-%d').date()
                        except ValueError:
                            self.stdout.write(self.style.WARNING(f'Invalid date format for match: {row["match_date"]}'))
                            continue
                    else:
                        match_date = row['match_date']
                else:
                    self.stdout.write(self.style.WARNING('Match date is required'))
                    continue
                
                opponent = row['opponent'] if 'opponent' in row and pd.notna(row['opponent']) else None
                if not opponent:
                    self.stdout.write(self.style.WARNING('Opponent is required'))
                    continue
                
                match = Match.objects.filter(match_date=match_date, opponent=opponent).first()
                if not match:
                    self.stdout.write(self.style.WARNING(f'Match not found: {match_date} vs {opponent}'))
                    continue
                
                # Find the player
                player_name = row['player_name'] if 'player_name' in row and pd.notna(row['player_name']) else None
                if not player_name:
                    self.stdout.write(self.style.WARNING('Player name is required'))
                    continue
                
                player_parts = player_name.split()
                if len(player_parts) > 1:
                    first_name = ' '.join(player_parts[:-1])
                    last_name = player_parts[-1]
                    player = Player.objects.filter(first_name=first_name, last_name=last_name).first()
                    if not player:
                        self.stdout.write(self.style.WARNING(f'Player not found: {player_name}'))
                        continue
                else:
                    self.stdout.write(self.style.WARNING(f'Invalid player name format: {player_name}'))
                    continue
                
                # Get innings number
                innings_number = int(row['innings_number']) if 'innings_number' in row and pd.notna(row['innings_number']) else 1
                
                # Create or update match player
                mp_obj, created = MatchPlayer.objects.get_or_create(
                    match=match,
                    player=player,
                    innings_number=innings_number,
                    defaults={
                        'batting_order': int(row['batting_order']) if 'batting_order' in row and pd.notna(row['batting_order']) else 0,
                        'runs_scored': int(row['runs_scored']) if 'runs_scored' in row and pd.notna(row['runs_scored']) else 0,
                        'balls_faced': int(row['balls_faced']) if 'balls_faced' in row and pd.notna(row['balls_faced']) else 0,
                        'fours': int(row['fours']) if 'fours' in row and pd.notna(row['fours']) else 0,
                        'sixes': int(row['sixes']) if 'sixes' in row and pd.notna(row['sixes']) else 0,
                        'how_out': row['how_out'] if 'how_out' in row and pd.notna(row['how_out']) else '',
                        'overs_bowled': float(row['overs_bowled']) if 'overs_bowled' in row and pd.notna(row['overs_bowled']) else 0,
                        'maidens_bowled': int(row['maidens_bowled']) if 'maidens_bowled' in row and pd.notna(row['maidens_bowled']) else 0,
                        'runs_conceded': int(row['runs_conceded']) if 'runs_conceded' in row and pd.notna(row['runs_conceded']) else 0,
                        'wickets_taken': int(row['wickets_taken']) if 'wickets_taken' in row and pd.notna(row['wickets_taken']) else 0,
                        'wides': int(row['wides']) if 'wides' in row and pd.notna(row['wides']) else 0,
                        'no_balls': int(row['no_balls']) if 'no_balls' in row and pd.notna(row['no_balls']) else 0,
                        'is_playing_xi': True
                    }
                )
                
                if created:
                    count += 1
                else:
                    # Update existing match player
                    if 'batting_order' in row and pd.notna(row['batting_order']):
                        mp_obj.batting_order = int(row['batting_order'])
                    if 'runs_scored' in row and pd.notna(row['runs_scored']):
                        mp_obj.runs_scored = int(row['runs_scored'])
                    if 'balls_faced' in row and pd.notna(row['balls_faced']):
                        mp_obj.balls_faced = int(row['balls_faced'])
                    if 'fours' in row and pd.notna(row['fours']):
                        mp_obj.fours = int(row['fours'])
                    if 'sixes' in row and pd.notna(row['sixes']):
                        mp_obj.sixes = int(row['sixes'])
                    if 'how_out' in row and pd.notna(row['how_out']):
                        mp_obj.how_out = row['how_out']
                    if 'overs_bowled' in row and pd.notna(row['overs_bowled']):
                        mp_obj.overs_bowled = float(row['overs_bowled'])
                    if 'maidens_bowled' in row and pd.notna(row['maidens_bowled']):
                        mp_obj.maidens_bowled = int(row['maidens_bowled'])
                    if 'runs_conceded' in row and pd.notna(row['runs_conceded']):
                        mp_obj.runs_conceded = int(row['runs_conceded'])
                    if 'wickets_taken' in row and pd.notna(row['wickets_taken']):
                        mp_obj.wickets_taken = int(row['wickets_taken'])
                    if 'wides' in row and pd.notna(row['wides']):
                        mp_obj.wides = int(row['wides'])
                    if 'no_balls' in row and pd.notna(row['no_balls']):
                        mp_obj.no_balls = int(row['no_balls'])
                    mp_obj.save()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error importing match player: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS(f'Imported {count} match players'))
