from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0001_initial'),
    ]

    operations = [
        # Create BowlingStyle model
        migrations.CreateModel(
            name='BowlingStyle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Bowling Style',
                'verbose_name_plural': 'Bowling Styles',
                'ordering': ['name'],
            },
        ),
        
        # Create BattingStyle model
        migrations.CreateModel(
            name='BattingStyle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Batting Style',
                'verbose_name_plural': 'Batting Styles',
                'ordering': ['name'],
            },
        ),
        
        # Create PlayerClass model
        migrations.CreateModel(
            name='PlayerClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Player Class',
                'verbose_name_plural': 'Player Classes',
                'ordering': ['name'],
            },
        ),
        
        # Create Venue model
        migrations.CreateModel(
            name='Venue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, unique=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=100, null=True)),
                ('capacity', models.PositiveIntegerField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Venue',
                'verbose_name_plural': 'Venues',
                'ordering': ['name'],
            },
        ),
        
        # Create MatchResult model
        migrations.CreateModel(
            name='MatchResult',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Match Result',
                'verbose_name_plural': 'Match Results',
                'ordering': ['name'],
            },
        ),
        
        # Create DismissalType model
        migrations.CreateModel(
            name='DismissalType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Dismissal Type',
                'verbose_name_plural': 'Dismissal Types',
                'ordering': ['name'],
            },
        ),
        
        # Update Player model to use ForeignKeys
        migrations.AlterField(
            model_name='player',
            name='batting_style',
            field=models.ForeignKey(null=True, on_delete=models.deletion.SET_NULL, related_name='players', to='cricket_stats.battingstyle'),
        ),
        migrations.AlterField(
            model_name='player',
            name='bowling_style',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='players', to='cricket_stats.bowlingstyle'),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_class',
            field=models.ForeignKey(null=True, on_delete=models.deletion.SET_NULL, related_name='players', to='cricket_stats.playerclass'),
        ),
        
        # Update Match model to use ForeignKeys
        migrations.AlterField(
            model_name='match',
            name='venue',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='matches', to='cricket_stats.venue'),
        ),
        migrations.AlterField(
            model_name='match',
            name='result',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='matches', to='cricket_stats.matchresult'),
        ),
        
        # Update MatchPlayer model to use ForeignKey for how_out
        migrations.AlterField(
            model_name='matchplayer',
            name='how_out',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='match_player_dismissals', to='cricket_stats.dismissaltype'),
        ),
        
        # Update BattingInnings model to use ForeignKey for how_out
        migrations.AlterField(
            model_name='battinginnings',
            name='how_out',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.deletion.SET_NULL, related_name='batting_innings_dismissals', to='cricket_stats.dismissaltype'),
        ),
    ]
