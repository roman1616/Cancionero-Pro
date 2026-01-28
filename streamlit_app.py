import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Pro 2026", layout="centered")

# Diccionario de cifrado americano (Standard 2026)
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# --- MEJORA: VALIDACIÓN DE NOTAS ---
# Solo convertimos si la palabra es EXACTAMENTE una nota conocida.
# Esto evita que palabras como "Dime" (empieza por Di) o "Solo" (empieza por Sol) se rompan.
def procesar_renglon_notas(linea):
    palabras = linea.split()
    resultado = []
    for p in palabras:
        p_clean = p.upper().strip(".,!?()") # Limpieza básica de puntuación
        # Si la palabra está en nuestro diccionario, la convertimos; si no, la dejamos igual
        resultado.append(CONVERSION.get(p_clean, p))
    return "   ".join(resultado)

# --- ESTILO CSS DARK PRO ---
st.markdown("""
    <style>
    .stTextArea textarea {
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        padding-top: 0px !important;
        background-image: linear-gradient(#1E1E1E 50%, #252A34 50%) !important;
        background-size: 100% 64px !important;
        background-attachment: local !important;
        border: 1px solid #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

def al_subir():
    if st.session_state.uploader_key:
        st.session_state.texto_maestro = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.editor_interactivo = st.session_state.texto_maestro

# --- INTERFAZ ---
st.title("🎸 Editor Transpositor 2026")
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir)

# Altura dinámica
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_fija = (n_lineas * 32) + 20

st.session_state.texto_maestro = st.text_area(
    "Editor:", height=altura_fija, key="editor_interactivo",
    value=st.session_state.texto_maestro, label_visibility="collapsed"
)

# --- ACCIONES ---
st.divider()
c1, c2, c3 = st.columns(3)
btn_prev = c1.button("👁️ Previsualizar", use_container_width=True)

if c2.button("🗑️ Limpiar Todo", use_container_width=True):
    st.session_state.texto_maestro = ""
    st.session_state.editor_interactivo = ""
    st.rerun()

if st.session_state.texto_maestro:
    lineas = st.session_state.texto_maestro.split('\n')
    resultado_final = []
    
    for i, linea in enumerate(lineas):
        if (i + 1) % 2 != 0: # Renglón IMPAR: Notas con validación
            resultado_final.append(procesar_renglon_notas(linea))
        else: # Renglón PAR: Letra (se mantiene intacta)
            resultado_final.append(linea)

    c3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_corregida.txt",
        use_container_width=True
    )

    if btn_prev:
        st.subheader("Previsualización:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if (i + 1) % 2 != 0:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    st.markdown(f"<span style='color:white'>{linea}</span>", unsafe_allow_html=True)
