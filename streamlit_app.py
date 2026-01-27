import streamlit as st

# Configuración inicial
st.set_page_config(page_title="Music Transposer 2026", layout="wide")

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

# --- GESTIÓN DE ESTADO ---
if "contenido_musical" not in st.session_state:
    st.session_state.contenido_musical = ""

def al_subir_archivo():
    if st.session_state.uploader_input:
        texto = st.session_state.uploader_input.read().decode("utf-8")
        st.session_state.contenido_musical = texto

# --- INTERFAZ DE USUARIO ---
st.title("🎸 Editor con Renglones Dinámicos")

# 1. Cargador de archivos
st.file_uploader(
    "Carga tu archivo .txt", 
    type=["txt"], 
    key="uploader_input", 
    on_change=al_subir_archivo
)

st.subheader("Editor de Canción")

# 2. GENERACIÓN DINÁMICA DE RENGLONES
# Dividimos el texto actual para contar líneas
lineas_actuales = st.session_state.contenido_musical.split("\n")
total_lineas = len(lineas_actuales) if st.session_state.contenido_musical else 1

col_numeros, col_editor = st.columns([0.04, 0.96], gap="small")

with col_numeros:
    # Creamos los números con el mismo espaciado que el text_area
    numeros_lista = "<br>".join([f"{i+1}" for i in range(total_lineas)])
    st.markdown(
        f"""
        <div style="
            line-height: 1.6; 
            font-family: monospace; 
            font-size: 1.2rem; 
            text-align: right; 
            color: #555; 
            padding-top: 40px;
            user-select: none;
        ">
            {numeros_lista}
        </div>
        """, 
        unsafe_allow_html=True
    )

with col_editor:
    # El editor actualiza el estado 'contenido_musical' en cada cambio
    texto_editado = st.text_area(
        label="Editor de texto",
        value=st.session_state.contenido_musical,
        height=400,
        key="editor_principal",
        label_visibility="collapsed",
        on_change=lambda: setattr(st.session_state, 'contenido_musical', st.session_state.editor_principal)
    )
    # Sincronizamos el estado global
    st.session_state.contenido_musical = texto_editado

# 3. PREVISUALIZACIÓN PROCESADA
if st.session_state.contenido_musical:
    st.divider()
    st.subheader("👁️ Previsualización (Notas Convertidas)")
    
    lineas_proceso = st.session_state.contenido_musical.split('\n')
    resultado_final = []
    
    with st.container(border=True):
        for i, linea in enumerate(lineas_proceso):
            num = i + 1
            if num % 2 != 0: # IMPAR: Convertir a Americano
                notas_c = convertir_linea_notas(linea)
                resultado_final.append(notas_c)
                st.markdown(f"**`:blue[{notas_c}]`**")
            else: # PAR: Mantener Letra
                resultado_final.append(linea)
                st.markdown(f"&nbsp;{linea}")

    # 4. BOTONES
    st.divider()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            label="💾 Descargar TXT",
            data="\n".join(resultado_final),
            file_name="cancion_cifrada_2026.txt",
            mime="text/plain",
            use_container_width=True
        )
    with c2:
        if st.button("🗑️ Borrar todo", use_container_width=True):
            st.session_state.contenido_musical = ""
            st.rerun()
