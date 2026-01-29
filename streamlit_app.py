import streamlit as st                                          # Importa el framework de interfaz web
import re                                                       # Importa librería para expresiones regulares
import streamlit.components.v1 as components                     # Permite usar HTML/JS personalizado

# --- CONFIGURACIÓN DE COLORES (Control total aquí) ---
COLOR_FONDO = "#0E1117"                                         # Define el color de fondo de la web
COLOR_TEXTO = "#FFFFFF"                                         # Define el color de los textos generales
COLOR_PRIMARIO = "#FF4B4B"                                      # Define color de botones y avisos
COLOR_BLOQUE_CODIGO = "#000000"                                 # Define fondo del área de resultado
COLOR_TEXTO_CODIGO = "#00FF00"                                  # Define color de las letras del resultado

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered") # Configura el título de la pestaña

# Inyección de Estilos CSS para personalizar la visualización
st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLOR_FONDO}; color: {COLOR_TEXTO}; }} /* Aplica fondo a la app */
        h1, h2, h3, p, span, label {{ color: {COLOR_TEXTO} !important; }}  /* Forza color a etiquetas */
        .stButton>button {{ background-color: {COLOR_PRIMARIO}; color: white; border-radius: 8px; width: 100%; }} /* Estilo botón */
        code {{ background-color: {COLOR_BLOQUE_CODIGO} !important; color: {COLOR_TEXTO_CODIGO} !important; }} /* Estilo resultado */
    </style>
""", unsafe_allow_html=True)                                    # Permite renderizar el CSS en la app

LATINO_A_AMERICANO = {                                          # Diccionario de traducción de notas
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):                                     # Función para detectar acordes claros
    linea_u = linea.upper()                                     # Pasa la línea a mayúsculas para comparar
    if not linea.strip(): return False                          # Si está vacía, no es música
    tiene_simbolos = re.search(r'[#B]|/|DIM|AUG|SUS|MAJ|ADD|[A-G]\d', linea_u) # Busca símbolos musicales
    if tiene_simbolos: return True                              # Si tiene símbolos, es música
    if "  " in linea: return True                               # Si tiene muchos espacios, suelen ser acordes
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea_u) # Busca nombres de notas latinas
    palabras = re.findall(r'\w+', linea)                        # Cuenta palabras totales en la línea
    if len(palabras) == 1 and len(notas_mayus) == 1: return True # Si hay una sola palabra y es nota, es música
    if len(set(notas_mayus)) >= 2: return True                  # Si hay dos notas distintas, es música
    return False                                                # Si no cumple nada, no se marca como música

def tiene_potencial_duda(linea):                                # Función para detectar líneas dudosas
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea.upper()) # Busca notas latinas
    return len(notas_mayus) > 0                                 # Devuelve True si encontró alguna nota

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):   # Función principal de transformación
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n') # Normaliza texto a mayúsculas y separa líneas
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)' # Regex para acordes latinos
    
    def traducir_acorde(match):                                 # Sub-función para traducir cada hallazgo
        raiz_lat = match.group(1)                               # Captura nota (Ej: SOL)
        alter = match.group(2) or ""                            # Captura alteración (Ej: #)
        cualidad = match.group(3) or ""                         # Captura cualidad (Ej: MIN)
        num = match.group(4) or ""                              # Captura número (Ej: 7)
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)  # Traduce a americano (Ej: G)
        if cualidad in ["M", "MIN"]: cualidad = "m"             # Convierte específicamente la m a minúscula
        return f"{raiz_amer}{alter}{cualidad}{num}"             # Retorna el acorde reconstruido

    resultado_traduccion = []                                   # Lista para almacenar líneas traducidas
    for i, linea in enumerate(lineas):                          # Recorre todas las líneas del texto
        if i in lineas_a_procesar:                              # Si la línea fue marcada como música
            resultado_traduccion.append(re.sub(patron_latino, traducir_acorde, linea)) # Traduce notas
        else:                                                   # Si es texto normal (letra)
            resultado_traduccion.append(linea)                  # La deja igual pero en mayúsculas

    resultado_final = []                                        # Lista para el paso final (apóstrofes)
    patron_americano = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD)?[0-9]*(?:/[A-G][#B]?)?)\b' # Regex acorde americano

    for i, linea in enumerate(resultado_traduccion):            # Recorre las líneas ya traducidas
        if i not in lineas_a_procesar:                          # Si no es música
            resultado_final.append(linea)                       # Añade la línea tal cual
            continue                                            # Salta a la siguiente
        linea_lista = list(linea)                               # Convierte línea en lista de caracteres
        ajuste = 0                                              # Contador para no perder la posición al insertar
        for m in re.finditer(patron_americano, linea):          # Busca cada acorde americano
            fin = m.end() + ajuste                              # Encuentra el final del acorde
            if fin < len(linea_lista):                          # Si no es el final de la línea
                if linea_lista[fin] not in ["'", "*"]:          # Si no tiene ya un apóstrofe
                    linea_lista.insert(fin, "'"); ajuste += 1   # Inserta el apóstrofe decorativo
            else:                                               # Si es el final de la línea
                linea_lista.append("'"); ajuste += 1            # Añade el apóstrofe al final
        resultado_final.append("".join(linea_lista))            # Une los caracteres de nuevo
    return '\n'.join(resultado_final)                           # Une todas las líneas en un solo texto

# --- INTERFAZ DE USUARIO ---
st.title("🎸 Cancionero Inteligente 2026")                      # Muestra el título principal
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"]) # Crea el selector de archivos

if archivo:                                                     # Si el usuario subió un archivo
    contenido = archivo.getvalue().decode("utf-8")              # Lee y decodifica el contenido del texto
    lineas_orig = contenido.split('\n')                         # Separa el contenido original por líneas
    confirmados_auto, indices_duda = [], []                     # Listas para clasificar líneas detectadas
    es_linea_musica_anterior = False                            # Bandera para evitar marcar letra como acordes

    for idx, linea in enumerate(lineas_orig):                   # Analiza el archivo línea por línea
        if es_linea_musica_anterior:                            # Si la anterior fue música, esta suele ser letra
            es_linea_musica_anterior = False                    # Reinicia la bandera
            continue                                            # Salta el análisis de esta línea
        if es_musica_obvia(linea):                              # Si detecta acordes claros
            confirmados_auto.append(idx)                        # Guarda el índice como música confirmada
            es_linea_musica_anterior = True                     # Activa bandera (la siguiente línea será letra)
        elif tiene_potencial_duda(linea):                       # Si hay duda (palabras que parecen notas)
            indices_duda.append(idx)                            # Guarda para preguntar al usuario
        else:                                                   # Si es texto plano
            es_linea_musica_anterior = False                    # Asegura que la bandera esté apagada

    st.subheader("🔍 Análisis")                                 # Subtítulo de sección
    st.success(f"Detección automática: {len(confirmados_auto)} líneas.") # Muestra cuántas líneas detectó solo

    seleccion_manual = []                                       # Lista para lo que el usuario confirme a mano
    if indices_duda:                                            # Si hubo líneas dudosas
        st.warning("Confirma estas líneas:")                    # Muestra aviso naranja
        for idx in indices_duda:                                # Crea un checkbox por cada duda
            if st.checkbox(f"L{idx+1}: {lineas_orig[idx].strip()}", key=idx): # Muestra el texto de la línea
                seleccion_manual.append(idx)                    # Si marca el check, se suma a música
    
    if st.button("✨ Procesar"):                                # Botón para ejecutar la magia
        texto_final = procesar_texto_selectivo(contenido, confirmados_auto + seleccion_manual) # Procesa todo
        st.subheader("Resultado:")                              # Subtítulo del resultado
        st.code(texto_final, language="text")                   # Muestra el texto final en el bloque negro

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$") # Escapa caracteres para el JavaScript
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: {COLOR_PRIMARIO}; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer;">💾 FINALIZAR / COMPARTIR</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;             // Pasa el texto procesado a JS
                    const fileName = "PRO_{archivo.name}";      // Crea el nombre del nuevo archivo
                    const blob = new Blob([contenido], {{ type: 'text/plain' }}); // Crea el objeto de archivo
                    const file = new File([blob], fileName, {{ type: 'text/plain' }}); // Prepara para compartir
                    if (confirm("🎵 ¿Compartir archivo?")) {{    // Pregunta si quiere usar menú nativo (móvil)
                        if (navigator.share) {{                 // Si el navegador soporta compartir
                            try {{ await navigator.share({{ files: [file] }}); return; }} catch(e) {{}}
                        }}
                    }}
                    const a = document.createElement('a');      // Si no comparte, crea link de descarga
                    a.href = URL.createObjectURL(blob);         // Genera URL temporal del archivo
                    a.download = fileName; a.click();           // Dispara la descarga automática
                }};
            </script>
        """, height=120)                                        # Ajusta el alto del componente JS
