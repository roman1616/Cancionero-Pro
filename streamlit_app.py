import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Dark 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

# --- CSS: BOTÓN COMPACTO Y EDITOR ---
bg_color_1 = "#1E1E1E" 
bg_color_2 = "#252A34" 
text_color = "#FFFFFF" 
ancho_virtual = "2500px"

st.markdown(f"""
    <style>
    /* 1. ESTILIZAR CARGADOR COMO BOTÓN COMPACTO */
    section[data-testid="stFileUploader"] > label {{ display: none; }} /* Oculta el texto "Browse files" */
    section[data-testid="stFileUploader"] {{
        width: fit-content;
        margin-bottom: -50px;
    }}
    div[data-testid="stFileUploaderDropzone"] {{
        padding: 0 !important;
        border: none !important;
        background: transparent !important;
    }}
    div[data-testid="stFileUploaderDropzone"] > button {{
        width: 100%;
        background-color: #4A4A4A !important;
        color: white !important;
        border-radius: 5px !important;
        padding: 0.5rem 1rem !important;
    }}

    /* 2. EDITOR CON SCROLL Y FONDO SINCRONIZADO */
    .stTextArea div[data-baseweb="textarea"] {{
        overflow-x: auto !important;
        background: 
            linear-gradient(to right, {bg_color_1} 30%, rgba(0,0,0,0)),
            linear-gradient(to right, rgba(0,0,0,0), {bg_color_1} 70%) 100% 0,
            radial-gradient(farthest-side at 0% 50%, rgba(0,0,0,.5), rgba(0,0,0,0)),
            radial-gradient(farthest-side at 100% 50%, rgba(0,0,0,.5), rgba(0,0,0,0)) 100% 0 !important;
        background-repeat: no-repeat !important;
        background-size: 40px 100%, 40px 100%, 14px 100%, 14px 100% !important;
        background-attachment: local, local, scroll, scroll !important;
    }}

    .stTextArea textarea {{
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        width: {ancho_virtual} !important; 
        white-space: pre !important;
        overflow-wrap: normal !important;
        background-image: linear-gradient({bg_color_1} 50%, {bg_color_2} 50%) !important;
        background-size: {ancho_virtual} 64px !important; 
        background-attachment: local !important;
        background-repeat: repeat-y !important;
        border: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- LÓGICA ---
def al_subir_archivo():
    if st.session_state.uploader_key:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.texto_maestro = contenido
        st.session_state.editor_interactivo = contenido

# --- INTERFAZ ---
st.title("🎸 Editor Transpositor 2026")

# Botón de carga compacto (estilizado vía CSS arriba)
st.file_uploader("Subir", type=["txt"], key="uploader_key", on_change=al_subir_archivo, label_visibility="collapsed")

# Altura y Editor
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_fija = (n_lineas * 32) + 20

st.session_state.texto_maestro = st.text_area(
    "Editor:",
    height=altura_fija,
    key="editor_interactivo",
    value=st.session_state.texto_maestro,
    label_visibility="collapsed"
)

# Botones de Acción
st.divider()
c1, c2, c3 = st.columns(3)

if c1.button("👁️ Previsualizar", use_container_width=True):
    st.session_state.show_preview = True
else:
    st.session_state.show_preview = False

if c2.button("🗑️ Limpiar", use_container_width=True):
    st.session_state.texto_maestro = ""
    st.rerun()

# Procesamiento para descarga
if st.session_state.texto_maestro:
    lineas = st.session_state.texto_maestro.split('\n')
    resultado_final = []
    for i, linea in enumerate(lineas):
        if (i + 1) % 2 != 0:
            notas = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
            resultado_final.append(notas)
        else:
            resultado_final.append(linea)

    c3.download_button("💾 Descargar", "\n".join(resultado_final), "cancion.txt", use_container_width=True)

    if st.session_state.show_preview:
        st.subheader("Vista de Ensayo")
        preview_html = "".join([f"<div style='background-color:{bg_color_1 if (i+1)%2!=0 else bg_color_2}; color:white; min-width:{ancho_virtual}; padding: 2px 10px; white-space: pre; font-family: monospace;'>{linea if linea.strip() else '&nbsp;'}</div>" for i, linea in enumerate(resultado_final)])
        st.markdown(f'<div style="overflow-x: auto; border-radius: 8px; border: 1px solid #444;">{preview_html}</div>', unsafe_allow_html=True)

