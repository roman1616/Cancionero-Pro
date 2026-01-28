import streamlit as st

# 1. Configuración original
st.set_page_config(page_title="Editor Musical Pro", layout="wide")

# Diccionario de cifrado del historial
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS ORIGINAL (Rescatado) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .alerta-naranja {
        background-color: #FFA500;
        padding: 15px;
        border-radius: 8px;
        color: black !important;
        font-weight: bold;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- ESTADO DE SESIÓN (Persistencia de datos) ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""
if "ver_analisis" not in st.session_state:
    st.session_state.ver_analisis = False

# --- FUNCIÓN DE CARGA ---
def al_cargar():
    if st.session_state.uploader_key:
        st.session_state.texto_maestro = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.ver_analisis = False

# --- INTERFAZ ---
st.title("🎸 Transpositor con Detector de Coincidencias")

# Cargador
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_cargar)

# Editor (Muestra el contenido del txt o lo que escribas)
st.session_state.texto_maestro = st.text_area(
    "1. Edita el texto original:",
    value=st.session_state.texto_maestro,
    height=250,
    key="editor_raw"
)

if st.button("🔍 Analizar Coincidencias"):
    st.session_state.ver_analisis = True

# --- PANEL DE VALIDACIÓN CON ALERTA NARANJA ---
if st.session_state.ver_analisis and st.session_state.texto_maestro:
    st.divider()
    st.subheader("2. Validación de Oraciones")
    
    lineas = st.session_state.texto_maestro.split('\n')
    decisiones = []

    for i, linea in enumerate(lineas):
        if not linea.strip(): 
            decisiones.append(("", False))
            continue
        
        palabras = linea.upper().split()
        notas_detectadas = [p for p in palabras if p in CONVERSION]
        
        # Lógica de conflicto original
        es_impar = (i + 1) % 2 != 0
        hay_conflicto = (es_impar and not notas_detectadas) or (not es_impar and notas_detectadas)
        
        col_check, col_texto = st.columns([0.08, 0.92])
        
        with col_check:
            es_nota = st.checkbox("", value=es_impar, key=f"c_{i}")
        
        with col_texto:
            if hay_conflicto:
                # MENSAJE EXACTO DEL HISTORIAL
                st.markdown(f'''
                    <div class="alerta-naranja">
                        ⚠️ Se ha detectado una posible coincidencia entre texto y notas musicales en el renglón {i+1}.<br>
                        "{linea}"
                    </div>
                ''', unsafe_allow_html=True)
            else:
                st.text(linea)
        
        decisiones.append((linea, es_nota))

    # --- ACCIONES FINALES ---
    st.divider()
    if st.button("🚀 Generar Cifrado Final"):
        res = []
        for txt, es_n in decisiones:
            if es_n:
                conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in txt.split()])
                res.append(conv)
            else:
                res.append(txt)
        
        st.code("\n".join(res), language=None)
        st.download_button("💾 Descargar Resultado", "\n".join(res), file_name="final.txt")

if st.button("🗑️ Reiniciar Todo"):
    st.session_state.texto_maestro = ""
    st.session_state.ver_analisis = False
    st.rerun()
