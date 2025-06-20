# app_str.py
import streamlit as st
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
import base64

# --- Configuración de página ---
st.set_page_config(page_title="Formulario S-24", layout="centered")

# --- Estilo global moderno ---
st.markdown("""
    <style>
    body {
        background-color: #f4f6f8;
        font-family: 'Segoe UI', sans-serif;
    }
    .stApp {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }
    input[type="number"], input[type="text"] {
        font-size: 24px !important;
    }
    .stNumberInput input, .stTextInput input {
        font-size: 24px !important;
        padding: 0.5rem;
        border-radius: 8px;
    }
    label, .stRadio label, .stSelectbox label, .stTextInput label, .stNumberInput label {
        font-size: 20px !important;
    }
    h3 {
        font-size: 26px !important;
    }
    .markdown-text-container, .stMarkdown {
        font-size: 20px !important;
    }
    button[kind="primary"] {
        font-size: 20px !important;
        padding: 0.6rem 1.2rem;
        border-radius: 8px !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📄 Generador de PDF - Registro de Transacción S-24")

# --- Fecha manual ---
st.subheader("📆 Fecha de transacción")
dias = list(range(1, 32))
meses = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
         "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
anios = list(range(2020, 2031))

col1, col2, col3 = st.columns(3)
with col1:
    dia = st.selectbox("Día", dias, index=dias.index(date.today().day))
with col2:
    mes = st.selectbox("Mes", meses, index=date.today().month - 1)
with col3:
    anio = st.selectbox("Año", anios, index=anios.index(date.today().year))

fecha_str = f"{dia:02d} {mes} {anio}"

# --- Formulario de datos ---
with st.form("formulario"):
    tipo = st.radio("Seleccione el tipo de transacción", [
        "DONACIÓN", "PAGO", "DEPÓSITO EN LA CAJA DE EFECTIVO", "ADELANTO DE EFECTIVO"])

    st.subheader("💰 Donaciones")
    don_obra = st.number_input("Donaciones (Obra mundial)", min_value=0.0, value=0.0)
    don_congre = st.number_input("Donaciones (Gastos de la congregación)", min_value=0.0, value=0.0)

    st.subheader("📌 Concepto adicional (opcional)")
    concepto = st.text_input("Descripción del concepto")
    valor_concepto = st.number_input("Valor del concepto", min_value=0.0, value=0.0)

    total = sum(v for v in [don_obra, don_congre, valor_concepto] if v is not None)
    st.markdown(f"**TOTAL: ${total:,.2f} COP**")

    nombre_1 = st.text_input("Nombre de quien rellena")
    nombre_2 = st.text_input("Nombre de quien verifica")

    st.subheader("✍️ Firmas")
    st.markdown("**Firma de quien rellena:**")
    firma1 = st_canvas(key="firma1", height=300, width=900, drawing_mode="freedraw",
                       stroke_width=2, stroke_color="black", background_color="white")
    st.markdown("**Firma de quien verifica:**")
    firma2 = st_canvas(key="firma2", height=300, width=900, drawing_mode="freedraw",
                       stroke_width=2, stroke_color="black", background_color="white")

    enviado = st.form_submit_button("📤 Generar PDF")

# --- Dibujar checkbox cuadrado ---
def dibujar_checkbox_cuadrado(canvas, x, y, marcado=False, size=12):
    canvas.rect(x, y, size, size, stroke=1, fill=0)
    if marcado:
        canvas.setFont("Helvetica-Bold", size-2)
        x_center = x + size/2 - 3
        y_center = y + 2
        canvas.drawString(x_center, y_center, "X")

# --- Insertar firmas ---
def insertar_firmas(pdf_bytes, firma1_data, firma2_data, firma_y_pos):
    firma_buffer = BytesIO()
    can = canvas.Canvas(firma_buffer, pagesize=landscape(letter))

    for idx, firma_data in enumerate([firma1_data, firma2_data]):
        if firma_data is not None:
            firma_img = Image.fromarray(firma_data)
            import numpy as np
            from scipy import ndimage
            firma_array = np.array(firma_img)
            mascara_firma = np.all(firma_array[:, :, :3] == [0, 0, 0], axis=-1)
            mascara_gruesa = ndimage.binary_dilation(mascara_firma, iterations=4)
            firma_array[mascara_gruesa] = [0, 0, 255, 255]
            firma_img_azul = Image.fromarray(firma_array)
            img_stream = BytesIO()
            firma_img_azul.save(img_stream, format="PNG")
            img_stream.seek(0)
            x = 190 if idx == 0 else 490
            y = firma_y_pos + 5
            can.drawImage(ImageReader(img_stream), x, y, width=120, height=40)

    can.save()
    firma_buffer.seek(0)
    base_pdf = PdfReader(pdf_bytes)
    firma_pdf = PdfReader(firma_buffer)
    writer = PdfWriter()
    page = base_pdf.pages[0]
    page.merge_page(firma_pdf.pages[0])
    writer.add_page(page)
    final_output = BytesIO()
    writer.write(final_output)
    final_output.seek(0)
    return final_output

# --- Crear PDF (usa la versión final que ajustamos contigo) ---
from crear_pdf_funcion import crear_pdf

# --- Generar y descargar PDF ---
if enviado:
    try:
        if firma1.image_data is None or firma2.image_data is None:
            st.error("❌ Ambas firmas son obligatorias para generar el PDF.")
        else:
            pdf_base, firma_y_position = crear_pdf()
            pdf_final = insertar_firmas(pdf_base, firma1.image_data, firma2.image_data, firma_y_position)
            pdf_bytes = pdf_final.getvalue()

            if pdf_bytes:
                nombre_archivo = f"{fecha_str} - {tipo}.pdf"
                st.markdown("""
                <div style="border:1px solid #ccc; padding:10px; border-radius:10px; background:#f9f9f9">
                📱 <b>¿Usas un celular?</b><br>
                Es posible que el archivo descargado tenga un nombre genérico como <i>file.pdf</i>. Puedes renombrarlo después.<br><br>
                Para <b>compartir</b> el archivo (por WhatsApp, correo, Google Drive, etc.), abre el PDF desde tu dispositivo y usa el botón de <i>Compartir</i>.
                </div>
                """, unsafe_allow_html=True)

                st.download_button(
                    "📥 Descargar PDF",
                    data=pdf_bytes,
                    file_name=nombre_archivo,
                    mime="application/pdf"
                )
            else:
                st.error("❌ El PDF generado está vacío. Verifica los datos ingresados.")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al generar el PDF: {e}")
