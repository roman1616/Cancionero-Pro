import streamlit as st
import re
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE COLORES (Cámbialos aquí) ---
COLOR_FONDO = "#0E1117"
COLOR_TEXTO = "#FFFFFF"
COLOR_PRIMARIO = "#FF4B4B"  # Botones y acentos
COLOR_BLOQUE_CODIGO = "#000000"
COLOR_TEXTO_CODIGO = "#00FF00" # Verde terminal

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Inyección de Estilos Personalizados
st.markdown(f"""
    <style>
        .stApp {{ background-color: {COLOR_FONDO}; color: {COLOR_TEXTO}; }}
        h1, h2, h3, p, span, label {{ color: {COLOR_TEXTO} !important; }}
        .stButton>button {{ 
            background-color: {COLOR_PRIMARIO}; 
            color: white; 
            border-radius: 8px;
            width: 100%;
        }}
        code {{ 
            background-color: {COLOR_BLOQUE_CODIGO} !important; 
            color: {COLOR_TEXTO_CODIGO} !important; 
        }}
    </style>
""", unsafe_allow_html=True)

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    linea_u = linea.upper()
    if not linea.strip(): return False
    tiene_simbolos = re.search(r'[#B]|/|DIM|AUG|SUS|MAJ|ADD|[A-G]\d', linea_u)
    if tiene_simbolos: return True
    if "  " in linea: return True
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea_u)
    palabras = re.findall(r'\w+', linea)
    if len(palabras) == 1 and len(notas_mayus) == 1: return True
    if len(set(notas_mayus)) >= 2: return True
    return False

def tiene_potencial_duda(linea):
    notas_mayus = re.findall(r'\b(DO|RE|MI|FA|SOL|LA|SI)\b', linea.upper())
    return len(notas_mayus) > 0

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n')
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1)
        alter = match.group(2) or ""
        cualidad = match.group(3) or ""
        num = match.group(4) or ""
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        if cualidad in ["M", "MIN"]: cualidad = "m"
        return f"{raiz_amer}{alter}{cualidad}{num}"

    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            resultado_traduccion.append(re.sub(patron_latino, traducir_acorde, linea))
        else:
            resultado_traduccion.append(linea)

    resultado_final = []
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
                    linea_lista.insert(fin, "'"); ajuste += 1
            else:
                linea_lista.append("'"); ajuste += 1
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)

# --- INTERFAZ ---
st.title("🎸 Cancionero Inteligente 2026")
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas_orig = contenido.split('\n')
    confirmados_auto, indices_duda = [], []
    es_linea_musica_anterior = False

    for idx, linea in enumerate(lineas_orig):
        if es_linea_musica_anterior:
            es_linea_musica_anterior = False
            continue
        if es_musica_obvia(linea):
            confirmados_auto.append(idx)
            es_linea_musica_anterior = True
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx)
        else:
            es_linea_musica_anterior = False

    st.subheader("🔍 Análisis")
    st.success(f"Detección automática: {len(confirmados_auto)} líneas.")

    seleccion_manual = []
    if indices_duda:
        st.warning("Confirma estas líneas:")
        for idx in indices_duda:
            if st.checkbox(f"L{idx+1}: {lineas_orig[idx].strip()}", key=idx):
                seleccion_manual.append(idx)
    
    if st.button("✨ Procesar"):
        texto_final = procesar_texto_selectivo(contenido, confirmados_auto + seleccion_manual)
        st.subheader("Resultado:")
        st.code(texto_final, language="text")

        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: {COLOR_PRIMARIO}; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer;">💾 FINALIZAR / COMPARTIR</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    if (confirm("🎵 ¿Compartir archivo?")) {{
                        if (navigator.share) {{
                            try {{ await navigator.share({{ files: [file] }}); return; }} catch(e) {{}}
                        }}
                    }}
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(blob);
                    a.download = fileName; a.click();
                }};
            </script>
        """, height=120)
