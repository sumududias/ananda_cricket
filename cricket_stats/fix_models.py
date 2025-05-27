"""
This script updates the related_name attributes in the models.py file
to fix the conflicts between MatchPlayer.how_out and BattingInnings.how_out
"""

import os
import re

def fix_models():
    models_path = os.path.join('cricket_stats', 'models.py')
    
    with open(models_path, 'r') as file:
        content = file.read()
    
    # Replace the related_name in MatchPlayer model (line 487)
    content = content.replace(
        "    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name='batting_innings')",
        "    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name='match_player_dismissals')"
    )
    
    # Replace the related_name in BattingInnings model (line 619)
    content = content.replace(
        "    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name='match_player_dismissals')",
        "    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name='batting_innings_dismissals')"
    )
    
    with open(models_path, 'w') as file:
        file.write(content)
    
    print("Models updated successfully!")

if __name__ == "__main__":
    fix_models()
