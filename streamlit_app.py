import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Fuerza Letra Negra y Fondo Bicolor) ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 1.6 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        color: #000000 !important; /* Fuerza color de letra negro */
        -webkit-text-fill-color: #000000 !important; /* Asegura visibilidad en Safari/Chrome */
        background-image: linear-gradient(#ffffff 50%, #f0f7ff 50%) !important;
        background-size: 100% 51.2px !important;
        background-attachment: local !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

def procesar_carga_archivo():
    """Lee el archivo e inyecta el contenido en el editor inmediatamente."""
    if st.session_state.uploader_key is not None:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        # Actualizamos la key del widget y la variable de estado
        st.session_state.editor_key = contenido
        st.session_state.texto_maestro = contenido

# --- INTERFAZ ---
st.title("🎸 Editor de Notas y Letras")
st.markdown("Guía visual: Renglón **Blanco = Notas** | Renglón **Azul = Letra**")

# Cargador de archivos
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=procesar_carga_archivo)

# Altura dinámica para evitar scroll
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_dinamica = max(300, n_lineas * 26 + 40)

# EDITOR: Vinculado a 'editor_key' para que el contenido subido sea visible
texto_area = st.text_area(
    "Editor de contenido:",
    height=altura_dinamica,
    key="editor_key"
)

# Sincronizamos el estado con lo escrito manualmente
st.session_state.texto_maestro = texto_area

# --- ACCIONES ---
st.divider()
col1, col2, col3 = st.columns(3)

btn_previsualizar = col1.button("👁️ Previsualizar", use_container_width=True)

if col2.button("🗑️ Limpiar Todo", use_container_width=True):
    st.session_state.texto_maestro = ""
    st.session_state.editor_key = ""
    st.rerun()

# Lógica de procesamiento
if st.session_state.texto_maestro:
    lineas = st.session_state.texto_maestro.split('\n')
    resultado_final = []
    
    for i, linea in enumerate(lineas):
        if (i + 1) % 2 != 0: # Impar: Notas
            notas_c = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
            resultado_final.append(notas_c)
        else: # Par: Letra
            resultado_final.append(linea)
    
    # Botón de Descarga
    col3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_cifrada.txt",
        mime="text/plain",
        use_container_width=True
    )

    # Mostrar previsualización solo bajo demanda
    if btn_previsualizar:
        st.subheader("Resultado Transpuesto:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if (i + 1) % 2 != 0:
                    st.markdown(f"**`:blue[{linea}]`**") # Notas en azul en la vista previa
                else:
                    st.markdown(f"<span style='color:black'>{linea}</span>", unsafe_allow_html=True) # Letra en negro

