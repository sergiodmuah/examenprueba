#!/usr/bin/env python

from flask import Flask, jsonify, request
import os
import redis
import json
from google.cloud import storage  # Importamos la biblioteca oficial de Google Cloud Storage

# Explicación de la importación:
# La biblioteca 'google.cloud.storage' permite interactuar directamente con Google Cloud Storage (GCS).
# Es más eficiente y segura que usar la API REST manualmente, ya que maneja autenticación y errores de forma integrada.
# La usamos para subir y descargar objetos del bucket en GCS.

# Crear el objeto que representa la aplicación web
APP = Flask(__name__)
nombre = os.environ['AUTHOR_NAME']
email = os.environ['AUTHOR_EMAIL']
BUCKET_NAME = "sdm-examenprueba"
redis_location = os.environ['REDIS_LOCATION']
redis_port = os.environ['REDIS_PORT']
r = redis.Redis(host=redis_location, port=redis_port, db=0)

# Inicializamos el cliente de Google Cloud Storage
storage_client = storage.Client()

@APP.route('/author')
def dev_info():
    """ Muestra la página inicial asociada al recurso `/author`
        y que estará devolvera un json con el author y email
    """
    mensaje = {
        "author": nombre,
        "email": email
    }
    return jsonify(mensaje)

@APP.route('/risk/<city_id>', methods=['POST'])
def create_risk(city_id):
    try:
        # Obtener los datos de la petición
        data = request.get_json()
        city_name = data['city_name']
        risk = data['risk']
        level = data['level']

        # Validar los datos
        if len(risk) > 80:
            return jsonify({"error": "Risk description too long, max 80 characters"}), 400
        if level <= 0:
            return jsonify({"error": "Level must be a positive integer"}), 400

        # Crear el objeto de riesgo
        risk_data = {
            "city_id": city_id,
            "city": city_name,
            "risk": risk,
            "level": level
        }
        # Se podria usar un r.set
        # Guardar el riesgo en Redis con una expiración de 10 segundos 
        r.setex(city_id, 10, json.dumps(risk_data))

        # Subir el riesgo a GCS
        bucket = storage_client.bucket(BUCKET_NAME)  # Accedemos al bucket
        blob = bucket.blob(city_id)  # Creamos un blob (archivo) con el ID de la ciudad
        blob.upload_from_string(json.dumps(risk_data), content_type='application/json')  # Subimos los datos

        # Retornar la respuesta
        return jsonify(risk_data), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@APP.route('/risk/<city_id>', methods=['GET'])
def get_risk(city_id):
    try:
        # Consultar si el riesgo existe en Redis
        risk_data = r.get(city_id)
        if risk_data:
            risk_data = json.loads(risk_data.decode('utf-8'))
        if not risk_data:
            # Buscar en GCS si no está en Redis
            bucket = storage_client.bucket(BUCKET_NAME)  # Accedemos al bucket
            blob = bucket.blob(city_id)  # Accedemos al blob con el ID de la ciudad
            if blob.exists():
                risk_data = blob.download_as_string()  # Descargamos los datos
                risk_data = json.loads(risk_data)  # Convertimos los datos a diccionario

                # Restaurar en Redis
                r.setex(city_id, 10, json.dumps(risk_data))
            else:
                return jsonify({"error": "Risk not found or expired"}), 404

        # Convertir el riesgo de vuelta a un diccionario (json)
        return jsonify(risk_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    APP.debug = True
    APP.run(host='0.0.0.0', port=os.environ['PORT'])
