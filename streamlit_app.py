import streamlit as st

st.markdown("<style>.alerta-naranja {background-color: #FFA500; padding: 10px; border-radius: 5px; color: black; font-weight: bold;}</style>", unsafe_allow_html=True)

CONVERSION = {"DO": "C", "RE": "D", "MI": "E", "FA": "F", "SOL": "G", "LA": "A", "SI": "B"}

st.title("🎸 Validador Visual de Conflictos")
texto_bruto = st.text_area("Editor:", height=200)

if texto_bruto:
    lineas = texto_bruto.split('\n')
    for i, linea in enumerate(lineas):
        palabras = linea.upper().split()
        notas_detectadas = [p for p in palabras if p in CONVERSION]
        
        # Lógica de conflicto
        es_impar = (i + 1) % 2 != 0
        hay_conflicto = (es_impar and not notas_detectadas) or (not es_impar and notas_detectadas)
        
        col_check, col_texto = st.columns([0.1, 0.9])
        with col_check:
            es_nota = st.checkbox("", value=es_impar, key=f"v_{i}")
        with col_texto:
            if hay_conflicto:
                st.markdown(f'<div class="alerta-naranja">⚠️ Revisar: {linea}</div>', unsafe_allow_html=True)
            else:
                st.write(linea)
