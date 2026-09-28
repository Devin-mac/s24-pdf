"""
Estilos CSS de la aplicación S-24.
Todo el bloque visual (colores, tarjetas, inputs, botones) vive aquí
para no mezclarlo con la lógica del formulario.
"""
import streamlit as st

CSS_STYLES = """
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

/* ── Márgenes de Streamlit: recortados para ganar espacio en pantalla ── */
[data-testid="stHeader"],
[data-testid="stToolbar"] {
    display: none !important;
}
.block-container,
[data-testid="stMainBlockContainer"] {
    padding-top: 0.8rem !important;
    padding-bottom: 2rem !important;
}

/* ── Encabezado (compacto) ── */
.main-header {
    background: linear-gradient(135deg, #1a3a6e 0%, #2563eb 100%);
    color: #ffffff !important;
    padding: 0.7rem 1.1rem;
    border-radius: 12px;
    margin-bottom: 0.8rem;
    box-shadow: 0 4px 14px rgba(37,99,235,0.22);
}
.main-header h1 { font-size: 1.2rem; font-weight: 700; margin: 0 0 0.1rem 0; padding: 0; color: #ffffff !important; }
.main-header p  { font-size: 0.8rem; opacity: 0.85; margin: 0; color: #ffffff !important; }

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
    height: 6.8rem !important;
    display: flex !important;
    align-items: center !important;
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

/* ── Pestañas de navegación ── */
[data-testid="stTabs"] [data-baseweb="tab-list"],
[data-baseweb="tab-list"] {
    gap: 10px !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"],
button[data-baseweb="tab"],
[data-baseweb="tab"] {
    height: 8.5rem !important;
    padding: 0 2.2rem !important;
}
[data-testid="stTabs"] button[data-baseweb="tab"] p,
button[data-baseweb="tab"] p,
[data-baseweb="tab"] p {
    font-size: 3.1rem !important;
    font-weight: 700 !important;
}

/* Canvas firmas */
canvas { border-radius: 10px; border: 2px solid var(--border) !important; }

footer { visibility: hidden; }
</style>
"""


def inyectar_estilos():
    """Inserta el CSS de la aplicación en la página actual."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
