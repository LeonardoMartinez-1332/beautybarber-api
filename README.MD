# 💈 BeautyBarber API

Backend profesional desarrollado con **FastAPI + PostgreSQL + Docker**  
Proyecto orientado a arquitectura SaaS escalable para gestión de barberías.

---

## 🚀 Stack Tecnológico

- Python 3.12
- FastAPI
- PostgreSQL 16
- SQLAlchemy 2.0
- Alembic (migraciones)
- Docker & Docker Compose

---

## 📦 Estructura del Proyecto

pp/
├── api/ # Rutas (endpoints)
├── core/ # Utilidades y lógica compartida
├── db/ # Configuración de base de datos
├── models/ # Modelos SQLAlchemy
├── schemas/ # Esquemas Pydantic
├── services/ # Lógica de negocio
└── main.py # Entry point FastAPI

migrations/ # Versionado de base de datos (Alembic)
Dockerfile
docker-compose.yml
requirements.txt
