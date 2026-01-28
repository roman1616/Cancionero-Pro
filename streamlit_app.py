import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Dark 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

# --- CSS ACTUALIZADO (Scroll + Sombra) ---
bg_color_1 = "#1E1E1E" 
bg_color_2 = "#252A34" 
text_color = "#FFFFFF" 

st.markdown(f"""
    <style>
    /* Contenedor del área de texto para forzar scroll lateral */
    .stTextArea div[data-baseweb="textarea"] {{
        overflow-x: auto !important;
        background: 
            linear-gradient(to right, {bg_color_1} 30%, rgba(255,255,255,0)),
            linear-gradient(to right, rgba(255,255,255,0), {bg_color_1} 70%) 0 100%,
            radial-gradient(farthest-side at 100% 50%, rgba(0,0,0,0.4), rgba(0,0,0,0)) !important;
        background-repeat: no-repeat !important;
        background-size: 40px 100%, 40px 100%, 14px 100% !important;
        background-position: 0 0, 100% 0, 100% 0 !important;
        background-attachment: local, local, scroll !important;
    }}

    .stTextArea textarea {{
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        width: 1500px !important; /* Ancho extendido para evitar saltos de línea */
        white-space: pre !important;
        overflow-wrap: normal !important;
        background-image: linear-gradient({bg_color_1} 50%, {bg_color_2} 50%) !important;
        background-size: 100% 64px !important;
        background-attachment: local !important;
        border: none !important;
    }}
    
    /* Personalización barra de scroll */
    .stTextArea div[data-baseweb="textarea"]::-webkit-scrollbar {{
        height: 6px;
    }}
    .stTextArea div[data-baseweb="textarea"]::-webkit-scrollbar-thumb {{
        background: #444;
        border-radius: 10px;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def al_subir_archivo():
    if st.session_state.uploader_key:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.texto_maestro = contenido
        st.session_state.editor_interactivo = contenido

# --- INTERFAZ ---
st.title("🎸 Editor Transpositor 2026")
st.markdown(f"Guía: **Renglón Gris = Notas** | **Renglón Azul = Letra** (Scroll lateral activo)")

st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir_archivo)

n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_fija = (n_lineas * 32) + 40

st.session_state.texto_maestro = st.text_area(
    "Editor:",
    height=altura_fija,
    key="editor_interactivo",
    value=st.session_state.texto_maestro,
    label_visibility="collapsed"
)

# --- ACCIONES ---
st.divider()
c1, c2, c3 = st.columns(3)
btn_prev = c1.button("👁️ Previsualizar", use_container_width=True)

if c2.button("🗑️ Limpiar Todo", use_container_width=True):
    st.session_state.texto_maestro = ""
    if "editor_interactivo" in st.session_state:
        st.session_state.editor_interactivo = ""
    st.rerun()

if st.session_state.texto_maestro:
    lineas = st.session_state.texto_maestro.split('\n')
    resultado_final = []
    
    for i, linea in enumerate(lineas):
        if (i + 1) % 2 != 0: # Notas
            notas_c = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
            resultado_final.append(notas_c)
        else: # Letra
            resultado_final.append(linea)

    c3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_2026.txt",
        mime="text/plain",
        use_container_width=True
    )

    if btn_prev:
        st.subheader("Previsualización:")
        # Aplicamos el mismo estilo de scroll a la previsualización
        preview_html = "".join([f"<div style='color:{'#58a6ff' if (i+1)%2!=0 else 'white'}; font-weight:{'bold' if (i+1)%2!=0 else 'normal'};'>{linea}</div>" for i, linea in enumerate(resultado_final)])
        st.markdown(f"""
            <div style="overflow-x: auto; white-space: pre; font-family: 'Courier New'; background: #111; padding: 20px; border-radius: 10px;">
                {preview_html}
            </div>
            """, unsafe_allow_html=True)
