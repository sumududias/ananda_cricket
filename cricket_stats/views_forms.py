from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .models import Player, Match
from .forms import PlayerForm, MatchForm

@login_required
def player_form(request, player_id=None):
    """View for adding or editing a player with searchable dropdowns."""
    if player_id:
        player = get_object_or_404(Player, pk=player_id)
        title = f"Edit Player: {player.first_name} {player.last_name}"
    else:
        player = None
        title = "Add New Player"
    
    if request.method == 'POST':
        form = PlayerForm(request.POST, request.FILES, instance=player)
        if form.is_valid():
            player = form.save()
            messages.success(request, f"Player {player.first_name} {player.last_name} has been {'updated' if player_id else 'added'} successfully.")
            return redirect('cricket_stats:player_detail', pk=player.id)
    else:
        form = PlayerForm(instance=player)
    
    context = {
        'form': form,
        'title': title,
        'player': player,
        'batting_style_search_url': reverse('cricket_stats:search_batting_styles'),
        'bowling_style_search_url': reverse('cricket_stats:search_bowling_styles'),
        'player_class_search_url': reverse('cricket_stats:search_player_classes'),
        'add_dropdown_url': reverse('cricket_stats:add_dropdown_option'),
    }
    
    return render(request, 'cricket_stats/player_form.html', context)

@login_required
def match_form(request, match_id=None):
    """View for adding or editing a match with searchable dropdowns."""
    if match_id:
        match = get_object_or_404(Match, pk=match_id)
        title = f"Edit Match: {match}"
    else:
        match = None
        title = "Add New Match"
    
    if request.method == 'POST':
        form = MatchForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save()
            messages.success(request, f"Match has been {'updated' if match_id else 'added'} successfully.")
            return redirect('cricket_stats:match_detail', match_id=match.id)
    else:
        form = MatchForm(instance=match)
    
    context = {
        'form': form,
        'title': title,
        'match': match,
        'venue_search_url': reverse('cricket_stats:search_venues'),
        'match_result_search_url': reverse('cricket_stats:search_match_results'),
        'add_dropdown_url': reverse('cricket_stats:add_dropdown_option'),
    }
    
    return render(request, 'cricket_stats/match_form.html', context)

@login_required
def match_player_form(request, match_id, player_id=None):
    """View for adding or editing a match player with searchable dismissal type dropdown."""
    from .models import MatchPlayer
    from .forms import MatchPlayerForm
    
    match = get_object_or_404(Match, pk=match_id)
    
    if player_id:
        match_player = get_object_or_404(MatchPlayer, match=match, player_id=player_id)
        title = f"Edit Player Performance: {match_player.player.first_name} {match_player.player.last_name}"
    else:
        match_player = None
        title = "Add Player to Match"
    
    if request.method == 'POST':
        form = MatchPlayerForm(request.POST, instance=match_player)
        if form.is_valid():
            match_player = form.save(commit=False)
            match_player.match = match
            match_player.save()
            messages.success(request, f"Player performance has been {'updated' if player_id else 'added'} successfully.")
            return redirect('cricket_stats:match_detail', match_id=match.id)
    else:
        initial_data = {'match': match}
        form = MatchPlayerForm(instance=match_player, initial=initial_data)
    
    context = {
        'form': form,
        'title': title,
        'match': match,
        'match_player': match_player,
        'dismissal_type_search_url': reverse('cricket_stats:search_dismissal_types'),
        'add_dropdown_url': reverse('cricket_stats:add_dropdown_option'),
    }
    
    return render(request, 'cricket_stats/match_player_form.html', context)
