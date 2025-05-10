from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchplayer',
            name='selection_notes',
            field=models.TextField(blank=True, help_text='Add any special notes about player selection (e.g., U17 player promoted to first XI)', null=True),
        ),
        migrations.AddField(
            model_name='matchplayer',
            name='approved_by',
            field=models.CharField(blank=True, help_text='Name of person who approved this player\'s selection', max_length=100, null=True),
        ),
    ]
