import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Bicolor para guiar Notas/Letra) ---
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

# --- GESTIÓN DE ESTADO ---
if "texto_editor" not in st.session_state:
    st.session_state.texto_editor = ""

def al_subir_archivo():
    if st.session_state.uploader_key:
        # Leemos el archivo y actualizamos el estado
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.texto_editor = contenido

# --- INTERFAZ ---
st.title("🎸 Editor de Canciones")
st.markdown("Renglón **Blanco = Notas** | Renglón **Azul = Letra**")

# Cargador de archivos (Callback para carga inmediata)
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_subir_archivo)

# Cálculo de altura dinámica para evitar scroll dentro del cuadro
n_lineas = max(len(st.session_state.texto_editor.split("\n")), 1)
altura_dinamica = max(300, n_lineas * 26 + 40)

# Editor de texto: vinculado a la sesión para que se llene al subir el archivo
texto_input = st.text_area(
    "Edita tu contenido aquí:",
    value=st.session_state.texto_editor,
    height=altura_dinamica,
    key="area_edicion"
)

# Actualizamos el estado con lo que se escriba
st.session_state.texto_editor = texto_input

# --- ACCIONES ---
st.divider()
col1, col2, col3 = st.columns(3)

# Botón para PROCESAR y ver la previsualización (Solo se ve si pulsas aquí)
ver_previsualizacion = col1.button("👁️ Previsualizar Notas", use_container_width=True)

if col2.button("🗑️ Limpiar Todo", use_container_width=True):
    st.session_state.texto_editor = ""
    st.rerun()

# Lógica de Procesamiento para Descarga y Previsualización
if st.session_state.texto_editor:
    lineas = st.session_state.texto_editor.split('\n')
    resultado_procesado = []
    
    for i, linea in enumerate(lineas):
        if (i + 1) % 2 != 0: # Renglón IMPAR: Notas
            notas_conv = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
            resultado_procesado.append(notas_conv)
        else: # Renglón PAR: Letra
            resultado_procesado.append(linea)
    
    texto_final = "\n".join(resultado_procesado)

    # Botón de Descarga
    col3.download_button(
        label="💾 Descargar TXT",
        data=texto_final,
        file_name="cancion_cifrada.txt",
        mime="text/plain",
        use_container_width=True
    )

    # Mostrar previsualización solo si se pulsó el botón
    if ver_previsualizacion:
        st.subheader("Resultado del Cifrado:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_procesado):
                if (i + 1) % 2 != 0:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    st.text(linea)
