from flask import Blueprint, request, jsonify
from clasificador.services.clasificador_service import clasificar_archivo
import requests


clasificador_bp = Blueprint('clasificador', __name__)

@clasificador_bp.route('/', methods=['POST'])
def clasificar():
    archivo = request.files.get('archivo')
    url_cliente = request.form.get('url') or (request.json.get('url') if request.is_json else None)

    funcion = 'clasificar'
    notificar_dispersion(url_cliente,funcion)

    if not archivo:
        return jsonify({'error': 'Archivo no recibido'}), 400

    if not url_cliente:
        return jsonify({'error': 'URL del cliente no recibida'}), 400

    
    resultado = clasificar_archivo(archivo)
    return jsonify({'resultado': resultado})

def notificar_dispersion(url_cliente, funcion):
    data = {
        "url": url_cliente,
        "funcion": funcion    }

    response = requests.post(
        "https://dispersion-718759852530.us-central1.run.app/dispersion",
        json=data
    )

    if response.status_code == 200:
        print("Registro en dispersión exitoso")
    else:
        print(f"Error en dispersión: {response.status_code} - {response.text}")