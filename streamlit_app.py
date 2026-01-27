import streamlit as st
import re

# Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# Diccionario de conversión
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# --- FUNCIONES DE LÓGICA ---
def limpiar_prefijo(linea):
    """Elimina el número de línea '01 | ' para procesar el texto."""
    return re.sub(r'^\d+\s\|\s', '', linea)

def numerar_texto(texto):
    """Añade prefijos numéricos a cada renglón."""
    lineas = texto.split('\n')
    return "\n".join([f"{i+1:02d} | {limpiar_prefijo(l)}" for i, l in enumerate(lineas)])

def convertir_notas(linea):
    """Limpia y convierte notas a cifrado americano."""
    contenido = limpiar_prefijo(linea)
    palabras = contenido.upper().split()
    return "   ".join([CONVERSION.get(p, p) for p in palabras])

# --- GESTIÓN DE ESTADO ---
# Inicializamos el estado si no existe
if "editor_content" not in st.session_state:
    st.session_state.editor_content = "01 | "

def procesar_archivo():
    """Callback que inyecta el archivo en el editor al subirlo."""
    if st.session_state.uploader_key is not None:
        contenido_raw = st.session_state.uploader_key.read().decode("utf-8")
        # Inyectamos el texto numerado directamente en el estado del editor
        st.session_state.editor_content = numerar_texto(contenido_raw)

# --- INTERFAZ DE USUARIO ---
st.title("🎸 Editor Transpositor Sincronizado")

# 1. Cargador de archivos con Callback crítico
st.file_uploader(
    "Sube tu archivo .txt", 
    type=["txt"], 
    key="uploader_key", 
    on_change=procesar_archivo
)

# 2. Área de Edición
# IMPORTANTE: Usamos 'key' vinculada al session_state para sincronización total
texto_input = st.text_area(
    "Cuadro de Edición (Renglones automáticos):",
    height=400,
    key="editor_content"
)

# Botón para reordenar números si se descuadran al editar manualmente
if st.button("🔢 Corregir Numeración"):
    st.session_state.editor_content = numerar_texto(texto_input)
    st.rerun()

# 3. Previsualización y Procesamiento
if texto_input:
    st.divider()
    st.subheader("👁️ Previsualización Final (Sin números)")
    
    lineas = texto_input.split('\n')
    resultado_limpio = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            idx = i + 1
            if idx % 2 != 0: # IMPAR: Notas
                notas_c = convertir_notas(linea)
                resultado_limpio.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # PAR: Letra
                letra_l = limpiar_prefijo(linea)
                resultado_limpio.append(letra_l)
                st.text(letra_l)

    # 4. Exportación
    st.divider()
    st.download_button(
        label="💾 Descargar TXT (Limpio)",
        data="\n".join(resultado_limpio),
        file_name="cancion_cifrada.txt",
        mime="text/plain",
        use_container_width=True
    )

