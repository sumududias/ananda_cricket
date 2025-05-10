from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0004_merge_20250511_0325'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchplayer',
            name='how_out',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='matchplayer',
            name='innings_number',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='matchplayer',
            name='is_playing_xi',
            field=models.BooleanField(default=True),
        ),
    ]
