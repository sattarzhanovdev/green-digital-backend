# Django Backend

REST API for Green Digital Kyrgyzstan.

## Local Run

```bash
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver 127.0.0.1:8000
```

Then set the frontend environment variable:

```env
NEXT_PUBLIC_API_URL="http://127.0.0.1:8000"
```

## API

- `POST /api/registrations/`
- `POST /api/admin/login/`
- `GET /api/admin/dashboard/`
- `GET /api/admin/registrations/`
- `GET /api/admin/registrations/{id}/`
- `PATCH /api/admin/registrations/{id}/`
- `GET /api/admin/export/csv/`

Admin endpoints use JWT:

```txt
Authorization: Bearer <access_token>
```

## Deploy

Use PostgreSQL in production:

```env
DATABASE_URL="postgresql://USER:PASSWORD@PUBLIC_HOST/DATABASE?sslmode=require"
SECRET_KEY="long-secret"
JWT_SECRET="long-secret"
CORS_ALLOWED_ORIGINS="https://green-digital-hackathon.netlify.app"
ADMIN_USERNAME="admin"
ADMIN_PASSWORD="strong-password"
ALLOWED_HOSTS="your-backend-domain.onrender.com"
DEBUG="false"
```

Build/start commands:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn config.wsgi:application
```
