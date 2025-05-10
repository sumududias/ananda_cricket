from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0005_update_matchplayer_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='substitution',
            options={},
        ),
        migrations.AlterField(
            model_name='substitution',
            name='comments',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='substitution',
            name='substitution_time',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='substitution',
            name='approved_by',
            field=models.CharField(blank=True, default='', max_length=100),
        ),
        migrations.AlterField(
            model_name='substitution',
            name='reason',
            field=models.CharField(choices=[('INJURY', 'Injury'), ('TACTICAL', 'Tactical'), ('OTHER', 'Other')], max_length=20),
        ),
    ]
