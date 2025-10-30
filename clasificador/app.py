import sys
import os
from flask import Flask
from clasificador.controllers.clasificador_controller import clasificador_bp
from clasificador.controllers.procesador_controller import procesador_bp


# Agrega rutas al sys.path solo si lo necesitas (evita esto si usas un paquete con __init__.py)
#sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)
app.register_blueprint(clasificador_bp, url_prefix='/clasificar')
app.register_blueprint(procesador_bp, url_prefix="/metadatos")




#port = int(os.environ.get('PORT', 8080))
#app.run(debug=True, host='0.0.0.0', port=port)