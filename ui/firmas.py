"""
Componente de firma: un canvas de dibujo con botones "Deshacer" y "Borrar"
que funcionan también en celular/tablet (no dependen del hover del mouse).
"""
import copy
import streamlit as st
from streamlit_drawable_canvas import st_canvas


def widget_firma(prefijo, etiqueta):
    """
    Muestra un campo de firma con sus botones de control.

    prefijo : identificador único para esta firma, p. ej. "firma1".
    etiqueta: texto mostrado junto al campo.

    Devuelve el objeto resultado de st_canvas (con .image_data y .json_data).
    """
    key_version = f"{prefijo}_version"      # cambia -> se monta un canvas nuevo
    key_json = f"{prefijo}_json"            # último dibujo reportado por el canvas
    key_inicial = f"{prefijo}_inicial"      # dibujo con el que arranca el canvas actual
    key_aplicada = f"{prefijo}_aplicada"    # última versión ya renderizada

    if key_version not in st.session_state:
        st.session_state[key_version] = 0
    if key_json not in st.session_state:
        st.session_state[key_json] = None
    if key_inicial not in st.session_state:
        st.session_state[key_inicial] = None
    if key_aplicada not in st.session_state:
        st.session_state[key_aplicada] = -1

    col_txt, col_undo, col_btn = st.columns([3, 1, 1])
    with col_txt:
        st.markdown(f"**{etiqueta}**")
    with col_undo:
        if st.button("↩️ Deshacer", key=f"undo_{prefijo}"):
            datos = st.session_state[key_json]
            if datos and datos.get("objects"):
                datos = copy.deepcopy(datos)
                datos["objects"] = datos["objects"][:-1]
                st.session_state[key_json] = datos
                st.session_state[key_inicial] = datos
                st.session_state[key_version] += 1
                st.rerun()
    with col_btn:
        if st.button("🗑️ Borrar", key=f"borrar_{prefijo}"):
            st.session_state[key_json] = None
            st.session_state[key_inicial] = None
            st.session_state[key_version] += 1
            st.rerun()

    version_actual = st.session_state[key_version]
    primer_render = st.session_state[key_aplicada] != version_actual
    st.session_state[key_aplicada] = version_actual

    # initial_drawing se mantiene IGUAL entre reruns (solo cambia con
    # Deshacer/Borrar, que además cambian la key): así el canvas no se
    # redibuja ni se vacía mientras el usuario firma.
    resultado = st_canvas(
        key=f"{prefijo}_{version_actual}",
        height=240, width=550,
        drawing_mode="freedraw", stroke_width=2,
        stroke_color="#000000", background_color="#ffffff",
        return_image_data=True,
        initial_drawing=st.session_state[key_inicial],
    )

    # En el primer render de un canvas nuevo puede devolver un estado vacío
    # antes de cargar el dibujo inicial; no lo guardamos para no perderlo.
    if resultado.json_data is not None and not primer_render:
        st.session_state[key_json] = resultado.json_data

    return resultado
