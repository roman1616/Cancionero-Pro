import streamlit as st
import re
import streamlit.components.v1 as components

# 1. Configuración de página
st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# Diccionario de conversión
MAPA = {'DO': 'C', 'RE': 'D', 'MI': 'E', 'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'}

def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    res = []
    patron = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'
    for linea in lineas:
        lista = list(linea)
        for m in re.finditer(patron, linea, flags=re.IGNORECASE):
            ini, fin = m.start(), m.end()
            if ini > 0 and linea[ini-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', linea[fin:]): continue
            if re.match(r'^[a-zñáéíóú]', linea[fin:]): continue
            
            raiz_nueva = MAPA.get(m.group(1).upper(), m.group(1).upper())
            acorde = f"{raiz_nueva}{m.group(2)}"
            if not (linea[fin:].startswith("'") or linea[fin:].startswith("*")): acorde += "'"
            
            ancho = len(m.group(0))
            if linea[fin:].startswith("'") or linea[fin:].startswith("*"): ancho += 1
            sustitucion = acorde.ljust(ancho)
            for i, char in enumerate(sustitucion):
                if ini + i < len(lista): lista[ini + i] = char
        res.append("".join(lista))
    return '\n'.join(res)

# --- INTERFAZ ---
st.markdown("<h1 style='text-align: center;'>🎸 Procesador de Acordes</h1>", unsafe_allow_html=True)

# SOLUCIÓN DEFINITIVA: Área de texto manual (La más estable en Android)
st.write("Copia el texto de tu archivo (Dropbox/Drive) y pégalo aquí abajo:")
texto_entrada = st.text_area("Pegar contenido aquí:", height=200, placeholder="Escribe o pega tu canción aquí...")

if texto_entrada:
    texto_pro = procesar_texto(texto_entrada)
    
    st.subheader("Vista Previa:")
    st.code(texto_pro, language="text")

    # Botones flotantes con JS nativo para compartir/guardar
    js_txt = texto_pro.replace("`", "\\`").replace("$", "\\$")
    
    components.html(f"""
        <style>
            .bar {{ position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); display: flex; gap: 15px; z-index: 9999; }}
            .btn {{ width: 140px; height: 50px; border: none; border-radius: 25px; font-family: sans-serif; font-size: 16px; font-weight: bold; cursor: pointer; color: white; box-shadow: 0 4px 15px rgba(0,0,0,0.4); display: flex; align-items: center; justify-content: center; gap: 8px; }}
            .dl {{ background-color: #007AFF; }} .sh {{ background-color: #34C759; }}
        </style>
        <div class="bar">
            <button onclick="dl()" class="btn dl">💾 Guardar</button>
            <button onclick="sh()" class="btn sh">📤 Compartir</button>
        </div>
        <script>
            const t = `{js_txt}`;
            function dl() {{
                const b = new Blob([t], {{type: 'text/plain'}});
                const a = document.createElement('a');
                a.href = URL.createObjectURL(b);
                a.download = "cancion_procesada.txt";
                a.click();
            }}
            async function sh() {{
                const f = new File([new Blob([t])], "cancion.txt", {{type: 'text/plain'}});
                if (navigator.share) {{ 
                    try {{ await navigator.share({{ files: [f] }}); }} catch (e) {{ console.log(e); }} 
                }} else {{ alert("Usa 'Guardar'"); }}
            }}
        </script>
    """, height=100)

st.info("💡 Consejo para Android: Si tienes el archivo en Dropbox, ábrelo, selecciona todo, cópialo y pégalo aquí arriba. Es la forma más rápida y sin errores de red.")





