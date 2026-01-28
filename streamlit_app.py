import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Validador Musical Pro 2026", layout="wide")

# Diccionario de cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

# Palabras que suelen causar confusión (Ambiguas)
AMBIGUAS = ["SOL", "LA", "SI", "DO", "RE"]

# --- ESTILO CSS ---
st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: white; }
    .status-error { color: #FF4B4B; font-weight: bold; }
    .status-warning { color: #FFA500; font-style: italic; }
    </style>
    """, unsafe_allow_html=True)

if "texto_bruto" not in st.session_state:
    st.session_state.texto_bruto = ""

# --- CARGA DE ARCHIVO ---
def al_cargar():
    if st.session_state.uploader_key:
        st.session_state.texto_bruto = st.session_state.uploader_key.read().decode("utf-8")

st.title("🎸 Transpositor con Detector de Errores")
st.file_uploader("📂 Cargar canción (.txt)", type=["txt"], key="uploader_key", on_change=al_subir)

st.session_state.texto_bruto = st.text_area("Pega o edita el texto aquí:", value=st.session_state.texto_bruto, height=200)

if st.button("🔍 Analizar Coincidencias y Errores"):
    if st.session_state.texto_bruto:
        lineas = st.session_state.texto_bruto.split('\n')
        resultado_final = []
        
        st.divider()
        st.subheader("⚠️ Informe de Análisis por Renglón:")

        for i, linea in enumerate(lineas):
            palabras = linea.upper().split()
            # Buscamos si hay notas musicales en el renglón
            notas_encontradas = [p for p in palabras if p in CONVERSION]
            # Buscamos si hay palabras ambiguas (como "SOL" o "LA")
            notas_ambiguas = [p for p in palabras if p in AMBIGUAS]
            
            col_check, col_info, col_texto = st.columns([0.1, 0.4, 0.5])
            
            with col_check:
                # Sugerencia inteligente: si hay notas y no son todas ambiguas, es música
                es_nota_sugerido = len(notas_encontradas) > 0 and (i + 1) % 2 != 0
                es_nota = st.checkbox("", value=es_nota_sugerido, key=f"c_{i}")
            
            with col_info:
                if not notas_encontradas:
                    st.write("✅ Texto puro")
                elif len(notas_ambiguas) > 0 and len(notas_encontradas) == len(notas_ambiguas):
                    st.markdown(f"<span class='status-warning'>❓ Ambigüedad: '{', '.join(notas_ambiguas)}'</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<span class='status-error'>🎵 Notas detectadas: {', '.join(notas_encontradas)}</span>", unsafe_allow_html=True)
            
            with col_texto:
                st.write(f"**{linea}**")
            
            # Guardamos decisión
            if es_nota:
                conv = "   ".join([CONVERSION.get(p.upper(), p) for p in linea.split()])
                resultado_final.append(conv)
            else:
                resultado_final.append(linea)

        # --- GENERAR DESCARGA ---
        st.divider()
        st.download_button(
            label="💾 Descargar Resultado Corregido",
            data="\n".join(resultado_final),
            file_name="cancion_validada.txt",
            use_container_width=True
        )
