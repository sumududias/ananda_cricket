"""
Choices for dropdown options in the Ananda Cricket application.
These choices provide options for various dropdown menus.
"""

# Bowling Styles
BOWLING_STYLE_CHOICES = [
    ('RFM', 'Right-arm Fast Medium'),
    ('RF', 'Right-arm Fast'),
    ('RM', 'Right-arm Medium'),
    ('ROB', 'Right-arm Off Break'),
    ('RLB', 'Right-arm Leg Break'),
    ('LFM', 'Left-arm Fast Medium'),
    ('LF', 'Left-arm Fast'),
    ('LM', 'Left-arm Medium'),
    ('LOB', 'Left-arm Orthodox'),
    ('LCH', 'Left-arm Chinaman'),
    ('OTHER', 'Other')
]

# Batting Styles
BATTING_STYLE_CHOICES = [
    ('RHB', 'Right-handed Batsman'),
    ('LHB', 'Left-handed Batsman')
]

# Player Classes
PLAYER_CLASS_CHOICES = [
    ('SENIOR', 'Senior'),
    ('JUNIOR', 'Junior'),
    ('U19', 'Under 19'),
    ('U17', 'Under 17'),
    ('U15', 'Under 15'),
    ('U13', 'Under 13')
]

# Common Venues
VENUE_CHOICES = [
    ('SSC', 'Sinhalese Sports Club Ground'),
    ('RPICS', 'R Premadasa International Cricket Stadium'),
    ('PALLEKELE', 'Pallekele International Cricket Stadium'),
    ('GALLE', 'Galle International Stadium'),
    ('CAMPBELL', 'Campbell Park'),
    ('ANANDA', 'Ananda College Ground'),
    ('ROYAL', 'Royal College Ground'),
    ('OTHER', 'Other')
]

# Match Results
MATCH_RESULT_CHOICES = [
    ('WIN', 'Won'),
    ('LOSS', 'Lost'),
    ('DRAW', 'Draw'),
    ('TIE', 'Tie'),
    ('NR', 'No Result'),
    ('ABANDONED', 'Abandoned')
]

# Dismissal Types
DISMISSAL_TYPE_CHOICES = [
    ('BOWLED', 'Bowled'),
    ('CAUGHT', 'Caught'),
    ('LBW', 'LBW'),
    ('RUN_OUT', 'Run Out'),
    ('STUMPED', 'Stumped'),
    ('HIT_WICKET', 'Hit Wicket'),
    ('RETIRED_HURT', 'Retired Hurt'),
    ('RETIRED_OUT', 'Retired Out'),
    ('OBSTRUCTING', 'Obstructing the Field'),
    ('TIMED_OUT', 'Timed Out'),
    ('HANDLED_BALL', 'Handled the Ball'),
    ('NOT_OUT', 'Not Out')
]


# Note: The model classes have been replaced with choice constants above.
# This allows for simpler implementation of searchable dropdowns without
# requiring complex database migrations.
