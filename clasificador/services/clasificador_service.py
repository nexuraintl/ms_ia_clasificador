from pathlib import Path
from clasificador.utils.conversor_texto import (
    extraer_texto_pdf,
    extraer_texto_pdf_ocr,
    extraer_texto_imagen,
    extraer_texto_word,
    extraer_texto_excel
)
#from clasificador.prompts.generador_prompt import clasificar_documento
from clasificador.services.pipeline import procesar_documento

EXTENSIONES_SOPORTADAS = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx', '.xls', '.xlsx']

def clasificar_archivo(archivo) -> str:
    try:
        contenido = archivo.read()
        extension = Path(archivo.filename).suffix.lower()

        if extension not in EXTENSIONES_SOPORTADAS:
            return f"Tipo de archivo no soportado: {extension}"

        texto = ""

        if extension == '.pdf':
            texto = extraer_texto_pdf(contenido)
            if len(texto.strip()) < 1000:
                texto_ocr = extraer_texto_pdf_ocr(contenido)
                if len(texto_ocr) > len(texto):
                    texto = texto_ocr

        elif extension in ['.jpg', '.jpeg', '.png']:
            texto = extraer_texto_imagen(contenido)

        elif extension in ['.doc', '.docx']:
            
            texto = extraer_texto_word(contenido)

        elif extension in ['.xls', '.xlsx']:
            texto = extraer_texto_excel(contenido)

        if not texto.strip():
            return "No se pudo extraer texto del archivo."

        return procesar_documento(texto)

    except Exception as e:
        return f"Error procesando el archivo: {str(e)}"