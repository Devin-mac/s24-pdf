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
            # Convertir firma a azul y más gruesa
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
            can.drawImage(ImageReader(img_stream), x, y, width=186, height=60)

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

    # ESPACIADO AUMENTADO EN 50%: de 21 a 31.5 puntos
    espaciado_lineas = 29.5

    # Posiciones base
    x_base_izq = 90
    x_base_der = 700
    y = 550

    # Título centrado (sin sangría)
    can.setFont("Helvetica-Bold", 26)
    can.drawCentredString(396, y, "REGISTRO DE TRANSACCIÓN")
    y -= 50  # Aumentado de 40 a 50 (25% más)

    # Línea de selección (sin sangría)
    can.setFont("Helvetica-Bold", 18)
    can.drawString(x_base_izq, y, "Seleccione el tipo de transacción:")
    
    # Fecha a la derecha
    # Texto de la fecha separado: "Fecha:" en negrita, valor en regular
    etiqueta = "Fecha:"
    valor = fecha_str if fecha_str else "_______________"
    
    # Medimos el ancho de los textos
    can.setFont("Helvetica-Bold", 18)
    ancho_etiqueta = can.stringWidth(etiqueta + " ", "Helvetica-Bold", 18)
    
    can.setFont("Helvetica", 18)
    ancho_valor = can.stringWidth(valor, "Helvetica", 18)
    
    # Posición final derecha
    x_final = x_base_der
    
    # Dibujo las partes por separado, alineadas a la derecha
    # Primero el valor sin negrita
    can.setFont("Helvetica", 18)
    can.drawString(x_final - ancho_valor, y, valor)
    
    # Luego "Fecha:" en negrita, a la izquierda del valor
    can.setFont("Helvetica-Bold", 18)
    can.drawString(x_final - ancho_valor - ancho_etiqueta, y, etiqueta)

    # 🔽 Evitar superposición con checkboxes
    y -= espaciado_lineas

    # APLICAR SANGRÍAS A PARTIR DE AQUÍ
    sangria = 28.35  # 1cm en puntos
    x_izq = x_base_izq + sangria
    x_der = x_base_der - sangria

    # CONFIGURACIÓN PARA LÍNEAS DE VALORES
    longitud_linea_valores = 80  # Ancho fijo para cifras como 12,000,000
    separacion_conceptos = 42.5  # 1.5cm en puntos
    x_inicio_lineas = x_der - longitud_linea_valores

    # Checkboxes con sangrías aplicadas
    #can.setFont("Helvetica", 22)
    col_izq_x = x_izq + 20
    col_der_x = 396
    checkbox_size = 12
    
    # Fila 1 - CON SANGRÍAS
    dibujar_checkbox_cuadrado(can, x_izq, y-2, tipo == "DONACIÓN", checkbox_size)
    can.setFont("Helvetica", 18)
    can.drawString(col_izq_x, y, "Donación")
    
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "PAGO", checkbox_size)
    can.setFont("Helvetica", 18)
    can.drawString(col_der_x + 20, y, "Pago")
    y -= espaciado_lineas  # Cambiado de 21 a espaciado_lineas
    
    # Fila 2 - CON SANGRÍAS
    dibujar_checkbox_cuadrado(can, x_izq, y-2, tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO", checkbox_size)
    can.setFont("Helvetica", 18)
    can.drawString(col_izq_x, y, "Depósito en la caja de efectivo")
    
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "ADELANTO DE EFECTIVO", checkbox_size)
    can.setFont("Helvetica", 18)
    can.drawString(col_der_x + 20, y, "Adelanto de efectivo")
    y -= 45  # Aumentado de 30 a 45 (50% más)

    # TODAS LAS SECCIONES SIGUIENTES CON SANGRÍAS CONSISTENTES
    can.setFont("Helvetica", 18)
    
    # Donaciones (Obra mundial) - CON SANGRÍA
    can.drawString(x_izq, y, "Donaciones (Obra mundial)")
    can.drawRightString(x_der, y, f"{don_obra:,.2f}")
    y -= espaciado_lineas  # Cambiado de 21 a espaciado_lineas

    # Donaciones (Gastos de la congregación) - CON SANGRÍA
    can.drawString(x_izq, y, "Donaciones (Gastos de la congregación)")
    can.drawRightString(x_der, y, f"{don_congre:,.2f}")
    y -= espaciado_lineas  # Cambiado de 21 a espaciado_lineas

    # Concepto adicional - CON SANGRÍA
    if concepto:
        can.drawString(x_izq, y, concepto)
        if valor_concepto > 0:
            can.drawRightString(x_der, y, f"{valor_concepto:,}")
        else:
            can.line(x_inicio_lineas, y + 2, x_der, y + 2)
        y -= espaciado_lineas  # Cambiado de 21 a espaciado_lineas

    # Líneas adicionales en blanco - CON SANGRÍAS
    lineas_extra = 3 if not concepto else 2
    for i in range(lineas_extra):
        # Calcular posición para el concepto (1.5cm de separación de la línea de valores)
        x_concepto_fin = x_inicio_lineas - separacion_conceptos
        
        # Línea para concepto (desde sangría hasta 1.5cm antes de la línea de valores)
        can.line(x_izq, y + 2, x_concepto_fin, y + 2)
        
        # Línea para valores (longitud fija)
        can.line(x_inicio_lineas, y + 2, x_der, y + 2)
        
        y -= espaciado_lineas  # Cambiado de 21 a espaciado_lineas

    y -= 15  # Aumentado de 10 a 15 (50% más)

    # TOTAL - Alineado con el final de las líneas de conceptos
    can.setFont("Helvetica-Bold", 22)
    
    # Calcular posición donde terminan las líneas de conceptos
    x_concepto_fin = x_inicio_lineas - separacion_conceptos
    
    # Posicionar "TOTAL:" para que los ":" terminen justo donde termina la línea de conceptos
    can.drawRightString(x_concepto_fin, y, "TOTAL:")
    
    can.drawRightString(x_der, y, f"{total:,.2f}")
    y -= 90  # Aumentado de 60 a 90 (50% más)

    # Sección de firmas (centradas, sin sangría)
    firma1_x = 240
    firma2_x = 550
    firma_y = y - 40
    
    # Líneas para firmas
    linea_width = 186
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
    try:
        # Crear PDF base
        pdf_base, firma_y_position = crear_pdf()

        # Insertar firmas si hay datos válidos
        if firma1.image_data is not None and firma2.image_data is not None:
            pdf_final = insertar_firmas(pdf_base, firma1.image_data, firma2.image_data, firma_y_position)
        else:
            st.warning("⚠️ Al menos una firma está vacía. El PDF se generará sin firmas.")
            pdf_final = pdf_base

        # Verificar tamaño del PDF generado
        pdf_bytes = pdf_final.getvalue()
        st.write("Tamaño PDF final:", len(pdf_bytes))

        if pdf_bytes:
            # Codificar en base64 para vista previa
            try:
                b64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                pdf_viewer = f'''
                    <iframe 
                        src="data:application/pdf;base64,{b64_pdf}" 
                        width="100%" 
                        height="500" 
                        type="application/pdf">
                    </iframe>
                '''
                st.success("✅ Vista previa del PDF generada:")
                components.html(pdf_viewer, height=510, scrolling=True, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error al generar la vista previa en base64: {e}")
        else:
            st.error("❌ El PDF generado está vacío. Verifica los datos ingresados.")

        # Botón de descarga
        nombre_archivo = f"{fecha_str} - {tipo}.pdf"
        st.download_button("📥 Descargar PDF", data=pdf_bytes, file_name=nombre_archivo, mime="application/pdf")

    except Exception as e:
        st.error(f"❌ Ocurrió un error al generar el PDF: {e}")

