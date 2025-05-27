from django import forms
from django.forms import ModelForm, Select, TextInput, DateInput
from .models import Player, Match, MatchPlayer, BattingInnings, BowlingInnings
from .models_choices import (
    BOWLING_STYLE_CHOICES, BATTING_STYLE_CHOICES, PLAYER_CLASS_CHOICES,
    VENUE_CHOICES, MATCH_RESULT_CHOICES, DISMISSAL_TYPE_CHOICES
)

class PlayerForm(ModelForm):
    class Meta:
        model = Player
        fields = ['first_name', 'last_name', 'dob', 'jersey_number', 'batting_style', 
                  'bowling_style', 'primary_role', 'player_class', 'year_joined', 'is_active']
        widgets = {
            'dob': DateInput(attrs={'type': 'date'}),
            'batting_style': Select(attrs={'class': 'form-control select2'}),
            'bowling_style': Select(attrs={'class': 'form-control select2'}),
            'player_class': Select(attrs={'class': 'form-control select2'}),
        }

class MatchForm(ModelForm):
    class Meta:
        model = Match
        fields = ['name', 'team_name', 'team', 'opponent', 'match_date', 'venue', 
                  'format', 'match_days', 'toss_winner', 'toss_decision', 'result', 
                  'tournament', 'man_of_match']
        widgets = {
            'match_date': DateInput(attrs={'type': 'date'}),
            'venue': Select(attrs={'class': 'form-control select2'}),
            'result': Select(attrs={'class': 'form-control select2'}),
        }

class MatchPlayerForm(ModelForm):
    class Meta:
        model = MatchPlayer
        fields = ['player', 'innings_number', 'batting_order', 'runs_scored', 'balls_faced', 
                  'fours', 'sixes', 'how_out', 'bowler', 'fielder', 'overs_bowled', 
                  'maidens_bowled', 'runs_conceded', 'wickets_taken', 'wides', 'no_balls', 
                  'is_playing_xi', 'is_captain', 'is_keeper', 'catches', 'run_outs', 
                  'stumpings', 'direct_hits', 'dropped_catches', 'comments']
        widgets = {
            'how_out': Select(attrs={'class': 'form-control select2'}),
        }

class BattingInningsForm(ModelForm):
    class Meta:
        model = BattingInnings
        fields = ['player', 'match', 'innings_number', 'batting_position', 'runs_scored', 
                  'balls_faced', 'fours', 'sixes', 'how_out', 'bowler', 'fielder']
        widgets = {
            'how_out': Select(attrs={'class': 'form-control select2'}),
        }

class BowlingInningsForm(ModelForm):
    class Meta:
        model = BowlingInnings
        fields = ['player', 'match', 'innings_number', 'overs', 'maidens', 
                  'runs_conceded', 'wickets', 'wides', 'no_balls']

# Custom forms for adding new dropdown items
# Custom forms for adding new dropdown items
class BowlingStyleForm(forms.Form):
    value = forms.CharField(max_length=10, required=True, label='Value')
    display = forms.CharField(max_length=100, required=True, label='Display Text')

class BattingStyleForm(forms.Form):
    value = forms.CharField(max_length=10, required=True, label='Value')
    display = forms.CharField(max_length=100, required=True, label='Display Text')

class PlayerClassForm(forms.Form):
    value = forms.CharField(max_length=10, required=True, label='Value')
    display = forms.CharField(max_length=100, required=True, label='Display Text')

class VenueForm(forms.Form):
    value = forms.CharField(max_length=10, required=True, label='Value')
    display = forms.CharField(max_length=100, required=True, label='Display Text')

class MatchResultForm(forms.Form):
    value = forms.CharField(max_length=10, required=True, label='Value')
    display = forms.CharField(max_length=100, required=True, label='Display Text')

class DismissalTypeForm(forms.Form):
    value = forms.CharField(max_length=10, required=True, label='Value')
    display = forms.CharField(max_length=100, required=True, label='Display Text')
