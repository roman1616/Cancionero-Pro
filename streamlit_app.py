import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de estabilidad para 2026
st.set_page_config(page_title="Cancionero Pro", layout="centered")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    resultado_final = []
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            inicio = match.start()
            
            lo_que_sigue = linea[fin:]
            # Filtros de exclusión para evitar procesar letras de canción
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            raiz_nueva = LATINO_A_AMERICANO.get(match.group(1).upper(), match.group(1).upper())
            nuevo_acorde = f"{raiz_nueva}{match.group(2)}"
            if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*")):
                nuevo_acorde += "'"

            ancho_original = len(acorde_original)
            if lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*"): ancho_original += 1
            sustitucion = nuevo_acorde.ljust(ancho_original)

            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)

# Opción A: Cargador de archivos estándar (Si da error de red, usa la Opción B)
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

# Opción B: Área de texto manual (Salvavidas si falla la red en el móvil)
texto_manual = st.text_area("O pega el texto aquí:", height=150, help="Usa esto si el cargador de archivos da error de red.")

# Prioridad al archivo, luego al texto manual
contenido_final = ""
nombre_final = "cancion.txt"

if archivo:
    try:
        contenido_final = archivo.read().decode("utf-8")
        nombre_final = archivo.name
    except:
        st.error("Error al leer el archivo. Intenta pegando el texto.")
elif texto_manual:
    contenido_final = texto_manual

if contenido_final:
    texto_procesado = procesar_texto(contenido_final)
    st.subheader("Resultado:")
    st.code(texto_procesado, language="text")

    # Inyectamos botones con JS puro para evitar bloqueos de Axios/CORS
    texto_js = texto_procesado.replace("`", "\\`").replace("$", "\\$")
    
    components.html(f"""
        <style>
            .bar {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 9999; }}
            .btn {{ width: 140px; height: 48px; border: none; border-radius: 24px; font-family: sans-serif; font-size: 15px; font-weight: bold; cursor: pointer; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; gap: 8px; }}
            .dl {{ background-color: #007AFF; }}
            .sh {{ background-color: #34C759; }}
        </style>
        <div class="bar">
            <button onclick="descargar()" class="btn dl">💾 Guardar</button>
            <button onclick="compartir()" class="btn sh">📤 Compartir</button>
        </div>
        <script>
            const txt = `{texto_js}`;
            function descargar() {{
                const blob = new Blob([txt], {{type: 'text/plain'}});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = "PRO_{nombre_final}";
                a.click();
            }}
            async function compartir() {{
                const file = new File([txt], "{nombre_final}", {{type: 'text/plain'}});
                if (navigator.share) {{
                    try {{ await navigator.share({{ files: [file] }}); }} catch (e) {{ console.log(e); }}
                }} else {{ alert("Navegador no compatible con compartir."); }}
            }}
        </script>
    """, height=100)
