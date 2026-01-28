import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def obtener_lista_acordes(texto):
    # Detecta posibles acordes latinos para pedir confirmación
    patron = r'\b(DO|RE|MI|FA|SOL|LA|SI)(?:m|maj|min|aug|dim|sus|add|M)?(?:[#b])?(?:[0-9]*)?\b'
    matches = re.finditer(patron, texto, flags=re.IGNORECASE)
    # Guardamos el texto exacto encontrado y su posición para que el usuario sepa qué es
    encontrados = []
    for m in matches:
        encontrados.append(m.group(0))
    return sorted(list(set(encontrados))) # Retorna lista única de términos encontrados

def procesar_texto_selectivo(texto_bruto, items_aprobados):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN UTF-8 ---
    texto = texto_bruto.replace('\r\n', '\n')
    
    # --- BLOQUE 2: CONVERSIÓN DE CIFRADO ---
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir_acorde(match):
        texto_original = match.group(0)
        # SI el texto exacto no fue aprobado por el usuario, se queda igual
        if texto_original not in items_aprobados:
            return texto_original
            
        raiz_lat = match.group(1).upper()
        cualidad = match.group(2) or ""
        alteracion = match.group(3) or ""
        numero = match.group(4) or ""
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    lineas = texto.split('\n')
    texto_convertido = [re.sub(patron_latino, traducir_acorde, l, flags=re.IGNORECASE) for l in lineas]

    # --- BLOQUE 3: COLOCACIÓN DE APÓSTROFES ---
    resultado_final = []
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for linea in texto_convertido:
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_final, linea):
            # Solo ponemos apóstrofe a lo que se convirtió (o ya era americano)
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
st.title("🎸 Cancionero Pro 2026")

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    
    # 1. Escaneo de candidatos
    candidatos = obtener_lista_acordes(contenido)
    
    if candidatos:
        st.subheader("Confirmación de Notas Musicales")
        st.write("Selecciona los elementos que son **acordes** (los que no marques se tratarán como texto normal):")
        
        # Crear un grid de checkboxes para que sea fácil seleccionar
        cols = st.columns(3)
        aprobados = []
        for i, cand in enumerate(candidatos):
            with cols[i % 3]:
                # Por defecto marcamos los que tienen símbolos (m, #, 7) porque casi seguro son notas
                es_nota_probable = any(char in cand.lower() for char in ['m', '#', 'b', '7', '4', 's'])
                if st.checkbox(f"Convertir '{cand}'", value=es_nota_probable, key=cand):
                    aprobados.append(cand)
        
        if st.button("Procesar Cambios"):
            texto_final = procesar_texto_selectivo(contenido, aprobados)
            
            st.subheader("Vista Previa:")
            st.code(texto_final, language="text")

            # --- ACCIONES ---
            texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
            components.html(f"""
                <style>
                    .action-bar {{ position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; }}
                    .btn {{ width: 140px; height: 45px; border: none; border-radius: 20px; font-weight: bold; cursor: pointer; color: white; }}
                    .dl {{ background: #007AFF; }} .sh {{ background: #34C759; }}
                </style>
                <div class="action-bar">
                    <button id="dl" class="btn dl">💾 Guardar</button>
                    <button id="sh" class="btn sh">📤 Compartir</button>
                </div>
                <script>
                    const txt = `{texto_js}`;
                    document.getElementById('dl').onclick = () => {{
                        const b = new Blob([txt], {{type:'text/plain'}});
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                    }};
                    document.getElementById('sh').onclick = async () => {{
                        const b = new Blob([txt], {{type:'text/plain'}});
                        const f = new File([b], "{archivo.name}", {{type:'text/plain'}});
                        if(navigator.share) await navigator.share({{files:[f]}});
                    }};
                </script>
            """, height=100)
    else:
        st.warning("No se detectaron notas latinas en el archivo.")
