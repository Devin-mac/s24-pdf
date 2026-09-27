"""
Componente de firma: un canvas de dibujo con botones "Deshacer" y "Borrar"
que funcionan también en celular/tablet (no dependen del hover del mouse).
"""
import streamlit as st
from streamlit_drawable_canvas import st_canvas


def widget_firma(prefijo, etiqueta):
    """
    Muestra un campo de firma con sus botones de control.

    prefijo : identificador único para esta firma, p. ej. "firma1".
              Se usa para las keys de session_state y del canvas.
    etiqueta: texto mostrado junto al campo, p. ej. "Firma — quien rellena:".

    Devuelve el objeto resultado de st_canvas (con .image_data y .json_data),
    igual que si se hubiera llamado a st_canvas directamente.
    """
    key_version = f"{prefijo}_version"
    key_json = f"{prefijo}_json"

    if key_version not in st.session_state:
        st.session_state[key_version] = 0
    if key_json not in st.session_state:
        st.session_state[key_json] = None

    col_txt, col_undo, col_btn = st.columns([3, 1, 1])
    with col_txt:
        st.markdown(f"**{etiqueta}**")
    with col_undo:
        if st.button("↩️ Deshacer", key=f"undo_{prefijo}"):
            datos = st.session_state[key_json]
            if datos and datos.get("objects"):
                datos["objects"] = datos["objects"][:-1]
                st.session_state[key_json] = datos
            st.session_state[key_version] += 1
            st.rerun()
    with col_btn:
        if st.button("🗑️ Borrar", key=f"borrar_{prefijo}"):
            st.session_state[key_json] = None
            st.session_state[key_version] += 1
            st.rerun()

    resultado = st_canvas(
        key=f"{prefijo}_{st.session_state[key_version]}",
        height=240, width=550,
        drawing_mode="freedraw", stroke_width=2,
        stroke_color="#000000", background_color="#ffffff",
        return_image_data=True,
        initial_drawing=st.session_state[key_json],
    )
    if resultado.json_data is not None:
        st.session_state[key_json] = resultado.json_data

    return resultado
