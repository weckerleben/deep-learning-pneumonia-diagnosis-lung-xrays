import os
from datetime import date, datetime

import logging
from logging.handlers import RotatingFileHandler

from flasgger import Swagger, swag_from
from flask import Flask, request, jsonify
from fastai.vision.all import load_learner, PILImage
import json

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff'}
MAX_FILE_SIZE_MB = 15
CONFIDENCE_THRESHOLD = float(os.environ.get('CONFIDENCE_THRESHOLD', '0.70'))

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
    if 'imagen' not in request.files:
        return jsonify({'ERROR': 'No se envió ningún archivo'}), 400

    archivo = request.files['imagen']

    if archivo.filename == '':
        return jsonify({'ERROR': 'Nombre de archivo vacío'}), 400

    extension = os.path.splitext(archivo.filename)[1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        return jsonify({'ERROR': f'Formato no soportado. Usar: {", ".join(ALLOWED_EXTENSIONS)}'}), 415

    # Verificar tamaño (leer en memoria temporalmente)
    archivo.seek(0, 2)
    file_size_mb = archivo.tell() / (1024 * 1024)
    archivo.seek(0)
    if file_size_mb > MAX_FILE_SIZE_MB:
        return jsonify({'ERROR': f'Archivo demasiado grande. Máximo: {MAX_FILE_SIZE_MB}MB'}), 413

    # Construir ruta con jerarquía de fecha
    fecha_formateada = date.today().strftime("%Y/%m/%d")
    directorio = f"tmp/{fecha_formateada}"
    os.makedirs(directorio, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
    file_name = f"RX_{timestamp}{extension}"
    ruta_archivo = os.path.join(directorio, file_name)
    archivo.save(ruta_archivo)
    app.logger.info(f'Imagen guardada en: {ruta_archivo}')

    try:
        # FastAI maneja el preprocessing completo (resize, normalización, RGB)
        # de la misma forma que en el entrenamiento
        img = PILImage.create(ruta_archivo)
        pred_class, pred_idx, probs = model.predict(img)
    except Exception as e:
        app.logger.error(f'Error al procesar imagen: {e}')
        return jsonify({'ERROR': 'No se pudo procesar la imagen'}), 500

    max_prob = float(probs.max())

    if max_prob < CONFIDENCE_THRESHOLD:
        return jsonify({
            'file': archivo.filename,
            'prediction': 'INCONCLUSIVE',
            'probability': round(max_prob, 4),
            'message': f'Confianza insuficiente ({max_prob:.1%}). Se requiere radiografía de mayor calidad.'
        })

    return jsonify({
        'file': archivo.filename,
        'prediction': str(pred_class),
        'probability': round(max_prob, 4)
    })


if __name__ == '__main__':
    host = os.environ.get('API_HOST', '0.0.0.0')
    port = int(os.environ.get('API_PORT', '1796'))
    app.run(host=host, port=port)
