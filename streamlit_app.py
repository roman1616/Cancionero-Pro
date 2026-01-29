import streamlit as st                                          # Importa framework de interfaz
import re                                                       # Importa librería de expresiones regulares
import streamlit.components.v1 as components                     # Importa componentes para HTML/JS

# --- CONFIGURACIÓN DE COLORES ---
COLOR_FONDO = "#0E1117"                                         # Fondo de la aplicación
COLOR_TEXTO = "#FFFFFF"                                         # Texto general
COLOR_PRIMARIO = "#FF4B4B"                                      # Botones y acentos
COLOR_BLOQUE_CODIGO = "#000000"                                 # Fondo del resultado
COLOR_TEXTO_CODIGO = "#00FF00"                                  # Texto del resultado
COLOR_SELECTOR = "#1E1E1E"                                      # Fondo del área de subida

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered") # Configura la página

# Inyección de CSS para tunear el File Uploader y el resto de la interfaz
st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLOR_FONDO}; color: {COLOR_TEXTO}; }} # Color de fondo app
        h1, h2, h3, p, span, label {{ color: {COLOR_TEXTO} !important; }}  # Color de textos
        
        /* Estilo para el contenedor del Selector de Archivos */
        [data-testid="stFileUploader"] {{
            background-color: {COLOR_SELECTOR};                 # Color de fondo del selector
            border: 2px dashed {COLOR_PRIMARIO};                # Borde punteado del color primario
            border-radius: 15px;                                # Bordes redondeados
            padding: 10px;                                      # Espaciado interno
        }}
        
        /* Cambia el color del botón "Browse files" dentro del selector */
        [data-testid="stFileUploader"] button {{
            background-color: {COLOR_PRIMARIO} !important;      # Color del botón interno
            color: white !important;                            # Color texto botón interno
            border: none !important;                            # Quita borde
        }}

        .stButton>button {{ background-color: {COLOR_PRIMARIO}; color: white; border-radius: 8px; width: 100%; }} # Botón procesar
        code {{ background-color: {COLOR_BLOQUE_CODIGO} !important; color: {COLOR_TEXTO_CODIGO} !important; }} # Bloque código
    </style>
""", unsafe_allow_html=True)                                    # Renderiza el CSS

LATINO_A_AMERICANO = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'} # Mapa de notas

def es_musica_obvia(linea):                                     # Detecta líneas de acordes
    linea_u = linea.upper()                                     # Normaliza a mayúsculas
    if not linea.strip(): return False                          # Ignora líneas vacías
    tiene_simbolos = re.search(r'[#B]|/|DIM|AUG|SUS|MAJ|ADD|[A-G]\d', linea_u) # Busca símbolos
    if tiene_simbolos: return True                              # Si hay símbolos, es música
    if "  " in linea: return True                               # Si hay huecos, es música
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea_u) # Busca nombres notas
    palabras = re.findall(r'\w+', linea)                        # Cuenta palabras
    if len(palabras) == 1 and len(notas_mayus) == 1: return True # Una nota sola
    if len(set(notas_mayus)) >= 2: return True                  # Varias notas latinas
    return False                                                # No es música

def tiene_potencial_duda(linea):                                # Detecta dudas
    return len(re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea.upper())) > 0 # Busca notas

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):   # Función procesadora
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n') # Mayúsculas y split
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)' # Regex latino
    
    def traducir_acorde(match):                                 # Traduce acorde individual
        raiz_amer = LATINO_A_AMERICANO.get(match.group(1), match.group(1)) # Traduce raíz
        alter = match.group(2) or ""; cualidad = match.group(3) or ""; num = match.group(4) or "" # Partes
        if cualidad in ["M", "MIN"]: cualidad = "m"             # m minúscula para menor
        return f"{raiz_amer}{alter}{cualidad}{num}"             # Arma el acorde

    resultado_traduccion = [re.sub(patron_latino, traducir_acorde, L) if i in lineas_a_procesar else L for i, L in enumerate(lineas)] # Traduce notas

    res_final = []                                              # Lista para apóstrofes
    patron_am = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD)?[0-9]*(?:/[A-G][#B]?)?)\b' # Regex americano
    for i, linea in enumerate(resultado_traduccion):            # Recorre traducidas
        if i not in lineas_a_procesar: res_final.append(linea); continue # Si no es música, pasa
        l_lista = list(linea); ajuste = 0                       # Prepara inserción
        for m in re.finditer(patron_am, linea):                 # Busca cada acorde
            fin = m.end() + ajuste                              # Fin del acorde
            if fin < len(l_lista) and l_lista[fin] not in ["'", "*"]: l_lista.insert(fin, "'"); ajuste += 1 # Inserta apóstrofe
            elif fin >= len(l_lista): l_lista.append("'"); ajuste += 1 # Al final de línea
        res_final.append("".join(l_lista))                      # Une línea
    return '\n'.join(res_final)                                 # Retorna todo unido

# --- INTERFAZ ---
st.title("🎸 Cancionero Inteligente 2026")                      # Título
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"]) # El selector con estilo nuevo

if archivo:                                                     # Si hay archivo
    cont = archivo.getvalue().decode("utf-8"); l_orig = cont.split('\n') # Lee contenido
    conf, duda = [], []; es_mus = False                         # Listas de control
    for idx, lin in enumerate(l_orig):                          # Escanea líneas
        if es_mus: es_mus = False; continue                     # Si anterior fue música, salta letra
        if es_musica_obvia(lin): conf.append(idx); es_mus = True # Música confirmada
        elif tiene_potencial_duda(lin): duda.append(idx)        # Duda
    
    st.subheader("🔍 Análisis")                                 # Título sección
    if duda:                                                    # Si hay dudas
        st.warning("Confirma estas líneas:")                    # Aviso
        sel = [idx for idx in duda if st.checkbox(f"L{idx+1}: {l_orig[idx].strip()}", key=idx)] # Checkboxes
    else: sel = []                                              # No hay selección manual
    
    if st.button("✨ Procesar"):                                # Botón acción
        txt_fin = procesar_texto_selectivo(cont, conf + sel)    # Procesa
        st.code(txt_fin, language="text")                       # Muestra
        js = txt_fin.replace("`", "\\`").replace("$", "\\$")    # Escapa para JS
        components.html(f"""<div style="text-align: center;"><button id="btn" style="padding: 15px; background: {COLOR_PRIMARIO}; color: white; border: none; border-radius: 12px; cursor: pointer; font-weight: bold;">💾 GUARDAR / COMPARTIR</button></div>
        <script>document.getElementById('btn').onclick = async () => {{
            const blob = new Blob([`{js}`], {{type: 'text/plain'}});
            const file = new File([blob], "PRO_{archivo.name}", {{type: 'text/plain'}});
            if (navigator.share && confirm("¿Compartir?")) await navigator.share({{files: [file]}});
            else {{ const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = "PRO_{archivo.name}"; a.click(); }}
        }};</script>""", height=100)                             # Componente JS de descarga
