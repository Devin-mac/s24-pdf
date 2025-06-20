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
    st.markdown(f"**TOTAL: ${total:,} COP**")

    nombre_1 = st.text_input("Nombre de quien rellena")
    nombre_2 = st.text_input("Nombre de quien verifica")

    st.subheader("✍️ Firmas")
    st.markdown("**Firma de quien rellena:**")
    firma1 = st_canvas(
        key="firma1",
        height=300,
        width=900,
        drawing_mode="freedraw",
        stroke_width=2,
        stroke_color="black",
        background_color="white"
    )

    st.markdown("**Firma de quien verifica:**")
    firma2 = st_canvas(
        key="firma2",
        height=300,
        width=900,
        drawing_mode="freedraw",
        stroke_width=2,
        stroke_color="black",
        background_color="white"
    )

    enviado = st.form_submit_button("📤 Generar PDF")

# --- Insertar firmas ---
def insertar_firmas(pdf_bytes, firma1_data, firma2_data, firma_y_pos):
    firma_buffer = BytesIO()
    can = canvas.Canvas(firma_buffer, pagesize=landscape(letter))  # CAMBIO 2: Orientación horizontal

    for idx, firma_data in enumerate([firma1_data, firma2_data]):
        if firma_data is not None:
            # CAMBIO 1: Convertir firma a azul y más gruesa
            firma_img = Image.fromarray(firma_data)
            # Convertir a azul y hacer más gruesa la firma
            import numpy as np
            firma_array = np.array(firma_img)
            # Crear máscara para píxeles negros (firma)
            mascara_firma = np.all(firma_array[:, :, :3] == [0, 0, 0], axis=-1)
            # Hacer la firma más gruesa (dilatación simple)
            from scipy import ndimage
            mascara_gruesa = ndimage.binary_dilation(mascara_firma, iterations=4)
            # Aplicar color azul a la firma gruesa
            firma_array[mascara_gruesa] = [0, 0, 255, 255]  # Azul
            firma_img_azul = Image.fromarray(firma_array)
            
            img_stream = BytesIO()
            firma_img_azul.save(img_stream, format="PNG")
            img_stream.seek(0)

            # Ajustar posiciones para orientación horizontal
            x = 190 if idx == 0 else 490  # Posiciones ajustadas para horizontal
            y = firma_y_pos + 5  # Posicionar las firmas justo encima de las líneas de nombres
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
    can = canvas.Canvas(buffer, pagesize=landscape(letter))  # CAMBIO 2: Orientación horizontal

    x_izq = 90
    x_derecha = 700  # CAMBIO 2: Ajuste para orientación horizontal (792-60)
    y = 550  # CAMBIO 2: Ajuste altura inicial para horizontal

    # Título centrado
    can.setFont("Helvetica-Bold", 20)
    can.drawCentredString(396, y, "REGISTRO DE TRANSACCIÓN")  # CAMBIO 2: Centro horizontal (792/2)
    y -= 40

    # Línea con "Seleccione el tipo de transacción" y "Fecha"
    can.setFont("Helvetica-Bold", 16)
    can.drawString(x_izq, y, "Seleccione el tipo de transacción:")
    
    # Fecha a la derecha con línea
    fecha_text = f"Fecha: {fecha_str}" if fecha_str else "Fecha: _______________"
    can.drawRightString(x_derecha, y, fecha_text)
    y -= 25

    # Tipos de transacción en 2 columnas
    can.setFont("Helvetica", 14)
    
    # Columna izquierda
    col_izq_x = x_izq
    col_der_x = 396  # CAMBIO 2: Centro de la página horizontal
    
    # Fila 1
    marca_donacion = "X" if tipo == "DONACIÓN" else " "
    marca_pago = "X" if tipo == "PAGO" else " "
    can.drawString(col_izq_x, y, f"[ {marca_donacion} ] Donación")
    can.drawString(col_der_x, y, f"[ {marca_pago} ] Pago")
    y -= 15
    
    # Fila 2
    marca_deposito = "X" if tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO" else " "
    marca_adelanto = "X" if tipo == "ADELANTO DE EFECTIVO" else " "
    can.drawString(col_izq_x, y, f"[ {marca_deposito} ] Depósito en la caja de efectivo")
    can.drawString(col_der_x, y, f"[ {marca_adelanto} ] Adelanto de efectivo")
    y -= 30

    # Sección de donaciones y conceptos
    can.setFont("Helvetica", 16)
    
    # Donaciones (Obra mundial)
    can.drawString(x_izq, y, "Donaciones (Obra mundial)")
    if don_obra > 0:
        can.drawRightString(x_derecha, y, f"{don_obra:,}")
    else:
        can.drawRightString(x_derecha, y, "_______________")
    y -= 15

    # Donaciones (Gastos de la congregación)
    can.drawString(x_izq, y, "Donaciones (Gastos de la congregación)")
    if don_congre > 0:
        can.drawRightString(x_derecha, y, f"{don_congre:,}")
    else:
        can.drawRightString(x_derecha, y, "_______________")
    y -= 15

    # Concepto adicional si existe
    if concepto:
        can.drawString(x_izq, y, concepto)
        if valor_concepto > 0:
            can.drawRightString(x_derecha, y, f"{valor_concepto:,}")
        else:
            can.drawRightString(x_derecha, y, "_______________")
        y -= 15

    # Líneas adicionales en blanco (3 líneas como en el diseño)
    lineas_extra = 3 if not concepto else 2
    for i in range(lineas_extra):
        can.drawString(x_izq, y, "_" * 45)
        can.drawRightString(x_derecha, y, "_______________")
        y -= 15

    y -= 10

    # Total
    can.setFont("Helvetica-Bold", 18)
    can.drawRightString(x_derecha - 100, y, "TOTAL:")
    if total > 0:
        can.drawRightString(x_derecha, y, f"{total:,}")
    else:
        can.drawRightString(x_derecha, y, "_______________")
    y -= 60

    # Sección de firmas
    # Posiciones centradas para las firmas - CAMBIO 2: Ajustadas para horizontal
    firma1_x = 240
    firma2_x = 550
    firma_y = y - 40
    
    # Líneas para firmas
    linea_width = 120
    linea_y = firma_y - 10
    can.line(firma1_x - linea_width/2, linea_y, firma1_x + linea_width/2, linea_y)
    can.line(firma2_x - linea_width/2, linea_y, firma2_x + linea_width/2, linea_y)
    
    # Nombres sobre las líneas
    can.setFont("Helvetica", 12)
    if nombre_1:
        can.drawCentredString(firma1_x, linea_y + 5, nombre_1)
    if nombre_2:
        can.drawCentredString(firma2_x, linea_y + 5, nombre_2)
    
    # Etiquetas debajo de las líneas
    can.setFont("Helvetica", 9)
    can.drawCentredString(firma1_x, linea_y - 15, "(Rellenado por)")
    can.drawCentredString(firma2_x, linea_y - 15, "(Verificado por)")

    # Código del formulario - CAMBIO 3: Dos líneas después de "Rellenado por"
    can.setFont("Helvetica-Bold", 10)
    codigo_y = linea_y - 15 - 20  # Dos líneas después de "(Rellenado por)"
    can.drawString(90, codigo_y, "S-24-S  5/21")

    can.save()
    buffer.seek(0)
    return buffer, firma_y

# --- Generar y mostrar PDF ---
if enviado:
    pdf_base, firma_y_position = crear_pdf()
    pdf_final = insertar_firmas(pdf_base, firma1.image_data, firma2.image_data, firma_y_position)
    nombre_archivo = f"{fecha_str} - {tipo}.pdf"

    b64_pdf = base64.b64encode(pdf_final.getvalue()).decode("utf-8")
    pdf_viewer = f'<iframe src="data:application/pdf;base64,{b64_pdf}" width="700" height="500" type="application/pdf"></iframe>'
    st.success("✅ Vista previa del PDF generada:")
    components.html(pdf_viewer, height=510)

    st.download_button("📥 Descargar PDF", data=pdf_final, file_name=nombre_archivo, mime="application/pdf")
