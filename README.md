# Fahimni

Focused AI-powered professor-student platform with messaging, announcements, and grades.

## Stack
- Backend: Python 3.12, FastAPI, SQLAlchemy 2 async, Alembic, PostgreSQL 16
- Auth: JWT (`python-jose`) + bcrypt (`passlib`)
- AI: Anthropic Claude (`claude-sonnet-4-20250514`) + ChromaDB
- Jobs: Celery + Redis
- Files: MinIO (`boto3`)
- Tooling: `uv`, pytest, Ruff, mypy
- Frontend: React + Vite

## Project Layout
- Backend app: `src/fahimni`
- Frontend app: `frontend`
- Tests: `tests`
- Postman collection: `postman/fahimni.postman_collection.json`

## Environment
1. Copy `.env.example` to `.env`.
2. Update secrets and API keys.
3. Ensure `.python-version` is `3.12`.

## Start Infrastructure
```powershell
docker compose up -d
```

## Install Dependencies
```powershell
uv sync
```

## Run Backend
```powershell
uv run uvicorn fahimni.main:app --reload --reload-dir src
```

## Run Celery Worker
```powershell
uv run celery -A fahimni.core.celery_app.celery_app worker --loglevel=info
```

## Run Frontend
```powershell
cd frontend
npm install
npm run dev
```

## Database Migrations
Generate migration:
```powershell
uv run alembic revision --autogenerate -m "add academic domain tables"
```

Apply migration:
```powershell
uv run alembic upgrade head
```

## Tests and Quality
```powershell
uv run pytest -v
uv run mypy src/
uv run ruff check src tests
```

## API Modules Implemented
- `api/v1/auth.py`: register, login, current user
- `api/v1/courses.py`: create/list courses, enroll
- `api/v1/announcements.py`: create/list course announcements
- `api/v1/messages.py`: private direct messages
- `api/v1/grades.py`: assignments and grade posting/listing

All routers use dependency injection for auth and DB sessions and rely on repositories for data access.

## React UI Notes
The React UI in `frontend/src` includes your requested style system:
- Course cards: 240x200, radius 28, white, shadow/stroke palette
- Buttons: 95x35 with `#D7BAFF`, `#D8EE80`, `#A5A1F4`
- Sidebar icon buttons: 75x45, white, bordered/shadowed
- Typography: Poppins, text color `#26244A`
- Layout colors: sidebar white, page background `#F6F6F6`
- Grades page card: 990x177 with current grade and next assignment/announcement
- Materials + assignments area with underlined messages section

## Postman
Import `postman/fahimni.postman_collection.json` and set variables:
- `baseUrl`
- `token`
- `courseId`, `studentId`, `recipientId`, `assignmentId`

