# Ananda Cricket Backend

Backend API for the Ananda Cricket Statistics Application. This application helps manage cricket statistics for Ananda College cricket teams.

## Features

- Player Management
- Team Statistics
- Match Records
- Performance Analytics
- JWT Authentication
- REST API

## Tech Stack

- Django
- Django REST Framework
- PostgreSQL (Production)
- SQLite (Development)
- JWT Authentication

## Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/ananda-cricket-backend.git
cd ananda-cricket-backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run migrations:
```bash
python manage.py migrate
```

4. Create superuser:
```bash
python manage.py createsuperuser
```

5. Run development server:
```bash
python manage.py runserver
```

## API Documentation

- `/api/players/` - Player management
- `/api/teams/` - Team management
- `/api/matches/` - Match records
- `/api/statistics/` - Performance statistics
- `/api/token/` - JWT token authentication 