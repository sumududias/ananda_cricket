import os
import django
import sys
import json
from django.db import connection

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ananda_cricket.settings')
django.setup()

from cricket_stats.models import Player, Match, MatchPlayer
from cricket_stats.models_choices import (
    BOWLING_STYLE_CHOICES, BATTING_STYLE_CHOICES, PLAYER_CLASS_CHOICES,
    VENUE_CHOICES, MATCH_RESULT_CHOICES, DISMISSAL_TYPE_CHOICES
)

def ensure_custom_choices_dir():
    """Ensure the custom_choices directory exists"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    choices_dir = os.path.join(base_dir, 'cricket_stats', 'custom_choices')
    if not os.path.exists(choices_dir):
        os.makedirs(choices_dir)
    return choices_dir

def create_empty_json_files():
    """Create empty JSON files for each choice type"""
    choices_dir = ensure_custom_choices_dir()
    choice_types = [
        'bowling_style', 'batting_style', 'player_class',
        'venue', 'match_result', 'dismissal_type'
    ]
    
    for choice_type in choice_types:
        file_path = os.path.join(choices_dir, f'{choice_type}.json')
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                json.dump([], f)
            print(f"Created empty JSON file for {choice_type}")

def apply_migrations():
    """Apply the migrations to convert from model-based dropdowns to choice-based dropdowns"""
    try:
        # Check if migration 0009 is already applied
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT app, name FROM django_migrations WHERE app = 'cricket_stats' AND name = '0009_convert_to_choice_fields'"
            )
            if cursor.fetchone():
                print("Migration 0009_convert_to_choice_fields already applied.")
                return
        
        # Apply the migration
        print("Applying migration 0009_convert_to_choice_fields...")
        os.system('python manage.py migrate cricket_stats 0009_convert_to_choice_fields')
        print("Migration applied successfully.")
        
    except Exception as e:
        print(f"Error applying migrations: {e}")
        sys.exit(1)

def update_player_fields():
    """Update Player model fields to use choice values"""
    try:
        # Update batting_style field
        players_with_batting_style = Player.objects.exclude(batting_style__isnull=True).exclude(batting_style='')
        for player in players_with_batting_style:
            # Find the closest match in BATTING_STYLE_CHOICES
            for choice_value, choice_display in BATTING_STYLE_CHOICES:
                if choice_display.lower() in player.batting_style.lower():
                    player.batting_style = choice_value
                    player.save(update_fields=['batting_style'])
                    print(f"Updated batting style for {player.first_name} {player.last_name} to {choice_value}")
                    break
        
        # Update bowling_style field
        players_with_bowling_style = Player.objects.exclude(bowling_style__isnull=True).exclude(bowling_style='')
        for player in players_with_bowling_style:
            # Find the closest match in BOWLING_STYLE_CHOICES
            for choice_value, choice_display in BOWLING_STYLE_CHOICES:
                if choice_display.lower() in player.bowling_style.lower():
                    player.bowling_style = choice_value
                    player.save(update_fields=['bowling_style'])
                    print(f"Updated bowling style for {player.first_name} {player.last_name} to {choice_value}")
                    break
        
        # Update player_class field
        players_with_player_class = Player.objects.exclude(player_class__isnull=True).exclude(player_class='')
        for player in players_with_player_class:
            # Find the closest match in PLAYER_CLASS_CHOICES
            for choice_value, choice_display in PLAYER_CLASS_CHOICES:
                if choice_display.lower() in player.player_class.lower():
                    player.player_class = choice_value
                    player.save(update_fields=['player_class'])
                    print(f"Updated player class for {player.first_name} {player.last_name} to {choice_value}")
                    break
    
    except Exception as e:
        print(f"Error updating player fields: {e}")

def update_match_fields():
    """Update Match model fields to use choice values"""
    try:
        # Update venue field
        matches_with_venue = Match.objects.exclude(venue__isnull=True).exclude(venue='')
        for match in matches_with_venue:
            # Find the closest match in VENUE_CHOICES
            for choice_value, choice_display in VENUE_CHOICES:
                if choice_display.lower() in match.venue.lower():
                    match.venue = choice_value
                    match.save(update_fields=['venue'])
                    print(f"Updated venue for match {match.id} to {choice_value}")
                    break
        
        # Update result field
        matches_with_result = Match.objects.exclude(result__isnull=True).exclude(result='')
        for match in matches_with_result:
            # Find the closest match in MATCH_RESULT_CHOICES
            for choice_value, choice_display in MATCH_RESULT_CHOICES:
                if choice_display.lower() in match.result.lower():
                    match.result = choice_value
                    match.save(update_fields=['result'])
                    print(f"Updated result for match {match.id} to {choice_value}")
                    break
    
    except Exception as e:
        print(f"Error updating match fields: {e}")

def update_match_player_fields():
    """Update MatchPlayer model fields to use choice values"""
    try:
        # Update how_out field
        match_players_with_how_out = MatchPlayer.objects.exclude(how_out__isnull=True).exclude(how_out='')
        for match_player in match_players_with_how_out:
            # Find the closest match in DISMISSAL_TYPE_CHOICES
            for choice_value, choice_display in DISMISSAL_TYPE_CHOICES:
                if choice_display.lower() in match_player.how_out.lower():
                    match_player.how_out = choice_value
                    match_player.save(update_fields=['how_out'])
                    print(f"Updated how_out for match player {match_player.id} to {choice_value}")
                    break
    
    except Exception as e:
        print(f"Error updating match player fields: {e}")

if __name__ == "__main__":
    print("Starting dropdown migration process...")
    
    # Create empty JSON files for custom choices
    create_empty_json_files()
    
    # Apply the migrations
    apply_migrations()
    
    # Update model fields to use choice values
    update_player_fields()
    update_match_fields()
    update_match_player_fields()
    
    print("Dropdown migration completed successfully!")
