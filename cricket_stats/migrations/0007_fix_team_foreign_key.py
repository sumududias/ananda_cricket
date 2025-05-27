from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('cricket_stats', '0006_trainingsession_alter_playerattendance_options_and_more'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Rename existing team_id to temp_team_id
            ALTER TABLE cricket_stats_match 
            CHANGE COLUMN team_id temp_team_id VARCHAR(100) NULL;
            
            -- Add new team_id as BIGINT
            ALTER TABLE cricket_stats_match 
            ADD COLUMN team_id BIGINT NULL;
            
            -- Copy data from temp_team_id to team_id
            -- This assumes temp_team_id contains valid team IDs
            UPDATE cricket_stats_match 
            SET team_id = CAST(temp_team_id AS UNSIGNED)
            WHERE temp_team_id IS NOT NULL AND temp_team_id != '';
            
            -- Drop the temporary column
            ALTER TABLE cricket_stats_match 
            DROP COLUMN temp_team_id;
            
            -- Add the foreign key constraint
            ALTER TABLE cricket_stats_match 
            ADD CONSTRAINT fk_team_team
            FOREIGN KEY (team_id) REFERENCES cricket_stats_team(id)
            ON DELETE SET NULL;
            """,
            reverse_sql="""
            -- This is the reverse migration in case we need to rollback
            ALTER TABLE cricket_stats_match 
            DROP FOREIGN KEY fk_team_team;
            
            ALTER TABLE cricket_stats_match 
            ADD COLUMN temp_team_id VARCHAR(100) NULL;
            
            UPDATE cricket_stats_match 
            SET temp_team_id = CAST(team_id AS CHAR)
            WHERE team_id IS NOT NULL;
            
            ALTER TABLE cricket_stats_match 
            DROP COLUMN team_id,
            CHANGE COLUMN temp_team_id team_id VARCHAR(100) NULL;
            """
        ),
    ]