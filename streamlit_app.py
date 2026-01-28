import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Clasificador Musical 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- GESTIÓN DE ESTADO ---
if "texto_bruto" not in st.session_state:
    st.session_state.texto_bruto = ""
if "mostrar_clasificador" not in st.session_state:
    st.session_state.mostrar_clasificador = False

# --- CSS PARA MODO OSCURO ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .linea-contenedor { display: flex; align-items: center; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA DE ARCHIVO ---
def al_cargar():
    if st.session_state.uploader_key:
        st.session_state.texto_bruto = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.mostrar_clasificador = True

st.title("🎸 Clasificador de Notas y Letras")
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_cargar)

# Editor inicial
st.session_state.texto_bruto = st.text_area(
    "Pega o edita el texto aquí:",
    value=st.session_state.texto_bruto,
    height=200,
    key="editor_inicial"
)

if st.button("🔍 Clasificar Oraciones"):
    st.session_state.mostrar_clasificador = True

# --- PANEL DE CLASIFICACIÓN (Lo que buscabas) ---
if st.session_state.mostrar_clasificador and st.session_state.texto_bruto:
    st.divider()
    st.subheader("Selecciona las líneas que son NOTAS:")
    
    lineas = [l.strip() for l in st.session_state.texto_bruto.split('\n') if l.strip()]
    decisiones = []

    # Se muestra cada oración con su check ANTES de procesar
    for i, oracion in enumerate(lineas):
        # Creamos una fila visual para cada oración
        col_check, col_texto = st.columns([0.1, 0.9])
        with col_check:
            es_nota = st.checkbox("", value=((i+1)%2!=0), key=f"check_{i}")
        with col_texto:
            st.markdown(f"**{oracion}**")
        
        decisiones.append((oracion, es_nota))

    # --- RESULTADO FINAL ---
    st.divider()
    if st.button("⚙️ Procesar y Generar Cifrado"):
        resultado_final = []
        for texto, marca_nota in decisiones:
            if marca_nota:
                palabras = texto.split()
                # Conversión estricta con diccionario
                procesada = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in palabras])
                resultado_final.append(procesada)
            else:
                resultado_final.append(texto)
        
        texto_unido = "\n".join(resultado_final)
        
        st.success("¡Cifrado generado!")
        st.code(texto_unido, language=None)
        
        st.download_button(
            label="💾 Descargar TXT Final",
            data=texto_unido,
            file_name="cancion_cifrada.txt",
            use_container_width=True
        )

if st.button("🗑️ Limpiar Todo"):
    st.session_state.texto_bruto = ""
    st.session_state.mostrar_clasificador = False
    st.rerun()
