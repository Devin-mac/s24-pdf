"""
Generación del PDF base del formulario S-24 (sin las firmas insertadas;
eso lo hace pdf/firmas_pdf.py después).

NOTA DE REFACTOR: en el archivo original, crear_pdf() leía variables como
`tipo`, `fecha_str`, `don_obra`, `don_congre`, `total`, `nombre_1`, `nombre_2`
directamente del ámbito global del script. Eso funcionaba porque todo vivía
en un único archivo, pero se rompe al separar en módulos. Aquí se reciben
todas como parámetros explícitos — el comportamiento es idéntico, solo
cambia de dónde vienen los datos.
"""
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape


def dibujar_checkbox_cuadrado(c, x, y, marcado=False, size=18):
    c.rect(x, y, size, size, stroke=1, fill=0)
    if marcado:
        c.setFont("Helvetica-Bold", size - 2)
        c.drawString(x + size / 2 - 3, y + 2, "X")


def crear_pdf(tipo, fecha_str, don_obra, don_congre,
              conc1_nombre, conc1_valor, conc2_nombre, conc2_valor,
              deposito_valor, total, nombre_1, nombre_2,
              titulo_metadatos):
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
    separacion_conceptos = 42.5
    x_inicio_lineas = x_der - longitud_linea_valores
    checkbox_size = 14
    col_izq_x = x_izq + 20
    col_der_x = 396

    dibujar_checkbox_cuadrado(can, x_izq, y - 2, tipo == "DONACIÓN", checkbox_size)
    can.setFont("Helvetica", 18)
    can.drawString(col_izq_x, y, "Donación")
    dibujar_checkbox_cuadrado(can, col_der_x, y - 2, tipo == "PAGO", checkbox_size)
    can.drawString(col_der_x + 20, y, "Pago")
    y -= espaciado_lineas

    dibujar_checkbox_cuadrado(can, x_izq, y - 2, tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO", checkbox_size)
    can.drawString(col_izq_x, y, "Depósito en la caja de efectivo")
    dibujar_checkbox_cuadrado(can, col_der_x, y - 2, tipo == "ADELANTO DE EFECTIVO", checkbox_size)
    can.drawString(col_der_x + 20, y, "Adelanto de efectivo")
    y -= 45

    can.setFont("Helvetica", 18)

    # Línea 1: Donaciones Obra mundial — siempre presente
    can.drawString(x_izq, y, "Donaciones (Obra mundial)")
    can.drawRightString(x_der, y, f"{don_obra:,.2f}" if don_obra > 0 else "")
    can.line(x_inicio_lineas, y - 4, x_der, y - 4)
    y -= espaciado_lineas

    # Línea 2: Donaciones Congregación — siempre presente
    can.drawString(x_izq, y, "Donaciones (Gastos de la congregación)")
    can.drawRightString(x_der, y, f"{don_congre:,.2f}" if don_congre > 0 else "")
    can.line(x_inicio_lineas, y - 4, x_der, y - 4)
    y -= espaciado_lineas

    # Líneas 3-5: conceptos adicionales según tipo
    if tipo == "DEPÓSITO EN LA CAJA DE EFECTIVO":
        # El valor del depósito va directo al total, líneas en blanco
        for _ in range(3):
            x_concepto_fin = x_inicio_lineas - separacion_conceptos
            can.line(x_izq, y + 2, x_concepto_fin, y + 2)
            can.line(x_inicio_lineas, y + 2, x_der, y + 2)
            y -= espaciado_lineas
    else:
        # DONACIÓN, PAGO, ADELANTO, OTRO — mostrar conceptos si los hay
        conceptos_mostrados = 0
        if conc1_nombre and conc1_nombre != "." and conc1_valor > 0:
            can.drawString(x_izq, y, conc1_nombre)
            can.drawRightString(x_der, y, f"{conc1_valor:,.2f}")
            y -= espaciado_lineas
            conceptos_mostrados += 1
        if conc2_nombre and conc2_nombre != "." and conc2_valor > 0:
            can.drawString(x_izq, y, conc2_nombre)
            can.drawRightString(x_der, y, f"{conc2_valor:,.2f}")
            y -= espaciado_lineas
            conceptos_mostrados += 1
        for _ in range(3 - conceptos_mostrados):
            x_concepto_fin = x_inicio_lineas - separacion_conceptos
            can.line(x_izq, y + 2, x_concepto_fin, y + 2)
            can.line(x_inicio_lineas, y + 2, x_der, y + 2)
            y -= espaciado_lineas

    y -= 15
    can.setFont("Helvetica-Bold", 22)
    can.drawRightString(x_inicio_lineas - separacion_conceptos, y, "TOTAL:")
    can.setFont("Helvetica-Bold", 18)
    can.drawRightString(x_der, y, f"{total:,.2f}")
    y -= 90

    firma1_x = 240
    firma2_x = 550
    firma_y = y - 40
    linea_w = 206
    linea_y = firma_y - 10

    can.line(firma1_x - linea_w / 2, linea_y, firma1_x + linea_w / 2, linea_y)
    can.line(firma2_x - linea_w / 2, linea_y, firma2_x + linea_w / 2, linea_y)

    can.setFont("Helvetica", 14)
    if nombre_1:
        can.drawCentredString(firma1_x, linea_y + 5, nombre_1)
    if nombre_2:
        can.drawCentredString(firma2_x, linea_y + 5, nombre_2)

    can.setFont("Helvetica", 9)
    can.drawCentredString(firma1_x, linea_y - 15, "(Rellenado por)")
    can.drawCentredString(firma2_x, linea_y - 15, "(Verificado por)")

    can.setFont("Helvetica-Bold", 10)
    can.drawString(90, linea_y - 35, "S-24-S  5/21")
    can.save()
    buffer.seek(0)
    return buffer, firma_y
