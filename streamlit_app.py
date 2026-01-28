import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

# Diccionario de cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# --- ESTILO CSS (Modo Oscuro y Alerta Naranja) ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    .alerta-naranja {
        background-color: #FF8C00;
        padding: 12px;
        border-radius: 8px;
        color: #000000 !important;
        font-weight: bold;
        margin: 5px 0px;
        border-left: 5px solid #CC6600;
    }
    .renglon-ok {
        padding: 12px;
        color: #FFFFFF;
        border-bottom: 1px solid #31333F;
    }
    /* Estilo del editor de texto */
    .stTextArea textarea {
        background-color: #1E1E1E !important;
        color: #FFFFFF !important;
        font-family: 'Courier New', monospace !important;
        font-size: 16px !important;
        border: 1px solid #444 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""
if "analisis_listo" not in st.session_state:
    st.session_state.analisis_listo = False

def al_cargar():
    if st.session_state.uploader:
        st.session_state.texto_maestro = st.session_state.uploader.read().decode("utf-8")
        st.session_state.analisis_listo = False

# --- INTERFAZ DE ENTRADA ---
st.title("🎸 Validador de Notas y Conflictos")
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader", on_change=al_cargar)

# Editor Inicial
st.session_state.texto_maestro = st.text_area(
    "1. Pega o edita el texto original aquí:",
    value=st.session_state.texto_maestro,
    height=250,
    key="editor_principal"
)

col_btns = st.columns([0.3, 0.7])
if col_btns[0].button("🔍 Analizar Oraciones"):
    st.session_state.analisis_listo = True

# --- PANEL DE VALIDACIÓN (LO QUE BUSCABAS) ---
if st.session_state.analisis_listo and st.session_state.texto_maestro:
    st.divider()
    st.subheader("2. Revisa los Conflictos (Naranja)")
    st.info("Marca el checkbox si el renglón es MÚSICA. El color naranja avisa si hay incoherencias.")
    
    lineas = st.session_state.texto_maestro.split('\n')
    decisiones = []

    for i, linea in enumerate(lineas):
        if not linea.strip():
            decisiones.append(("", False))
            continue
            
        palabras = linea.upper().split()
        notas_detectadas = [p for p in palabras if p in CONVERSION]
        
        # Lógica de conflicto:
        # Si es impar pero no tiene notas O si es par pero TIENE notas
        es_impar = (i + 1) % 2 != 0
        hay_conflicto = (es_impar and not notas_detectadas) or (not es_impar and notas_detectadas)
        
        col_check, col_visual = st.columns([0.08, 0.92])
        
        with col_check:
            # Checkbox para confirmar si es música
            es_nota = st.checkbox("", value=es_impar, key=f"c_{i}")
        
        with col_visual:
            if hay_conflicto:
                # Fondo naranja si el sistema duda
                st.markdown(f'<div class="alerta-naranja">⚠️ {linea}</div>', unsafe_allow_html=True)
            else:
                # Fondo normal si parece correcto
                st.markdown(f'<div class="renglon-ok">{linea}</div>', unsafe_allow_html=True)
        
        decisiones.append((linea, es_nota))

    # --- GENERACIÓN Y DESCARGA ---
    st.divider()
    if st.button("🚀 Generar y Descargar Cifrado"):
        resultado_final = []
        for txt, es_n in decisiones:
            if es_n:
                pals = txt.split()
                # Conversión aplicando el diccionario musical
                conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in pals])
                resultado_final.append(conv)
            else:
                resultado_final.append(txt)
        
        texto_final = "\n".join(resultado_final)
        
        st.success("¡Procesamiento finalizado!")
        st.code(texto_final, language=None)
        
        st.download_button(
            label="💾 Descargar TXT Final",
            data=texto_final,
            file_name="cancion_corregida.txt",
            mime="text/plain",
            use_container_width=True
        )

# Botón limpiar
if st.button("🗑️ Reiniciar Todo"):
    st.session_state.texto_maestro = ""
    st.session_state.analisis_listo = False
    st.rerun()
