"""
Inserta las firmas dibujadas (imágenes del canvas) dentro del PDF base,
y escribe los metadatos finales del archivo.
"""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import pikepdf


def procesar_firma(firma_data):
    try:
        if firma_data is not None:
            img = Image.fromarray(firma_data)
            buf = BytesIO()
            img.save(buf, format="PNG")
            buf.seek(0)
            return buf
        return None
    except Exception as e:
        print(f"Error procesando firma: {e}")
        return None


def insertar_firmas(pdf_bytes, firma1_data, firma2_data, firma_y_pos, nombre_archivo="S-24"):
    try:
        # 1) Dibujar capa de firmas con ReportLab
        firma_buffer = BytesIO()
        c = canvas.Canvas(firma_buffer, pagesize=landscape(letter))
        for idx, fdata in enumerate([firma1_data, firma2_data]):
            if fdata is not None:
                stream = procesar_firma(fdata)
                if stream:
                    x = 150 if idx == 0 else 470
                    c.drawImage(ImageReader(stream), x, firma_y_pos + 5,
                                width=226, height=80, preserveAspectRatio=True)
        c.save()
        firma_buffer.seek(0)

        # 2) Merge con PyPDF2
        base_pdf = PdfReader(pdf_bytes)
        firma_pdf = PdfReader(firma_buffer)
        writer = PdfWriter()
        page = base_pdf.pages[0]
        page.merge_page(firma_pdf.pages[0])
        writer.add_page(page)
        merged = BytesIO()
        writer.write(merged)
        merged.seek(0)

        # 3) Escribir metadata con pikepdf (unico metodo confiable en movil)
        titulo_limpio = nombre_archivo.replace(".pdf", "")
        merged_out = BytesIO()
        with pikepdf.open(merged) as pdf:
            with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
                meta["dc:title"] = titulo_limpio
                meta["dc:subject"] = titulo_limpio
                meta["dc:creator"] = ["Congregación S-24"]
            # Tambien escribir en DocInfo clasico para lectores antiguos
            pdf.docinfo["/Title"] = titulo_limpio
            pdf.docinfo["/Subject"] = titulo_limpio
            pdf.docinfo["/Author"] = "Congregación S-24"
            pdf.docinfo["/Creator"] = "Formulario S-24"
            pdf.save(merged_out)
        merged_out.seek(0)
        return merged_out
    except Exception as e:
        print(f"Error insertando firmas: {e}")
        return BytesIO(pdf_bytes.getvalue())
