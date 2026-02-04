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
    'FA': 'F', 'SOL': 'G', 'LA': 'A', 'SI': 'B'
}

# ──────────────────── MEMORIA GLOBAL ────────────────────
if "decision_memoria" not in st.session_state:
    st.session_state.decision_memoria = {
        "nota_sola": None,
        "linea_multi": None
    }

if "conflict_checks" not in st.session_state:
    st.session_state.conflict_checks = {}

if "archivo_actual" not in st.session_state:
    st.session_state.archivo_actual = None

# ──────────────────── FUNCIONES ────────────────────
def es_linea_acordes(linea):
    tokens = linea.strip().split()
    if len(tokens) < 2:
        return False

    acordes = 0
    for t in tokens:
        if re.fullmatch(
            r'[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?:/[A-G](#|b)?)?',
            t,
            re.IGNORECASE
        ):
            acordes += 1

    return acordes >= 2


def es_linea_conflictiva(linea):
    if es_linea_acordes(linea):
        return False

    return bool(
        re.search(r'\b[A-G]\b', linea)
        and not re.search(
            r'\b[A-G](#|b|m|maj|min|dim|aug|sus|add|[0-9]|/)',
            linea,
            re.IGNORECASE
        )
    )


def tipo_linea_ambigua(linea):
    if re.fullmatch(r'\s*[A-G]\s*', linea):
        return "nota_sola"
    return "linea_multi"


def resaltar_notas_conflictivas(linea):
    return re.sub(r'\b([A-G])\b', r'**\1**', linea)


def procesar_texto_selectivo(texto_bruto, lineas_a_procesar, modo_origen, corregir_posicion, formato_salida):
    lineas = texto_bruto.replace('\r\n', '\n').split('\n')

    # 1. Corrección de posición
    if corregir_posicion == "Activada":
        patron_pos = r'\b(DO|RE|MI|FA|SOL|LA|SI)(M|m|MAJ|MIN|maj|min|aug|dim|sus|add)?([#b])'
        for i in range(len(lineas)):
            if i in lineas_a_procesar:
                lineas[i] = re.sub(patron_pos, r'\1\3\2', lineas[i], flags=re.IGNORECASE)

    # 2. Traducción Latino → Americano
    resultado_intermedio = []
    if "Latino" in modo_origen:
        patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#b])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'

        def traducir(match):
            raiz = LATINO_A_AMERICANO[match.group(1).upper()]
            alt = match.group(2) or ""
            cual = match.group(3) or ""
            num = match.group(4) or ""
            if cual.upper() == "MIN":
                cual = "m"
            elif cual.upper() in ["M", "MAJ"]:
                cual = ""
            return f"{raiz}{alt}{cual}{num}"

        for i, l in enumerate(lineas):
            if i in lineas_a_procesar:
                resultado_intermedio.append(re.sub(patron_latino, traducir, l, flags=re.IGNORECASE))
            else:
                resultado_intermedio.append(l)
    else:
        resultado_intermedio = lineas

    if formato_salida == "Original":
        return "\n".join(resultado_intermedio)

    # 3. Apostrofado
    patron_acorde = r'\b[A-G](#|b)?(m|maj|min|dim|aug|sus|add)?[0-9]?(?:/[A-G](#|b)?)?\b'
    resultado_final = []

    for i, linea in enumerate(resultado_intermedio):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue

        chars = list(linea)
        matches = list(re.finditer(patron_acorde, linea, re.IGNORECASE))

        for m in reversed(matches):
            fin = m.end()
            if fin < len(chars):
                if chars[fin] not in ["'", "*"]:
                    chars.insert(fin, "'")
            else:
                chars.append("'")

        resultado_final.append("".join(chars))

    return "\n".join(resultado_final)

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
        st.session_state.conflict_checks = {}
        st.success("Preferencias reiniciadas")

# ──────────────────── PROCESO ────────────────────
if archivo:
    # Reset si cambia el archivo
    if st.session_state.archivo_actual != archivo.name:
        st.session_state.archivo_actual = archivo.name
        st.session_state.conflict_checks = {}

    contenido = archivo.getvalue().decode("utf-8")
    lineas = contenido.split("\n")

    auto = [i for i, l in enumerate(lineas) if es_linea_acordes(l)]
    conflictivas = [i for i, l in enumerate(lineas) if es_linea_conflictiva(l)]

    procesar_todo = st.checkbox("⚙️ Procesar TODO (sin seleccionar líneas)", value=False)

    if conflictivas:
        st.warning("⚠️ Líneas

