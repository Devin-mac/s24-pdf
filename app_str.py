import streamlit as st
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
import base64
import streamlit.components.v1 as components

# --- Configuración de página ---
st.set_page_config(page_title="Formulario S-24", layout="centered")
st.title("📄 Generador de PDF - Registro de Transacción S-24")

# --- Fecha manual (día, mes, año) ---
st.subheader("📆 Fecha de transacción")
dias = list(range(1, 32))
meses = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]
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
        "DONACIÓN", "PAGO", "DEPÓSITO EN LA CAJA DE EFECTIVO", "ADELANTO DE EFECTIVO"
    ])

    st.subheader("💰 Donaciones")
    don_obra = st.number_input("Donaciones (Obra mundial)", min_value=0, value=0)
    don_congre = st.number_input("Donaciones (Gastos de la congregación)", min_value=0, value=0)

    st.subheader("📌 Concepto adicional (opcional)")
    concepto = st.text_input("Descripción del concepto")
    valor_concepto = st.number_input("Valor del concepto", min_value=0, value=0)

    total = sum(v for v in [don_obra, don_congre, valor_concepto] if v is not None)
    st.markdown(f"**TOTAL: ${total:,.0f} COP**")

    nombre_1 = st.text_input("Nombre de quien rellena")
    nombre_2 = st.text_input("Nombre de quien verifica")

    st.subheader("✍️ Firmas")
    st.markdown("**Firma de quien rellena:**")
    firma1 = st_canvas(
        key="firma1",
        height=100,
        width=300,
        drawing_mode="freedraw",
        stroke_width=2,
        stroke_color="black",
        background_color="white"
    )

    st.markdown("**Firma de quien verifica:**")
    firma2 = st_canvas(
        key="firma2",
        height=100,
        width=300,
        drawing_mode="freedraw",
        stroke_width=2,
        stroke_color="black",
        background_color="white"
    )

    enviado = st.form_submit_button("📤 Generar PDF")

# --- Insertar firmas ---
def insertar_firmas(pdf_bytes):
    firma_buffer = BytesIO()
    can = canvas.Canvas(firma_buffer, pagesize=letter)

    for idx, firma_data in enumerate([firma1.image_data, firma2.image_data]):
        if firma_data is not None:
            firma_img = Image.fromarray(firma_data)
            img_stream = BytesIO()
            firma_img.save(img_stream, format="PNG")
            img_stream.seek(0)

            x = 60 if idx == 0 else 310
            y = 100  # altura corregida para que esté dentro del recuadro
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

# --- Crear PDF desde cero ---
def crear_pdf():
    buffer = BytesIO()
    can = canvas.Canvas(buffer, pagesize=letter)

    x_izq = 60
    x_derecha = 540
    y = 760

    # Título
    can.setFont("Helvetica-Bold", 14)
    can.drawCentredString(300, y, "REGISTRO DE TRANSACCIÓN")
    y -= 30

    # Fecha
    can.setFont("Helvetica", 10)
    can.drawRightString(x_derecha, y, f"Fecha: {fecha_str}")
    y -= 20

    # Tipo transacción
    can.setFont("Helvetica-Bold", 10)
    can.drawString(x_izq, y, "Seleccione el tipo de transacción:")
    y -= 18

    can.setFont("Helvetica", 10)
    opciones = {
        "DONACIÓN": "Donación",
        "PAGO": "Pago",
        "DEPÓSITO EN LA CAJA DE EFECTIVO": "Depósito en la caja de efectivo",
        "ADELANTO DE EFECTIVO": "Adelanto de efectivo"
    }
    for clave, texto in opciones.items():
        marca = "X" if clave == tipo else " "
        can.drawString(x_izq, y, f"[{marca}] {texto}")
        y -= 15

    can.line(x_izq, y, x_derecha, y)
    y -= 25

    # Donaciones
    can.setFont("Helvetica-Bold", 10)
    can.drawString(x_izq, y, "DETALLES DE LA TRANSACCIÓN")
    y -= 18
    can.setFont("Helvetica", 10)

    can.drawString(x_izq, y, "Donaciones (Obra mundial):")
    can.drawRightString(x_derecha, y, f"${don_obra:,.0f}")
    y -= 15

    can.drawString(x_izq, y, "Donaciones (Gastos de la congregación):")
    can.drawRightString(x_derecha, y, f"${don_congre:,.0f}")
    y -= 15

    if concepto:
        can.drawString(x_izq, y, f"{concepto}:")
        can.drawRightString(x_derecha, y, f"${valor_concepto:,.0f}")
        y -= 15

    y -= 10
    can.line(x_izq, y, x_derecha, y)
    y -= 25

    # Total
    can.setFont("Helvetica-Bold", 12)
    can.drawString(x_izq, y, "TOTAL:")
    can.drawRightString(x_derecha, y, f"${total:,.0f}")
    y -= 40

    # Nombres
        # Nombres centrados
    can.setFont("Helvetica", 10)
    nombres_y = y  # guardar y para usarlo luego con firmas
    texto_nombres = f"Rellenado por: {nombre_1}        Verificado por: {nombre_2}"
    can.drawCentredString(300, y, texto_nombres)

    # Líneas debajo de los nombres (centradas también)
    can.line(120, y - 2, 250, y - 2)  # debajo de "Rellenado por"
    can.line(360, y - 2, 490, y - 2)  # debajo de "Verificado por"
    y -= 60


    # Firmas
    can.setFont("Helvetica", 10)
    can.drawString(x_izq, y + 45, "Firma de quien rellena:")
    can.rect(x_izq, y, 120, 40)

    can.drawString(x_izq + 250, y + 45, "Firma de quien verifica:")
    can.rect(x_izq + 250, y, 120, 40)

    # Etiqueta
    can.setFont("Helvetica-Bold", 8)
    can.drawString(260, 30, "S-24-S 5/21")

    can.save()
    buffer.seek(0)
    return buffer

# --- Generar y mostrar PDF ---
if enviado:
    pdf_base = crear_pdf()
    pdf_final = insertar_firmas(pdf_base, firma1.image_data, firma2.image_data)
    nombre_archivo = f"{fecha_str} - {tipo}.pdf"

    b64_pdf = base64.b64encode(pdf_final.getvalue()).decode("utf-8")
    pdf_viewer = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
    st.success("✅ Vista previa del PDF generada:")
    components.html(pdf_viewer, height=510)

    st.download_button("📥 Descargar PDF", data=pdf_final, file_name=nombre_archivo, mime="application/pdf")
