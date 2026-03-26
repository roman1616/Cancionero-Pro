# ───────── BUSCAR / REEMPLAZAR ─────────
if st.session_state.texto_reemplazado:

    st.markdown("### 🔎 Buscar y Reemplazar")

    colb, colr = st.columns(2)
    with colb:
        buscar = st.text_input(
            "Buscar (Regex)",
            value="([A-G])'#"
        )
    with colr:
        reemplazar = st.text_input(
            "Reemplazar por",
            value="\\1#'"
        )

    if st.button("Aplicar reemplazo", key="btn_replace"):
        if buscar:
            st.session_state.texto_reemplazado = re.sub(
                buscar,
                reemplazar,
                st.session_state.texto_reemplazado
            )

    # Mostrar el texto reemplazado
    texto_final = st.session_state.texto_reemplazado
    st.code(texto_final, language="text")

    # Preparar texto para descarga/compartir
    texto_js = (
        texto_final
        .replace("\\", "\\\\")
        .replace("`", "\\`")
        .replace("$", "\\$")
    )

    # Botón de guardar/compartir
    if archivo:
        components.html(
            f"""
            <button id="actionBtn"
                style="width:100%; height:45px; background-color:#FF4B4B; color:white; border:none; border-radius:8px; cursor:pointer; font-weight:bold; font-family:sans-serif;">
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
