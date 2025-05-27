# Ananda Cricket - Deployment Guide

This guide provides instructions for deploying the Ananda Cricket application on PythonAnywhere and fixing any database issues.

## Deployment Steps

### 1. Set Up PythonAnywhere

1. Log in to your PythonAnywhere account
2. Create a new web app using Django and Python 3.9
3. Set up a MySQL database

### 2. Upload Code

1. Upload your code to PythonAnywhere using Git or the Upload feature
2. Navigate to your app directory: `/home/anandacricket/ananda_cricket`

### 3. Set Up Virtual Environment

```bash
mkvirtualenv --python=/usr/bin/python3.9 ananda_cricket_env
pip install -r requirements.txt
```

### 4. Configure Settings

Update `ananda_cricket/settings.py` with the correct database settings for PythonAnywhere:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'anandacricket$default',
        'USER': 'anandacricket',
        'PASSWORD': 'your-database-password',
        'HOST': 'anandacricket.mysql.pythonanywhere-services.com',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

MEDIA_ROOT = '/home/anandacricket/ananda_cricket/media'
STATIC_ROOT = '/home/anandacricket/ananda_cricket/staticfiles'
```

### 5. Fix Database Issues

If you encounter database issues (missing tables), run the fix_database.py script:

```bash
cd /home/anandacricket/ananda_cricket
python fix_database.py
```

This script will:
- Check for missing tables like django_session and cricket_stats_tournament
- Apply all migrations
- Verify database integrity

### 6. Configure WSGI File

Make sure your WSGI file (`/var/www/anandacricket_pythonanywhere_com_wsgi.py`) has the correct path:

```python
import os
import sys

path = '/home/anandacricket/ananda_cricket'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'ananda_cricket.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

### 7. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 8. Set Up Database Backup

Make the backup script executable:

```bash
chmod +x backup_db.sh
```

Add a scheduled task in PythonAnywhere to run the backup script daily:

```bash
/home/anandacricket/ananda_cricket/backup_db.sh
```

### 9. Import Historical Data

To import historical data from Excel files:

```bash
# First, create Excel templates
python manage.py create_excel_templates

# After filling the templates with data, import them
python manage.py import_excel_data --match-formats /path/to/match_formats.xlsx
python manage.py import_excel_data --teams /path/to/teams.xlsx
python manage.py import_excel_data --players /path/to/players.xlsx
python manage.py import_excel_data --matches /path/to/matches.xlsx
python manage.py import_excel_data --match-players /path/to/match_players.xlsx
```

## Troubleshooting

### Common Issues

1. **Missing Tables**: Run the `fix_database.py` script to create missing tables.
2. **Static Files Not Loading**: Make sure you've run `collectstatic` and configured your static files correctly.
3. **Media Files Not Accessible**: Check the permissions on your media directory.
4. **Import Errors**: Ensure your Excel files match the required format from the templates.

### Performance Optimization

1. **Database Indexing**: Apply the performance indexes migration:
   ```bash
   python manage.py migrate cricket_stats 0002_performance_indexes
   ```

2. **Caching**: Make sure caching is properly configured in your settings.py file.

## Contact

For support, please contact the development team.
