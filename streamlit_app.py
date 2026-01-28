import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Validador Visual 2026", layout="wide")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- GESTIÓN DE ESTADO ---
if "texto_bruto" not in st.session_state:
    st.session_state.texto_bruto = ""
if "fase_analisis" not in st.session_state:
    st.session_state.fase_analisis = False

# --- CSS PARA ALERTAS NARANJAS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; }
    .alerta-naranja {
        background-color: #FFA500;
        padding: 10px;
        border-radius: 5px;
        color: #000000 !important;
        font-weight: bold;
        margin: 2px 0px;
    }
    .renglon-limpio {
        padding: 10px;
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- CARGA ---
def al_cargar():
    if st.session_state.uploader:
        st.session_state.texto_bruto = st.session_state.uploader.read().decode("utf-8")
        st.session_state.fase_analisis = True

st.title("🎸 Transpositor con Alerta de Conflicto")
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader", on_change=al_cargar)

# Editor
st.session_state.texto_bruto = st.text_area("Editor:", value=st.session_state.texto_bruto, height=200)

if st.button("🔍 Analizar Conflictos"):
    st.session_state.fase_analisis = True

# --- PANEL DE VALIDACIÓN CON MARCAS NARANJAS ---
if st.session_state.fase_analisis and st.session_state.texto_bruto:
    st.divider()
    st.subheader("Revisión de Renglones:")
    
    lineas = st.session_state.texto_bruto.split('\n')
    decisiones = []

    for i, linea in enumerate(lineas):
        palabras = linea.upper().split()
        notas_detectadas = [p for p in palabras if p in CONVERSION]
        
        # Lógica de conflicto:
        # Si es impar (notas) pero no tiene notas -> NARANJA
        # Si es par (letra) pero tiene notas -> NARANJA
        es_impar = (i + 1) % 2 != 0
        hay_conflicto = (es_impar and not notas_detectadas) or (not es_impar and notas_detectadas)
        
        col_check, col_texto = st.columns([0.1, 0.9])
        
        with col_check:
            es_nota = st.checkbox("", value=es_impar, key=f"c_{i}")
        
        with col_texto:
            if hay_conflicto:
                # Mostramos la línea con fondo naranja si hay duda
                st.markdown(f'<div class="alerta-naranja">⚠️ Conflicto detectado: {linea}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="renglon-limpio">{linea}</div>', unsafe_allow_html=True)
        
        decisiones.append((linea, es_nota))

    # --- PROCESAMIENTO FINAL ---
    st.divider()
    if st.button("⚙️ Generar Resultado Final"):
        resultado = []
        for txt, es_n in decisiones:
            if es_n:
                conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in txt.split()])
                resultado.append(conv)
            else:
                resultado.append(txt)
        
        st.success("¡Cifrado generado!")
        st.code("\n".join(resultado), language=None)
        st.download_button("💾 Descargar", data="\n".join(resultado), file_name="final.txt")

if st.button("🗑️ Limpiar"):
    st.session_state.texto_bruto = ""
    st.session_state.fase_analisis = False
    st.rerun()

