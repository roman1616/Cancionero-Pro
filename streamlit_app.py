import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# --- BLOQUE CSS: CAMBIA EL COLOR DEL CUADRO DE ÉXITO AQUÍ ---
st.markdown("""
    <style>
    /* Personaliza el cuadro st.success (el que dice 'Se detectaron X líneas...') */
    div[data-testid="stNotificationV2"]:has(div[aria-label="success"]) {
        background-color: #007AFF !important; /* Fondo Azul Pro */
        color: #FFFFFF !important;           /* Texto Blanco */
        border-radius: 10px;
        border: none;
    }
    
    /* Icono dentro del cuadro de éxito */
    div[data-testid="stNotificationV2"]:has(div[aria-label="success"]) svg {
        fill: white !important;
    }

    /* Opcional: Personaliza el cuadro de advertencia (st.warning) */
    div[data-testid="stNotificationV2"]:has(div[aria-label="warning"]) {
        background-color: #FF9500 !important; /* Naranja Pro */
        color: white !important;
        border-radius: 10px;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# ... (Resto del código de lógica de notas igual que antes)

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
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    def traducir_acorde(match):
        raiz_lat = match.group(1).upper()
        cualidad = match.group(2) or ""
        alteracion = match.group(3) or ""
        numero = match.group(4) or ""
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"
    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            resultado_traduccion.append(re.sub(patron_latino, traducir_acorde, linea))
        else:
            resultado_traduccion.append(linea)
    resultado_final = []
    patron_americano = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'
    for i, linea in enumerate(resultado_traduccion):
        if i not in lineas_a_procesar:
            resultado_final.append(linea); continue
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
st.title("🎸 Cancionero Inteligente")
archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split('\n')
    confirmados_auto = []
    indices_duda = []
    es_linea_musica_anterior = False

    for idx, linea in enumerate(lineas):
        if es_linea_musica_anterior:
            es_linea_musica_anterior = False; continue
        if es_musica_obvia(linea):
            confirmados_auto.append(idx); es_linea_musica_anterior = True
        elif tiene_potencial_duda(linea):
            indices_duda.append(idx); es_linea_musica_anterior = False
        else:
            es_linea_musica_anterior = False

    st.subheader("🔍 Análisis")
    # AQUÍ ESTÁ EL CUADRO QUE CAMBIA DE COLOR CON EL CSS DE ARRIBA
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
                        if (navigator.share) {{ try {{ await navigator.share({{ files: [file] }}); return; }} catch(e) {{}} }}
                    }}
                    if (confirm("💾 ¿Deseas DESCARGAR el archivo?")) {{
                        const a = document.createElement('a'); a.href = URL.createObjectURL(blob); a.download = fileName; a.click();
                    }}
                }};
            </script>
        """, height=120)
