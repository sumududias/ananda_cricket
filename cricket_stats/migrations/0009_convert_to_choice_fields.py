from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0008_add_dropdown_models'),
    ]

    operations = [
        # Convert ForeignKey fields to CharField fields with choices
        migrations.AlterField(
            model_name='player',
            name='batting_style',
            field=models.CharField(max_length=20, choices=[
                ('RHB', 'Right Hand Batsman'),
                ('LHB', 'Left Hand Batsman'),
            ], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='bowling_style',
            field=models.CharField(max_length=50, choices=[
                ('RF', 'Right Arm Fast'),
                ('RM', 'Right Arm Medium'),
                ('ROS', 'Right Arm Off Spin'),
                ('RLS', 'Right Arm Leg Spin'),
                ('LF', 'Left Arm Fast'),
                ('LM', 'Left Arm Medium'),
                ('LOS', 'Left Arm Off Spin'),
                ('LLS', 'Left Arm Leg Spin'),
            ], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='player',
            name='player_class',
            field=models.CharField(max_length=20, choices=[
                ('A', 'Class A'),
                ('B', 'Class B'),
                ('C', 'Class C'),
                ('D', 'Class D'),
            ], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='venue',
            field=models.CharField(max_length=100, choices=[
                ('ANC', 'Ananda College Ground'),
                ('SSC', 'Sinhalese Sports Club'),
                ('PSS', 'P Sara Stadium'),
                ('RPS', 'Rangiri Dambulla Stadium'),
                ('PAL', 'Pallekele International Cricket Stadium'),
            ], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='match',
            name='result',
            field=models.CharField(max_length=100, choices=[
                ('WIN', 'Win'),
                ('LOSS', 'Loss'),
                ('DRAW', 'Draw'),
                ('TIE', 'Tie'),
                ('NR', 'No Result'),
                ('ABD', 'Abandoned'),
            ], blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='matchplayer',
            name='how_out',
            field=models.CharField(max_length=50, choices=[
                ('BOWL', 'Bowled'),
                ('CAUGHT', 'Caught'),
                ('LBW', 'LBW'),
                ('RUN_OUT', 'Run Out'),
                ('STUMPED', 'Stumped'),
                ('HIT_WICKET', 'Hit Wicket'),
                ('RETIRED', 'Retired'),
                ('RETIRED_HURT', 'Retired Hurt'),
                ('NOT_OUT', 'Not Out'),
                ('DNB', 'Did Not Bat'),
            ], blank=True, null=True),
        ),
    ]
