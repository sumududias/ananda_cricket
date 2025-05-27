# 0005_update_tournament_fields.py
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0004_add_tournament_model'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tournament',
            name='season',
        ),
        migrations.RemoveField(
            model_name='tournament',
            name='organizer',
        ),
        migrations.AddField(
            model_name='tournament',
            name='location',
            field=models.CharField(default='Colombo', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tournament',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterModelOptions(
            name='tournament',
            options={'ordering': ['-start_date']},
        ),
    ]