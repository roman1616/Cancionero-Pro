import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 
    'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

def obtener_candidatos(texto):
    # Busca notas latinas (RE, MI, SOL, LA, SI) que podrían ser palabras
    patron = r'\b(RE|MI|SOL|LA|SI)(?:m|maj|min|aug|dim|sus|add|M)?(?:[#b])?(?:[0-9]*)?\b'
    candidatos = re.findall(patron, texto, flags=re.IGNORECASE)
    # Limpiamos duplicados y devolvemos lista única
    return sorted(list(set([c.upper() for c in candidatos])))

def procesar_texto_final(texto_bruto, notas_confirmadas):
    if not texto_bruto: return ""
    
    # --- BLOQUE 1: NORMALIZACIÓN ---
    texto = texto_bruto.replace('\r\n', '\n')
    
    # --- BLOQUE 2: CONVERSIÓN CONTROLADA ---
    # Solo convertimos si la raíz está en notas_confirmadas o es DO/FA (seguras)
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(m|maj|min|aug|dim|sus|add|M)?([#b])?([0-9]*)'
    
    def traducir(match):
        raiz_lat = match.group(1).upper()
        # Si es una nota dudosa y NO fue confirmada, se deja igual
        if raiz_lat in ['RE', 'MI', 'SOL', 'LA', 'SI'] and raiz_lat not in notas_confirmadas:
            return match.group(0)
            
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        cualidad = match.group(2) or ""
        alteracion = match.group(3) or ""
        numero = match.group(4) or ""
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    lineas = texto.split('\n')
    texto_convertido = [re.sub(patron_latino, traducir, l, flags=re.IGNORECASE) for l in lineas]

    # --- BLOQUE 3: APÓSTROFES ---
    resultado_final = []
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for linea in texto_convertido:
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_final, linea):
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
st.title("🎸 Cancionero Pro: Selección Manual")

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    
    # 1. Encontrar candidatos dudosos
    dudosos = obtener_candidatos(contenido)
    
    st.subheader("🔎 Paso 1: Confirmar cambios")
    st.info("He detectado estas posibles notas. Selecciona solo las que REALMENTE sean acordes musicales:")
    
    # Selector visual
    confirmados = st.multiselect(
        "Notas a transformar:",
        options=dudosos,
        default=[],
        help="Las notas que no selecciones se mantendrán como texto original (ej: 'la' se quedará como 'la' y no como 'A'')."
    )

    if st.button("✅ Procesar y Generar Archivo"):
        # Procesar (DO y FA se procesan siempre por defecto internamente)
        texto_final = procesar_texto_final(contenido, confirmados)
        
        st.subheader("📝 Vista Previa Final:")
        st.code(texto_final, language="text")

        # JavaScript para descarga y compartir
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <style>
                .bar {{ position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); display: flex; gap: 10px; }}
                .btn {{ padding: 12px 20px; border: none; border-radius: 15px; color: white; font-weight: bold; cursor: pointer; }}
                .dl {{ background: #007AFF; }} .sh {{ background: #34C759; }}
            </style>
            <div class="bar">
                <button id="dl" class="btn dl">💾 Guardar PRO</button>
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
