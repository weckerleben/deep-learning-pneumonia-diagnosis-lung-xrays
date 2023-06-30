from datetime import date
from email.mime import image

import cv2
import logging
from logging.handlers import RotatingFileHandler

import numpy as np
from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify
from fastai.vision.all import *
import json

app = Flask(__name__)
swagger = Swagger(app)

# Configurar el registro
log_file = 'app.log'
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024 * 10, backupCount=10)
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

app.logger.addHandler(log_handler)
app.logger.setLevel(logging.INFO)

# Carga del modelo
model = load_learner("./model.pkl")

with open('swagger.json', 'r') as file:
    swagger_json = json.load(file)


@app.route('/health-check', methods=['GET'])
@swag_from(swagger_json['health-check'])
def health_check():
    return jsonify({'status': 'ok'})


@app.route('/neumoscan', methods=['POST'])
@swag_from(swagger_json['neumoscan'])
def analizar_imagen():
    # image_path=""

    # # Get image
    # try:
    # Obtener la fecha actual
    fecha_actual = date.today()
    fecha_formateada = fecha_actual.strftime("%Y/%m/%d")

    # Directorio donde se guardará el archivo
    directorio = f"tmp/{fecha_formateada}"

    # Verificar si el directorio existe, si no, crearlo
    if not os.path.exists(directorio):
        os.makedirs(directorio)

    # Obtener el archivo enviado
    archivo = request.files['imagen']

    extension = os.path.splitext(archivo.filename)[1]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
    file_name = f"RX_{timestamp}{extension}"

    # Guardar el archivo en el directorio
    ruta_archivo = os.path.join(directorio, file_name)
    archivo.save(ruta_archivo)

    #     api.logger.info('Imagen recibida y guardada con éxito en:' + str(ruta_archivo))
    # except:
    #     api.logger.error('Imagen no ha podido ser guardada')

    # Cargar la imagen con OpenCV y convertirla a un formato válido
    image = cv2.imread(ruta_archivo)

    if image is not None:
        # image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.resize(image, (224, 224))

        image_array = np.array(image)

        # Convertir el array numpy a un tensor de PyTorch
        image_tensor = torch.from_numpy(image_array)

        # Ahora puedes enviar el tensor al modelo para realizar la predicción
        pred = model.predict(image_tensor)
    else:
        app.logger.error('No se pudo leer la imagen correctamente')
        return jsonify({'ERROR': 'No se pudo leer la imagen correctamente'})

    # Retorna la respuesta al cliente en formato JSON
    return jsonify({'file': archivo.filename, 'prediction': str(pred[0]), 'probability': float(max(pred[2]))})


if __name__ == '__main__':
    app.run(host='192.168.100.216', port='1796')
