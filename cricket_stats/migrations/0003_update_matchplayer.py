from django.db import migrations, models

def migrate_innings_data(apps, schema_editor):
    MatchPlayer = apps.get_model('cricket_stats', 'MatchPlayer')
    # Copy data from old innings field to new innings_number field
    MatchPlayer.objects.all().update(innings_number=models.F('innings'))

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0002_alter_match_result'),
    ]

    operations = [
        migrations.RenameField(
            model_name='matchplayer',
            old_name='innings',
            new_name='innings_number',
        ),
        migrations.AddField(
            model_name='matchplayer',
            name='substitution_reason',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='matchplayer',
            name='substitution_comments',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='matchplayer',
            name='substituted_player',
            field=models.ForeignKey('cricket_stats.MatchPlayer', null=True, blank=True, on_delete=models.SET_NULL, related_name='substitute_for'),
        ),
        migrations.AlterUniqueTogether(
            name='matchplayer',
            unique_together={('match', 'player', 'innings_number')},
        ),
        migrations.AlterModelOptions(
            name='matchplayer',
            options={'ordering': ['innings_number', 'batting_order']},
        ),
    ]
