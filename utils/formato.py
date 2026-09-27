"""
Utilidades genéricas: formato de fecha en español y sanitización de nombres
de archivo (necesaria para que Telegram no falle con tildes/ñ en el header
Content-Disposition).
"""
import unicodedata

MESES_ESPANOL = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]


def formatear_fecha_espanol(fecha):
    """Convierte un date de Python a 'DD MES AAAA', p. ej. '24 SEPTIEMBRE 2026'."""
    return f"{fecha.day:02d} {MESES_ESPANOL[fecha.month - 1]} {fecha.year}"


def sanitizar_nombre(nombre):
    """Convierte tildes y caracteres especiales a ASCII para evitar
    problemas en el Content-Disposition header de Telegram."""
    normalizado = unicodedata.normalize("NFD", nombre)
    solo_ascii = normalizado.encode("ascii", "ignore").decode("ascii")
    return solo_ascii
