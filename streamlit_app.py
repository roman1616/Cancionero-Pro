import streamlit as st

# 1. Configuración de página
st.set_page_config(page_title="Procesador Musical de Confirmación", layout="centered")

# Diccionario de cifrado
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B", 
              "DO#": "C#", "RE#": "D#", "FA#": "F#", "SOL#": "G#", "LA#": "A#",
              "REB": "Db", "MIB": "Eb", "SOLB": "Gb", "LAB": "Ab", "SIB": "Bb"}

# --- GESTIÓN DE ESTADO ---
if "texto_maestro" not in st.session_state:
    st.session_state.texto_maestro = ""
if "procesar" not in st.session_state:
    st.session_state.procesar = False

def al_subir():
    if st.session_state.uploader:
        st.session_state.texto_maestro = st.session_state.uploader.read().decode("utf-8")
        st.session_state.procesar = False # Reset al cargar nuevo

# --- INTERFAZ DE ENTRADA ---
st.title("🎸 Procesador con Confirmación")
st.file_uploader("📂 Sube tu .txt", type=["txt"], key="uploader", on_change=al_subir)

# Editor principal
st.session_state.texto_maestro = st.text_area(
    "1. Edita el texto original aquí:",
    value=st.session_state.texto_maestro,
    height=250,
    key="editor_raw"
)

if st.button("🛠️ Preparar Oraciones para Clasificar"):
    st.session_state.procesar = True

# --- SECCIÓN DE CLASIFICACIÓN (Lo que buscabas) ---
if st.session_state.procesar and st.session_state.texto_maestro:
    st.divider()
    st.subheader("2. Selecciona qué líneas son NOTAS:")
    
    lineas = st.session_state.texto_maestro.split('\n')
    mapa_notas = []
    
    # Aquí se muestra cada oración con su check individual
    for i, linea in enumerate(lineas):
        if linea.strip(): # Solo líneas con contenido
            # El check aparece antes de la oración
            es_nota = st.checkbox(f"L{i+1}: {linea}", value=((i+1)%2!=0), key=f"check_{i}")
            mapa_notas.append((linea, es_nota))
        else:
            mapa_notas.append(("", False))

    # --- GENERACIÓN FINAL ---
    st.divider()
    if st.button("✅ Generar Cifrado Final"):
        resultado_final = []
        for texto, es_nota in mapa_notas:
            if es_nota:
                # Procesa solo las palabras que son notas reales
                palabras = texto.split()
                conv = "   ".join([CONVERSION.get(p.upper().strip(".,!"), p) for p in palabras])
                resultado_final.append(conv)
            else:
                resultado_final.append(texto)
        
        # Guardamos resultado para descargar
        texto_final = "\n".join(resultado_final)
        
        st.success("¡Cifrado generado con éxito!")
        st.subheader("3. Resultado Final:")
        st.code(texto_final, language=None)
        
        st.download_button(
            label="💾 Descargar Resultado",
            data=texto_final,
            file_name="cancion_procesada.txt",
            use_container_width=True
        )

if st.button("🗑️ Limpiar Todo"):
    st.session_state.texto_maestro = ""
    st.session_state.procesar = False
    st.rerun()
