import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Alineación Absoluta Bicolor) ---
st.markdown("""
    <style>
    /* Forzamos que cada renglón mida exactamente 32px */
    .stTextArea textarea {
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        /* Fondo: Blanco (32px) y Azul (32px) */
        background-image: linear-gradient(#ffffff 50%, #f0f7ff 50%) !important;
        background-size: 100% 64px !important;
        background-attachment: local !important;
        background-position: 0 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

def al_subir_archivo():
    if st.session_state.uploader_key is not None:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        # Inyectamos el texto directamente en el estado del widget
        st.session_state.editor_interactivo = contenido
        st.session_state.texto_maestro = contenido

# --- INTERFAZ ---
st.title("🎸 Editor de Notas y Letras")
st.markdown("Instrucciones: **Blanco = Notas** | **Azul = Letra**")

# Cargador de archivos
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_subir_archivo)

# Cálculo de líneas para altura dinámica
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_fija = (n_lineas * 32) + 20 # 32px por cada renglón

# EDITOR: Vinculado a la memoria para carga inmediata
texto_area = st.text_area(
    "Editor:",
    height=altura_fija,
    key="editor_interactivo"
)

# Sincronización manual
st.session_state.texto_maestro = texto_area

# --- ACCIONES ---
st.divider()
col1, col2, col3 = st.columns(3)

btn_prev = col1.button("👁️ Previsualizar", use_container_width=True)

if col2.button("🗑️ Limpiar Todo", use_container_width=True):
    st.session_state.texto_maestro = ""
    st.session_state.editor_interactivo = ""
    st.rerun()

if st.session_state.texto_maestro:
    lineas = st.session_state.texto_maestro.split('\n')
    resultado_final = []
    
    for i, linea in enumerate(lineas):
        if (i + 1) % 2 != 0: # IMPAR: Notas
            notas_c = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
            resultado_final.append(notas_c)
        else: # PAR: Letra
            resultado_final.append(linea)

    # Botón Descarga
    col3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_2026.txt",
        mime="text/plain",
        use_container_width=True
    )

    # Vista previa bajo demanda
    if btn_prev:
        st.subheader("Previsualización:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if (i + 1) % 2 != 0:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    st.markdown(f"<span style='color:black'>{linea}</span>", unsafe_allow_html=True)
