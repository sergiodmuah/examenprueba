FROM python:3.12
# Declaramos la carpeta de trabajo
WORKDIR /app

# Copiamos el archivo requirements.txt dentro de la imagen del contenedor.
COPY requirements.txt /app

# Copiar el archivo de credenciales al contenedor
COPY clave123.json /app/clave123.json

# Establecer la variable de entorno para las credenciales de Google Cloud
ENV GOOGLE_APPLICATION_CREDENTIALS="/app/clave123.json"

# Instalamos las dependencias dentro de la imagen
RUN pip install -r requirements.txt

# Copiamos la aplicación web dentro de la imagen
COPY . /app

# Puerto en el que escuchará el contenedor
EXPOSE 8080

ENTRYPOINT ["python", "main.py"]
