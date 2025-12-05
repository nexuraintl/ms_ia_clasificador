import sys
import os
from flask import Flask
from flask_cors import CORS
from clasificador.controllers.clasificador_controller import clasificador_bp
from clasificador.controllers.procesador_controller import procesador_bp


# Agrega rutas al sys.path solo si lo necesitas (evita esto si usas un paquete con __init__.py)
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
app.register_blueprint(clasificador_bp, url_prefix='/clasificar')
app.register_blueprint(procesador_bp, url_prefix="/metadatos")

# Configuración de CORS en el dominio de producción
CORS(
    app,
    resources={r"/*": {"origins": "https://pruebas-servicios.nexura.com"}},
    supports_credentials=True,
    expose_headers=["Content-Type", "Authorization"],
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS"],
)

#port = int(os.environ.get('PORT', 8080))
#app.run(debug=True, host='0.0.0.0', port=port)