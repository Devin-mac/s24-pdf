import streamlit as st
from datetime import date, datetime
import pytz
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfbase.pdfmetrics import stringWidth
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from reportlab.lib.utils import ImageReader
from PyPDF2 import PdfReader, PdfWriter
import pikepdf
import base64
import streamlit.components.v1 as components

# ─── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(page_title="Formulario S-24", layout="centered")

# ─── CSS: adaptativo a modo claro y oscuro ─────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* ── Tokens de color adaptativos ── */
:root {
    --text-main:    #0f172a;
    --text-label:   #1e293b;
    --bg-card:      #f8faff;
    --border:       #94a3b8;
    --border-focus: #2563eb;
    --bg-input:     #ffffff;
    --shadow-card:  0 2px 12px rgba(0,0,0,0.07);
}
@media (prefers-color-scheme: dark) {
    :root {
        --text-main:    #f1f5f9;
        --text-label:   #e2e8f0;
        --bg-card:      #1e293b;
        --border:       #475569;
        --border-focus: #60a5fa;
        --bg-input:     #0f172a;
        --shadow-card:  0 2px 12px rgba(0,0,0,0.35);
    }
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Encabezado ── */
.main-header {
    background: linear-gradient(135deg, #1a3a6e 0%, #2563eb 100%);
    color: #ffffff !important;
    padding: 2rem 2rem 1.5rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(37,99,235,0.22);
}
.main-header h1 { font-size: 1.7rem; font-weight: 700; margin: 0 0 0.3rem 0; color: #ffffff !important; }
.main-header p  { font-size: 0.95rem; opacity: 0.85; margin: 0; color: #ffffff !important; }

/* ── Tarjetas de sección ── */
.section-card {
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: 14px;
    padding: 1.5rem 1.5rem 1.2rem 1.5rem;
    margin-bottom: 1.6rem;
    box-shadow: var(--shadow-card);
}
.section-title {
    font-size: 1rem;
    font-weight: 700;
    color: #2563eb;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 1rem;
}

/* ── Labels: legibles en ambos modos ── */
label,
.stTextInput > label,
.stNumberInput > label,
.stSelectbox > label,
.stRadio > label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p {
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    color: var(--text-label) !important;
    margin-bottom: 5px !important;
    line-height: 1.4 !important;
}

/* ── Inputs de texto y numero: borde completo en todos los lados ── */
input[type="text"],
input[type="number"],
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    font-size: 1.2rem !important;
    font-weight: 500 !important;
    color: var(--text-main) !important;
    background: var(--bg-input) !important;
    padding: 0.85rem 1.1rem !important;
    height: 3.4rem !important;
    border-radius: 10px !important;
    border: 2px solid var(--border) !important;
    border-bottom: 2px solid var(--border) !important;
    box-shadow: none !important;
    -webkit-appearance: none !important;
    appearance: none !important;
}
/* Fondo azul claro uniforme al escribir en TODOS los inputs */
input[type="text"]:focus,
input[type="number"]:focus,
input[type="text"]:not(:placeholder-shown),
input[type="number"]:not(:placeholder-shown),
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextInput input:not(:placeholder-shown),
.stNumberInput input:not(:placeholder-shown) {
    border-color: var(--border-focus) !important;
    background: #eff6ff !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
    outline: none !important;
}
@media (prefers-color-scheme: dark) {
    input[type="text"]:focus,
    input[type="number"]:focus,
    input[type="text"]:not(:placeholder-shown),
    input[type="number"]:not(:placeholder-shown) {
        background: #1e3a5f !important;
    }
}
/* Ocultar hint "press Enter to submit" de Streamlit */
[data-testid="InputInstructions"],
.stTextInput small,
.stNumberInput small {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* ── Selectbox ── */
.stSelectbox > div > div {
    font-size: 1.15rem !important;
    font-weight: 500 !important;
    color: var(--text-main) !important;
    background: var(--bg-input) !important;
    min-height: 3.2rem !important;
    border-radius: 10px !important;
    border: 2px solid var(--border) !important;
}


/* ── Radio como botones ── */
.stRadio > div { display: flex; flex-direction: column; gap: 0.55rem; }
.stRadio label {
    background: var(--bg-input) !important;
    border: 2px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 0.72rem 1.2rem !important;
    font-size: 1.08rem !important;
    font-weight: 600 !important;
    color: var(--text-label) !important;
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
}
.stRadio label:hover {
    border-color: var(--border-focus) !important;
    background: #eff6ff !important;
}

/* ── Total destacado ── */
.total-box {
    background: linear-gradient(90deg, #1a3a6e 0%, #2563eb 100%);
    color: #ffffff !important;
    border-radius: 12px;
    padding: 1.1rem 1.5rem;
    font-size: 1.4rem;
    font-weight: 700;
    text-align: right;
    margin: 1.1rem 0 0.5rem 0;
    box-shadow: 0 4px 16px rgba(37,99,235,0.22);
}

/* ── Tarjeta resumen ── */
.summary-card {
    background: var(--bg-card);
    border: 2px solid #0ea5e9;
    border-radius: 16px;
    padding: 1.4rem 1.8rem;
    margin: 1.4rem 0;
    box-shadow: var(--shadow-card);
}
.summary-card h3 {
    color: #0369a1;
    margin-top: 0;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
}
.summary-row {
    display: flex;
    justify-content: space-between;
    padding: 0.42rem 0;
    border-bottom: 1px solid var(--border);
    font-size: 1.05rem;
}
.summary-row:last-child { border-bottom: none; }
.summary-label { color: var(--text-label); font-weight: 500; }
.summary-value { color: var(--text-main); font-weight: 700; }

/* ── Separador entre firmas ── */
.firma-spacer { margin-top: 2.2rem; margin-bottom: 0.4rem; }

/* ── Botón principal ── */
.stButton > button {
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    padding: 0.8rem 2rem !important;
    border-radius: 12px !important;
    background: linear-gradient(90deg, #1a3a6e, #2563eb) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.25) !important;
    width: 100%;
    transition: transform 0.15s, box-shadow 0.15s;
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(37,99,235,0.35) !important;
}

/* Canvas firmas */
canvas { border-radius: 10px; border: 2px solid var(--border) !important; }

footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── Teclado numérico en móvil ─────────────────────────────────────────────────
components.html("""
<script>
function fixInputs() {
    document.querySelectorAll('input[type=number], input[type=text]').forEach(el => {
        if (el.getAttribute('inputmode') !== 'text') {
            el.setAttribute('inputmode', 'numeric');
            el.setAttribute('pattern', '[0-9]*');
        }
    });
}
setTimeout(fixInputs, 800);
setTimeout(fixInputs, 2500);
</script>
""", height=0)

# ─── Zona horaria Colombia ─────────────────────────────────────────────────────
col_tz = pytz.timezone('America/Bogota')
fecha_actual = datetime.now(col_tz).date()

meses_espanol = [
    "ENERO","FEBRERO","MARZO","ABRIL","MAYO","JUNIO",
    "JULIO","AGOSTO","SEPTIEMBRE","OCTUBRE","NOVIEMBRE","DICIEMBRE"
]

# ─── Encabezado ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📄 Registro de Transacción S-24</h1>
    <p>Generador de formulario oficial · Congregación</p>
</div>
""", unsafe_allow_html=True)

# ─── Helper: campo numérico con vista previa formateada ───────────────────────
def formatear_numero_elegante(key, label, help_text="Monto en pesos colombianos"):
    col_input, col_fmt = st.columns([2, 1])
    with col_input:
        valor_raw = st.text_input(label, key=key, placeholder="Ej: 50000", help=help_text)
    if valor_raw and valor_raw.strip():
        try:
            solo = ''.join(filter(str.isdigit, valor_raw))
            if solo:
                n = int(solo)
                with col_fmt:
                    if n >= 1_000_000:
                        st.success(f"💰 **${n:,}**")
                    elif n >= 100_000:
                        st.info(f"💰 **${n:,}**")
                    elif n > 0:
                        st.write(f"💰 **${n:,}**")
                return n
            return 0
        except ValueError:
            with col_fmt:
                st.error("❌ Solo números")
            return 0
    return 0

# ─── FORMULARIO (sin st.form para que el resumen sea en vivo) ─────────────────

# — Fecha —
st.markdown('<div class="section-card"><div class="section-title">📅 Fecha de transacción</div>', unsafe_allow_html=True)
fecha_seleccionada = st.date_input(
    "Selecciona la fecha:",
    value=fecha_actual,
    min_value=date(2020, 1, 1),
    max_value=date(2030, 12, 31),
    format="DD/MM/YYYY",
    key="fecha_selector"
)
fecha_str = f"{fecha_seleccionada.day:02d} {meses_espanol[fecha_seleccionada.month - 1]} {fecha_seleccionada.year}"
st.success(f"✅ **Fecha:** {fecha_str}")
st.markdown('</div>', unsafe_allow_html=True)

# — Tipo de transacción —
st.markdown('<div class="section-card"><div class="section-title">🔖 Tipo de transacción</div>', unsafe_allow_html=True)
tipo = st.radio("", [
    "DONACIÓN", "PAGO", "DEPÓSITO EN LA CAJA DE EFECTIVO", "ADELANTO DE EFECTIVO", "OTRO"
], label_visibility="collapsed", key="tipo_trans")
st.markdown('</div>', unsafe_allow_html=True)

# — Donaciones —
st.markdown('<div class="section-card"><div class="section-title">💰 Donaciones</div>', unsafe_allow_html=True)
don_obra   = formatear_numero_elegante("don_obra_key",   "Obra Mundial (OM)")
don_congre = formatear_numero_elegante("don_congre_key", "Gastos de la Congregación (GC)")
st.markdown('</div>', unsafe_allow_html=True)

# — Otros conceptos —
st.markdown('<div class="section-card"><div class="section-title">📌 Otros conceptos</div>', unsafe_allow_html=True)
conc1_nombre = st.text_input("Nombre del Concepto 1", value=".", key="conc1_nom")
conc1_valor  = formatear_numero_elegante("conc1_valor_key", "Valor del Concepto 1")
conc2_nombre = st.text_input("Nombre del Concepto 2", value=".", key="conc2_nom")
conc2_valor  = formatear_numero_elegante("conc2_valor_key", "Valor del Concepto 2")

total = don_obra + don_congre + conc1_valor + conc2_valor
st.markdown(f'<div class="total-box">TOTAL: ${total:,} COP</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# — Personas y firmas —
st.markdown('<div class="section-card"><div class="section-title">👤 Personas responsables</div>', unsafe_allow_html=True)
col_n1, col_n2 = st.columns(2)
with col_n1:
    nombre_1 = st.text_input("Quien rellena", placeholder="Nombre completo", key="nombre_rellena")
with col_n2:
    nombre_2 = st.text_input("Quien verifica", placeholder="Nombre completo", key="nombre_verifica")
# Forzar rerender cuando nombre_2 cambia sin necesidad de salir del campo
st.caption(f" ")  # espacio invisible que obliga rerender continuo

st.markdown("**✍️ Firma — quien rellena:**")
firma1 = st_canvas(
    key="firma1", height=120, width=400,
    drawing_mode="freedraw", stroke_width=2,
    stroke_color="black", background_color="white"
)

st.markdown('<div class="firma-spacer"></div>', unsafe_allow_html=True)
st.markdown("---")
st.markdown("**✍️ Firma — quien verifica:**")
firma2 = st_canvas(
    key="firma2", height=120, width=400,
    drawing_mode="freedraw", stroke_width=2,
    stroke_color="black", background_color="white"
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Resumen en vivo ANTES del botón ───────────────────────────────────────────
st.markdown("---")
_filas_prev = [
    ("Fecha",        fecha_str),
    ("Tipo",         tipo),
    ("Obra Mundial", f"${don_obra:,} COP"),
    ("Congregación", f"${don_congre:,} COP"),
]
if conc1_nombre and conc1_nombre != "." and conc1_valor > 0:
    _filas_prev.append((conc1_nombre[:30], f"${conc1_valor:,} COP"))
if conc2_nombre and conc2_nombre != "." and conc2_valor > 0:
    _filas_prev.append((conc2_nombre[:30], f"${conc2_valor:,} COP"))
_filas_prev.append(("TOTAL",         f"${total:,} COP"))
_filas_prev.append(("Rellenado por", nombre_1 or "—"))
_filas_prev.append(("Verificado por",nombre_2 or "—"))

_html_prev = '<div class="summary-card"><h3>📋 Resumen — revisa antes de generar</h3>'
for _lbl, _val in _filas_prev:
    _bold = " style='font-size:1.15rem;color:#0c4a6e;'" if _lbl == "TOTAL" else ""
    _html_prev += (
        f'<div class="summary-row">'
        f'<span class="summary-label">{_lbl}</span>'
        f'<span class="summary-value"{_bold}>{_val}</span>'
        f'</div>'
    )
_html_prev += '</div>'
st.markdown(_html_prev, unsafe_allow_html=True)

enviado = st.button("📤 Confirmar y generar PDF", use_container_width=True)

# ─── Funciones PDF (exactamente como en el archivo funcional) ──────────────────
def dibujar_checkbox_cuadrado(c, x, y, marcado=False, size=18):
    c.rect(x, y, size, size, stroke=1, fill=0)
    if marcado:
        c.setFont("Helvetica-Bold", size - 2)
        c.drawString(x + size/2 - 3, y + 2, "X")

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
        base_pdf  = PdfReader(pdf_bytes)
        firma_pdf = PdfReader(firma_buffer)
        writer    = PdfWriter()
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
                meta["dc:title"]   = titulo_limpio
                meta["dc:subject"] = titulo_limpio
                meta["dc:creator"] = ["Congregación S-24"]
            # Tambien escribir en DocInfo clasico para lectores antiguos
            pdf.docinfo["/Title"]   = titulo_limpio
            pdf.docinfo["/Subject"] = titulo_limpio
            pdf.docinfo["/Author"]  = "Congregación S-24"
            pdf.docinfo["/Creator"] = "Formulario S-24"
            pdf.save(merged_out)
        merged_out.seek(0)
        return merged_out
    except Exception as e:
        print(f"Error insertando firmas: {e}")
        return BytesIO(pdf_bytes.getvalue())

def crear_pdf(conc1_nombre, conc1_valor, conc2_nombre, conc2_valor, titulo_metadatos):
    buffer = BytesIO()
    can = canvas.Canvas(buffer, pagesize=landscape(letter))
    can.setTitle(titulo_metadatos)
    can.setAuthor("Congregacion S-24")
    can.setSubject(titulo_metadatos)

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
    valor_fecha = fecha_str if fecha_str else "_______________"
    ancho_et = can.stringWidth(etiqueta + " ", "Helvetica-Bold", 18)
    can.setFont("Helvetica", 18)
    ancho_val = can.stringWidth(valor_fecha, "Helvetica", 18)
    can.drawString(x_base_der - ancho_val, y, valor_fecha)
    can.setFont("Helvetica-Bold", 18)
    can.drawString(x_base_der - ancho_val - ancho_et, y, etiqueta)
    y -= espaciado_lineas

    sangria = 28.35
    x_izq = x_base_izq + sangria
    x_der = x_base_der - sangria
    longitud_linea_valores = 80
    separacion_conceptos   = 42.5
    x_inicio_lineas        = x_der - longitud_linea_valores
    checkbox_size = 14
    col_izq_x = x_izq + 20
    col_der_x = 396

    dibujar_checkbox_cuadrado(can, x_izq,     y-2, tipo == "DONACIÓN",                       checkbox_size)
    can.setFont("Helvetica", 18)
    can.drawString(col_izq_x, y, "Donación")
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "PAGO",                           checkbox_size)
    can.drawString(col_der_x + 20, y, "Pago")
    y -= espaciado_lineas

    dibujar_checkbox_cuadrado(can, x_izq,     y-2, tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO",checkbox_size)
    can.drawString(col_izq_x, y, "Depósito en la caja de efectivo")
    dibujar_checkbox_cuadrado(can, col_der_x, y-2, tipo == "ADELANTO DE EFECTIVO",           checkbox_size)
    can.drawString(col_der_x + 20, y, "Adelanto de efectivo")
    y -= 45

    can.setFont("Helvetica", 18)
    can.drawString(x_izq, y, "Donaciones (Obra mundial)")
    can.drawRightString(x_der, y, f"{don_obra:,.2f}")
    y -= espaciado_lineas

    can.drawString(x_izq, y, "Donaciones (Gastos de la congregación)")
    can.drawRightString(x_der, y, f"{don_congre:,.2f}")
    y -= espaciado_lineas

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

    for _ in range(3 - conceptos_mostrados):
        x_concepto_fin = x_inicio_lineas - separacion_conceptos
        can.line(x_izq, y + 2, x_concepto_fin, y + 2)
        can.line(x_inicio_lineas, y + 2, x_der,  y + 2)
        y -= espaciado_lineas

    y -= 15
    can.setFont("Helvetica-Bold", 22)
    can.drawRightString(x_inicio_lineas - separacion_conceptos, y, "TOTAL:")
    can.setFont("Helvetica-Bold", 18)
    can.drawRightString(x_der, y, f"{total:,.2f}")
    y -= 90

    firma1_x = 240
    firma2_x = 550
    firma_y  = y - 40
    linea_w  = 206
    linea_y  = firma_y - 10

    can.line(firma1_x - linea_w/2, linea_y, firma1_x + linea_w/2, linea_y)
    can.line(firma2_x - linea_w/2, linea_y, firma2_x + linea_w/2, linea_y)

    can.setFont("Helvetica", 14)
    if nombre_1: can.drawCentredString(firma1_x, linea_y + 5, nombre_1)
    if nombre_2: can.drawCentredString(firma2_x, linea_y + 5, nombre_2)

    can.setFont("Helvetica", 9)
    can.drawCentredString(firma1_x, linea_y - 15, "(Rellenado por)")
    can.drawCentredString(firma2_x, linea_y - 15, "(Verificado por)")

    can.setFont("Helvetica-Bold", 10)
    can.drawString(90, linea_y - 35, "S-24-S  5/21")
    can.save()
    buffer.seek(0)
    return buffer, firma_y

# ─── Notificación Telegram ─────────────────────────────────────────────────────
def enviar_donacion_telegram(tipo_trans, om, gc, c1_nom, c1_val, c2_nom, c2_val,
                              total_gen, pdf_file, nombre_archivo):
    try:
        token   = str(st.secrets["TELEGRAM_TOKEN"]).strip()
        chat_id = str(st.secrets["TELEGRAM_CHAT_ID"]).strip()

        sep = "─" * 26 + "\n"
        montos = ""
        if om     > 0: montos += f"  ▪️ Obra Mundial:  <b>${om:,}</b>\n"
        if gc     > 0: montos += f"  ▪️ Congregación: <b>${gc:,}</b>\n"
        if c1_val > 0: montos += f"  ▪️ {c1_nom}: <b>${c1_val:,}</b>\n"
        if c2_val > 0: montos += f"  ▪️ {c2_nom}: <b>${c2_val:,}</b>\n"

        mensaje = (
            "📄 <b>REGISTRO DE TRANSACCIÓN S-24</b>\n"
            f"{sep}"
            f"📅 <b>Fecha:</b>          {fecha_str}\n"
            f"📝 <b>Tipo:</b>            {tipo_trans}\n"
            f"{sep}"
            f"{montos}"
            f"{sep}"
            f"💰 <b>TOTAL: ${total_gen:,} COP</b>\n"
            f"{sep}"
            f"✍️ <b>Rellenado por:</b>  {nombre_1 or '—'}\n"
            f"✍️ <b>Verificado por:</b> {nombre_2 or '—'}\n"
            f"{sep}"
            "📎 <i>El recibo oficial se adjunta a continuación.</i>"
        )

        url_msg = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url_msg,
                      json={"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"},
                      timeout=10)

        url_doc = f"https://api.telegram.org/bot{token}/sendDocument"
        pdf_file.seek(0)
        files    = {'document': (nombre_archivo, pdf_file, 'application/pdf')}
        response = requests.post(url_doc, data={'chat_id': chat_id}, files=files, timeout=15)

        if response.status_code == 200:
            st.success("✅ Notificación y recibo enviados a Telegram 🔔")
    except Exception as e:
        st.error(f"⚠️ El PDF se generó pero no se pudo notificar a Telegram: {e}")

# ─── Generar y mostrar resultados ─────────────────────────────────────────────
if enviado:
    try:
        if firma1.image_data is None or firma2.image_data is None:
            st.error("❌ Ambas firmas son obligatorias para generar el PDF.")
        else:
            nombre_archivo = f"{fecha_str} - {tipo}.pdf"
            pdf_base, firma_y_pos = crear_pdf(conc1_nombre, conc1_valor,
                                              conc2_nombre, conc2_valor,
                                              nombre_archivo)
            pdf_final  = insertar_firmas(pdf_base, firma1.image_data,
                                         firma2.image_data, firma_y_pos,
                                         nombre_archivo)
            pdf_bytes  = pdf_final.getvalue()

            if pdf_bytes:
                # — Nota informativa —
                st.markdown("""
                <div style="border:1.5px solid #94a3b8; padding:14px; border-radius:12px;
                            background:var(--bg-card,#f8faff); margin:1rem 0; font-size:0.97rem;">
                ⚠️ <b>Antes de descargar</b> — Verifica que toda la información sea correcta.<br><br>
                📱 <b>¿Usas celular?</b> El archivo puede descargarse como <i>file.pdf</i>;
                puedes renombrarlo después. Para compartirlo (WhatsApp, Telegram, Drive),
                abre el PDF y usa el botón <i>Compartir</i>.
                </div>
                """, unsafe_allow_html=True)

                # — Telegram —
                enviar_donacion_telegram(
                    tipo, don_obra, don_congre,
                    conc1_nombre, conc1_valor,
                    conc2_nombre, conc2_valor,
                    total, pdf_final, nombre_archivo
                )

                # — Descarga —
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
