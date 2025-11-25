import requests
import os
import json
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def generar_prompt(texto):
    if not GEMINI_API_KEY:
        return {"error": "API key no configurada"}

    prompt = f"""Rol<Experto hallando metadatos de archivos o recurso con Dublin Core>

INSTRUCCIONES:
-Responde únicamente en JSON válido.
-De no encontrar un campo o haber error devuelve "no identificado".
-Si un campo aparece parcialmente, incluye lo que esté disponible
-fechas devuelvelas en formato: YYYY-MM-DD.
-prioriza retornar un valor a los campos CAMPOS A EXTRAER:

ENTRADA:
<<<
{texto[:15000]}
>>>

CAMPOS A EXTRAER:
-Titulo(de no encontrar o haber error devolver vacio))
-Creador(Entidad responsable de la creación del contenido)
-Fecha (creacion publicacion del articulo)
-Tema 
-Descripcion (literal, de no haber error devuelve vacio)
-Formato
-Identificador(Una referencia única para el recurso, ejemplo: URL)
-Editor
-Tipo (artículo,libro, imagen de no encontrar o haber error devolver vacio)
-Relacion (Infiere si exite vinculo, relacion, version con otro recurso)
-Derechos: (propiedad intelectual, licencia)
-Fuente(procedencia o de donde se derivo el contenido) 
-Cobertura(lugar sin abreviatura - tiempo)
"""

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        params={"key": GEMINI_API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    text_result = (
        result.get("candidates", [{}])[0]
        .get("content", {})
        .get("parts", [{}])[0]
        .get("text", result)
    )

    # Limpieza del texto antes de parsear
    text_result = re.sub(r"```json|```", "", str(text_result)).strip()
    text_result = re.sub(r'(:\s*")([^"]*?)"([^"]*?")', r"\1\2\\\"\3", text_result)

    try:
        json_result = json.loads(text_result)

        # Si "contenido" es lista de diccionarios → unificar
        if isinstance(json_result.get("contenido"), list):
            contenido_unido = {}
            for item in json_result["contenido"]:
                if isinstance(item, dict):
                    contenido_unido.update(item)
            json_result["contenido"] = contenido_unido

        # 🔹 Limpieza final de barras invertidas sobrantes al final
        def limpiar_valores(data):
            if isinstance(data, dict):
                return {k: limpiar_valores(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [limpiar_valores(v) for v in data]
            elif isinstance(data, str):
                return re.sub(r"\\+$", "", data).strip()
            return data

        json_result = limpiar_valores(json_result)

        return json_result

    except Exception as e:
        return {
            "error": f"No se pudo parsear la respuesta de Gemini: {e}",
            "respuesta_original": text_result,
        }
