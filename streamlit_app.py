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

# --- MUESTRA VISUAL DE COLORES (Cuadraditos) ---
st.write("### 🎨 Paleta Activa")                                 # Título de paleta
cols = st.columns(6)                                            # Crea 6 columnas
col_data = [                                                    # Datos para los cuadritos
    ("Fondo", COLOR_FONDO), ("Texto", COLOR_TEXTO), 
    ("Prim.", COLOR_PRIMARIO), ("Cód.", COLOR_BLOQUE_CODIGO),
    ("T.Cód", COLOR_TEXTO_CODIGO), ("Sel.", COLOR_SELECTOR)
]
for i, (name, color) in enumerate(col_data):                    # Itera y dibuja
    cols[i].markdown(f"**{name}**")                             # Nombre del color
    cols[i].markdown(f'<div style="background:{color};height:20px;border-radius:4px;border:1px solid grey"></div>', unsafe_allow_html=True)

# Inyección de CSS para diseño centrado y sin fondos innecesarios
st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLOR_FONDO}; color: {COLOR_TEXTO}; }} # Fondo app
        h1, h2, h3, p, span, label {{ color: {COLOR_TEXTO} !important; text-align: center; }}  # Centra textos
        
        /* Contenedor del Selector de Archivos (SIN FONDO, ESTRECHO Y CENTRADO) */
        [data-testid="stFileUploader"] {{
            background-color: transparent !important;           # Quita fondo gris
            border: 1px dashed {COLOR_PRIMARIO};                # Borde primario
            border-radius: 10px;                                # Redondeado
            max-width: 250px;                                   # Estrecho
            margin: 0 auto;                                     # Centrado
            padding: 5px;                                       # Espaciado
        }}
        [data-testid="stFileUploader"] section {{ background-color: transparent !important; }} # Quita fondo interno
        [data-testid="stFileUploader"] section > div {{ display: none; }} # Oculta textos largos
        
        /* Botón PROCESAR (ESTRECHO Y CENTRADO) */
        div.stButton {{ text-align: center; }}                  # Centra contenedor
        div.stButton > button {{
            background-color: {COLOR_PRIMARIO} !important;      # Color primario
            color: white !important;                            # Texto blanco
            width: 250px !important;                            # Mismo ancho que selector
            margin: 0 auto;                                     # Centrado
        }}

        iframe {{ border: none !important; }}                     # Quita borde del componente JS
        code {{ background-color: {COLOR_BLOQUE_CODIGO} !important; color: {COLOR_TEXTO_CODIGO} !important; }} # Estilo código
    </style>
""", unsafe_allow_html=True)                                    # Aplica el CSS

LATINO_A_AMERICANO = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'} # Mapa notas

def es_musica_obvia(linea):                                     # Detecta acordes claros
    linea_u = linea.upper()                                     # Normaliza
    if not linea.strip(): return False                          # Vacía no
    tiene_sim = re.search(r'[#B]|/|DIM|AUG|SUS|MAJ|ADD|[A-G]\d', linea_u) # Busca símbolos
    if tiene_sim: return True                                   # Es música
    if "  " in linea: return True                               # Espacios largos = música
    notas = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea_u) # Busca notas
    pals = re.findall(r'\w+', linea)                            # Palabras
    return (len(pals) == 1 and len(notas) == 1) or len(set(notas)) >= 2 # Lógica detección

def tiene_potencial_duda(linea):                                # Detecta dudas
    return len(re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea.upper())) > 0 # Notas latinas

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):   # Función principal
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n') # Mayúsculas
    pat_lat = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)' # Regex
    
    def traducir_acorde(m):                                     # Traduce cada acorde
        raiz = LATINO_A_AMERICANO.get(m.group(1), m.group(1))   # Raíz americana
        alt = m.group(2) or ""; cual = m.group(3) or ""; n = m.group(4) or "" # Partes
        if cual in ["M", "MIN"]: cual = "m"                     # Estandariza m minúscula
        return f"{raiz}{alt}{cual}{n}"                          # Reconstruye

    trad = [re.sub(pat_lat, traducir_acorde, L) if i in lineas_a_procesar else L for i, L in enumerate(lineas)] # Mapea

    res = []                                                    # Paso apóstrofes
    pat_am = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD)?[0-9]*(?:/[A-G][#B]?)?)\b' # Regex americano
    for i, linea in enumerate(trad):                            # Recorre
        if i not in lineas_a_procesar: res.append(linea); continue # Salta letra
        lis = list(linea); aju = 0                              # Procesa caracteres
        for m in re.finditer(pat_am, linea):                    # Busca acordes
            fin = m.end() + aju                                 # Posición final
            if fin < len(lis) and lis[fin] not in ["'", "*"]: lis.insert(fin, "'"); aju += 1 # Inserta '
            elif fin >= len(lis): lis.append("'"); aju += 1     # Fin de línea
        res.append("".join(lis))                                # Une
    return '\n'.join(res)                                       # Retorna todo

# --- INTERFAZ ---
st.title("🎸 Cancionero 2026")                                  # Título
archivo = st.file_uploader("Archivo .txt", type=["txt"])         # Selector transparente y pequeño

if archivo:                                                     # Si hay archivo
    cont = archivo.getvalue().decode("utf-8"); l_orig = cont.split('\n') # Lee
    conf, duda = [], []; es_mus = False                         # Listas control
    for idx, lin in enumerate(l_orig):                          # Escanea
        if es_mus: es_mus = False; continue                     # Salta letra tras música
        if es_musica_obvia(lin): conf.append(idx); es_mus = True # Música
        elif tiene_potencial_duda(lin): duda.append(idx)        # Duda
    
    if duda:                                                    # Si hay dudas
        st.warning("¿Son música?")                              # Aviso centrado
        sel = [idx for idx in duda if st.checkbox(f"L{idx+1}: {l_orig[idx].strip()}", key=idx)] # Checks
    else: sel = []                                              # Sin selección
    
    if st.button("✨ Procesar"):                                # Botón procesar centrado
        txt_fin = procesar_texto_selectivo(cont, conf + sel)    # Ejecuta proceso
        st.code(txt_fin, language="text")                       # Muestra resultado
        js = txt_fin.replace("`", "\\`").replace("$", "\\$")    # Escapa para JS
        
        components.html(f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <button id="btn" style="
                padding: 12px 20px; background: {COLOR_PRIMARIO}; color: white; border: none; 
                border-radius: 10px; cursor: pointer; font-weight: bold; width: 250px; font-family: sans-serif;
            ">💾 GUARDAR / COMPARTIR</button>
        </div>
        <script>
            document.getElementById('btn').onclick = async () => {{
                const b = new Blob([`{js}`], {{type: 'text/plain'}});
                const f = new File([b], "PRO_{archivo.name}", {{type: 'text/plain'}});
                if (navigator.share && confirm("¿Compartir?")) {{
                    try {{ await navigator.share({{files: [f]}}); return; }} catch(e) {{}}
                }}
                const a = document.createElement('a'); a.href = URL.createObjectURL(b);
                a.download = "PRO_{archivo.name}"; a.click();
            }};
        </script>
        """, height=80)                                         # Botón final centrado y sin recuadro
