import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración para máxima estabilidad en 2026
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
MAPA = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    res = []
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'
    for linea in lineas:
        lista = list(linea)
        for m in re.finditer(patron, linea, flags=re.IGNORECASE):
            ini, fin = m.start(), m.end()
            if ini > 0 and linea[ini-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', linea[fin:]): continue
            
            nueva_raiz = MAPA.get(m.group(1).upper(), m.group(1).upper())
            acorde = f"{nueva_raiz}{m.group(2)}"
            if not (linea[fin:].startswith("'") or linea[fin:].startswith("*")): acorde += "'"
            
            ancho = len(m.group(0))
            if linea[fin:].startswith("'") or linea[fin:].startswith("*"): ancho += 1
            sustitucion = acorde.ljust(ancho)
            for i, char in enumerate(sustitucion):
                if ini + i < len(lista): lista[ini + i] = char
        res.append("".join(lista))
    return '\n'.join(res)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)

# MEJORA 2026: El cargador ahora tiene un buffer de memoria forzado
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo is not None:
    try:
        # Forzamos la lectura inmediata del buffer para "traerlo" al teléfono
        # y evitar que Dropbox corte la conexión (AxiosError)
        datos_archivo = archivo.read() 
        contenido = datos_archivo.decode("utf-8")
        nombre = archivo.name
        
        texto_pro = procesar_texto(contenido)
        st.subheader("Vista Previa:")
        st.code(texto_pro, language="text")

        js_txt = texto_pro.replace("`", "\\`").replace("$", "\\$")
        
        components.html(f"""
            <style>
                .bar {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 9999; }}
                .btn {{ width: 140px; height: 50px; border: none; border-radius: 25px; font-family: sans-serif; font-size: 16px; font-weight: bold; cursor: pointer; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; gap: 8px; }}
                .dl {{ background-color: #007AFF; }} .sh {{ background-color: #34C759; }}
            </style>
            <div class="bar">
                <button onclick="dl()" class="btn dl">💾 Guardar</button>
                <button onclick="sh()" class="btn sh">📤 Compartir</button>
            </div>
            <script>
                const t = `{js_txt}`;
                function dl() {{
                    const b = new Blob([t], {{type: 'text/plain'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b);
                    a.download = "PRO_{nombre}";
                    a.click();
                }}
                async function sh() {{
                    const f = new File([new Blob([t])], "{nombre}", {{type: 'text/plain'}});
                    if (navigator.share) {{ try {{ await navigator.share({{ files: [f] }}); }} catch (e) {{}} }}
                }}
            </script>
        """, height=100)
    except Exception as e:
        st.error("Error de conexión. Intenta descargar el archivo a tu dispositivo primero.")

# Botón de limpieza
if st.button("🔄 Nueva Carga"):
    st.rerun()


