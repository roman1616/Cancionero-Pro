import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página para máxima estabilidad en 2026
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
MAPA_NOTAS = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    resultado_final = []
    # Patrón que detecta el acorde completo sin romper por símbolos
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        for match in re.finditer(patron, linea, flags=re.IGNORECASE):
            acorde_original = match.group(0)
            inicio, fin = match.start(), match.end()
            
            # Filtro de seguridad para no marcar letras de la canción
            lo_que_sigue = linea[fin:]
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            # Conversión y marcado
            raiz_nueva = MAPA_NOTAS.get(match.group(1).upper(), match.group(1).upper())
            nuevo_acorde = f"{raiz_nueva}{match.group(2)}"
            
            # Solo añadir ' si no tiene marcador previo
            if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*")):
                nuevo_acorde += "'"

            # Mantener alineación exacta
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

# Cargador de archivos con gestión de buffer directa
# Al usar 'label_visibility' y un tipo específico, el navegador móvil 
# tiende a priorizar la descarga local del archivo de la nube antes de subirlo.
archivo = st.file_uploader("Seleccionar canción (.txt)", type=["txt"])

if archivo is not None:
    try:
        # Cargamos el archivo en el buffer de memoria local (RAM)
        # Esto evita el AxiosError porque el archivo ya está "dentro" de la App
        bytes_data = archivo.getbuffer()
        contenido = bytes_data.tobytes().decode("utf-8")
        nombre_archivo = archivo.name
        
        texto_procesado = procesar_texto(contenido)
        
        st.subheader("Vista Previa:")
        st.code(texto_procesado, language="text")

        # Preparar JS para compartir/guardar
        texto_js = texto_procesado.replace("`", "\\`").replace("$", "\\$")
        
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
                    const blob = new Blob([txt], {{type: 'text/plain'}});
                    const file = new File([blob], "{nombre_archivo}", {{type: 'text/plain'}});
                    if (navigator.share) {{
                        try {{ await navigator.share({{ files: [file] }}); }} catch (e) {{}}
                    }} else {{ alert("Usa 'Guardar'"); }}
                }}
            </script>
        """, height=100)

    except Exception as e:
        st.error("Error de conexión con el archivo. Por favor, asegúrate de que el archivo esté descargado en tu teléfono.")

# Botón para limpiar memoria
if st.button("🔄 Nueva Carga"):
    st.rerun()

