import streamlit as st  # Librería principal para la interfaz web interactiva
import re  # Módulo de Expresiones Regulares para búsqueda y manipulación de texto
import streamlit.components.v1 as components  # Permite inyectar código HTML/JS personalizado

# Configura la página: Título en la pestaña y ancho centrado del contenido
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de mapeo para transformar notas latinas a cifrado americano
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    if not linea.strip(): return False  # Si la línea está vacía, no es música
    # Detecta símbolos exclusivos de acordes (#, b, barra, tipos de acorde o números)
    tiene_simbolos = re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea)
    if tiene_simbolos: return True  # Si tiene símbolos técnicos, es música confirmada
    if "  " in linea: return True  # Doble espacio indica alineación manual de acordes
    # Busca notas latinas en MAYÚSCULAS para diferenciarlas de preposiciones
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    palabras = re.findall(r'\w+', linea)  # Cuenta todas las palabras de la línea
    # Si la línea tiene solo una palabra y esa palabra es una nota, es música
    if len(palabras) == 1 and len(notas_mayus) == 1: return True
    # Si hay 2 o más notas latinas diferentes en la misma línea, es música
    if len(set(notas_mayus)) >= 2: return True
    return False  # Si no cumple lo anterior, se marca como posible texto

def tiene_potencial_duda(linea):
    # Detecta si hay notas en mayúsculas mezcladas con texto para pedir confirmación
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    return len(notas_mayus) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):
    # Normaliza saltos de línea y separa el texto en una lista renglón por renglón
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    
    # Expresión regular para capturar nota + cualidad + alteración + número (ej: SOLm#7)
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()  # Captura la nota base (DO, RE...)
        cualidad = match.group(2) or ""  # Captura si es menor, maj, etc.
        alteracion = match.group(3) or ""  # Captura el sostenido o bemol
        numero = match.group(4) or ""  # Captura tensiones como 7, 9, 4
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)  # Traduce raíz a letra (C, D...)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"  # Rearma el acorde americano

    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            # Aplica la traducción solo a las líneas confirmadas como música
            linea_traducida = re.sub(patron_latino, traducir_acorde, linea)
            resultado_traduccion.append(linea_traducida)
        else:
            resultado_traduccion.append(linea)  # Mantiene la línea original si es texto

    # Lógica para insertar el apóstrofe (') al final de cada acorde ya traducido
    resultado_final = []
    patron_americano = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(resultado_traduccion):
        if i not in lineas_a_procesar:
            resultado_final.append(linea); continue # Salta si no es línea musical
            
        linea_lista = list(linea)  # Convierte línea a lista para insertar caracteres
        ajuste = 0  # Compensa el cambio de índices al insertar apóstrofes
        for m in re.finditer(patron_americano, linea):
            fin = m.end() + ajuste  # Ubica el final del acorde (ej: justo después de A#)
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]: # Evita duplicar si ya tiene
                    linea_lista.insert(fin, "'")  # Inserta el apóstrofe al final del acorde
                    ajuste += 1
            else:
                linea_lista.append("'")  # Si es el final de la línea, lo añade al final
                ajuste += 1
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)  # Une todo el texto procesado nuevamente

# --- INTERFAZ DE USUARIO ---
st.title("🎸 Cancionero Inteligente 2026") # Título principal en pantalla
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"]) # Widget para subir archivos

if archivo:
    contenido = archivo.getvalue().decode("utf-8") # Lee y decodifica el archivo subido
    lineas = contenido.split('\n') # Divide el contenido para el análisis visual
    confirmados_auto = [] # Lista para líneas que el sistema sabe que son música
    indices_duda = [] # Lista para líneas donde el sistema no está seguro
    es_linea_musica_anterior = False # Bandera para aplicar lógica de adyacencia

    for idx, linea in enumerate(lineas):
        if es_linea_musica_anterior: # Si arriba hubo música, esto suele ser letra
            es_linea_musica_anterior = False; continue # Saltamos para evitar falsos positivos
        if es_musica_obvia(linea): # Aplicamos reglas automáticas
            confirmados_auto.append(idx); es_linea_musica_anterior = True # Confirmado
        elif tiene_potencial_duda(linea): # Si hay notas en mayúsculas sin símbolos
            indices_duda.append(idx); es_linea_musica_anterior = False # Guardamos para preguntar
        else:
            es_linea_musica_anterior = False # Línea de texto puro

    st.subheader("🔍 Análisis") # Subtítulo de estado
    st.success(f"Se detectaron {len(confirmados_auto)} líneas de acordes automáticamente.")

    seleccion_manual = [] # Lista para las respuestas del usuario
    if indices_duda:
        st.warning("Confirma si estas líneas son música:") # Alerta de revisión manual
        for idx in indices_duda:
            # Crea un checkbox por cada línea dudosa
            if st.checkbox(f"Renglón {idx+1}: {lineas[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx) # Si marca, se procesará como música
    
    if st.button("✨ Procesar"): # Botón que dispara la transformación final
        total_indices = confirmados_auto + seleccion_manual # Suma autos + manuales
        texto_final = procesar_texto_selectivo(contenido, total_indices) # Procesa todo
        
        st.subheader("Resultado:") # Título para la vista previa
        st.code(texto_final, language="text") # Muestra el resultado final en un bloque de código

        # Bloque de JavaScript para manejar guardado y compartición con diálogos de confirmación
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$") # Escapa caracteres para JS
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: #007AFF; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px;">💾 FINALIZAR</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`; // Pasa el texto procesado a JS
                    const fileName = "PRO_{archivo.name}"; // Define nombre del archivo de salida
                    const blob = new Blob([contenido], {{ type: 'text/plain' }}); // Crea el archivo en memoria
                    const file = new File([blob], fileName, {{ type: 'text/plain' }}); // Prepara objeto archivo
                    
                    // Primer cuadro de aceptación: Compartir (WhatsApp, Email, etc)
                    if (confirm("🎵 ¿Deseas COMPARTIR el archivo?")) {{
                        if (navigator.share) {{
                            try {{ await navigator.share({{ files: [file] }}); return; }} 
                            catch(e) {{}}
                        }}
                    }}

                    // Segundo cuadro de aceptación (si cancela el primero): Descarga directa
                    if (confirm("💾 ¿Deseas DESCARGAR el archivo?")) {{
                        const a = document.createElement('a'); // Crea enlace invisible
                        a.href = URL.createObjectURL(blob); // Genera link de descarga
                        a.download = fileName; // Asigna nombre
                        a.click(); // Simula click para descargar
                    }}
                }};
            </script>
        """, height=120) # Define altura del componente JS

