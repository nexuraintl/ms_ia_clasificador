import requests
import os
import json
import re

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

def extraer_datos(texto: str, tipo_documento: str):
    if not GEMINI_API_KEY:
        return {"error": "API key no configurada"}

    prompt = f""" <ROL: Experto en documentos publicos de Colombia> El documento detectado es "{tipo_documento}".
    Extrae solo los campos relevantes segun este tipo y devuelvelos como JSON valido.

    TAREA:
    Analiza TODO el texto buscando la informacion que corresponda a los campos definidos para el tipo documental identificado.    

    SI ES ALGUN TIPO DE CONTRATO:
    - Lee TODO el documento, no asumas que los datos estan en el cuerpo principal del contrato examina especialmente secciones:FORMATO, TABLAS, DATOS DEL CONTRATO, HOJA DE VIDA DEL CONTRATISTA, ANEXO(contiene datos reales del contratista).
    Cada campo debe extraerse con base en coincidencias semanticas o textuales cercanas de los campos definidos o de contacto.  

    INSTRUCCIONES DE EXTRACCION:

    - Nombre: busca despues de "CONTRATISTA", "identificado", en tablas, en anexos
    - Cedula: busca "C.C.", 7-10 dígitos
    - Direccion: busca "Dirección" o en tablas
    - Email: busca "@", "correo", "e-mail"
    - Celular: busca números de 10 dígitos, "celular", "teléfono", "móvil"
    - Ciudad: busca nombre de ciudad seguido de paréntesis o cerca de dirección
    - Valor: se encuentra en cifras grandes con "$" o "PESOS", "por valor de", en clausulas economicas, de ser necesario multipica la cantidad de meses * salario mensual, *solo devuevlve el numero*
    - Objeto: busca "CLÁUSULA PRIMERA", "OBJETO", "tiene por objeto"
    - Fechas: busca "inicia", "desde el", formato de fecha, "plazo"
  
TEXTO:
<<<
{texto[:len(texto)]}
>>>

SALIDA ESPERADA: 
- Formato JSON válido sin ```, ni texto adicional, Si falta: "no disponible".
- Escapa todas las comillas dobles internas como \\". 
- Las fechas devuelvelas en el formato: YYYY-MM-DD. 
- Si un valor hace referencia a un anexo (por ejemplo, "ver Anexo No.1", "descrita en el Anexo", "según tabla anexa"), busca ese campo en la seccion del anexo mas adelante, usa el valor real (por ejemplo, un número, nombre o fecha) en lugar de repetir el texto de referencia.
-Si es un tipo de contrato diferente a los especificados extrae los campos importantes
CAMPOS CLAVE POR TIPO DOCUMENTAL: 

FACTURA: 
- Número de factura 
- Fecha de emisión 
- Fecha de vencimiento 
- Nombre del proveedor 
- NIT del proveedor 
- Dirección del proveedor 
- Nombre del cliente 
- NIT del cliente 
- Dirección del cliente 
- Concepto o descripción del servicio/producto 
- Cantidad 
- Valor unitario 
- Subtotal 
- IVA 
- Descuentos 
- Total a pagar 
- Forma de pago 
- Estado de pago (pagada, pendiente, vencida) 

DOCUMENTO DE IDENTIDAD: 
- Tipo de documento 
- Número de documento 
- Nombres 
- Apellidos 
- Fecha de nacimiento 
- Lugar de nacimiento 
- Nacionalidad 
- Sexo 
- Rh o grupo sanguíneo 
- Fecha de expedición 
- Lugar de expedición 
- Entidad emisora 
- Código MRZ (si aplica) 
- Estado del documento (vigente, vencido, cancelado) 

### CRITERIOS ESPECIFICOS PARA CONTRATOS: No devuelvas ningún campo adicional.

**Contrato de prestacion de servicios - persona natural (PS PN)**
-Nombre contratista 
-Doc. Identidad del contratista 
-Dirección de notificación del contratista 
-Ciudad del contratista 
-E-mail del contratista 
-Celular del contratista 
-Cláusula primera - Objeto 
-Cláusula Segunda. - Valor del Contrato(numero) 
-Empleador 
-fecha de inicio (Fecha de ejecución o fecha de firma) 
-valor total: si se mencionan auxilios, bonos, salario en especie o Beneficio extralegal sumarlos al valor del contrato


**Contrato de prestacion de servicios - persona jurídica (PS PJ)**
El contratista es una empresa o entidad (palabras clave: “NIT”, “razón social”, “sociedad”, “S.A.S.”, “S.A.”, “E.U.”, “persona jurídica”, “empresa contratista”).

-Nombre empleador
-Nombre persona juridica
-Objeto del contrato (sintetizar no mas de 80 caracteres)
-Fecha de inicio (Fecha de ejecución o fecha de firma esta antes de la firma no tomes la fecha de version del documento) 
-Valor del Contrato (devolver la totalidad del valor en numeros) 
-Tipo de pago (mensual o cumplimiento de actividades) sintetizar a partir de clausulas economicas

**Contrato laboral a termino indefinido**
Menciona conceptos laborales (“empleado”, “trabajador”, “subordinado”, “salario”, “nomina”, “prestaciones”, “beneficios laborales”).
-Nombre del empleador 
-Valor del Contrato (devolver la totalidad del valor en numeros, de no encontrarlo ve a la secciones que lo especifican para obtenerlo)
-Fecha inicio 
-Objeto del contrato o segunda -funciones 
-Nombre empleado 
-Identificacion del empleado
"""
    
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        params={"key": GEMINI_API_KEY},
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0,
                "topK": 1,
                "topP": 0
            }
        }
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

        # Limpieza final de barras invertidas sobrantes al final
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
    

