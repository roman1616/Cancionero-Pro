import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Pro", layout="wide")

# Diccionario de cifrado del historial
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- ESTILO CSS (Rescatado) ---
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

# --- ESTADO DE SESIÓN ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""
if "analisis_listo" not in st.session_state:
    st.session_state.analisis_listo = False

# --- FUNCIÓN DE CARGA ---
def al_cargar():
    if st.session_state.uploader:
        st.session_state.texto_maestro = st.session_state.uploader.read().decode("utf-8")
        st.session_state.analisis_listo = False

# --- INTERFAZ ---
st.title("🎸 Transpositor con Detector de Coincidencias")

st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader", on_change=al_cargar)

# Editor principal
st.session_state.texto_maestro = st.text_area(
    "1. Edita el texto original:",
    value=st.session_state.texto_maestro,
    height=250,
    key="editor_principal"
)

if st.button("🔍 Analizar Oraciones"):
    st.session_state.analisis_listo = True

# --- PANEL DE VALIDACIÓN CON MENSAJE DE ALERTA ---
if st.session_state.analisis_listo and st.session_state.texto_maestro:
    st.divider()
    st.subheader("2. Revisión de Renglones")
    
    lineas = st.session_state.texto_maestro.split('\n')
    decisiones = []

    for i, linea in enumerate(lineas):
        if not linea.strip():
            decisiones.append(("", False))
            continue
            
        palabras = linea.upper().split()
        notas_detectadas = [p for p in palabras if p in CONVERSION]
        
        es_impar = (i + 1) % 2 != 0
        hay_conflicto = (es_impar and not notas_detectadas) or (not es_impar and notas_detectadas)
        
        col_check, col_visual = st.columns([0.08, 0.92])
        
        with col_check:
            es_nota = st.checkbox("", value=es_impar, key=f"v_{i}")
        
        with col_visual:
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

    # --- GENERACIÓN ---
    st.divider()
    if st.button("🚀 Generar Cifrado Final"):
        resultado_final = []
        for txt, es_n in decisiones:
            if es_n:
                pals = txt.split()
                conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in pals])
                resultado_final.append(conv)
            else:
                resultado_final.append(txt)
        
        texto_final = "\n".join(resultado_final)
        st.code(texto_final, language=None)
        st.download_button("💾 Descargar TXT", data=texto_final, file_name="cancion.txt")

if st.button("🗑️ Reiniciar"):
    st.session_state.texto_maestro = ""
    st.session_state.analisis_listo = False
    st.rerun()
