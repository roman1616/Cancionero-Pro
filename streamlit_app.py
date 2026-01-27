import streamlit as st

# Diccionario de conversión
CONVERSION = {
    "DO": "C", "RE": "D", "MI": "E", "FA": "F", 
    "SOL": "G", "LA": "A", "SI": "B",
    "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
    "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"
}

def convertir_linea_notas(linea):
    palabras = linea.upper().split()
    convertidas = [CONVERSION.get(p, p) for p in palabras]
    return "   ".join(convertidas)

# --- FUNCIÓN PARA CARGAR EL ARCHIVO AL EDITOR ---
def cargar_archivo_al_state():
    if st.session_state.uploader is not None:
        # Leemos el archivo y lo inyectamos directamente en la 'key' del editor
        contenido = st.session_state.uploader.read().decode("utf-8")
        st.session_state.main_editor = contenido

st.set_page_config(page_title="Editor Musical Pro 2026", layout="wide")

st.title("🎸 Transpositor con Líneas Laterales")

# 1. Cargador de archivos (Usa callback para actualizar el editor al instante)
st.file_uploader(
    "Sube tu archivo .txt", 
    type=["txt"], 
    key="uploader", 
    on_change=cargar_archivo_al_state
)

# 2. Área de Edición con Números
st.subheader("Editor de Contenido")

# Aseguramos que la key del editor exista en el session_state
if "main_editor" not in st.session_state:
    st.session_state.main_editor = ""

col_indices, col_texto = st.columns([0.05, 0.95])

with col_indices:
    # Calculamos cuántas líneas hay para poner los números
    lineas_actuales = st.session_state.main_editor.split("\n")
    n_lineas = max(len(lineas_actuales), 1)
    numeros_html = "<br>".join([f"<b>{i+1}</b>" for i in range(n_lineas)])
    # Estilo CSS para alinear números con los renglones del editor
    st.markdown(
        f"<div style='line-height: 2.3; text-align: right; color: #888; padding-top: 25px;'>{numeros_html}</div>", 
        unsafe_allow_html=True
    )

with col_texto:
    # El text_area usa la 'key' que actualizamos con el cargador
    texto_input = st.text_area(
        "Edición (Impares=Notas, Pares=Letra)",
        key="main_editor",
        height=400,
        label_visibility="collapsed"
    )

# 3. Previsualización y Descarga
if texto_input:
    st.divider()
    st.subheader("👁️ Previsualización (Cifrado Americano)")
    
    resultado_final = []
    lineas = texto_input.split('\n')
    
    with st.container(border=True):
        for i, linea in enumerate(lineas):
            if (i + 1) % 2 != 0: # NOTAS
                notas_c = convertir_linea_notas(linea)
                resultado_final.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # LETRA
                resultado_final.append(linea)
                st.text(linea)

    st.divider()
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            label="💾 Descargar TXT",
            data="\n".join(resultado_final),
            file_name="cancion_cifrada.txt",
            mime="text/plain",
            use_container_width=True
        )
    with col_d2:
        if st.button("🗑️ Limpiar Todo", use_container_width=True):
            st.session_state.main_editor = ""
            st.rerun()
