import streamlit as st
import re
import streamlit.components.v1 as components

st.set_page_config(page_title="Cancionero Pro 2026", layout="centered")

# ──────────────────── ESTILO ────────────────────
st.markdown("""
<style>
div[data-baseweb="radio"] div[aria-checked="true"] > div { background-color: #FF4B4B !important; }
div.stButton > button {
    width: 100% !important;
    background-color: #FF4B4B !important;
    color: white !important;
    border-radius: 8px !important;
    border: none !important;
    font-weight: bold !important;
    height: 45px !important;
}
div.stButton > button:hover { background-color: #E03E3E !important; }
iframe { width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────── CONSTANTES ────────────────────
LATINO_A_AMERICANO = {
    'DO': 'C', 'RE': 'D', 'MI': 'E',
    'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B',
    'DOb': 'Cb', 'REb': 'Db', 'MIb': 'Eb', 'FAb': 'Fb',
    'SOLb': 'Gb', 'LAb': 'Ab', 'SIb': 'Bb'
}

# ──────────────────── MEMORIA GLOBAL ────────────────────
if "decision_memoria" not in st.session_state:
    st.session_state.decision_memoria = {"nota_sola": None, "linea_multi": None}

if "conflict_checks" not in st.session_state:
    st.session_state.conflict_checks = {}

# ──────────────────── FUNCIONES ────────────────────
def es_linea_acordes(linea):
    tokens = linea.strip().split()
    if len(tokens) < 2:
        return False

    acordes = 0
    for t in tokens:
        if re.fullmatch(
            r'[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]{0,2}(?:/[A-G](#|b)?)?',
            t,
            re.IGNORECASE
        ):
            acordes += 1
    return acordes >= 2

def es_linea_conflictiva(linea):
    if es_linea_acordes(linea):
        return False
    return bool(re.search(r'\b[A-G]\b', linea))

def tipo_linea_ambigua(linea):
    if re.fullmatch(r'\s*[A-G]\s*', linea):
        return "nota_sola"
    return "linea_multi"

def resaltar_notas_conflictivas(linea):
    return re.sub(r'\b([A-G])\b', r'**\1**', linea)

def procesar_linea(linea, modo_origen, corregir_posicion, formato_salida):
    """
    Procesa SOLO la sección inicial de acordes de una línea.
    Si encuentra texto no-acorde, deja el resto intacto.
    """
    patron_acorde_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)(b|#)?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
    patron_acorde_amer = r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]{0,2}(?:/[A-G](#|b)?)?\b(?![a-z])'

    tokens = re.split(r'(\s+)', linea)

    procesar = True
    resultado = []

    for tok in tokens:
        if re.fullmatch(r'\s+', tok):
            resultado.append(tok)
            continue

        if not procesar:
            resultado.append(tok)
            continue

        # Traducción latino
        if modo_origen == "Latino":
            if corregir_posicion == "Activada":
                tok = re.sub(
                    r'\b(DO|RE|MI|FA|SOL|LA|SI)(M|m|MAJ|MIN|maj|min|aug|dim|sus|add)?([#b])',
                    r'\1\3\2', tok, flags=re.IGNORECASE
                )

            def traducir(match):
                raiz = match.group(1).upper()
                alt = match.group(2) or ""
                cual = match.group(3) or ""
                num = match.group(4) or ""

                nota_completa = raiz + alt
                raiz_amer = LATINO_A_AMERICANO.get(nota_completa, LATINO_A_AMERICANO.get(raiz, raiz))

                if cual.upper() == "MIN":
                    cual = "m"
                elif cual.upper() in ["M", "MAJ"]:
                    cual = ""

                return f"{raiz_amer}{cual}{num}"

            tok = re.sub(patron_acorde_latino, traducir, tok, flags=re.IGNORECASE)

        if not re.fullmatch(patron_acorde_amer, tok, re.IGNORECASE):
            procesar = False
            resultado.append(tok)
            continue

        if formato_salida == "Apostrofado":
            if not tok.endswith("'"):
                tok = tok + "'"

        resultado.append(tok)

    return "".join(resultado)

def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, modo_origen, corregir_posicion, formato_salida):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')
    resultado = []

    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            resultado.append(procesar_linea(linea, modo_origen, corregir_posicion, formato_salida))
        else:
            resultado.append(linea)

    return "\n".join(resultado)

# ──────────────────── INTERFAZ ────────────────────
st.markdown("<h1 style='text-align:center;'>🎵 Cancionero Pro</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    opt_posicion = st.radio("Posición símbolos", ["Activada", "Desactivada"])
with col2:
    opt_origen = st.radio("Cifrado entrada", ["Latino", "Americano"])
with col3:
    opt_salida = st.radio("Formato salida", ["Apostrofado", "Original"])

archivo = st.file_uploader("Sube tu archivo .txt", type=["txt"])

with st.sidebar:
    st.markdown("### Preferencias aprendidas")
    if st.button("🧹 Borrar lo recordado"):
        st.session_state.decision_memoria = {"nota_sola": None, "linea_multi": None}
        st.success("Preferencias reiniciadas")

# ──────────────────── PROCESO ────────────────────
if archivo:
    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split("\n")

    auto = [i for i, l in enumerate(lineas) if es_linea_acordes(l)]
    conflictivas = [i for i, l in enumerate(lineas) if es_linea_conflictiva(l)]

    if conflictivas:
        st.warning("⚠️ Líneas ambiguas detectadas. Decide si contienen acordes.")

        colA, colB = st.columns(2)
        with colA:
            if st.button("✅ Aceptar todas"):
                for i in conflictivas:
                    st.session_state.conflict_checks[i] = True
        with colB:
            if st.button("❌ Rechazar todas"):
                for i in conflictivas:
                    st.session_state.conflict_checks[i] = False

        st.markdown("---")

        for i in conflictivas:
            tipo = tipo_linea_ambigua(lineas[i])
            default = st.session_state.decision_memoria.get(tipo, False)

            marcado = st.checkbox(
                f"Línea {i+1}: {resaltar_notas_conflictivas(lineas[i])}",
                value=st.session_state.conflict_checks.get(i, default),
                key=f"chk_{i}"
            )
            st.session_state.conflict_checks[i] = marcado

    # ──────────────────── CHECKBOX DE CONFIRMACIÓN GENERAL ────────────────────
    procesar_ok = st.checkbox(
        "✅ Confirmo que las líneas seleccionadas deben procesarse",
        value=False
    )

    # ──────────────────── BOTÓN PROCESAR ────────────────────
    if st.button("✨ PROCESAR"):

        if not procesar_ok:
            st.error("Debes confirmar antes de procesar.")
        else:
            if conflictivas and not any(st.session_state.conflict_checks.get(i, False) for i in conflictivas):
                st.warning("Marca al menos una línea conflictiva para procesarla.")
            else:
                for i, v in st.session_state.conflict_checks.items():
                    tipo = tipo_linea_ambigua(lineas[i])
                    st.session_state.decision_memoria[tipo] = v

                lineas_finales = set(auto) | {i for i, v in st.session_state.conflict_checks.items() if v}

                texto_final = procesar_texto_selectivo(
                    contenido,
                    lineas_finales,
                    opt_origen,
                    "Activada" if opt_posicion == "Activada" else "Desactivada",
                    opt_salida
                )

                st.code(texto_final, language="text")

                texto_js = (
                    texto_final
                    .replace("\\", "\\\\")
                    .replace("`", "\\`")
                    .replace("$", "\\$")
                )

                components.html(
                    f"""
                    <button id="actionBtn"
                        style="
                            width:100%;
                            height:45px;
                            background-color:#FF4B4B;
                            color:white;
                            border:none;
                            border-radius:8px;
                            cursor:pointer;
                            font-weight:bold;
                            font-family:sans-serif;
                        ">
                        💾 GUARDAR Y COMPARTIR
                    </button>

                    <script>
                        const btn = document.getElementById('actionBtn');

                        btn.onclick = async () => {{
                            const blob = new Blob([`{texto_js}`], {{ type: 'text/plain' }});
                            const file = new File([blob], "{archivo.name}", {{ type: 'text/plain' }});

                            if (confirm("🎵 ¿Deseas COMPARTIR el archivo?")) {{
                                if (navigator.share) {{
                                    try {{
                                        await navigator.share({{ files: [file] }});
                                        return;
                                    }} catch (e) {{}}
                                }} else {{
                                    alert("La opción compartir funciona mejor en móvil.");
                                }}
                            }}

                            if (confirm("💾 ¿Deseas DESCARGAR el archivo?")) {{
                                const a = document.createElement('a');
                                a.href = URL.createObjectURL(blob);
                                a.download = "{archivo.name}";
                                a.click();
                                URL.revokeObjectURL(a.href);
                            }}
                        }};
                    </script>
                    """,
                    height=60
                )
