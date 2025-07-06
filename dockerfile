FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    build-essential \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 flask && chown -R flask:flask /app
USER flask

# Exponer el puerto
EXPOSE 5000

# Variables de entorno
ENV FLASK_APP=app.py
ENV PYTHONPATH=/app

# Comando para ejecutar la aplicación
CMD ["python", "app.py"]