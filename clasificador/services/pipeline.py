from clasificador.prompts.generador_prompt import clasificar_documento
from clasificador.prompts.extractor_prompt import extraer_datos


def procesar_documento(texto: str):
    
    # Orquesta el flujo completo de procesamiento:
    # 1. Clasifica el tipo de documento.
    # 2. Extrae los campos clave según el tipo detectado.
  

    #  Paso: Clasificar tipo de documento
    tipo_resultado = clasificar_documento(texto)
    tipo_doc = tipo_resultado.get("tipo_documento")

    if not tipo_doc or "error" in tipo_resultado:
        return {
            "error": "No se pudo determinar el tipo de documento",
            "detalle": tipo_resultado
        }

    #  Extraer los datos relevantes segun el tipo
    extraccion = extraer_datos(texto, tipo_doc)

    if "error" in extraccion:
        return {
            "error": "No se pudieron extraer los campos",
            "tipo_documento": tipo_doc,
            "detalle": extraccion
        }

    # Combinar resultados
    return {
        "tipo_documento": tipo_doc,
        "campos_extraidos": extraccion
    }