import streamlit as st
import re
import streamlit.components.v1 as components

# Configuración
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

LATINO_A_AMERICANO = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'}

def transformar_linea(linea):
    """Procesa una sola línea de texto"""
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'
    linea_lista = list(linea)
    for match in re.finditer(patron_universal, linea, flags=re.IGNORECASE):
        acorde_original = match.group(0)
        raiz_orig = match.group(1).upper()
        resto_acorde = match.group(2)
        inicio, fin = match.start(), match.end()
        
        lo_que_sigue = linea[fin:]
        if inicio > 0 and linea[inicio-1].isalpha(): continue
        if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
        if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

        raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
        nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
        if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*")):
            nuevo_acorde += "'"

        ancho_original = len(acorde_original)
        if lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*"):
            ancho_original += 1
        
        sustitucion = nuevo_acorde.ljust(ancho_original)
        for i, char in enumerate(sustitucion):
            if inicio + i < len(linea_lista):
                linea_lista[inicio + i] = char
    return "".join(linea_lista)

# Interfaz
st.markdown("<h1 style='text-align: center;'>🎹 Cancionero Pro</h1>", unsafe_allow_html=True)

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"], label_visibility="collapsed")

if archivo:
    # Leemos todas las líneas
    lineas_originales = archivo.getvalue().decode("utf-8").splitlines()
    total_lineas = len(lineas_originales)
    
    st.markdown("### 📝 Selección de Renglones")
    
    # Creamos las opciones para el selector
    opciones = [i for i in range(total_lineas)]
    # Pre-seleccionamos desde el renglón 7 (índice 6) hasta el final
    predeterminados = [i for i in range(6, total_lineas)]
    
    seleccionadas = st.multiselect(
        "Renglones a procesar (por defecto desde el 7):",
        options=opciones,
        default=predeterminados,
        format_func=lambda x: f"Renglón {x+1}: {lineas_originales[x][:50]}..."
    )

    if st.button("🚀 Procesar y Generar"):
        resultado = []
        for i, linea in enumerate(lineas_originales):
            if i in seleccionadas:
                resultado.append(transformar_linea(linea))
            else:
                resultado.append(linea)
        
        texto_final = "\n".join(resultado)
        st.subheader("Vista Previa:")
        st.code(texto_final, language="text")

        # JavaScript para descarga y compartir
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <style>
                .action-bar {{ position: fixed; bottom: 25px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 999; }}
                .btn {{ width: 140px; height: 48px; border: none; border-radius: 24px; font-weight: bold; cursor: pointer; color: white; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }}
                .dl {{ background: #007AFF; }} .sh {{ background: #34C759; }}
            </style>
            <div class="action-bar">
                <button id="dl" class="btn dl">💾 Guardar</button>
                <button id="sh" class="btn sh">📤 Compartir</button>
            </div>
            <script>
                const content = `{texto_js}`;
                document.getElementById('dl').onclick = () => {{
                    const b = new Blob([content], {{type:'text/plain;charset=utf-8'}});
                    const a = document.createElement('a');
                    a.href = URL.createObjectURL(b); a.download = "PRO_{archivo.name}"; a.click();
                }};
                document.getElementById('sh').onclick = async () => {{
                    const b = new Blob([content], {{type:'text/plain;charset=utf-8'}});
                    const file = new File([b], "{archivo.name}", {{type:'text/plain'}});
                    if(navigator.share) await navigator.share({{files: [file]}});
                }};
            </script>
        """, height=100)
