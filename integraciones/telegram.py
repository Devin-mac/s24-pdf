"""
Notificación por Telegram al generar un PDF.

Si algo falla, se muestra en pantalla el motivo real que devuelve Telegram
(sin exponer el token).
"""
import streamlit as st
import requests


def _explicar_error(resp, token):
    """Devuelve un texto claro con el motivo del fallo de la API de Telegram."""
    try:
        datos = resp.json()
    except Exception:
        datos = {}
    descripcion = str(datos.get("description", resp.text[:200])).replace(token, "***")
    pista = ""
    if resp.status_code == 401:
        pista = " → El TELEGRAM_TOKEN es inválido o fue revocado. Revisá los Secrets."
    elif resp.status_code == 400 and "chat not found" in descripcion.lower():
        pista = " → TELEGRAM_CHAT_ID incorrecto, o el bot no está dentro del grupo."
    elif resp.status_code == 400 and "upgraded to a supergroup" in descripcion.lower():
        nuevo = datos.get("parameters", {}).get("migrate_to_chat_id")
        pista = f" → El grupo pasó a supergrupo. Nuevo TELEGRAM_CHAT_ID: {nuevo}"
    elif resp.status_code == 403:
        pista = " → El bot fue expulsado del grupo o no tiene permiso para escribir."
    return f"Telegram respondió {resp.status_code}: {descripcion}{pista}"


def enviar_donacion_telegram(tipo_trans, om, gc, c1_nom, c1_val, c2_nom, c2_val,
                              total_gen, pdf_file, nombre_archivo,
                              fecha_str, nombre_1, nombre_2):
    token = ""
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

        r_msg = requests.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            json={"chat_id": chat_id, "text": mensaje, "parse_mode": "HTML"},
            timeout=10,
        )
        if r_msg.status_code != 200:
            st.error("⚠️ No se pudo enviar el mensaje a Telegram. " + _explicar_error(r_msg, token))
            return

        pdf_file.seek(0)
        files = {'document': (nombre_archivo, pdf_file, 'application/pdf')}
        r_doc = requests.post(
            f"https://api.telegram.org/bot{token}/sendDocument",
            data={'chat_id': chat_id}, files=files, timeout=15,
        )
        if r_doc.status_code == 200:
            st.success("✅ Notificación y recibo enviados a Telegram 🔔")
        else:
            st.error("⚠️ El mensaje llegó, pero no se pudo enviar el PDF. " + _explicar_error(r_doc, token))

    except KeyError as e:
        st.error(f"⚠️ Falta el secreto {e} en Streamlit (Settings → Secrets).")
    except Exception as e:
        detalle = str(e).replace(token, "***") if token else str(e)
        st.error(f"⚠️ El PDF se generó pero no se pudo notificar a Telegram: {detalle}")
