import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    if not linea.strip(): return False
    tiene_simbolos = re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea)
    if tiene_simbolos: return True
    if "  " in linea: return True
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    palabras = re.findall(r'\w+', linea)
    if len(palabras) == 1 and len(notas_mayus) == 1: return True
    if len(set(notas_mayus)) >= 2: return True
    return False

def tiene_potencial_duda(linea):
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    return len(notas_mayus) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    
    # 1. Patrón para capturar el acorde latino completo
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        cualidad = match.group(2) or ""
        alteracion = match.group(3) or ""
        numero = match.group(4) or ""
        # Colocamos la alteración (#/b) pegada a la raíz americana
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            # Primero convertimos a Americano (Ej: LA# -> A#)
            linea_traducida = re.sub(patron_latino, traducir_acorde, linea)
            resultado_traduccion.append(linea_traducida)
        else:
            resultado_traduccion.append(linea)

    # 2. Paso final: Colocar el apóstrofe al final del acorde americano (Ej: A# -> A#')
    resultado_final = []
    patron_americano = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(resultado_traduccion):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_americano, linea):
            fin = m.end() + ajuste
            # Insertar apóstrofe solo si no hay uno ya
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
            else:
                linea_lista.append("'")
                ajuste += 1
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.title("🎸 Cancionero Inteligente 2026")
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    confirmados_auto = []
    indices_duda = []
    es_linea_musica_anterior = False

    for idx, linea in enumerate(lineas):
        if es_linea_musica_anterior:
            es_linea_musica_anterior = False
            continue
        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
            es_linea_musica_anterior = True
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx)
            es_linea_musica_anterior = False
        else:
            es_linea_musica_anterior = False

    st.subheader("🔍 Análisis")
    st.success(f"Se detectaron {len(confirmados_auto)} líneas de acordes automáticamente.")

    seleccion_manual = []
    if indices_duda:
        st.warning("Confirma si estas líneas son música:")
        for idx in indices_duda:
            if st.checkbox(f"Renglón {idx+1}: {lineas[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    
    if st.button("✨ Procesar"):
        total_indices = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_indices)
        
        st.subheader("Resultado:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: #007AFF; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px;">💾 FINALIZAR</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    
                    if (confirm("🎵 ¿Deseas COMPARTIR el archivo?")) {{
                        if (navigator.share) {{
                            try {{ await navigator.share({{ files: [file] }}); return; }} 
                            catch(e) {{}}
                        }}
                    }}

                    if (confirm("💾 ¿Deseas DESCARGAR el archivo?")) {{
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = fileName;
                        a.click();
                    }}
                }};
            </script>
        """, height=120)





-----------------------------------------------------------------------------------------



import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    if not linea.strip(): return False
    tiene_simbolos = re.search(r'[#b]|/|dim|aug|sus|maj|add|[A-G]\d', linea)
    if tiene_simbolos: return True
    if "  " in linea: return True
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    palabras = re.findall(r'\w+', linea)
    if len(palabras) == 1 and len(notas_mayus) == 1: return True
    if len(set(notas_mayus)) >= 2: return True
    return False

def tiene_potencial_duda(linea):
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea)
    return len(notas_mayus) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):
    # Convertimos a mayúsculas para estandarizar, pero manejaremos la 'm' después
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n')
    
    # El patrón ahora busca específicamente variaciones de menor
    # Capturamos la raíz, luego si es menor (m), y luego el resto (7, maj7, etc.)
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1)
        alteracion = match.group(2) or ""
        cualidad = match.group(3) or ""
        numero = match.group(4) or ""
        
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        
        # Lógica para la 'm' minúscula:
        # Si la cualidad es 'M' sola o empieza por 'MIN', la convertimos en 'm'
        if cualidad == "M":
            cualidad = "m"
        elif cualidad == "MIN":
            cualidad = "m"
            
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            # Traducimos y aplicamos la m minúscula
            linea_traducida = re.sub(patron_latino, traducir_acorde, linea)
            resultado_traduccion.append(linea_traducida)
        else:
            resultado_traduccion.append(linea)

    # 2. Paso final: Colocar el apóstrofe
    resultado_final = []
    # Actualizamos el regex americano para que también reconozca la 'm' minúscula
    patron_americano = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD)?[0-9]*(?:/[A-G][#B]?)?)\b'

    for i, linea in enumerate(resultado_traduccion):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_americano, linea):
            fin = m.end() + ajuste
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
            else:
                linea_lista.append("'")
                ajuste += 1
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            # Primero convertimos a Americano (Ej: LA# -> A#)
            linea_traducida = re.sub(patron_latino, traducir_acorde, linea)
            resultado_traduccion.append(linea_traducida)
        else:
            resultado_traduccion.append(linea)

    # 2. Paso final: Colocar el apóstrofe al final del acorde americano (Ej: A# -> A#')
    resultado_final = []
    patron_americano = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(resultado_traduccion):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_americano, linea):
            fin = m.end() + ajuste
            # Insertar apóstrofe solo si no hay uno ya
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
            else:
                linea_lista.append("'")
                ajuste += 1
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.title("🎸 Cancionero Inteligente 2026")
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    confirmados_auto = []
    indices_duda = []
    es_linea_musica_anterior = False

    for idx, linea in enumerate(lineas):
        if es_linea_musica_anterior:
            es_linea_musica_anterior = False
            continue
        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
            es_linea_musica_anterior = True
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx)
            es_linea_musica_anterior = False
        else:
            es_linea_musica_anterior = False

    st.subheader("🔍 Análisis")
    st.success(f"Se detectaron {len(confirmados_auto)} líneas de acordes automáticamente.")

    seleccion_manual = []
    if indices_duda:
        st.warning("Confirma si estas líneas son música:")
        for idx in indices_duda:
            if st.checkbox(f"Renglón {idx+1}: {lineas[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    
    if st.button("✨ Procesar"):
        total_indices = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_indices)
        
        st.subheader("Resultado:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: #007AFF; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px;">💾 FINALIZAR</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    
                    if (confirm("🎵 ¿Deseas COMPARTIR el archivo?")) {{
                        if (navigator.share) {{
                            try {{ await navigator.share({{ files: [file] }}); return; }} 
                            catch(e) {{}}
                        }}
                    }}

                    if (confirm("💾 ¿Deseas DESCARGAR el archivo?")) {{
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = fileName;
                        a.click();
                    }}
                }};
            </script>
        """, height=120)



        ----------------------------------------------------


        import streamlit as st                                          # Framework de interfaz
import re                                                       # Expresiones regulares
import streamlit.components.v1 as components                     # Componentes HTML/JS

# --- CONFIGURACIÓN DE COLORES ---
COLOR_FONDO = "#0E1117"                                         # Fondo de la aplicación
COLOR_TEXTO = "#FFFFFF"                                         # Texto general
COLOR_PRIMARIO = "#FF4B4B"                                      # Botones y acentos
COLOR_BLOQUE_CODIGO = "#000000"                                 # Fondo del resultado
COLOR_TEXTO_CODIGO = "#00FF00"                                  # Texto del resultado
COLOR_SELECTOR = "#1E1E1E"                                      # Fondo del selector

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered") # Configura la página

# Inyección de CSS para un selector MUY ESTRECHO y limpieza de interfaz
st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLOR_FONDO}; color: {COLOR_TEXTO}; }} # Fondo app
        h1, h2, h3, p, span, label {{ color: {COLOR_TEXTO} !important; }}  # Color textos
        
        /* Contenedor del Selector de Archivos (MUY ESTRECHO) */
        [data-testid="stFileUploader"] {{
            background-color: {COLOR_SELECTOR};                 # Fondo selector
            border: 1px dashed {COLOR_PRIMARIO};                # Borde fino
            border-radius: 10px;                                # Bordes redondeados
            max-width: 250px;                                   # ANCHO MUY ESTRECHO
            margin: 0 auto;                                     # Centrado
            padding: 2px;                                       # Padding mínimo
        }}
        
        /* Ocultar textos nativos y bordes de componentes de Streamlit */
        [data-testid="stFileUploader"] section > div {{ display: none; }} # Oculta "Drag and drop"
        iframe {{ border: none !important; }}                     # QUITA RECUADRO EXTERIOR DEL BOTÓN FINAL
        
        [data-testid="stFileUploader"] button {{
            background-color: {COLOR_PRIMARIO} !important;      # Botón selector
            color: white !important;                            # Texto botón
            width: 100%;                                        # Botón al ancho total
            font-size: 11px !important;                         # Letra pequeña
        }}

        .stButton>button {{ background-color: {COLOR_PRIMARIO}; color: white; border-radius: 8px; width: 100%; }} # Botón procesar
        code {{ background-color: {COLOR_BLOQUE_CODIGO} !important; color: {COLOR_TEXTO_CODIGO} !important; }} # Resultado
    </style>
""", unsafe_allow_html=True)                                    # Inyecta el CSS

LATINO_A_AMERICANO = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'} # Mapa notas

def es_musica_obvia(linea):                                     # Detecta acordes claros
    linea_u = linea.upper()                                     # A mayúsculas
    if not linea.strip(): return False                          # Vacías no
    tiene_simbolos = re.search(r'[#B]|/|DIM|AUG|SUS|MAJ|ADD|[A-G]\d', linea_u) # Busca símbolos
    if tiene_simbolos: return True                              # Símbolos = música
    if "  " in linea: return True                               # Espacios = música
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea_u) # Busca notas
    palabras = re.findall(r'\w+', linea)                        # Cuenta palabras
    return (len(palabras) == 1 and len(notas_mayus) == 1) or len(set(notas_mayus)) >= 2 # Lógica música

def tiene_potencial_duda(linea):                                # Detecta dudas
    return len(re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea.upper())) > 0 # Busca notas

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):   # Función principal
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n') # Mayúsculas
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)' # Regex
    
    def traducir_acorde(match):                                 # Traduce cada acorde
        raiz_amer = LATINO_A_AMERICANO.get(match.group(1), match.group(1)) # A americano
        alter = match.group(2) or ""; cualidad = match.group(3) or ""; num = match.group(4) or "" # Partes
        if cualidad in ["M", "MIN"]: cualidad = "m"             # Menor a minúscula
        return f"{raiz_amer}{alter}{cualidad}{num}"             # Reconstruye

    resultado_traduccion = [re.sub(patron_latino, traducir_acorde, L) if i in lineas_a_procesar else L for i, L in enumerate(lineas)] # Traduce

    res_final = []                                              # Lista para apóstrofes
    patron_am = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD)?[0-9]*(?:/[A-G][#B]?)?)\b' # Regex am
    for i, linea in enumerate(resultado_traduccion):            # Recorre líneas
        if i not in lineas_a_procesar: res_final.append(linea); continue # Salta si no música
        l_lista = list(linea); ajuste = 0                       # Preparación
        for m in re.finditer(patron_am, linea):                 # Busca acordes
            fin = m.end() + ajuste                              # Final acorde
            if fin < len(l_lista) and l_lista[fin] not in ["'", "*"]: l_lista.insert(fin, "'"); ajuste += 1 # Inserta '
            elif fin >= len(l_lista): l_lista.append("'"); ajuste += 1 # Al final
        res_final.append("".join(l_lista))                      # Une línea
    return '\n'.join(res_final)                                 # Une todo

# --- INTERFAZ ---
st.title("<img src="https://raw.githubusercontent.com/roman1616/Cancionero-Pro/refs/heads/main/40.png" 
    alt="Icono de música" style="width: 40px; height: 40px; vertical-align: middle;">)                                  # Título corto
archivo = st.file_uploader("🎼 Sube tu cancion en formato .txt", type=["txt"])         # Selector estrecho

if archivo:                                                     # Si hay archivo
    cont = archivo.getvalue().decode("utf-8"); l_orig = cont.split('\n') # Lee
    conf, duda = [], []; es_mus = False                         # Listas control
    for idx, lin in enumerate(l_orig):                          # Escanea
        if es_mus: es_mus = False; continue                     # Salta letra tras música
        if es_musica_obvia(lin): conf.append(idx); es_mus = True # Música confirmada
        elif tiene_potencial_duda(lin): duda.append(idx)        # Línea dudosa
    
    st.subheader("🔍 Análisis")                                 # Sección análisis
    if duda:                                                    # Si hay dudas
        st.warning("Confirma si estas líneas son acordes:")                          # Aviso
        sel = [idx for idx in duda if st.checkbox(f"L{idx+1}: {l_orig[idx].strip()}", key=idx)] # Checks
    else: sel = []                                              # Sin selección
    
    if st.button("✨ Procesar"):                                # Botón procesar
        txt_fin = procesar_texto_selectivo(cont, conf + sel)    # Procesa
        st.code(txt_fin, language="text")                       # Muestra código
        js = txt_fin.replace("`", "\\`").replace("$", "\\$")    # Escapa JS
        
        # Botón final SIN RECUADRO, ESTRECHO Y CENTRADO
        components.html(f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <button id="btn" style="
                padding: 12px 20px; 
                background: {COLOR_PRIMARIO}; 
                color: white; 
                border: none; 
                border-radius: 10px; 
                cursor: pointer; 
                font-weight: bold; 
                width: 250px; 
                font-family: sans-serif;
                box-shadow: 0px 4px 10px rgba(0,0,0,0.3);
            ">💾 GUARDAR / COMPARTIR</button>
        </div>
        <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    
                    if (confirm("🎵 ¿Deseas COMPARTIR el archivo? 🎵")) {{
                        if (navigator.share) {{
                            try {{ await navigator.share({{ files: [file] }}); return; }} 
                            catch(e) {{}}
                        }}
                    }}

                    if (confirm("💾 ¿Deseas DESCARGAR el archivo? 💾")) {{
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = fileName;
                        a.click();
                    }}
                }};
            </script>
        """, height=80)                 
        
