# Usa una imagen ligera de Python 3.11
FROM python:3.11-slim


# Instalar dependencias del sistema necesarias para pdf2image y pytesseract

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    libtesseract-dev \
    libleptonica-dev \
    pkg-config \
    python3-dev \
    gcc \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

ENV PYTHONPATH=/app

# Copia todo el contenido del contexto al contenedor
COPY . /app

# Muestra el contenido para depuración (opcional, puedes quitarlo luego)
RUN echo "Contenido1 de /app:" && ls -l /app

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto por defecto de Gunicorn (Cloud Run usa el 8080)
EXPOSE 8080

# Comando para ejecutar la app usando Gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:8080 clasificador.app:app"]

#limitar teseract 
ENV OMP_THREAD_LIMIT=1
ENV TESSDATA_FAST=1
