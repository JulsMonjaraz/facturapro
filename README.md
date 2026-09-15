# 🧾 FacturaPro

> REST API for freelance invoicing — built with Django, DRF, Celery, and Redis.

[![Tests](https://github.com/JulsMonjaraz/facturapro/actions/workflows/tests.yml/badge.svg)](https://github.com/JulsMonjaraz/facturapro/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?style=flat&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-REST-ff1709?style=flat&logo=django&logoColor=white)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?style=flat&logo=postgresql)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=flat&logo=redis)](https://redis.io/)
[![Celery](https://img.shields.io/badge/Celery-5-37814A?style=flat&logo=celery)](https://docs.celeryq.dev/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=flat&logo=docker)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📖 Overview

**FacturaPro** is a multi-tenant SaaS backend that lets freelancers manage clients, projects, and invoices from a single REST API. It handles everything from invoice calculations (subtotal, taxes, discounts) to asynchronous PDF generation and automatic payment reminders.

The API is fully documented with Swagger/ReDoc and covered by an extensive test suite with 97% code coverage.

## ✨ Features

### Core
- **Multi-tenant architecture** — each user only sees their own data (enforced at the queryset level).
- **Full CRUD** for clients, projects, invoices, and invoice items.
- **Automatic invoice calculations** — subtotal, taxes, discounts, and total, computed with `Decimal` precision.
- **Custom endpoint** to recalculate invoice totals on demand (`POST /api/facturas/{id}/calcular/`).

### Async & Background Jobs
- **Celery + Redis** for background task processing.
- **Welcome emails** sent automatically when a client is created.
- **Invoice PDFs** generated on demand via `xhtml2pdf`.
- **Daily payment reminders** scheduled with **Celery Beat** — automatically emails clients whose invoices are due in 3 days.

### Auth & Security
- **JWT authentication** (access + refresh tokens) with `djangorestframework-simplejwt`.
- **Session auth** for browsing the API in the browser.
- Sensitive credentials loaded from environment variables.

### DevOps
- **Docker Compose** with 5 services: `web`, `db`, `redis`, `worker`, `beat`.
- **CI/CD with GitHub Actions** — tests run automatically on every push.
- **Swagger + ReDoc** — auto-generated API documentation.

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.12 |
| Framework | Django 6.1, Django REST Framework |
| Auth | JWT (SimpleJWT) |
| Database | PostgreSQL 15 |
| Cache & Broker | Redis 7 |
| Async Tasks | Celery 5 + Celery Beat |
| PDF Generation | xhtml2pdf |
| Testing | pytest, pytest-django, factory-boy |
| Docs | drf-spectacular (Swagger + ReDoc) |
| Container | Docker + Docker Compose |
| CI/CD | GitHub Actions |

## 🏗️ Architecture
┌───────────────────────────────────────────────────┐
│ Client (browser, Postman, mobile app) │
└──────────────────────┬────────────────────────────┘
│ HTTP + JWT
▼
┌───────────────────────────────────────────────────┐
│ Django + DRF (Gunicorn) │
│ ─ /api/clientes/ ─ /api/proyectos/ │
│ ─ /api/facturas/ ─ /api/items/ │
│ ─ /api/token/ ─ /api/docs/ │
└───────┬───────────────────┬───────────────────────┘
│ │
▼ ▼
┌───────────┐ ┌───────────┐
│ PostgreSQL│ │ Redis │
└───────────┘ └─────┬─────┘
│
┌──────┴────────┐
▼ ▼
┌───────────┐ ┌────────────┐
│ Worker │ │ Beat │
│ (Celery) │ │ (Celery) │
└───────────┘ └────────────┘

text

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose

### 1. Clone the repository
```bash
git clone https://github.com/JulsMonjaraz/facturapro.git
cd facturapro
2. Create the environment file

bash
cp .env.example .env
# Edit .env with your values
3. Build and start all services

bash
docker compose up --build
The API will be available at http://127.0.0.1:8000.

4. Run migrations and create a superuser

bash
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
📚 API Documentation

Once running, visit:

Swagger UI: http://127.0.0.1:8000/api/docs/
ReDoc: http://127.0.0.1:8000/api/redoc/
OpenAPI schema: http://127.0.0.1:8000/api/schema/
🔌 API Endpoints

Method	Endpoint	Description
POST	/api/token/	Obtain JWT access + refresh tokens
POST	/api/token/refresh/	Refresh access token
GET	/api/users/me/	Get current authenticated user
GET/POST	/api/clientes/	List / create clients
GET/PUT/PATCH/DELETE	/api/clientes/{id}/	Client detail
GET/POST	/api/proyectos/	List / create projects
GET/POST	/api/facturas/	List / create invoices
POST	/api/facturas/{id}/calcular/	Recalculate invoice totals
POST	/api/facturas/{id}/generar_pdf/	Generate invoice PDF (async)
GET/POST	/api/items/	List / create invoice items
🧪 Testing

Run the full test suite:

bash
pytest
With coverage report:

bash
pytest --cov=facturacion --cov-report=term-missing
Current coverage: 97%.

📁 Project Structure

text
facturapro/
├── .github/
│   └── workflows/
│       └── tests.yml              # CI/CD pipeline
├── config/
│   ├── celery.py                  # Celery configuration
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── facturacion/
│   ├── migrations/
│   ├── templates/facturacion/
│   │   └── factura_pdf.html       # Invoice PDF template
│   ├── tests/
│   │   ├── factories.py           # factory-boy factories
│   │   ├── test_api.py            # API tests
│   │   ├── test_models.py         # Model tests
│   │   └── test_tasks.py          # Celery task tests
│   ├── admin.py
│   ├── models.py                  # User, Cliente, Proyecto, Factura, ItemFactura
│   ├── permissions.py             # Custom DRF permissions
│   ├── serializers.py
│   ├── signals.py                 # Auto-recalculate invoice totals
│   ├── tasks.py                   # Celery tasks
│   ├── urls.py
│   └── views.py
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
🔐 Environment Variables

Variable	Description
SECRET_KEY	Django secret key
DB_NAME	PostgreSQL database name
DB_USER	PostgreSQL user
DB_PASSWORD	PostgreSQL password
DB_HOST	PostgreSQL host
DB_PORT	PostgreSQL port
REDIS_URL	Redis URL for cache
CELERY_BROKER_URL	Celery broker URL
CELERY_RESULT_BACKEND	Celery result backend URL
👨‍💻 Author

Julio Monjaraz
Backend developer specialized in Django and Python.

GitHub
LinkedIn
⭐ If you found this project interesting, consider giving it a star.

text

---

## 🛠️ PASO 2: Sube el README

```bash
git add README.md
git commit -m "Add professional README in English"
git push
