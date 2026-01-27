import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página centrada
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    if not texto: return ""
    
    # Asegurar UTF-8
    texto = texto.encode("utf-8").decode("utf-8")
    
    lineas = texto.split('\n')
    resultado_final = []
    
    # Patrón mejorado: Captura Nota (1), Sostenido (2) y Resto como m, 7, etc (3)
    # Ejemplo "Fam#": Grupo 1: Fa, Grupo 2: None, Grupo 3: m#
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])(#|b)?((?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?#?)'

    for linea in lineas:
        linea_lista = list(linea)
        matches = list(re.finditer(patron, linea, flags=re.IGNORECASE))
        
        # Procesar de atrás hacia adelante para no romper los índices al insertar caracteres
        for match in reversed(matches):
            inicio, fin = match.start(), match.end()
            raiz_orig = match.group(1).upper()
            alteracion = match.group(2) if match.group(2) else ""
            resto = match.group(3) if match.group(3) else ""
            
            # Filtros para no procesar palabras comunes
            lo_que_sigue = linea[fin:]
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            # CONVERSIÓN
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            
            # Combinamos todo el cuerpo del acorde (Ej: F + m)
            # Si el resto contiene un # (como en Fam#), lo movemos al final después del apóstrofe
            cuerpo_acorde = f"{raiz_nueva}{alteracion}{resto}"
            
            tiene_sostenido = False
            if '#' in cuerpo_acorde:
                tiene_sostenido = True
                cuerpo_acorde = cuerpo_acorde.replace('#', '')

            # Construcción final: Cuerpo + Apóstrofe + Sostenido (si lo tenía)
            # Resultado de Fam# -> Fm#'
            nuevo_acorde = f"{cuerpo_acorde}'#" if tiene_sostenido else f"{cuerpo_acorde}'"

            # Reemplazo en la línea
            linea_lista[inicio:fin] = list(nuevo_acorde)
                    
        resultado_final.append("".join(linea_lista))
    
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown(f"""
    <div style='display: flex; align-items: center; justify-content: center; gap: 10px;'>
        <img src='https://raw.githubusercontent.com' alt='Icono' style='width: 45px; height: 45px;'>
        <h1>Cancionero Pro</h1>   
    </div>""", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Versión 2026: Conversión exacta de sostenidos (Ej: Fam# -> Fm#')</p>", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    try:
        nombre_archivo = archivo.name
        contenido = archivo.getvalue().decode("utf-8")
        texto_final = procesar_texto(contenido)
        
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")

        components.html(f"""
            <style>
                .action-bar {{
                    position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%);
                    display: flex; gap: 15px; z-index: 9999;
                }}
                .btn {{
                    width: 150px; height: 50px; border: none; border-radius: 25px;
                    font-family: sans-serif; font-size: 16px; font-weight: bold;
                    cursor: pointer; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                }}
                .dl {{ background-color: #007AFF; }}
                .sh {{ background-color: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn dl">💾 Guardar</button>
                <button id="sh" class="btn sh">📤 Compartir</button>
            </div>
            <script>
                const content = `{texto_js}`;
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b);
                    a.download = "PRO_{nombre_archivo}";
                    a.click();
                }};
                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([content], {{ type: 'text/plain;charset=utf-8' }});
                    const f = new File([b], "{nombre_archivo}", {{ type: 'text/plain' }});
                    if (navigator.share) await navigator.share({{ files: [f] }});
                }};
            </script>
        """, height=100)
    
    except Exception as e:
        st.error(f"Error: {e}")
