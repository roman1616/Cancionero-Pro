import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Guía visual Bicolor) ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 1.6 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        background-image: linear-gradient(#ffffff 50%, #f0f7ff 50%) !important;
        background-size: 100% 51.2px !important;
        background-attachment: local !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO (Session State) ---
# Usamos una sola fuente de verdad para el texto
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

def procesar_carga_archivo():
    """Callback que lee el archivo y lo inyecta en el estado del editor."""
    if st.session_state.uploader_key is not None:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        # Inyectamos el texto directamente en la KEY del editor para que aparezca
        st.session_state.editor_interactivo = contenido
        st.session_state.texto_maestro = contenido

# --- INTERFAZ ---
st.title("🎸 Editor Transpositor")
st.markdown("Instrucciones: Renglón **Blanco = Notas** | Renglón **Azul = Letra**")

# Cargador de archivos con Callback crítico
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=procesar_carga_archivo)

# Cálculo de altura para evitar scroll interno
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_dinamica = max(300, n_lineas * 26 + 40)

# Editor: La 'key' debe estar sincronizada con el estado para mostrar el contenido subido
texto_area = st.text_area(
    "Contenido del editor:",
    height=altura_dinamica,
    key="editor_interactivo" # Esta key permite que procesar_carga_archivo() escriba aquí
)

# Sincronizamos el estado con cualquier edición manual
st.session_state.texto_maestro = texto_area

# --- ACCIONES Y BOTONES ---
st.divider()
col1, col2, col3 = st.columns(3)

# Botón 1: Solo procesa la previsualización si se pulsa
btn_previsualizar = col1.button("👁️ Previsualizar Notas", use_container_width=True)

# Botón 2: Limpiar todo
if col2.button("🗑️ Limpiar Todo", use_container_width=True):
    st.session_state.texto_maestro = ""
    st.session_state.editor_interactivo = ""
    st.rerun()

# Lógica de conversión para Descarga y Previsualización
if st.session_state.texto_maestro:
    lineas = st.session_state.texto_maestro.split('\n')
    resultado_final = []
    
    for i, linea in enumerate(lineas):
        if (i + 1) % 2 != 0: # Impar: Notas
            notas_c = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
            resultado_final.append(notas_c)
        else: # Par: Letra
            resultado_final.append(linea)
    
    # Botón 3: Descarga (Siempre disponible si hay texto)
    col3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_cifrada.txt",
        mime="text/plain",
        use_container_width=True
    )

    # Mostrar previsualización solo bajo demanda
    if btn_previsualizar:
        st.subheader("Resultado de la Transposición:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if (i + 1) % 2 != 0:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    st.text(linea)
