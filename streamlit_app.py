import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="centered")

# Diccionario de cifrado americano
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- GESTIÓN DE ESTADO ---
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = True

if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

# --- FUNCIONES ---
def al_subir_archivo():
    if st.session_state.uploader_key:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.texto_maestro = contenido
        # Actualizamos la key del editor para que se refresque visualmente
        if "editor_interactivo" in st.session_state:
            st.session_state.editor_interactivo = contenido

# --- CSS DINÁMICO SEGÚN TEMA ---
if st.session_state.tema_oscuro:
    bg_color_1 = "#1E1E1E" # Gris (Notas)
    bg_color_2 = "#252A34" # Azul Oscuro (Letra)
    text_color = "#FFFFFF" # Blanco
else:
    bg_color_1 = "#FFFFFF" # Blanco (Notas)
    bg_color_2 = "#F0F7FF" # Azul Claro (Letra)
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
    }}
    </style>
    """, unsafe_allow_html=True)

# --- INTERFAZ ---
col_t1, col_t2 = st.columns([0.7, 0.3])
with col_t1:
    st.title("🎸 Editor Musical Pro")
with col_t2:
    # Corrección del error: st.button no usa on_change de esta forma
    label_tema = "☀️ Modo Claro" if st.session_state.tema_oscuro else "🌙 Modo Oscuro"
    if st.button(label_tema, use_container_width=True):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun() # Forzamos recarga para aplicar el nuevo CSS

# Cargador de archivos
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir_archivo)

# Cálculo de altura
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_fija = (n_lineas * 32) + 20

# Editor principal
# Usamos 'key' para que el callback de carga pueda escribir aquí
texto_editado = st.text_area(
    "Editor:",
    height=altura_fija,
    key="editor_interactivo",
    value=st.session_state.texto_maestro,
    label_visibility="collapsed"
)

# Sincronización del texto editado
st.session_state.texto_maestro = texto_editado

# --- ACCIONES ---
st.divider()
c1, c2, c3 = st.columns(3)

btn_prev = c1.button("👁️ Previsualizar", use_container_width=True)

if c2.button("🗑️ Limpiar Todo", use_container_width=True):
    st.session_state.texto_maestro = ""
    # También debemos limpiar el valor de la key del widget
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
        file_name="cancion_transpuesta.txt",
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
                    c_prev = "white" if st.session_state.tema_oscuro else "black"
                    st.markdown(f"<span style='color:{c_prev}'>{linea}</span>", unsafe_allow_html=True)
