# Tech Context

## Technologies Used
- **Language**: Python 3.x
- **Web Framework**: Django 5.2.8
- **Database**: PostgreSQL 15
- **Server**: Gunicorn 21.2.0 (Production-ready WSGI server)
- **Containerization**: Docker, Docker Compose

## Development Setup
- **Dependency Management**: `requirements.txt`
- **Environment Variables**: `.env` file (referenced in `Docker-compose.yml`)
- **Local Run Command**: `docker-compose up --build`

## Technical Constraints
- **Database**: Must use PostgreSQL as configured in `settings.py` and `Docker-compose.yml`.
- **Static Files**: Configured to use `static/` directory.
- **Media Files**: `Referencia` model uses `upload_to='referencias/'`, implying local file storage configuration needs to be correct.

## Dependencies
- `Django==5.2.8`: Core framework.
- `psycopg2-binary==2.9.10`: PostgreSQL adapter.
- `python-dotenv==1.0.0`: Environment variable management.
- `gunicorn==21.2.0`: WSGI server.
- `asgiref`, `sqlparse`, `tzdata`: Django dependencies.

