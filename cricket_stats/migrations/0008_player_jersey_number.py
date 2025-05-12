from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0007_add_innings_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='jersey_number',
            field=models.IntegerField(
                null=True,
                blank=True,
                help_text="Player's jersey number",
                db_column='player_jersey_number'  # Explicitly specify the column name
            ),
        ),
    ]
