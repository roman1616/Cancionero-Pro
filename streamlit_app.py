import streamlit as st

# 1. Configuración Pro 2026
st.set_page_config(page_title="Validador Musical Avanzado", layout="wide")

# Diccionario de cifrado
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# Notas que pueden confundirse con palabras comunes
AMBIGUAS = ["SOL", "LA", "SI", "DO", "RE"]

# --- ESTILO DARK CON ALERTAS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .status-check { color: #00FF00; font-size: 0.9rem; } /* Verde: OK */
    .status-ambiguous { color: #FFA500; font-size: 0.9rem; font-weight: bold; } /* Naranja: Duda */
    .status-note { color: #FF4B4B; font-size: 0.9rem; } /* Rojo: Nota detectada */
    </style>
    """, unsafe_allow_html=True)

if "texto_bruto" not in st.session_state:
    st.session_state.texto_bruto = ""
if "fase_validacion" not in st.session_state:
    st.session_state.fase_validacion = False

# --- CARGA DE ARCHIVO ---
def al_cargar():
    if st.session_state.uploader_key:
        st.session_state.texto_bruto = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.fase_validacion = True

st.title("🎸 Transpositor con Detector de Ambigüedad")
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_cargar)

# Editor Inicial
st.session_state.texto_bruto = st.text_area(
    "1. Ingresa o edita el texto original:",
    value=st.session_state.texto_bruto,
    height=200,
    key="editor_inicial"
)

if st.button("🔍 Iniciar Análisis de Coincidencias"):
    st.session_state.fase_validacion = True

# --- FASE DE VALIDACIÓN INTELIGENTE ---
if st.session_state.fase_validacion and st.session_state.texto_bruto:
    st.divider()
    st.subheader("2. Revisión de Coincidencias y Errores")
    st.info("Revisa las alertas antes de procesar. Las notas sospechosas están marcadas en naranja.")
    
    lineas = [l.strip() for l in st.session_state.texto_bruto.split('\n') if l.strip()]
    decisiones_usuario = []

    for i, oracion in enumerate(lineas):
        palabras = oracion.upper().split()
        notas_reales = [p for p in palabras if p in CONVERSION and p not in AMBIGUAS]
        notas_dudosas = [p for p in palabras if p in AMBIGUAS]
        
        col_chk, col_stat, col_txt = st.columns([0.05, 0.25, 0.7])
        
        with col_chk:
            # Sugerimos que es nota si hay notas claras o es impar
            sugerencia = len(notas_reales) > 0 or (len(notas_dudosas) > 0 and (i+1)%2 != 0)
            es_nota = st.checkbox("", value=sugerencia, key=f"v_{i}")
        
        with col_stat:
            if notas_reales:
                st.markdown(f"<span class='status-note'>🎵 Notas: {', '.join(notas_reales)}</span>", unsafe_allow_html=True)
            elif notas_dudosas:
                st.markdown(f"<span class='status-ambiguous'>❓ Ambiguo: {', '.join(notas_dudosas)}</span>", unsafe_allow_html=True)
            else:
                st.markdown("<span class='status-check'>📝 Texto</span>", unsafe_allow_html=True)
        
        with col_txt:
            st.write(oracion)
        
        decisiones_usuario.append((oracion, es_nota))

    # --- PROCESO FINAL ---
    st.divider()
    if st.button("🚀 Generar Cifrado Validado"):
        resultado = []
        for txt, es_n in decisiones_usuario:
            if es_n:
                # Conversión aplicando diccionario
                pals = txt.split()
                linea_c = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in pals])
                resultado.append(linea_c)
            else:
                resultado.append(txt)
        
        final_txt = "\n".join(resultado)
        st.success("¡Archivo procesado sin ambigüedades!")
        st.code(final_txt, language=None)
        
        st.download_button("💾 Descargar Resultado Final", data=final_txt, file_name="musica_validada.txt")

if st.button("🗑️ Reiniciar Editor"):
    st.session_state.texto_bruto = ""
    st.session_state.fase_validacion = False
    st.rerun()
