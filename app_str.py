import streamlit as st
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter

# --- Configuración de página
st.set_page_config(page_title="Formulario S-24", layout="centered")

# --- Estilos CSS personalizados ---
custom_css = """
<style>
    body {
        font-family: 'Segoe UI', sans-serif;
    }
    .container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .section-title {
        font-size: 20px;
        font-weight: bold;
        color: #1f3a93;
        margin-top: 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }
    .section-title::before {
        content: "🔹";
        margin-right: 10px;
    }
    .resumen-box {
        background-color: #e8f5e9;
        padding: 15px;
        border-left: 5px solid #4caf50;
        border-radius: 10px;
        margin-top: 10px;
        margin-bottom: 20px;
        font-size: 16px;
    }
    .boton-principal {
        background-color: #1f3a93;
        color: white;
        font-size: 18px;
        padding: 10px 20px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        width: 100%;
    }
    .boton-principal:hover {
        background-color: #2980b9;
    }
    hr {
        border: 1px solid #ddd;
        margin-top: 20px;
        margin-bottom: 20px;
    }
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# --- Configuración de página ---

st.title("📄 Generador de PDF - Registro de Transacción S-24")

# --- Fecha con calendario ---
meses_espanol = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]



# --- Función para formatear números con separadores de miles ---
def formatear_numero_elegante(key, label, help_text="Monto en pesos colombianos"):
    col_input, col_formato = st.columns([2, 1])
    with col_input:
        valor_raw = st.text_input(label, key=key, placeholder="Ej: 50000", help=help_text)
    if valor_raw and valor_raw.strip():
        try:
            solo_numeros = ''.join(filter(str.isdigit, valor_raw))
            if solo_numeros:
                numero = int(solo_numeros)
                with col_formato:
                    if numero >= 1000000:
                        st.success(f"💰 **${numero:,}**")
                    elif numero >= 100000:
                        st.info(f"💰 **${numero:,}**")
                    elif numero > 0:
                        st.write(f"💰 **${numero:,}**")
                return numero
            else:
                return 0
        except ValueError:
            with col_formato:
                st.error("❌ Solo números")
            return 0
    else:
        return 0

# --- Formulario de datos ---
with st.form("formulario"):
    st.markdown('<div class="container">', unsafe_allow_html=True)

    st.markdown('<div class="section-title">📅 Fecha de transacción</div>', unsafe_allow_html=True)
    fecha_seleccionada = st.date_input(
        "Selecciona la fecha de la transacción:",
        value=date.today(),
        min_value=date(2020, 1, 1),
        max_value=date(2030, 12, 31),
        format="DD/MM/YYYY",
        key="fecha_selector",
        help="Haz clic en el campo para abrir el calendario"
    )
    fecha_str = f"{fecha_seleccionada.day:02d} {meses_espanol[fecha_seleccionada.month - 1]} {fecha_seleccionada.year}"
    st.success(f"✅ **Fecha seleccionada:** {fecha_str}")
    st.markdown('<hr>', unsafe_allow_html=True)


# tipo de transacción

    #st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📝 Tipo de transacción</div>', unsafe_allow_html=True)
    tipo = st.radio("Seleccione el tipo de transacción", [
        "DONACIÓN", "PAGO", "DEPÓSITO EN LA CAJA DE EFECTIVO", "ADELANTO DE EFECTIVO", "OTRO"
    ])

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">💰 Donaciones</div>', unsafe_allow_html=True)
    don_obra = formatear_numero_elegante("don_obra_key", "OBRA MUNDIAL (OM)")
    don_congre = formatear_numero_elegante("don_congre_key", "GASTOS DE LA CONGREGACIÓN (GC)")

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📌 Otros Conceptos</div>', unsafe_allow_html=True)
    conc1_nombre = st.text_input("Nombre del Concepto 1", value=".")
    conc1_valor = formatear_numero_elegante("conc1_valor_key", "Valor del Concepto 1")
    conc2_nombre = st.text_input("Nombre del Concepto 2", value=".")
    conc2_valor = formatear_numero_elegante("conc2_valor_key", "Valor del Concepto 2")

    total = don_obra + don_congre + conc1_valor + conc2_valor
    st.markdown(f"**TOTAL: ${total:,} COP**")

    st.markdown('<hr>', unsafe_allow_html=True)
    st.markdown('<div class="section-title">✍️ Firmas</div>', unsafe_allow_html=True)
    nombre_1 = st.text_input("Nombre de quien rellena")
    nombre_2 = st.text_input("Nombre de quien verifica")

    st.markdown("**Firma de quien rellena ✍️ :**")
    firma1 = st_canvas(
        key="firma1",
        height=300,
        width=900,
        drawing_mode="freedraw",
        stroke_width=2,
        stroke_color="black",
        background_color="white"
    )
    st.markdown("**Firma de quien verifica ✍️ :**")
    firma2 = st_canvas(
        key="firma2",
        height=300,
        width=900,
        drawing_mode="freedraw",
        stroke_width=2,
        stroke_color="black",
        background_color="white"
    )

    enviado = st.form_submit_button("📤 Generar PDF", help="Haz clic para generar el PDF con toda la información")
    st.markdown('</div>', unsafe_allow_html=True)



# --- Función para dibujar checkbox cuadrado con X ---
def dibujar_checkbox_cuadrado(canvas, x, y, marcado=False, size=18):
    canvas.rect(x, y, size, size, stroke=1, fill=0)
    if marcado:
        canvas.setFont("Helvetica-Bold", size-2)
        x_center = x + size/2 - 3
        y_center = y + 2
        canvas.drawString(x_center, y_center, "X")

# --- Funciones auxiliares para firmas ---
def procesar_firma(firma_data):
    try:
        if firma_data is not None:
            firma_img = Image.fromarray(firma_data)
            img_stream = BytesIO()
            firma_img.save(img_stream, format="PNG")
            img_stream.seek(0)
            return img_stream
        return None
    except Exception as e:
        print(f"Error procesando firma: {e}")
        return None

def insertar_firmas(pdf_bytes, firma1_data, firma2_data, firma_y_pos):
    try:
        firma_buffer = BytesIO()
        can = canvas.Canvas(firma_buffer, pagesize=landscape(letter))
        for idx, firma_data in enumerate([firma1_data, firma2_data]):
            if firma_data is not None:
                firma_stream = procesar_firma(firma_data)
                if firma_stream:
                    x = 150 if idx == 0 else 470
                    y = firma_y_pos + 5
                    can.drawImage(ImageReader(firma_stream), x, y, width=226, height=80, preserveAspectRatio=True)
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
    except Exception as e:
        print(f"Error insertando firmas: {e}")
        return BytesIO(pdf_bytes.getvalue())

# --- Crear PDF desde cero ---
def crear_pdf(conc1_nombre, conc1_valor, conc2_nombre, conc2_valor):
    buffer = BytesIO()
    can = canvas.Canvas(buffer, pagesize=landscape(letter))
    espaciado_lineas = 29.5
    x_base_izq = 90
    x_base_der = 700
    y = 550

    can.setFont("Helvetica-Bold", 26)
    can.drawCentredString(396, y, "REGISTRO DE TRANSACCIÓN")
    y -= 50

    can.setFont("Helvetica-Bold", 18)
    can.drawString(x_base_izq, y, "Seleccione el tipo de transacción:")
    etiqueta = "Fecha:"
    valor = fecha_str if fecha_str else "_______________"
    ancho_etiqueta = can.stringWidth(etiqueta + " ", "Helvetica-Bold", 18)
    can.setFont("Helvetica", 18)
    ancho_valor = can.stringWidth(valor, "Helvetica", 18)
    x_final = x_base_der
    can.setFont("Helvetica", 18)
    can.drawString(x_final - ancho_valor, y, valor)
    can.setFont("Helvetica-Bold", 18)
    can.drawString(x_final - ancho_valor - ancho_etiqueta, y, etiqueta)
    y -= espaciado_lineas

    sangria = 28.35
    x_izq = x_base_izq + sangria
    x_der = x_base_der - sangria
    longitud_linea_valores = 80
    separacion_conceptos = 42.5
    x_inicio_lineas = x_der - longitud_linea_valores
    checkbox_size = 14
    col_izq_x = x_izq + 20
    col_der_x = 396

    dibujar_checkbox_cuadrado(can, x_izq, y-2, tipo == "DONACIÓN", checkbox_size)
    can.setFont("Helvetica", 18)
    can.drawString(col_izq_x, y, "Donación")
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "PAGO", checkbox_size)
    can.drawString(col_der_x + 20, y, "Pago")
    y -= espaciado_lineas

    dibujar_checkbox_cuadrado(can, x_izq, y-2, tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO", checkbox_size)
    can.drawString(col_izq_x, y, "Depósito en la caja de efectivo")
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "ADELANTO DE EFECTIVO", checkbox_size)
    can.drawString(col_der_x + 20, y, "Adelanto de efectivo")
    y -= 45

    can.setFont("Helvetica", 18)
    can.drawString(x_izq, y, "Donaciones (Obra mundial)")
    can.drawRightString(x_der, y, f"{don_obra:,.2f}")
    y -= espaciado_lineas

    can.drawString(x_izq, y, "Donaciones (Gastos de la congregación)")
    can.drawRightString(x_der, y, f"{don_congre:,.2f}")
    y -= espaciado_lineas

    # Contar cuántos conceptos se van a mostrar
    conceptos_mostrados = 0
    
    if conc1_nombre and conc1_valor > 0:
        can.drawString(x_izq, y, conc1_nombre)
        can.drawRightString(x_der, y, f"{conc1_valor:,.2f}")
        y -= espaciado_lineas
        conceptos_mostrados += 1

    if conc2_nombre and conc2_valor > 0:
        can.drawString(x_izq, y, conc2_nombre)
        can.drawRightString(x_der, y, f"{conc2_valor:,.2f}")
        y -= espaciado_lineas
        conceptos_mostrados += 1

    # Dibujar líneas vacías para completar un total de 3 líneas
    lineas_vacias_necesarias = 3 - conceptos_mostrados
    
    for _ in range(lineas_vacias_necesarias):
        x_concepto_fin = x_inicio_lineas - separacion_conceptos
        can.line(x_izq, y + 2, x_concepto_fin, y + 2)
        can.line(x_inicio_lineas, y + 2, x_der, y + 2)
        y -= espaciado_lineas

    y -= 15
    can.setFont("Helvetica-Bold", 22)
    x_concepto_fin = x_inicio_lineas - separacion_conceptos
    can.drawRightString(x_concepto_fin, y, "TOTAL:")
    can.setFont("Helvetica-Bold", 18)
    can.drawRightString(x_der, y, f"{total:,.2f}")
    y -= 90

    firma1_x = 240
    firma2_x = 550
    firma_y = y - 40
    linea_width = 206
    linea_y = firma_y - 10
    can.line(firma1_x - linea_width/2, linea_y, firma1_x + linea_width/2, linea_y)
    can.line(firma2_x - linea_width/2, linea_y, firma2_x + linea_width/2, linea_y)

    can.setFont("Helvetica", 14)
    if nombre_1:
        can.drawCentredString(firma1_x, linea_y + 5, nombre_1)
    if nombre_2:
        can.drawCentredString(firma2_x, linea_y + 5, nombre_2)

    can.setFont("Helvetica", 9)
    can.drawCentredString(firma1_x, linea_y - 15, "(Rellenado por)")
    can.drawCentredString(firma2_x, linea_y - 15, "(Verificado por)")

    can.setFont("Helvetica-Bold", 10)
    codigo_y = linea_y - 15 - 20
    can.drawString(90, codigo_y, "S-24-S  5/21")
    can.save()
    buffer.seek(0)
    return buffer, firma_y









# Mostrar resumen después de enviar
if enviado:
    try:
        if firma1.image_data is None or firma2.image_data is None:
            st.error("❌ Ambas firmas son obligatorias para generar el PDF.")
        else:
            pdf_base, firma_y_position = crear_pdf(conc1_nombre, conc1_valor, conc2_nombre, conc2_valor)
            pdf_final = insertar_firmas(pdf_base, firma1.image_data, firma2.image_data, firma_y_position)
            pdf_bytes = pdf_final.getvalue()
            if pdf_bytes:
                nombre_archivo = f"{fecha_str} - {tipo}.pdf"

                # --- Mostrar resumen con estilo ---
                st.markdown('<div class="resumen-box">', unsafe_allow_html=True)
                st.subheader("💡 Resumen de totales")
                col_resumen1, col_resumen2 = st.columns(2)

                with col_resumen1:
                    st.write("**Donaciones:**")
                    st.write(f"• Obra mundial 💰: ${don_obra:,}")
                    st.write(f"• Gastos congregación 💰: ${don_congre:,}")

                with col_resumen2:
                    st.write("**Conceptos adicionales :**")
                    if conc1_nombre and conc1_valor > 0:
                        st.write(f"• {conc1_nombre[:25] + '...' if len(conc1_nombre) > 25 else conc1_nombre} 💰: ${conc1_valor:,}")
                    if conc2_nombre and conc2_valor > 0:
                        st.write(f"• {conc2_nombre[:25] + '...' if len(conc2_nombre) > 25 else conc2_nombre} 💰: ${conc2_valor:,}")

                st.markdown(f"### **TOTAL GENERAL: ${total:,} COP** 🎯")
                st.markdown('</div>', unsafe_allow_html=True)

                # Nota informativa para móviles
                st.markdown("""
                <div style="border:1px solid #ccc; padding:10px; border-radius:10px; background:#f9f9f9">
                ⚠️ <b>Antes de generar el pdf  </b><br>
                Asegurarse de que la información del recibo esté correcta.<br><br>
                📱 <b>¿Usas un celular?</b><br>
                Es posible que el archivo descargado tenga un nombre genérico como <i>file.pdf</i>. Puedes renombrarlo después.<br><br>
                Para <b>compartir</b> el archivo (por WhatsApp, Telegram, Google Drive, etc.), abre el PDF desde tu dispositivo y usa el botón de <i>Compartir</i>.
                </div>
                """, unsafe_allow_html=True)

                # Botón de descarga
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
