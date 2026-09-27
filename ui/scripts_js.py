"""
Scripts JS de la app (se inyectan UNA sola vez en la página principal):
- teclado numérico en móvil para los campos de montos
- punto de miles mientras se escribe
- tamaño de las pestañas

Antes, cada rerun de Streamlit creaba un iframe nuevo con su propio
MutationObserver, y se iban acumulando (causa del parpadeo al firmar).
Ahora el código se instala una sola vez y hay un único observer.
"""
import json
import streamlit.components.v1 as components

# ── Tamaño de las pestañas: ajustá aquí a tu gusto ────────────────────────────
TAB_ALTO = "2.4rem"
TAB_LETRA = "1rem"
TAB_PADDING = "0 0.9rem"

CODIGO_PAGINA = r"""
(function () {
    if (window.__s24Instalado) { return; }
    window.__s24Instalado = true;

    function formatearMiles(el) {
        var soloDigitos = el.value.replace(/\D/g, '');
        var formateado = soloDigitos.replace(/\B(?=(\d{3})+(?!\d))/g, '.');
        if (el.value === formateado) { return; }
        var cursorDesdeElFinal = el.value.length - el.selectionStart;
        var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
        setter.call(el, formateado);
        el.dispatchEvent(new Event('input', { bubbles: true }));
        var nuevaPos = Math.max(formateado.length - cursorDesdeElFinal, 0);
        el.setSelectionRange(nuevaPos, nuevaPos);
    }

    function fixInputs() {
        var camposTexto = ['nombre_rellena', 'nombre_verifica', 'conc1_nom', 'conc2_nom'];
        document.querySelectorAll('input[type="text"], input[type="number"]').forEach(function (el) {
            var ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
            var inputId = (el.id || '').toLowerCase();
            var esTextoLibre = camposTexto.some(function (k) {
                return inputId.includes(k) || ariaLabel.includes(k);
            });
            if (!esTextoLibre) {
                var container = el.closest('.stTextInput, .stNumberInput');
                var labelEl = container ? container.querySelector('label') : null;
                var labelText = labelEl ? labelEl.innerText.toLowerCase() : '';
                esTextoLibre = labelText.includes('nombre') || labelText.includes('quien') ||
                               labelText.includes('concepto') || labelText.includes('descripci');
            }
            if (esTextoLibre) {
                el.setAttribute('inputmode', 'text');
                el.removeAttribute('pattern');
            } else {
                el.setAttribute('inputmode', 'numeric');
                el.setAttribute('pattern', '[0-9]*');
                el.setAttribute('autocomplete', 'off');
                if (!el.dataset.milesListener) {
                    el.addEventListener('input', function () { formatearMiles(el); });
                    el.dataset.milesListener = 'true';
                }
            }
        });
    }

    function fixTabs() {
        document.querySelectorAll('[data-testid="stTab"]').forEach(function (tab) {
            tab.style.setProperty('height', '__TAB_ALTO__', 'important');
            tab.style.setProperty('display', 'flex', 'important');
            tab.style.setProperty('align-items', 'center', 'important');
            tab.style.setProperty('padding', '__TAB_PADDING__', 'important');
            var p = tab.querySelector('p');
            if (p) {
                p.style.setProperty('font-size', '__TAB_LETRA__', 'important');
                p.style.setProperty('font-weight', '700', 'important');
            }
        });
    }

    function aplicar() { fixInputs(); fixTabs(); }

    // Un solo observer, con freno: como mucho una pasada cada 200 ms
    var pendiente = null;
    new MutationObserver(function () {
        if (pendiente) { return; }
        pendiente = setTimeout(function () { pendiente = null; aplicar(); }, 200);
    }).observe(document.body, { childList: true, subtree: true });

    aplicar();
})();
"""

INSTALADOR = """
<script>
(function () {
    var doc = window.parent.document;
    if (doc.getElementById('s24-script')) { return; }   // ya instalado
    var s = doc.createElement('script');
    s.id = 's24-script';
    s.textContent = __CODIGO__;
    doc.head.appendChild(s);
})();
</script>
"""


def inyectar_scripts():
    """Instala (una sola vez) el script en la página principal."""
    codigo = (CODIGO_PAGINA
              .replace("__TAB_ALTO__", TAB_ALTO)
              .replace("__TAB_LETRA__", TAB_LETRA)
              .replace("__TAB_PADDING__", TAB_PADDING))
    html = INSTALADOR.replace("__CODIGO__", json.dumps(codigo))
    components.html(html, height=0)
