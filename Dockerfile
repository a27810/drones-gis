# Dockerfile
FROM python:3.12-slim

# Evitar que Python genere .pyc y use buffer en stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Crear directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema (psycopg2, etc.)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt /app/

# Instalar dependencias Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Recoger estáticos en /static
RUN python manage.py collectstatic --noinput

# Exponer el puerto del contenedor
EXPOSE 8000

# Comando por defecto: Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]
