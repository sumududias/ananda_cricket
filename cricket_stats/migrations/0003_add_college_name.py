from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0002_performance_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='college_name',
            field=models.CharField(default='Ananda College', max_length=100),
        ),
        migrations.AddField(
            model_name='match',
            name='team_name',
            field=models.CharField(default='Ananda College', max_length=100),
        ),
    ]
