#!/usr/bin/env python

from flask import Flask, jsonify 
import os

# Crear el objeto que representa la aplicacion web
APP = Flask(__name__)
nombre=os.environ['AUTHOR_NAME']
email=os.environ['AUTHOR_EMAIL']


@APP.route('/author')
def dev_info():
    """ Muestra la página inicial asociada al recurso `/author`
        y que estará devolvera un json con el author y email
    """
    mensaje={
        "author" : nombre ,
        "email" : email    
    }

    return jsonify(mensaje)


if __name__ == '__main__':
    APP.debug = True
    APP.run(host='0.0.0.0', port=os.environ['PORT'])
