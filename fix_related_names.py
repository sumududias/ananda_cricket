"""
This script fixes the related_name conflicts in the models.py file
"""

def fix_models():
    with open('cricket_stats/models.py', 'r') as f:
        lines = f.readlines()
    
    # Find and update the MatchPlayer.how_out field
    for i, line in enumerate(lines):
        if 'how_out = models.ForeignKey(DismissalType' in line and i > 480 and i < 490:
            lines[i] = '    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name="match_player_dismissals")\n'
    
    # Find and update the BattingInnings.how_out field
    for i, line in enumerate(lines):
        if 'how_out = models.ForeignKey(DismissalType' in line and i > 610 and i < 630:
            lines[i] = '    how_out = models.ForeignKey(DismissalType, on_delete=models.SET_NULL, null=True, blank=True, related_name="batting_innings_dismissals")\n'
    
    with open('cricket_stats/models.py', 'w') as f:
        f.writelines(lines)
    
    print("Models updated successfully!")

if __name__ == "__main__":
    fix_models()
