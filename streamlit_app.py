import streamlit as st
import re

# Configuración
st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

# Diccionario de conversión
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def limpiar_linea(linea):
    """Elimina cualquier número de línea previo (ej: '1 | ')"""
    return re.sub(r'^\d+\s\|\s', '', linea)

def numerar_texto(texto):
    """Añade o actualiza la numeración '1 | ', '2 | ' en cada renglón."""
    lineas = texto.split('\n')
    return "\n".join([f"{i+1:02d} | {limpiar_linea(l)}" for i, l in enumerate(lineas)])

def convertir_notas(linea):
    """Limpia el prefijo y convierte notas."""
    contenido = limpiar_linea(linea)
    palabras = contenido.upper().split()
    return "   ".join([CONVERSION.get(p, p) for p in palabras])

# --- LÓGICA DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = "01 | "

def al_subir():
    if st.session_state.uploader:
        contenido = st.session_state.uploader.read().decode("utf-8")
        st.session_state.texto_maestro = numerar_texto(contenido)

# --- INTERFAZ ---
st.title("🎸 Editor Musical Sincronizado")
st.markdown("Escribe tus notas en los renglones **impares** y la letra en los **pares**.")

st.file_uploader("Cargar archivo .txt", type=["txt"], key="uploader", on_change=al_subir)

# Editor con números inyectados
# Al usar el mismo prefijo '01 | ', los números se mueven con el texto
texto_input = st.text_area(
    "Cuadro de Edición (Los números se mantienen con el texto):",
    value=st.session_state.texto_maestro,
    height=400,
    key="editor_key"
)

# Botón para actualizar/reordenar la numeración si se descuadra al borrar
if st.button("🔢 Re-numerar Renglones"):
    st.session_state.texto_maestro = numerar_texto(texto_input)
    st.rerun()

# --- PREVISUALIZACIÓN ---
if texto_input:
    st.divider()
    st.subheader("👁️ Resultado Final (Cifrado Americano)")
    
    lineas = texto_input.split('\n')
    resultado_descarga = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            num_actual = i + 1
            if num_actual % 2 != 0: # NOTAS (Impar)
                notas_c = convertir_notas(linea)
                resultado_descarga.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # LETRA (Par)
                letra_c = limpiar_linea(linea)
                resultado_descarga.append(letra_c)
                st.text(letra_c)

    # --- DESCARGA ---
    st.divider()
    if st.download_button(
        label="💾 Descargar Canción (Sin números)",
        data="\n".join(resultado_descarga),
        file_name="cancion_2026.txt",
        mime="text/plain"
    ):
        st.success("¡Archivo descargado con éxito!")
