from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
import json
import os

from .models_choices import (
    BOWLING_STYLE_CHOICES, BATTING_STYLE_CHOICES, PLAYER_CLASS_CHOICES,
    VENUE_CHOICES, MATCH_RESULT_CHOICES, DISMISSAL_TYPE_CHOICES
)
from .forms import (
    BowlingStyleForm, BattingStyleForm, PlayerClassForm,
    VenueForm, MatchResultForm, DismissalTypeForm
)

# Path to the custom choices JSON file
def get_choices_file_path(choice_type):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'cricket_stats', 'custom_choices', f'{choice_type}.json')

# Ensure the custom_choices directory exists
def ensure_choices_dir_exists():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    choices_dir = os.path.join(base_dir, 'cricket_stats', 'custom_choices')
    if not os.path.exists(choices_dir):
        os.makedirs(choices_dir)
    return choices_dir

# Load custom choices from JSON file
def load_custom_choices(choice_type):
    ensure_choices_dir_exists()
    file_path = get_choices_file_path(choice_type)
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

# Save custom choices to JSON file
def save_custom_choices(choice_type, choices):
    ensure_choices_dir_exists()
    file_path = get_choices_file_path(choice_type)
    with open(file_path, 'w') as f:
        json.dump(choices, f, indent=4)

# Get all choices (default + custom)
def get_all_choices(choice_type):
    default_choices = {
        'bowling_style': BOWLING_STYLE_CHOICES,
        'batting_style': BATTING_STYLE_CHOICES,
        'player_class': PLAYER_CLASS_CHOICES,
        'venue': VENUE_CHOICES,
        'match_result': MATCH_RESULT_CHOICES,
        'dismissal_type': DISMISSAL_TYPE_CHOICES
    }.get(choice_type, [])
    
    custom_choices = load_custom_choices(choice_type)
    
    # Combine default and custom choices
    all_choices = default_choices.copy()
    for choice in custom_choices:
        if choice not in all_choices:
            all_choices.append(choice)
    
    return all_choices

# Generic function to handle dropdown options
def manage_dropdown_options(request, choice_type, form_class, template_name, redirect_url, item_name):
    all_choices = get_all_choices(choice_type)
    
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            value = form.cleaned_data['value']
            display = form.cleaned_data['display']
            
            # Add new choice to custom choices
            custom_choices = load_custom_choices(choice_type)
            new_choice = [value, display]
            if new_choice not in custom_choices:
                custom_choices.append(new_choice)
                save_custom_choices(choice_type, custom_choices)
                messages.success(request, f"{item_name} added successfully.")
            else:
                messages.warning(request, f"{item_name} already exists.")
                
            return redirect(redirect_url)
    else:
        form = form_class()
    
    context = {
        'items': all_choices,
        'form': form,
        'item_name': item_name
    }
    return render(request, template_name, context)

# Generic function to search dropdown options
def search_dropdown_options(request, choice_type):
    query = request.GET.get('q', '').lower()
    all_choices = get_all_choices(choice_type)
    
    if query:
        filtered_choices = [choice for choice in all_choices 
                          if query in choice[0].lower() or query in choice[1].lower()]
    else:
        filtered_choices = all_choices
    
    results = [{'id': choice[0], 'text': choice[1]} for choice in filtered_choices[:10]]
    return JsonResponse({'results': results})

# View functions for managing each dropdown type
@login_required
def manage_bowling_styles(request):
    return manage_dropdown_options(
        request, 
        'bowling_style', 
        BowlingStyleForm, 
        'cricket_stats/manage_dropdown.html', 
        'manage_bowling_styles',
        'Bowling Style'
    )

@login_required
def manage_batting_styles(request):
    return manage_dropdown_options(
        request, 
        'batting_style', 
        BattingStyleForm, 
        'cricket_stats/manage_dropdown.html', 
        'manage_batting_styles',
        'Batting Style'
    )

@login_required
def manage_player_classes(request):
    return manage_dropdown_options(
        request, 
        'player_class', 
        PlayerClassForm, 
        'cricket_stats/manage_dropdown.html', 
        'manage_player_classes',
        'Player Class'
    )

@login_required
def manage_venues(request):
    return manage_dropdown_options(
        request, 
        'venue', 
        VenueForm, 
        'cricket_stats/manage_dropdown.html', 
        'manage_venues',
        'Venue'
    )

@login_required
def manage_match_results(request):
    return manage_dropdown_options(
        request, 
        'match_result', 
        MatchResultForm, 
        'cricket_stats/manage_dropdown.html', 
        'manage_match_results',
        'Match Result'
    )

@login_required
def manage_dismissal_types(request):
    return manage_dropdown_options(
        request, 
        'dismissal_type', 
        DismissalTypeForm, 
        'cricket_stats/manage_dropdown.html', 
        'manage_dismissal_types',
        'Dismissal Type'
    )

# AJAX search endpoints for each dropdown type
def search_bowling_styles(request):
    return search_dropdown_options(request, 'bowling_style')

def search_batting_styles(request):
    return search_dropdown_options(request, 'batting_style')

def search_player_classes(request):
    return search_dropdown_options(request, 'player_class')

def search_venues(request):
    return search_dropdown_options(request, 'venue')

def search_match_results(request):
    return search_dropdown_options(request, 'match_result')

def search_dismissal_types(request):
    return search_dropdown_options(request, 'dismissal_type')

# Add new dropdown option via AJAX
@require_POST
@login_required
def add_dropdown_option(request):
    option_type = request.POST.get('option_type')
    value = request.POST.get('value')
    display = request.POST.get('display')
    
    if not value or not display:
        return JsonResponse({'success': False, 'message': 'Value and Display Text are required'})
    
    try:
        # Add new choice to custom choices
        custom_choices = load_custom_choices(option_type)
        new_choice = [value, display]
        
        # Check if choice already exists
        for choice in custom_choices:
            if choice[0] == value:
                return JsonResponse({'success': False, 'message': f'Value {value} already exists'})
        
        # Add the new choice
        custom_choices.append(new_choice)
        save_custom_choices(option_type, custom_choices)
        
        return JsonResponse({
            'success': True, 
            'message': 'Added successfully',
            'id': value,
            'text': display
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
