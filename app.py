import streamlit as st
from datetime import date, datetime
import pytz

from ui.estilos import inyectar_estilos
from ui.scripts_js import inyectar_scripts
from ui.campos import formatear_numero_elegante
from ui.firmas import widget_firma
from pdf.generador import crear_pdf
from pdf.firmas_pdf import insertar_firmas
from integraciones.telegram import enviar_donacion_telegram
from utils.formato import formatear_fecha_espanol, sanitizar_nombre

# ─── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(page_title="Formulario S-24", layout="centered")

# ─── CSS y JS ───────────────────────────────────────────────────────────────────
#inyectar_estilos()
inyectar_scripts()

# ─── Zona horaria Colombia ─────────────────────────────────────────────────────
col_tz = pytz.timezone('America/Bogota')
fecha_actual = datetime.now(col_tz).date()

# ─── Encabezado ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📄 Registro de Transacción S-24</h1>
    <p>Generador de formulario oficial · Congregación</p>
</div>
""", unsafe_allow_html=True)

# ─── Pestañas ───────────────────────────────────────────────────────────────────
tab_datos, tab_resp, tab_montos, tab_firmas, tab_enviar = st.tabs(
    ["📅 Datos", "👤 Responsables", "💰 Montos", "✍️ Firmas", "📤 Enviar"]
)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Datos: fecha, tipo de transacción
# ═══════════════════════════════════════════════════════════════════════════════
with tab_datos:
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
    fecha_str = formatear_fecha_espanol(fecha_seleccionada)
    st.success(f"✅ **Fecha:** {fecha_str}")
    st.markdown('</div>', unsafe_allow_html=True)

    # — Tipo de transacción —
    st.markdown('<div class="section-card"><div class="section-title">🔖 Tipo de transacción</div>', unsafe_allow_html=True)
    tipo = st.radio("", [
        "DONACIÓN", "PAGO", "DEPÓSITO EN LA CAJA DE EFECTIVO", "ADELANTO DE EFECTIVO", "OTRO"
    ], label_visibility="collapsed", key="tipo_trans")
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Responsables: quién rellena y quién verifica
# ═══════════════════════════════════════════════════════════════════════════════
with tab_resp:
    st.markdown('<div class="section-card"><div class="section-title">👤 Personas responsables</div>', unsafe_allow_html=True)
    col_n1, col_n2 = st.columns(2)
    with col_n1:
        nombre_1 = st.text_input("Quien rellena", placeholder="Nombre completo", key="nombre_rellena")
    with col_n2:
        nombre_2 = st.text_input("Quien verifica", placeholder="Nombre completo", key="nombre_verifica")
    st.markdown('</div>', unsafe_allow_html=True)
    # Forzar rerender cuando nombre_2 cambia sin necesidad de salir del campo
    st.caption(f" ")  # espacio invisible que obliga rerender continuo

# ── Limpiar campos al cambiar tipo de transacción ──────────────────────────────
# (no dibuja nada, solo maneja session_state — no necesita vivir dentro de una pestaña)
if "tipo_anterior" not in st.session_state:
    st.session_state["tipo_anterior"] = tipo
if st.session_state["tipo_anterior"] != tipo:
    for k in ["don_obra_key", "don_congre_key", "conc1_nom", "conc1_valor_key",
              "conc2_nom", "conc2_valor_key", "deposito_key"]:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["tipo_anterior"] = tipo

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Montos: campos dinámicos según el tipo + total
# ═══════════════════════════════════════════════════════════════════════════════
don_obra = don_congre = conc1_valor = conc2_valor = deposito_valor = 0
conc1_nombre = conc2_nombre = "."

with tab_montos:
    if tipo == "DONACIÓN":
        st.markdown('<div class="section-card"><div class="section-title">💰 Donaciones</div>', unsafe_allow_html=True)
        don_obra = formatear_numero_elegante("don_obra_key", "Obra Mundial (OM)")
        don_congre = formatear_numero_elegante("don_congre_key", "Gastos de la Congregación (GC)")
        st.markdown('</div>', unsafe_allow_html=True)

    elif tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO":
        st.markdown('<div class="section-card"><div class="section-title">🏦 Depósito en caja</div>', unsafe_allow_html=True)
        deposito_valor = formatear_numero_elegante("deposito_key", "Valor del depósito")
        st.markdown('</div>', unsafe_allow_html=True)

    else:  # PAGO, ADELANTO DE EFECTIVO, OTRO
        st.markdown('<div class="section-card"><div class="section-title">📌 Conceptos</div>', unsafe_allow_html=True)
        conc1_nombre = st.text_input("Nombre del Concepto 1", value=".", key="conc1_nom").upper()
        conc1_valor = formatear_numero_elegante("conc1_valor_key", "Valor del Concepto 1")
        conc2_nombre = st.text_input("Nombre del Concepto 2", value=".", key="conc2_nom").upper()
        conc2_valor = formatear_numero_elegante("conc2_valor_key", "Valor del Concepto 2")
        st.markdown('</div>', unsafe_allow_html=True)

    total = don_obra + don_congre + conc1_valor + conc2_valor + deposito_valor
    st.markdown(f'<div class="total-box">TOTAL: ${total:,} COP</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Firmas
# ═══════════════════════════════════════════════════════════════════════════════
with tab_firmas:
    firma1 = widget_firma("firma1", "Firma — quien rellena:")
    st.markdown("---")
    firma2 = widget_firma("firma2", "Firma — quien verifica:")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Enviar: clave, resumen y generación del PDF
# ═══════════════════════════════════════════════════════════════════════════════
with tab_enviar:
    # — Clave —
    st.markdown("🔒 **Clave de notificación** *(opcional — solo para el grupo autorizado)*")
    clave_ingresada = st.text_input(
        "Clave", placeholder="Ingresa la clave si perteneces al grupo",
        type="password", key="clave_notif"
    )

    # ── Resumen bajo demanda + botón generar ──────────────────────────────────
    st.markdown("---")

    if "mostrar_resumen" not in st.session_state:
        st.session_state["mostrar_resumen"] = False

    if st.button("📋 Ver(Actualizar) resumen", use_container_width=True):
        st.session_state["mostrar_resumen"] = True

    if st.session_state["mostrar_resumen"]:
        _filas_prev = [
            ("Fecha", fecha_str),
            ("Tipo", tipo),
        ]
        if tipo == "DONACIÓN":
            _filas_prev.append(("Obra Mundial", f"${don_obra:,} COP"))
            _filas_prev.append(("Congregación", f"${don_congre:,} COP"))
        elif tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO":
            _filas_prev.append(("Depósito", f"${deposito_valor:,} COP"))
        else:
            if conc1_nombre and conc1_nombre != "." and conc1_valor > 0:
                _filas_prev.append((conc1_nombre[:30], f"${conc1_valor:,} COP"))
            if conc2_nombre and conc2_nombre != "." and conc2_valor > 0:
                _filas_prev.append((conc2_nombre[:30], f"${conc2_valor:,} COP"))
        _filas_prev.append(("TOTAL", f"${total:,} COP"))
        _filas_prev.append(("Rellenado por", nombre_1 or "—"))
        if nombre_2 and nombre_2.strip():
            _filas_prev.append(("Verificado por", nombre_2))

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
        st.markdown("")
        enviado = st.button("📤 Confirmar y generar PDF", use_container_width=True)
    else:
        enviado = False

    # ─── Generar y mostrar resultados ──────────────────────────────────────────
    if enviado:
        try:
            if firma1.image_data is None or firma2.image_data is None:
                st.error("❌ Ambas firmas son obligatorias para generar el PDF.")
            else:
                nombre_archivo = f"{fecha_str} - {tipo}.pdf"
                nombre_archivo = sanitizar_nombre(nombre_archivo)  # sin tildes en el nombre del archivo

                pdf_base, firma_y_pos = crear_pdf(
                    tipo=tipo, fecha_str=fecha_str, don_obra=don_obra, don_congre=don_congre,
                    conc1_nombre=conc1_nombre, conc1_valor=conc1_valor,
                    conc2_nombre=conc2_nombre, conc2_valor=conc2_valor,
                    deposito_valor=deposito_valor, total=total,
                    nombre_1=nombre_1, nombre_2=nombre_2,
                    titulo_metadatos=nombre_archivo,
                )
                pdf_final = insertar_firmas(pdf_base, firma1.image_data,
                                             firma2.image_data, firma_y_pos,
                                             nombre_archivo)
                pdf_bytes = pdf_final.getvalue()

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
                    # Solo notificar si la clave es correcta
                    clave_correcta = "s24jw"  # cambia esta clave por la que quieras
                    _c1n = conc1_nombre if tipo not in ["DONACIÓN", "DEPÓSITO EN LA CAJA DE EFECTIVO"] else "Depósito"
                    _c1v = conc1_valor if tipo not in ["DONACIÓN", "DEPÓSITO EN LA CAJA DE EFECTIVO"] else deposito_valor
                    if clave_ingresada.strip() == clave_correcta:
                        enviar_donacion_telegram(
                            tipo,
                            don_obra if tipo == "DONACIÓN" else 0,
                            don_congre if tipo == "DONACIÓN" else 0,
                            _c1n, _c1v,
                            conc2_nombre, conc2_valor,
                            total, pdf_final, nombre_archivo,
                            fecha_str=fecha_str, nombre_1=nombre_1, nombre_2=nombre_2,
                        )
                    else:
                        if clave_ingresada.strip() != "":
                            st.warning("⚠️ Clave incorrecta — el PDF se generó pero no se envió notificación.")

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
