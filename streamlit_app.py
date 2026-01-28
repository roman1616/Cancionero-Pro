import streamlit as st

st.set_page_config(page_title="Clasificador Musical", layout="wide")
CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B"}

if "texto_bruto" not in st.session_state:
    st.session_state.texto_bruto = ""

st.title("🎸 Clasificador de Notas y Letras")
st.session_state.texto_bruto = st.text_area("Pega el texto aquí:", value=st.session_state.texto_bruto, height=200)

if st.session_state.texto_bruto:
    st.subheader("Selecciona las líneas que son NOTAS:")
    lineas = [l.strip() for l in st.session_state.texto_bruto.split('\n') if l.strip()]
    decisiones = []

    for i, oracion in enumerate(lineas):
        col_check, col_texto = st.columns([0.1, 0.9])
        with col_check:
            es_nota = st.checkbox("", value=((i+1)%2!=0), key=f"check_{i}")
        with col_texto:
            st.markdown(f"**{oracion}**")
        decisiones.append((oracion, es_nota))

    if st.button("⚙️ Procesar"):
        resultado = []
        for texto, marca_nota in decisiones:
            if marca_nota:
                conv = "   ".join([CONVERSION.get(p.upper(), p) for p in texto.split()])
                resultado.append(conv)
            else:
                resultado.append(texto)
        st.code("\n".join(resultado))
