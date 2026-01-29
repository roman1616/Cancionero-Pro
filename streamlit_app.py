import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def es_musica_obvia(linea):
    linea_u = linea.upper()
    if not linea.strip(): return False
    # Verificamos símbolos comunes de acordes
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
    # Estandarizamos todo a MAYÚSCULAS al inicio
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n')
    
    # Patrón: Raíz + Alteración (#/B) + Cualidad (M/MAJ/etc) + Número
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1)
        alteracion = match.group(2) or ""
        cualidad = match.group(3) or ""
        numero = match.group(4) or ""
        
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        
        # Convertimos a 'm' minúscula si es menor
        if cualidad in ["M", "MIN"]:
            cualidad = "m"
            
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            linea_traducida = re.sub(patron_latino, traducir_acorde, linea)
            resultado_traduccion.append(linea_traducida)
        else:
            resultado_traduccion.append(linea)

    # Paso final: Añadir apóstrofe al estilo americano
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
    lineas_orig = contenido.split('\n')
    confirmados_auto = []
    indices_duda = []
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
            es_linea_musica_anterior = False
        else:
            es_linea_musica_anterior = False

    st.subheader("🔍 Análisis")
    st.success(f"Se detectaron {len(confirmados_auto)} líneas automáticamente.")

    seleccion_manual = []
    if indices_duda:
        st.warning("Confirma si estas líneas son música:")
        for idx in indices_duda:
            if st.checkbox(f"Renglón {idx+1}: {lineas_orig[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    
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
