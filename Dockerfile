# Se usa una imagen oficial de Python como imagen base
FROM python:3.12-slim

# Todo se ejecuta dentro del folder /app del contenedor (a qui vive el proyecto).
WORKDIR /app

# Copia las dependencias antes del codigo para aprovechar el cacheo de Docker
COPY requirements.txt .

# Instala las dependencias del proyecto como por ejemplo FastAPI, Uvicorn, SQLAlchemy, psycopg.
RUN pip install --no-cache-dir -r requirements.txt

# Copia el backend FastAPI al contenedor
COPY ./app ./app

# Arranca el servidor FastAPI (0.0.0.0 es obligatirio para que Docker pueda mapear el puerto).
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]