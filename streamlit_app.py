import streamlit as st

# Configuración de página
st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

# Diccionario de cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def convertir_linea_notas(linea):
    palabras = linea.upper().split()
    return "   ".join([CONVERSION.get(p, p) for p in palabras])

# --- GESTIÓN DE ESTADO ---
if "texto_cancion" not in st.session_state:
    st.session_state.texto_cancion = ""

def al_cargar_archivo():
    if st.session_state.uploader_key:
        # Leemos e inyectamos directamente en el estado
        contenido = st.session_state.uploader_key.read().decode("utf-8")
        st.session_state.texto_cancion = contenido
        # Limpiamos el widget de carga para permitir nuevas subidas
        st.session_state.uploader_key = None

# --- INTERFAZ ---
st.title("🎸 Transpositor de Notas 2026")
st.caption("Los renglones impares se convierten a cifrado americano automáticamente.")

# 1. Cargador de archivos
st.file_uploader("📂 Sube tu archivo .txt", type=["txt"], key="uploader_key", on_change=al_cargar_archivo)

# 2. EDITOR Y NUMERACIÓN (Sin Scroll)
lineas = st.session_state.texto_cancion.split("\n")
n_lineas = max(len(lineas), 1)

# Calculamos una altura dinámica (aprox 25px por línea) para evitar el scroll interno
altura_dinamica = max(300, n_lineas * 31)

st.subheader("📝 Editor de Contenido")
col_num, col_edit = st.columns([0.04, 0.96], gap="small")

with col_num:
    # Números de línea estáticos alineados con el editor
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(
        f"""<div style='line-height: 1.58; font-family: monospace; font-size: 1.2rem; 
        text-align: right; color: #888; padding-top: 38px;'>{numeros_html}</div>""", 
        unsafe_allow_html=True
    )

with col_edit:
    # El editor usa el estado directamente. Al cambiar, actualiza la página.
    texto_input = st.text_area(
        "Editor",
        value=st.session_state.texto_cancion,
        height=altura_dinamica,
        key="main_editor",
        label_visibility="collapsed"
    )
    # Sincronización inmediata del estado
    if texto_input != st.session_state.texto_cancion:
        st.session_state.texto_cancion = texto_input
        st.rerun()

# 3. PREVISUALIZACIÓN Y RESULTADO
if st.session_state.texto_cancion:
    st.divider()
    st.subheader("👁️ Previsualización Final")
    
    resultado_final = []
    lineas_proceso = st.session_state.texto_cancion.split('\n')
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_proceso):
            if (i + 1) % 2 != 0: # NOTAS
                notas_c = convertir_linea_notas(linea)
                resultado_final.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # LETRA
                resultado_final.append(linea)
                st.text(linea)

    # 4. BOTONES
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="💾 Descargar TXT",
            data="\n".join(resultado_final),
            file_name="cancion_cifrada.txt",
            mime="text/plain",
            use_container_width=True
        )
    with c2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.texto_cancion = ""
            st.rerun()

