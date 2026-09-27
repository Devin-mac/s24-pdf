"""
Notificación por Telegram al generar un PDF.

NOTA DE REFACTOR: igual que con crear_pdf, la función original leía
`fecha_str`, `nombre_1` y `nombre_2` del ámbito global. Aquí se reciben
como parámetros explícitos.
"""
import streamlit as st
import requests


def enviar_donacion_telegram(tipo_trans, om, gc, c1_nom, c1_val, c2_nom, c2_val,
                              total_gen, pdf_file, nombre_archivo,
                              fecha_str, nombre_1, nombre_2):
    try:
        token = str(st.secrets["TELEGRAM_TOKEN"]).strip()
        chat_id = str(st.secrets["TELEGRAM_CHAT_ID"]).strip()

        sep = "─" * 26 + "\n"
        montos = ""
        if om > 0: montos += f"  ▪️ Obra Mundial:  <b>${om:,}</b>\n"
        if gc > 0: montos += f"  ▪️ Congregación: <b>${gc:,}</b>\n"
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
        files = {'document': (nombre_archivo, pdf_file, 'application/pdf')}
        response = requests.post(url_doc, data={'chat_id': chat_id}, files=files, timeout=15)

        if response.status_code == 200:
            st.success("✅ Notificación y recibo enviados a Telegram 🔔")
    except Exception as e:
        st.error(f"⚠️ El PDF se generó pero no se pudo notificar a Telegram: {e}")
