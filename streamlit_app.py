import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="centered")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- GESTIÓN DE ESTADO ---
if "tema_oscuro" not in st.session_state:
    st.session_state.tema_oscuro = True # Oscuro por defecto

if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""

# --- FUNCIONES ---
def al_subir_archivo():
    if st.session_state.uploader_key:
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.texto_maestro = contenido
        st.session_state.editor_interactivo = contenido

# --- CSS GLOBAL DINÁMICO ---
if st.session_state.tema_oscuro:
    main_bg = "#0E1117"        # Fondo oscuro oficial de Streamlit
    text_color = "#FFFFFF"     # Texto blanco
    card_bg = "#1E1E1E"        # Notas (Gris oscuro)
    card_bg_alt = "#252A34"    # Letra (Azul profundo)
    border_color = "#31333F"
else:
    main_bg = "#FFFFFF"        # Fondo blanco
    text_color = "#000000"     # Texto negro
    card_bg = "#FFFFFF"        # Notas (Blanco)
    card_bg_alt = "#F0F7FF"    # Letra (Azul muy claro)
    border_color = "#E6EAF1"

st.markdown(f"""
    <style>
    /* Estilo para toda la aplicación */
    .stApp {{
        background-color: {main_bg};
        color: {text_color};
    }}
    
    /* Estilo para el Editor */
    .stTextArea textarea {{
        line-height: 32px !important; 
        font-family: 'Courier New', monospace !important;
        font-size: 18px !important;
        color: {text_color} !important;
        -webkit-text-fill-color: {text_color} !important;
        background-image: linear-gradient({card_bg} 50%, {card_bg_alt} 50%) !important;
        background-size: 100% 64px !important;
        background-attachment: local !important;
        border: 1px solid {border_color} !important;
    }}

    /* Ajustar títulos y textos secundarios */
    h1, h2, h3, p, span, label {{
        color: {text_color} !important;
    }}
    </style>
    """, unsafe_allow_html=True)

# --- INTERFAZ ---
col_head, col_switch = st.columns([0.7, 0.3])
with col_head:
    st.title("🎸 Transpositor 2026")
with col_switch:
    # Botón de cambio de tema global
    label_btn = "☀️ Modo Claro" if st.session_state.tema_oscuro else "🌙 Modo Oscuro"
    if st.button(label_btn, use_container_width=True):
        st.session_state.tema_oscuro = not st.session_state.tema_oscuro
        st.rerun()

# Cargador
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_subir_archivo)

# Altura dinámica del editor
n_lineas = max(len(st.session_state.texto_maestro.split("\n")), 1)
altura_fija = (n_lineas * 32) + 20

# Editor
st.session_state.texto_maestro = st.text_area(
    "Editor",
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

    # Descarga
    c3.download_button(
        label="💾 Descargar TXT",
        data="\n".join(resultado_final),
        file_name="cancion_cifrada.txt",
        mime="text/plain",
        use_container_width=True
    )

    # Previsualización
    if btn_prev:
        st.subheader("Resultado:")
        with st.container(border=True):
            for i, linea in enumerate(resultado_final):
                if (i + 1) % 2 != 0:
                    st.markdown(f"**`:blue[{linea}]`**")
                else:
                    color_txt = "white" if st.session_state.tema_oscuro else "black"
                    st.markdown(f"<span style='color:{color_txt}'>{linea}</span>", unsafe_allow_html=True)
