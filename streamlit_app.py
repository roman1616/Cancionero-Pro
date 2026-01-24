import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página centrada y estable
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    resultado_final = []
    # Patrón robusto para detectar notas y acordes
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            fin = match.end()
            inicio = match.start()
            
            lo_que_sigue = linea[fin:]
            # Filtros para no romper la letra de la canción
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            # Conversión a Americano
            raiz_nueva = LATINO_A_AMERICANO.get(match.group(1).upper(), match.group(1).upper())
            nuevo_acorde = f"{raiz_nueva}{match.group(2)}"
            
            # Agregar apóstrofe si no tiene marcador
            if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*")):
                nuevo_acorde += "'"

            # Mantener alineación
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

# Cargador de archivos: Se usa un formato simplificado para evitar errores de red en móviles
archivo = st.file_uploader("Sube tu canción (.txt)", type=["txt"], help="Si da error de red, intenta mover el archivo a la memoria interna del móvil.")

if archivo is not None:
    try:
        # Leemos el archivo una sola vez para no saturar la conexión
        contenido = archivo.getvalue().decode("utf-8")
        nombre_archivo = archivo.name
        
        texto_procesado = procesar_texto(contenido)
        
        st.subheader("Vista Previa:")
        st.code(texto_procesado, language="text")

        # Escapamos el texto para el bloque JavaScript
        texto_js = texto_procesado.replace("`", "\\`").replace("$", "\\$")
        
        # Botones de Acción: Inyectados tras la carga exitosa
        components.html(f"""
            <style>
                .bar {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 9999; }}
                .btn {{ width: 140px; height: 50px; border: none; border-radius: 25px; font-family: sans-serif; font-size: 16px; font-weight: bold; cursor: pointer; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; gap: 8px; }}
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
                    a.download = "PRO_{nombre_archivo}";
                    a.click();
                }}
                async function compartir() {{
                    const file = new File([new Blob([txt])], "{nombre_archivo}", {{type: 'text/plain'}});
                    if (navigator.share) {{
                        try {{ await navigator.share({{ files: [file] }}); }} catch (e) {{ console.log(e); }}
                    }} else {{ alert("Compartir no soportado en este navegador."); }}
                }}
            </script>
        """, height=100)
    except Exception as e:
        st.error("Error de lectura. Por favor, asegúrate de que el archivo no esté protegido o en uso por otra App.")

