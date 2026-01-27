import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Transpositor Musical 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Bicolor y Sin Scroll) ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 1.6 !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        background-image: linear-gradient(#ffffff 50%, #f0f7ff 50%) !important;
        background-size: 100% 51.2px !important;
        background-attachment: local !important;
        padding-top: 10px !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto" not in st.session_state:
    st.session_state.texto = ""

def al_subir_archivo():
    if st.session_state.archivo_subido:
        # Leemos el archivo y actualizamos el estado
        contenido = st.session_state.archivo_subido.read().decode("utf-8")
        st.session_state.texto = contenido

# --- INTERFAZ ---
st.title("🎸 Transpositor de Notas")
st.markdown("Instrucciones: Renglón **Blanco = Notas** | Renglón **Azul = Letra**")

# Cargador de archivos
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="archivo_subido", on_change=al_subir_archivo)

# Cálculo de altura dinámica para evitar scroll dentro del cuadro
n_lineas = max(len(st.session_state.texto.split("\n")), 1)
altura_dinamica = max(300, n_lineas * 26 + 40)

# Editor de texto (Sin key para evitar conflictos con el value al cargar archivos)
texto_actual = st.text_area(
    "Editor de canción:",
    value=st.session_state.texto,
    height=altura_dinamica,
    help="Edita aquí tu música directamente."
)

# Sincronizamos el cambio manual
st.session_state.texto = texto_actual

# --- PREVISUALIZACIÓN Y PROCESAMIENTO ---
if st.session_state.texto:
    st.divider()
    st.subheader("👁️ Previsualización (Notas Convertidas)")
    
    lineas = st.session_state.texto.split('\n')
    resultado_final = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            if (i + 1) % 2 != 0: # IMPAR: Notas
                # Convertimos las notas detectadas en el renglón
                notas_convertidas = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
                resultado_final.append(notas_convertidas)
                st.markdown(f"**`:blue[{notas_convertidas}]`**")
            else: # PAR: Letra
                resultado_final.append(linea)
                st.text(linea)

    # --- BOTONES DE SALIDA ---
    st.divider()
    col1, col2 = st.columns(2)
    
    col1.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_final.txt",
        mime="text/plain",
        use_container_width=True
    )
    
    if col2.button("🗑️ Limpiar Todo", use_container_width=True):
        st.session_state.texto = ""
        st.rerun()
