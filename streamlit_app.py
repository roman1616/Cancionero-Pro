import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

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
        return f"{LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)}{alteracion}{cualidad}{numero}"

    resultado_final = []
    patron_final = r'\b([A-G][#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[A-G][#b]?)?)\b'

    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            nueva_linea = re.sub(patron_latino, traducir_acorde, linea)
            linea_lista = list(nueva_linea)
            ajuste = 0
            for m in re.finditer(patron_final, nueva_linea):
                fin = m.end() + ajuste
                if fin < len(linea_lista) and linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
                elif fin >= len(linea_lista):
                    linea_lista.append("'")
                    ajuste += 1
            resultado_final.append("".join(linea_lista))
        else:
            resultado_final.append(linea)
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

    st.subheader("🔍 Informe de Escaneo")
    st.success(f"Se detectaron {len(confirmados_auto)} líneas de acordes automáticamente.")

    seleccion_manual = []
    if indices_duda:
        st.warning("Marca solo las notas musicales")
        for idx in indices_duda:
            if st.checkbox(f"Renglón {idx+1}: {lineas[idx].strip()}", value=False, key=idx):
                seleccion_manual.append(idx)
    
    if st.button("✨ Procesar y Convertir"):
        total_indices = confirmados_auto + seleccion_manual
        texto_final = procesar_texto_selectivo(contenido, total_indices)
        
        st.subheader("Resultado Final:")
        st.code(texto_final, language="text")

        # --- JS CON DOBLE CUADRO DE ACEPTACIÓN ---
        texto_js = texto_final.replace("`", "\\`").replace("$", "\\$")
        components.html(f"""
            <div style="text-align: center; margin-top: 20px;">
                <button id="actionBtn" style="padding: 15px 30px; background: #007AFF; color: white; border: none; border-radius: 12px; font-weight: bold; cursor: pointer; font-size: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">💾 FINALIZAR ARCHIVO</button>
            </div>
            <script>
                document.getElementById('actionBtn').onclick = async () => {{
                    const contenido = `{texto_js}`;
                    const fileName = "PRO_{archivo.name}";
                    const blob = new Blob([contenido], {{ type: 'text/plain' }});
                    const file = new File([blob], fileName, {{ type: 'text/plain' }});
                    
                    // 1. PRIMER CUADRO: COMPARTIR
                    const deseaCompartir = confirm("🎵 COMPARTIR 🎵\\n\\n¿Deseas enviar el archivo por WhatsApp u otra App?");
                    
                    if (deseaCompartir) {{
                        if (navigator.share && navigator.canShare({{ files: [file] }})) {{
                            try {{
                                await navigator.share({{ files: [file] }});
                                return; // Éxito
                            }} catch (e) {{ console.log("Error al compartir"); }}
                        }} else {{
                            alert("Tu dispositivo no soporta la función de compartir archivos.");
                        }}
                    }}

                    // 2. SEGUNDO CUADRO: DESCARGAR (Solo si el anterior fue 'No' o falló)
                    const deseaDescargar = confirm("💾 DESCARGAR 💾\\n\\n¿Deseas guardar el archivo directamente en tu equipo?");
                    
                    if (deseaDescargar) {{
                        const a = document.createElement('a');
                        a.href = URL.createObjectURL(blob);
                        a.download = fileName;
                        a.click();
                    }}
                }};
            </script>
        """, height=120)
