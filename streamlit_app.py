import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Dark 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- GESTIÓN DE TEMA Y ESTADO ---
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = True  # Por defecto oscuro

if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

# --- CSS DINÁMICO SEGÚN TEMA ---
if st.session_state.tema_oscuro:
    bg_color_1 = "#1E1E1E" # Gris casi negro (Notas)
    bg_color_2 = "#252A34" # Azul oscuro profundo (Letra)
    text_color = "#FFFFFF" # Blanco
else:
    bg_color_1 = "#FFFFFF" # Blanco (Notas)
    bg_color_2 = "#F0F7FF" # Azul muy claro (Letra)
    text_color = "#000000" # Negro

st.markdown(f"""
    <style>
    .stTextArea textarea {{
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        padding-top: 0px !important;
        padding-bottom: 0px !important;
        background-image: linear-gradient({bg_color_1} 50%, {bg_color_2} 50%) !important;
        background-size: 100% 64px !important;
        background-attachment: local !important;
        background-position: 0 0 !important;
        border: 1px solid #444 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- FUNCIONES ---
def al_subir_archivo():
    if st.session_state.uploader_key:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.editor_interactivo = contenido
        st.session_state.texto_maestro = contenido

def cambiar_tema():
    st.session_state.tema_oscuro = not st.session_state.tema_oscuro

# --- INTERFAZ ---
col_t1, col_t2 = st.columns([0.8, 0.2])
with col_t1:
    st.title("🎸 Editor Transpositor 2026")
with col_t2:
    label_tema = "☀️ Modo Claro" if st.session_state.tema_oscuro else "🌙 Modo Oscuro"
    st.button(label_tema, on_change=cambiar_tema)

st.markdown(f"Configuración actual: **Renglón 1 ({'Gris' if st.session_state.tema_oscuro else 'Blanco'}) = Notas** | **Renglón 2 ({'Azul' if st.session_state.tema_oscuro else 'Celeste'}) = Letra**")

# Cargador
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir_archivo)

# Altura dinámica
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_fija = (n_lineas * 32) + 20

# Editor
st.session_state.texto_maestro = st.text_area(
    "Editor:",
    height=altura_fija,
    key="editor_interactivo",
    value=st.session_state.texto_maestro
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
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if (i + 1) % 2 != 0:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    color_prev = "white" if st.session_state.tema_oscuro else "black"
                    st.markdown(f"<span style='color:{color_prev}'>{linea}</span>", unsafe_allow_html=True)

