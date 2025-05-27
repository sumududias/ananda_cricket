# Ananda Cricket Backend

Backend API for the Ananda Cricket Statistics Application. This application helps manage cricket statistics for Ananda College cricket teams.

## Features

- Player Management
- Team Statistics
- Match Records
- Performance Analytics
- JWT Authentication
- REST API
- Searchable Dropdowns
- Continuous Integration/Deployment

## Tech Stack

- Django
- Django REST Framework
- MySQL (Production on PythonAnywhere)
- SQLite (Development)
- JWT Authentication
- Select2 (for searchable dropdowns)
- GitHub Actions (CI/CD)

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

## Searchable Dropdowns

The application uses searchable dropdowns for better user experience. See [DROPDOWN_CHANGES.md](DROPDOWN_CHANGES.md) for implementation details.

## Continuous Integration/Deployment

This project uses GitHub Actions for CI/CD:

1. Automated testing on pull requests and pushes to main branch
2. Code quality checks with flake8
3. Test coverage reporting
4. Automated deployment to PythonAnywhere when tests pass on main branch

To set up CI/CD for your fork:

```bash
python setup_github_ci.py
```

Follow the instructions to set up required GitHub secrets.