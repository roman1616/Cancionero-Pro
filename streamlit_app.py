import streamlit as st

# 1. Configuración (Debe ser lo primero)
st.set_page_config(page_title="Editor Musical Pro", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Rescatado del historial) ---
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

# --- INICIALIZACIÓN DE ESTADO (Para que los botones no mueran) ---
if "contenido" not in st.session_state: st.session_state.contenido = ""
if "fase" not in st.session_state: st.session_state.fase = "edicion"

# --- FUNCIONES DE ACCIÓN ---
def cargar_archivo():
    if st.session_state.uplo:
        st.session_state.contenido = st.session_state.uplo.read().decode("utf-8")

def procesar(): st.session_state.fase = "validacion"
def reiniciar(): 
    st.session_state.contenido = ""
    st.session_state.fase = "edicion"

# --- INTERFAZ ---
st.title("🎸 Transpositor con Detector de Coincidencias")

if st.session_state.fase == "edicion":
    st.file_uploader("📂 Sube tu .txt", type=["txt"], key="uplo", on_change=cargar_archivo)
    
    # El editor carga el contenido del archivo inmediatamente
    st.session_state.contenido = st.text_area("Editor:", value=st.session_state.contenido, height=300)
    
    if st.button("🔍 Analizar Coincidencias"):
        st.session_state.fase = "validacion"
        st.rerun()

elif st.session_state.fase == "validacion":
    st.subheader("2. Validación de Oraciones")
    lineas = st.session_state.contenido.split('\n')
    decisiones = []

    for i, linea in enumerate(lineas):
        if not linea.strip(): continue
        
        # Lógica de alerta naranja rescatada
        palabras = linea.upper().split()
        tiene_notas = any(p in CONVERSION for p in palabras)
        es_impar = (i + 1) % 2 != 0
        conflicto = (es_impar and not tiene_notas) or (not es_impar and tiene_notas)
        
        col1, col2 = st.columns([0.1, 0.9])
        with col1:
            es_musica = st.checkbox("Nota", value=es_impar, key=f"c_{i}")
        with col2:
            if conflicto:
                # MENSAJE EXACTO DEL HISTORIAL
                st.markdown(f'<div class="alerta-naranja">⚠️ Se ha detectado una posible coincidencia entre texto y notas musicales en el renglón {i+1}:<br>{linea}</div>', unsafe_allow_html=True)
            else:
                st.text(linea)
        decisiones.append((linea, es_musica))

    # Botones de salida
    if st.button("🚀 Generar Cifrado Final"):
        res = []
        for t, m in decisiones:
            if m:
                res.append("   ".join([CONVERSION.get(p.upper(), p) for p in t.split()]))
            else:
                res.append(t)
        st.code("\n".join(res))
        st.download_button("💾 Descargar", "\n".join(res), file_name="cancion.txt")

    if st.button("⬅️ Volver al Editor"):
        st.session_state.fase = "edicion"
        st.rerun()

if st.button("🗑️ Limpiar Todo"):
    reiniciar()
    st.rerun()
