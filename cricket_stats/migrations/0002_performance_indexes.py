from django.db import migrations
from django.db.models import Index

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0001_initial'),
    ]

    operations = [
        # Add indexes for frequently queried fields
        migrations.AddIndex(
            model_name='match',
            index=Index(fields=['match_date'], name='match_date_idx'),
        ),
        migrations.AddIndex(
            model_name='match',
            index=Index(fields=['team'], name='match_team_idx'),
        ),
        migrations.AddIndex(
            model_name='match',
            index=Index(fields=['format'], name='match_format_idx'),
        ),
        migrations.AddIndex(
            model_name='matchplayer',
            index=Index(fields=['match', 'player'], name='match_player_idx'),
        ),
        migrations.AddIndex(
            model_name='matchplayer',
            index=Index(fields=['innings_number'], name='innings_number_idx'),
        ),
        migrations.AddIndex(
            model_name='player',
            index=Index(fields=['first_name', 'last_name'], name='player_name_idx'),
        ),
        migrations.AddIndex(
            model_name='player',
            index=Index(fields=['is_active'], name='player_active_idx'),
        ),
    ]
