from PyPDF2 import PdfReader
from docx import Document
import pandas as pd
import pytesseract
from PIL import Image
import io
import re
from pdf2image import convert_from_bytes

def extraer_texto_pdf(file_bytes):
    # Intentar extracción por texto (PDF no escaneado)
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        texto = "".join([page.extract_text() or "" for page in reader.pages])
        return texto
    except Exception as e:
        return ""



def extraer_texto_pdf_ocr(file_bytes):
    try:
  
        if not texto_directo.strip():
            # Convertir cada página del PDF a imagen y aplicando OCR
            pages = convert_from_bytes(file_bytes, dpi=150)
            texto_total = ""

            for i, page in enumerate(pages):
                texto = pytesseract.image_to_string(page, lang="spa", config="--psm 6")
                texto_total += f"\n\n--- Página {i+1} ---\n{texto.strip()}"

            # Limpieza de texto
            texto_total = re.sub(r"\s+", " ", texto_total)
            texto_total = re.sub(r"[^\w\sáéíóúñÁÉÍÓÚÑ.,:;()\-/$%#°]", "", texto_total)
            texto_total = texto_total.strip()

            return texto_total

        else:
            texto_directo = re.sub(r"\s+", " ", texto_directo)
            return texto_directo.strip()

    except Exception as e:
        return f"Error procesando el archivo: {str(e)}"




def extraer_texto_imagen(file_bytes):
    image = Image.open(io.BytesIO(file_bytes))
    return pytesseract.image_to_string(image, lang="spa")

#extraer_texto_word
def extraer_texto_word(file_bytes) -> str:
    """Extrae texto de un archivo Word (.docx) dado como bytes."""
    doc = Document(io.BytesIO(file_bytes))
    lineas=[]
    #tratamiento si hay tablas 
    for table in doc.tables:
        for row in table.rows:
            celdas = [c.text.strip() for c in row.cells]
            lineas.append(" | ".join(celdas))
    #tratamiento si hay parrafos normales
    for p in doc.paragraphs:
        texto = p.text.strip()
        if texto:
            lineas.append(texto)   
    texto_completo= "\n".join(lineas)        
    if "ANEXO" in texto:
        partes = texto.split("ANEXO")
        texto = "ANEXO".join(partes[-2:]) + "\n\n" + texto
    return texto_completo
    
    



def extraer_texto_excel(file_bytes):
    """Extrae texto de un archivo Excel (.xls, .xlsx) dado como bytes."""
    try:
        xls = pd.read_excel(io.BytesIO(file_bytes), sheet_name=None)
        contenido = ""
        for nombre, hoja in xls.items():
            contenido += f"--- Hoja: {nombre} ---\n"
            contenido += hoja.to_string(index=False)
        return contenido
    except Exception as e:
        return f"Error leyendo Excel: {e}"