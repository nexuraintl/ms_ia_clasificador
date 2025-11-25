#imagen ligera de Python 3.11
FROM python:3.11-slim

# Evita que Python genere .pyc innecesarios
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependencias del sistema necesarias para:

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    libtesseract-dev \
    libleptonica-dev \
    gcc \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar los archivos del proyecto
COPY . /app

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Cloud Run usa el puerto 8080
EXPOSE 8080

# Limitar Tesseract para rendimiento
ENV OMP_THREAD_LIMIT=1
ENV TESSDATA_FAST=1

# Comando final: ejecutar con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "clasificador.app:app"]
