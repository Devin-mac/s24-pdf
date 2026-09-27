"""
Widgets de formulario reutilizables.
"""
import streamlit as st


def formatear_numero_elegante(key, label, help_text="Monto en pesos colombianos"):
    """
    Campo de texto para montos en pesos, con una vista previa formateada
    (con separador de miles) al lado del campo.

    Devuelve el valor entero ingresado (0 si está vacío o no es numérico).
    """
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
