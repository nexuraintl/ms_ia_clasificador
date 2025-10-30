import requests
import os
import json
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def clasificar_documento(texto):
    if not GEMINI_API_KEY:
        return {"error": "API key no configurada"}

    prompt = f""" <ROL: Eres un experto en documentos públicos de Colombia>
                Analiza el siguiente texto y determina el tipo de documento.

Tipos posibles:
- factura
- documento de identidad
- contrato laboral:
 contrato de prestación de servicios pn
 contrato de prestación de servicios pj
- resolución
- PQRS
- otro

###Criteros de desicion si es contrato###
- **PS PJ (persona jurídica):**
  Si el contratista es una empresa o entidad (palabras como “NIT”, “razón social”, “sociedad”, “S.A.S.”, “S.A.”, “E.U.”, “persona jurídica”, “empresa contratista”).

- **Contrato laboral a término indefinido o subordinado:**
  Si se evidencia una relación laboral (palabras como “empleado”, “trabajador”, “salario”, “subordinado”, “nómina”, “prestaciones”, “beneficios laborales”).

Responde *solo* con JSON válido en el formato:
{{"tipo_documento": "<tipo>"}}

Texto:
<<<
{texto[:3000]}
>>>
"""

    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        params={"key": GEMINI_API_KEY},
        json={"contents": [{"parts": [{"text": prompt}]}]},
    )

    if response.status_code != 200:
        return {"error": response.text}

    result = response.json()
    text_result = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", result)

    # Limpieza del texto antes de parsear
    text_result = re.sub(r"```json|```", "", str(text_result)).strip()
    text_result = re.sub(r'(:\s*")([^"]*?)"([^"]*?")', r'\1\2\\\"\3', text_result)

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
                return re.sub(r'\\+$', '', data).strip()
            return data

        json_result = limpiar_valores(json_result)

        return json_result

    except Exception as e:
        return {
            "error": f"No se pudo parsear la respuesta de Gemini: {e}",
            "respuesta_original": text_result
        }