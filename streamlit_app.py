import streamlit as st

# Configuración de página
st.set_page_config(page_title="Editor Musical 2026", layout="wide")

# Diccionario de cifrado americano
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def convertir_notas(linea):
    palabras = linea.upper().split()
    return "   ".join([CONVERSION.get(p, p) for p in palabras])

# --- INICIALIZACIÓN DE ESTADO (Evita el Error de Key/Value) ---
if "contenido_editor" not in st.session_state:
    st.session_state.contenido_editor = ""

# Función para cargar el archivo correctamente
def callback_archivo():
    if st.session_state.uploader_input:
        texto = st.session_state.uploader_input.read().decode("utf-8")
        st.session_state.contenido_editor = texto

# --- INTERFAZ ---
st.title("🎸 Transpositor de Notas 2026")

# 1. Cargador de archivos
st.file_uploader(
    "📂 Sube tu archivo .txt", 
    type=["txt"], 
    key="uploader_input", 
    on_change=callback_archivo
)

# 2. EDITOR CON NUMERACIÓN ESTÁTICA Y ALTURA DINÁMICA
st.subheader("📝 Editor de Contenido")

# Calculamos las líneas para la numeración y la altura
lineas_actuales = st.session_state.contenido_editor.split("\n")
n_lineas = max(len(lineas_actuales), 1)
# En 2026, 31px por línea es el estándar para evitar scroll interno en Streamlit
altura_dinamica = max(250, n_lineas * 31) 

col_num, col_edit = st.columns([0.04, 0.96], gap="small")

with col_num:
    # Generamos números estáticos
    numeros_html = "<br>".join([f"{i+1}" for i in range(n_lineas)])
    st.markdown(
        f"""<div style='line-height: 1.58; font-family: monospace; font-size: 1.2rem; 
        text-align: right; color: #888; padding-top: 40px;'>{numeros_html}</div>""", 
        unsafe_allow_html=True
    )

with col_edit:
    # Usamos solo la KEY vinculada al estado para evitar el error de duplicidad
    # El valor se sincroniza automáticamente a través de la key
    st.text_area(
        "Editor Principal",
        key="contenido_editor", 
        height=altura_dinamica,
        label_visibility="collapsed"
    )

# 3. PREVISUALIZACIÓN PROCESADA
if st.session_state.contenido_editor:
    st.divider()
    st.subheader("👁️ Previsualización (Notas Convertidas)")
    
    resultado_final = []
    lineas_proceso = st.session_state.contenido_editor.split('\n')
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_proceso):
            idx = i + 1
            if idx % 2 != 0: # Renglón IMPAR: Notas
                notas_c = convertir_notas(linea)
                resultado_final.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # Renglón PAR: Letra
                resultado_final.append(linea)
                st.text(linea)

    # 4. BOTONES DE ACCIÓN
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
            st.session_state.contenido_editor = ""
            st.rerun()
