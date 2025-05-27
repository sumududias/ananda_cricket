#!/bin/bash
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR=~/backups
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u anandacricket -h anandacricket.mysql.pythonanywhere-services.com -p'!amtheB3st' anandacricket\$default > $BACKUP_DIR/ananda_cricket_db_$DATE.sql

# Backup media files
tar -czf $BACKUP_DIR/ananda_cricket_media_$DATE.tar.gz ~/ananda_cricket/media

# Keep only last 10 backups
ls -t $BACKUP_DIR/ananda_cricket_db_* | tail -n +11 | xargs -r rm
ls -t $BACKUP_DIR/ananda_cricket_media_* | tail -n +11 | xargs -r rm

echo "Backup completed: $DATE"
