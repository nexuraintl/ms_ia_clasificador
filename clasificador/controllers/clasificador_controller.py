from flask import Blueprint, request, jsonify
from clasificador.services.clasificador_service import clasificar_archivo
import requests


clasificador_bp = Blueprint("clasificador", __name__)


@clasificador_bp.route("/", methods=["POST"])
def clasificar():
    archivo = request.files.get("archivo")

    if not archivo:
        return jsonify({"error": "Archivo no recibido"}), 400

    # Obtener url (opcional)
    url_cliente = request.form.get("url")
    if url_cliente is None and request.is_json:
        url_cliente = request.json.get("url")

    # solo si la url existe se notifica
    if url_cliente:
        notificar_dispersion(url_cliente, "clasificar")

    resultado = clasificar_archivo(archivo)
    return jsonify({"resultado": resultado})


def notificar_dispersion(url_cliente, funcion):

    data = {"url": url_cliente, "funcion": funcion}
    try:
        response = requests.post(
            "https://dispersion-718759852530.us-central1.run.app/dispersion",
            json=data,
            timeout=10,
        )

        if response.status_code == 200:
            print("Registro en dispersión exitoso")
        else:
            print(f"Error de dispersión: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Error al notificar dispersión: {str(e)}")
