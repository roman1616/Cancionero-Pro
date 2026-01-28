import streamlit as st

# 1. Configuración de la aplicación
st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

# Diccionario de cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# Notas que pueden ser texto común
AMBIGUAS = ["SOL", "LA", "SI", "DO", "RE"]

# --- ESTILO CSS (Modo Oscuro y Alerta Naranja) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .alerta-naranja {
        background-color: #FFA500;
        padding: 15px;
        border-radius: 8px;
        color: #000000 !important;
        font-weight: bold;
        margin-bottom: 10px;
        border: 2px solid #CC8400;
    }
    .renglon-ok {
        padding: 10px;
        border-bottom: 1px solid #31333F;
    }
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        font-family: 'Courier New', monospace !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""
if "fase_analisis" not in st.session_state:
    st.session_state.fase_analisis = False

def al_cargar():
    if st.session_state.uploader:
        st.session_state.texto_maestro = st.session_state.uploader.read().decode("utf-8")
        st.session_state.fase_analisis = True

# --- INTERFAZ ---
st.title("🎸 Transpositor con Detector de Coincidencias")

# Cargador de archivos
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader", on_change=al_cargar)

# Editor Inicial
st.session_state.texto_maestro = st.text_area(
    "1. Edita el texto original:",
    value=st.session_state.texto_maestro,
    height=200,
    key="editor_raw"
)

if st.button("🔍 Analizar Coincidencias"):
    st.session_state.fase_analisis = True

# --- PANEL DE VALIDACIÓN (HISTORIAL RESCATADO) ---
if st.session_state.fase_analisis and st.session_state.texto_maestro:
    st.divider()
    st.subheader("2. Validación de Oraciones y Posibles Errores")
    
    lineas = st.session_state.texto_maestro.split('\n')
    decisiones = []

    for i, linea in enumerate(lineas):
        if not linea.strip(): continue
        
        palabras = linea.upper().split()
        notas_encontradas = [p for p in palabras if p in CONVERSION]
        notas_dudosas = [p for p in palabras if p in AMBIGUAS]
        
        # Lógica de Alerta Naranja:
        es_impar = (i + 1) % 2 != 0
        hay_conflicto = (not es_impar and len(notas_encontradas) > 0) or \
                        (es_impar and len(notas_encontradas) == len(notas_dudosas) and len(notas_dudosas) > 0)
        
        col_chk, col_txt = st.columns([0.08, 0.92])
        
        with col_chk:
            # Checkbox de confirmación manual
            es_nota = st.checkbox("", value=es_impar, key=f"check_{i}")
        
        with col_txt:
            if hay_conflicto:
                # Mensaje de advertencia específico
                st.markdown(f'''
                    <div class="alerta-naranja">
                        ⚠️ Se ha detectado una posible coincidencia entre texto y notas musicales en el renglón {i+1}.<br>
                        "{linea}"
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="renglon-ok">{linea}</div>', unsafe_allow_html=True)
        
        decisiones.append((linea, es_nota))

    # --- ACCIONES FINALES ---
    st.divider()
    if st.button("🚀 Generar Cifrado Final"):
        resultado = []
        for txt, marcar_como_nota in decisiones:
            if marcar_como_nota:
                pals = txt.split()
                # Conversión estricta mediante el diccionario
                conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in pals])
                resultado.append(conv)
            else:
                resultado.append(txt)
        
        texto_unido = "\n".join(resultado)
        st.success("¡Procesamiento finalizado con éxito!")
        st.code(texto_unido, language=None)
        
        st.download_button(
            label="💾 Descargar TXT Validado",
            data=texto_unido,
            file_name="cancion_corregida.txt",
            mime="text/plain",
            use_container_width=True
        )

if st.button("🗑️ Reiniciar"):
    st.session_state.texto_maestro = ""
    st.session_state.fase_analisis = False
    st.rerun()
