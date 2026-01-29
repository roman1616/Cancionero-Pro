import streamlit as st                                          # Framework de interfaz
import re                                                       # Expresiones regulares
import streamlit.components.v1 as components                     # Componentes HTML/JS

# --- CONFIGURACIÓN DE COLORES ---
COLOR_FONDO = "#0E1117"                                         # Fondo de la aplicación
COLOR_TEXTO = "#FFFFFF"                                         # Texto general
COLOR_PRIMARIO = "#FF4B4B"                                      # Color de botones
COLOR_BLOQUE_CODIGO = "#000000"                                 # Fondo del resultado
COLOR_TEXTO_CODIGO = "#00FF00"                                  # Texto del resultado

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered") # Configura la página

# Inyección de CSS para quitar fondos y centrar botones
st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLOR_FONDO}; color: {COLOR_TEXTO}; }} # Fondo app
        h1, h2, h3, p, span, label {{ color: {COLOR_TEXTO} !important; text-align: center; }} # Textos centrados
        
        /* Selector de Archivos SIN FONDO y CENTRADO */
        [data-testid="stFileUploader"] {{
            background-color: transparent;                      # QUITA EL FONDO DEL SELECTOR
            border: 1px dashed {COLOR_PRIMARIO};                # Borde fino punteado
            max-width: 250px;                                   # Ancho estrecho
            margin: 0 auto;                                     # CENTRADO
        }}
        [data-testid="stFileUploader"] section {{ padding: 0; background-color: transparent; }} # Fondo sección transparente
        [data-testid="stFileUploader"] section > div {{ display: none; }} # Oculta textos largos
        
        /* Botón Procesar PEQUEÑO y CENTRADO */
        div.stButton {{ text-align: center; }}                  # Contenedor centrado
        div.stButton > button {{
            background-color: {COLOR_PRIMARIO} !important;      # Color botón
            color: white !important;                            # Texto blanco
            width: 250px !important;                            # Ancho igual al selector
            margin: 0 auto;                                     # Centrado
            border-radius: 10px;                                # Bordes redondeados
        }}

        /* Quitar bordes y fondos de los iframes de componentes */
        iframe {{ border: none !important; background: transparent !important; }} 

        code {{ background-color: {COLOR_BLOQUE_CODIGO} !important; color: {COLOR_TEXTO_CODIGO} !important; }} # Resultado
    </style>
""", unsafe_allow_html=True)                                    # Inyecta el CSS

LATINO_A_AMERICANO = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'} # Mapa notas

def es_musica_obvia(linea):                                     # Detecta acordes claros
    linea_u = linea.upper()                                     # A mayúsculas
    if not linea.strip(): return False                          # Vacías no
    tiene_simbolos = re.search(r'[#B]|/|DIM|AUG|SUS|MAJ|ADD|[A-G]\d', linea_u) # Símbolos
    if tiene_simbolos: return True                              # Música
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea_u) # Notas
    palabras = re.findall(r'\w+', linea)                        # Palabras
    return (len(palabras) == 1 and len(notas_mayus) == 1) or len(set(notas_mayus)) >= 2 # Lógica

def tiene_potencial_duda(linea):                                # Detecta dudas
    return len(re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea.upper())) > 0 # Busca notas

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):   # Proceso principal
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n') # Mayúsculas
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)' # Regex
    
    def traducir_acorde(match):                                 # Traduce acorde
        raiz_amer = LATINO_A_AMERICANO.get(match.group(1), match.group(1)) # Raíz
        alt = match.group(2) or ""; cual = match.group(3) or ""; n = match.group(4) or "" # Partes
        if cual in ["M", "MIN"]: cual = "m"                     # Menor a minúscula
        return f"{raiz_amer}{alt}{cual}{n}"                     # Reconstruye

    trad = [re.sub(patron_latino, traducir_acorde, L) if i in lineas_a_procesar else L for i, L in enumerate(lineas)] # Traduce

    res = []                                                    # Apóstrofes
    patron_am = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD)?[0-9]*(?:/[A-G][#B]?)?)\b' # Regex am
    for i, linea in enumerate(trad):                            # Recorre
        if i not in lineas_a_procesar: res.append(linea); continue # Salta letra
        l_l = list(linea); aj = 0                               # Preparación
        for m in re.finditer(patron_am, linea):                 # Busca
            fin = m.end() + aj                                  # Final
            if fin < len(l_l) and l_l[fin] not in ["'", "*"]: l_l.insert(fin, "'"); aj += 1 # Inserta
            elif fin >= len(l_l): l_l.append("'"); aj += 1      # Final línea
        res.append("".join(l_l))                                # Une
    return '\n'.join(res)                                       # Todo unido

# --- INTERFAZ ---
st.title("🎸 Cancionero 2026")                                  # Título
archivo = st.file_uploader("Subir .txt", type=["txt"])          # Selector transparente centrado

if archivo:                                                     # Si hay archivo
    cont = archivo.getvalue().decode("utf-8"); l_orig = cont.split('\n') # Lee
    conf, duda = [], []; es_m = False                           # Control
    for idx, lin in enumerate(l_orig):                          # Escanea
        if es_m: es_m = False; continue                         # Salta letra
        if es_musica_obvia(lin): conf.append(idx); es_m = True  # Música
        elif tiene_potencial_duda(lin): duda.append(idx)        # Duda
    
    if duda:                                                    # Si hay dudas
        st.warning("Confirma música:")                          # Aviso
        sel = [idx for idx in duda if st.checkbox(f"L{idx+1}: {l_orig[idx].strip()}", key=idx)] # Checks
    else: sel = []                                              # Sin selección
    
    if st.button("✨ Procesar"):                                # Botón procesar centrado
        txt_fin = procesar_texto_selectivo(cont, conf + sel)    # Procesa
        st.code(txt_fin, language="text")                       # Muestra
        js = txt_fin.replace("`", "\\`").replace("$", "\\$")    # Escapa JS
        
        components.html(f"""
        <div style="display: flex; justify-content: center; background: transparent;">
            <button id="btn" style="
                padding: 12px; background: {COLOR_PRIMARIO}; color: white; 
                border: none; border-radius: 10px; cursor: pointer; 
                font-weight: bold; width: 250px; font-family: sans-serif;
            ">💾 GUARDAR / COMPARTIR</button>
        </div>
        <script>
            document.getElementById('btn').onclick = async () => {{
                const blob = new Blob([`{js}`], {{type: 'text/plain'}});
                const file = new File([blob], "PRO_{archivo.name}", {{type: 'text/plain'}});
                if (navigator.share && confirm("¿Compartir?")) {{
                    try {{ await navigator.share({{files: [file]}}); return; }} catch(e) {{}}
                }}
                const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
                a.download = "PRO_{archivo.name}"; a.click();
            }};
        </script>
        """, height=60)                                         # Botón final sin recuadro
