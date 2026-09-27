"""
Scripts JS inyectados en la app:
- fixInputs(): fuerza teclado numérico en móvil para los campos de montos,
  y teclado normal (texto) para nombres/conceptos.
- formatearMiles(): agrega el punto de miles mientras el usuario escribe.
"""
import streamlit.components.v1 as components

SCRIPT_JS = """
<script>
function formatearMiles(el) {
    var soloDigitos = el.value.replace(/\\D/g, '');
    var formateado = soloDigitos.replace(/\\B(?=(\\d{3})+(?!\\d))/g, '.');

    // Si ya está formateado igual, no hacer nada: evita un bucle infinito,
    // porque el 'input' que disparamos abajo vuelve a llamar a esta misma función.
    if (el.value === formateado) { return; }

    var cursorDesdeElFinal = el.value.length - el.selectionStart;

    // Truco para que React (frontend de Streamlit) detecte el cambio real
    var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
    setter.call(el, formateado);
    el.dispatchEvent(new Event('input', { bubbles: true }));

    var nuevaPos = Math.max(formateado.length - cursorDesdeElFinal, 0);
    el.setSelectionRange(nuevaPos, nuevaPos);
}

function fixInputs() {
    var doc = window.parent.document;
    // Keys de campos que deben ser texto libre
    var camposTexto = ['nombre_rellena', 'nombre_verifica', 'conc1_nom', 'conc2_nom'];

    doc.querySelectorAll('input[type="text"], input[type="number"]').forEach(function(el) {
        // Obtener el aria-label o buscar label asociado
        var ariaLabel = (el.getAttribute('aria-label') || '').toLowerCase();
        var inputId   = (el.id || '').toLowerCase();

        // Verificar si es un campo de texto libre por su key o label
        var esTextoLibre = camposTexto.some(function(k) {
            return inputId.includes(k) || ariaLabel.includes(k);
        });

        // Segunda verificacion: buscar el label visible mas cercano
        if (!esTextoLibre) {
            var container = el.closest('.stTextInput, .stNumberInput');
            var labelEl   = container ? container.querySelector('label') : null;
            var labelText = labelEl ? labelEl.innerText.toLowerCase() : '';
            esTextoLibre  = labelText.includes('nombre') || labelText.includes('quien') ||
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
                el.addEventListener('input', function() { formatearMiles(el); });
                el.dataset.milesListener = "true";
            }
        }
    });
}
function fixTabs() {
    var doc = window.parent.document;
    var tabs = doc.querySelectorAll('[data-testid="stTab"]');

    tabs.forEach(function(btn) {
        btn.style.setProperty('height', '3.4rem', 'important');
        btn.style.setProperty('display', 'flex', 'important');
        btn.style.setProperty('align-items', 'center', 'important');
        btn.style.setProperty('padding', '0 0.9rem', 'important');
        var parrafo = btn.querySelector('p');
        if (parrafo) {
            parrafo.style.setProperty('font-size', '1.2rem', 'important');
            parrafo.style.setProperty('font-weight', '700', 'important');
        }
    });
}
setTimeout(fixTabs, 500);
setTimeout(fixTabs, 1200);
setTimeout(fixTabs, 3000);

// Reaplicar cada vez que Streamlit regenera el DOM
var observer = new MutationObserver(function(mutations) {
    var huboInputs = mutations.some(function(m) {
        return Array.from(m.addedNodes).some(function(n) {
            return n.nodeType === 1 && (n.tagName === 'INPUT' || (n.querySelector && n.querySelector('input')));
        });
    });
    if (huboInputs) { setTimeout(fixInputs, 100); }
    setTimeout(fixTabs, 100);
});
observer.observe(window.parent.document.body, { childList: true, subtree: true });
</script>
"""


def inyectar_scripts():
    """Inserta el script de teclado numérico / formato de miles en la página."""
    components.html(SCRIPT_JS, height=0)
