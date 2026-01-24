    # BARRA DE ACCIONES FLOTANTE (BOTONES IGUALES)
    components.html(f"""
        <style>
            .action-bar {{
                position: fixed;
                bottom: 25px;
                left: 50%;
                transform: translateX(-50%);
                display: flex;
                gap: 15px; /* Espacio entre botones */
                z-index: 9999;
            }}
            .btn {{
                width: 150px; /* Ancho fijo para que sean iguales */
                height: 50px; /* Altura fija */
                border: none;
                border-radius: 25px;
                font-family: -apple-system, system-ui, sans-serif;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center; /* Centra el texto e icono dentro del botón */
                gap: 8px;
                color: white;
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                transition: transform 0.1s;
            }}
            .btn:active {{ transform: scale(0.95); }}
            .download-btn {{ background-color: #007AFF; }}
            .share-btn {{ background-color: #34C759; }}
        </style>
        
        <div class="action-bar">
            <button id="btnDL" class="btn download-btn">💾 Guardar</button>
            <button id="btnSH" class="btn share-btn">📤 Compartir</button>
        </div>

        <script>
            const content = `{texto_js}`;
            const fileName = "{nombre_archivo}";

            document.getElementById('btnDL').onclick = () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = "PRO_" + fileName;
                a.click();
            }};

            document.getElementById('btnSH').onclick = async () => {{
                const blob = new Blob([content], {{ type: 'text/plain' }});
                const file = new File([blob], fileName, {{ type: 'text/plain' }});
                if (navigator.share) {{
                    try {{
                        await navigator.share({{ files: [file] }});
                    }} catch (err) {{ if (err.name !== 'AbortError') console.log(err); }}
                }} else {{
                    alert("Usa 'Guardar'.");
                }}
            }};
        </script>
    """, height=100)


