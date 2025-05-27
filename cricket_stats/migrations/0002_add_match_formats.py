from django.db import migrations

def create_initial_formats(apps, schema_editor):
    MatchFormat = apps.get_model('cricket_stats', 'MatchFormat')
    
    formats = [
        # 2 or 3 Day Match
        {
            'name': '2 or 3 Day Match',
            'short_name': '2/3D',
            'days': 3,  # Default to 3 days, can be adjusted per match
            'is_limited_overs': False,
            'is_practice': False,
            'is_active': True
        },
        # Limited Over Match
        {
            'name': 'Limited Over Match',
            'short_name': 'LO',
            'days': 1,
            'is_limited_overs': True,
            'is_practice': False,
            'is_active': True
        },
        # 2 or 3 Day Practice Match
        {
            'name': '2 or 3 Day Practice Match',
            'short_name': '2/3DP',
            'days': 3,  # Default to 3 days, can be adjusted per match
            'is_limited_overs': False,
            'is_practice': True,
            'is_active': True
        },
        # Limited Over Practice Match
        {
            'name': 'Limited Over Practice Match',
            'short_name': 'LOP',
            'days': 1,
            'is_limited_overs': True,
            'is_practice': True,
            'is_active': True
        }
    ]
    
    for format_data in formats:
        MatchFormat.objects.get_or_create(
            short_name=format_data['short_name'],
            defaults=format_data
        )


class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0001_initial'),  # This should match your last migration
    ]

    operations = [
        migrations.RunPython(create_initial_formats),
    ]