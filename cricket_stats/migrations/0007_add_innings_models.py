from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0006_update_substitution_model'),
    ]

    operations = [
        migrations.CreateModel(
            name='BattingInnings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('innings_number', models.IntegerField(default=1)),
                ('batting_position', models.IntegerField()),
                ('runs_scored', models.IntegerField(default=0)),
                ('balls_faced', models.IntegerField(default=0)),
                ('fours', models.IntegerField(default=0)),
                ('sixes', models.IntegerField(default=0)),
                ('how_out', models.CharField(blank=True, max_length=100, null=True)),
                ('bowler', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='wickets_taken_set', to='cricket_stats.player')),
                ('fielder', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='catches_taken_set', to='cricket_stats.player')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cricket_stats.match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cricket_stats.player')),
            ],
            options={
                'ordering': ['innings_number', 'batting_position'],
                'unique_together': {('match', 'player', 'innings_number')},
            },
        ),
        migrations.CreateModel(
            name='BowlingInnings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('innings_number', models.IntegerField(default=1)),
                ('overs', models.DecimalField(decimal_places=1, default=0, max_digits=4)),
                ('maidens', models.IntegerField(default=0)),
                ('runs_conceded', models.IntegerField(default=0)),
                ('wickets', models.IntegerField(default=0)),
                ('wides', models.IntegerField(default=0)),
                ('no_balls', models.IntegerField(default=0)),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cricket_stats.match')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cricket_stats.player')),
            ],
            options={
                'ordering': ['innings_number'],
                'unique_together': {('match', 'player', 'innings_number')},
            },
        ),
    ]
