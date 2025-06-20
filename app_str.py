import streamlit as st
from datetime import date
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

# --- Función para dibujar checkbox cuadrado con X ---
def dibujar_checkbox_cuadrado(canvas, x, y, marcado=False, size=12):
    """
    Dibuja un checkbox como cuadrado con X si está marcado
    """
    # Dibujar el cuadrado
    canvas.rect(x, y, size, size, stroke=1, fill=0)
    
    # Si está marcado, dibujar la X
    if marcado:
        canvas.setFont("Helvetica-Bold", size-2)
        # Centrar la X en el cuadrado
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

# --- Crear PDF desde cero ---
def crear_pdf():
    buffer = BytesIO()
    can = canvas.Canvas(buffer, pagesize=landscape(letter))

    # Posiciones base
    x_base_izq = 90
    x_base_der = 700
    y = 550

    # Título centrado (sin sangría)
    can.setFont("Helvetica-Bold", 26)
    can.drawCentredString(396, y, "REGISTRO DE TRANSACCIÓN")
    y -= 40

    # Línea de selección (sin sangría)
    can.setFont("Helvetica-Bold", 18)
    can.drawString(x_base_izq, y, "Seleccione el tipo de transacción:")
    
    # Fecha a la derecha
    fecha_text = f"Fecha: {fecha_str}" if fecha_str else "Fecha: _______________"
    can.drawRightString(x_base_der, y, fecha_text)
    y -= 25

    # APLICAR SANGRÍAS
    sangria = 28.35  # 1cm en puntos
    x_izq = x_base_izq + sangria
    x_der = x_base_der - sangria

    # Checkboxes (sin cambios)
    can.setFont("Helvetica", 18)
    col_izq_x = x_izq + 20
    col_der_x = 396
    checkbox_size = 12
    
    # Fila 1
    dibujar_checkbox_cuadrado(can, x_izq, y-2, tipo == "DONACIÓN", checkbox_size)
    can.drawString(col_izq_x, y, "Donación")
    
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "PAGO", checkbox_size)
    can.drawString(col_der_x + 20, y, "Pago")
    y -= 15
    
    # Fila 2
    dibujar_checkbox_cuadrado(can, x_izq, y-2, tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO", checkbox_size)
    can.drawString(col_izq_x, y, "Depósito en la caja de efectivo")
    
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "ADELANTO DE EFECTIVO", checkbox_size)
    can.drawString(col_der_x + 20, y, "Adelanto de efectivo")
    y -= 30

    # CONFIGURACIÓN PARA LÍNEAS DE VALORES
    # Definir longitud fija para todas las líneas de valores (12 millones = "12,000,000")
    longitud_linea_valores = 80  # Ancho fijo en puntos para líneas de valores
    separacion_conceptos = 42.5  # 1.5cm en puntos (1.5 * 28.35)
    
    # Calcular posición X donde empiezan las líneas de valores (alineadas a la derecha)
    x_inicio_lineas = x_der - longitud_linea_valores

    can.setFont("Helvetica", 18)
    
    # Donaciones (Obra mundial)
    can.drawString(x_izq, y, "Donaciones (Obra mundial)")
    if don_obra > 0:
        can.drawRightString(x_der, y, f"{don_obra:,}")
    else:
        # Dibujar línea de longitud fija
        can.line(x_inicio_lineas, y + 2, x_der, y + 2)
    y -= 15

    # Donaciones (Gastos de la congregación)
    can.drawString(x_izq, y, "Donaciones (Gastos de la congregación)")
    if don_congre > 0:
        can.drawRightString(x_der, y, f"{don_congre:,}")
    else:
        # Dibujar línea de longitud fija
        can.line(x_inicio_lineas, y + 2, x_der, y + 2)
    y -= 15

    # Concepto adicional (si existe)
    if concepto:
        can.drawString(x_izq, y, concepto)
        if valor_concepto > 0:
            can.drawRightString(x_der, y, f"{valor_concepto:,}")
        else:
            # Dibujar línea de longitud fija
            can.line(x_inicio_lineas, y + 2, x_der, y + 2)
        y -= 15

    # Líneas adicionales en blanco con separación de 1.5cm
    lineas_extra = 3 if not concepto else 2
    for i in range(lineas_extra):
        # Calcular posición para el concepto (1.5cm de separación de la línea de valores)
        x_concepto_fin = x_inicio_lineas - separacion_conceptos
        
        # Línea para concepto (desde sangría hasta 1.5cm antes de la línea de valores)
        can.line(x_izq, y + 2, x_concepto_fin, y + 2)
        
        # Línea para valores (longitud fija)
        can.line(x_inicio_lineas, y + 2, x_der, y + 2)
        
        y -= 15

    y -= 10

    # TOTAL
    can.setFont("Helvetica-Bold", 22)
    can.drawRightString(x_der - longitud_linea_valores - 10, y, "TOTAL:")
    if total > 0:
        can.drawRightString(x_der, y, f"{total:,}")
    else:
        # Línea para total (misma longitud fija)
        can.line(x_inicio_lineas, y + 2, x_der, y + 2)
    y -= 60

    # Resto del código permanece igual (firmas, etc.)
    firma1_x = 240
    firma2_x = 550
    firma_y = y - 40
    
    # Líneas para firmas
    linea_width = 120
    linea_y = firma_y - 10
    can.line(firma1_x - linea_width/2, linea_y, firma1_x + linea_width/2, linea_y)
    can.line(firma2_x - linea_width/2, linea_y, firma2_x + linea_width/2, linea_y)
    
    # Nombres sobre las líneas
    can.setFont("Helvetica", 14)
    if nombre_1:
        can.drawCentredString(firma1_x, linea_y + 5, nombre_1)
    if nombre_2:
        can.drawCentredString(firma2_x, linea_y + 5, nombre_2)
    
    # Etiquetas debajo de las líneas
    can.setFont("Helvetica", 9)
    can.drawCentredString(firma1_x, linea_y - 15, "(Rellenado por)")
    can.drawCentredString(firma2_x, linea_y - 15, "(Verificado por)")

    # Código del formulario
    can.setFont("Helvetica-Bold", 10)
    codigo_y = linea_y - 15 - 20
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
