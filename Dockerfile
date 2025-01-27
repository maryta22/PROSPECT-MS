FROM python:3.6-alpine

# Crear directorio de la aplicación
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Instalar dependencias necesarias para compilación y ejecución
RUN apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    python3-dev \
    libffi-dev \
    && apk add --no-cache libffi

# Copiar el archivo de requerimientos
COPY requirements.txt /usr/src/app/

# Instalar los paquetes de Python (incluye gunicorn si está en requirements.txt)
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . /usr/src/app

# Exponer el puerto 8080
EXPOSE 2034

# Configurar Gunicorn como servidor de aplicaciones
CMD ["gunicorn", "-b", "0.0.0.0:2034", "swagger_server.__main__:app", "--workers", "3", "--threads", "2"]
