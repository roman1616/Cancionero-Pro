def procesar_texto(texto):
    if not texto: return ""
    lineas = texto.split('\n')
    resultado_final = []
    
    # Patrón mejorado para capturar la raíz y TODO lo que sigue como parte del acorde
    patron_universal = r'(do|re|mi|fa|sol|la|si|[a-gA-G])([#b]?(?:m|maj|min|aug|dim|sus|add|M)?[0-9]*(?:/[a-gA-G][#b]?)?)'

    for linea in lineas:
        linea_lista = list(linea)
        # Usamos reversed para no alterar los índices de la línea al modificar caracteres
        matches = list(re.finditer(patron_universal, linea, flags=re.IGNORECASE))
        
        for match in matches:
            acorde_original = match.group(0)
            raiz_orig = match.group(1).upper()
            resto_acorde = match.group(2)
            inicio, fin = match.start(), match.end()
            
            # --- FILTROS ANTI-FRASES ---
            lo_que_sigue = linea[fin:]
            if inicio > 0 and linea[inicio-1].isalpha(): continue
            if re.match(r'^ +[a-zñáéíóú]', lo_que_sigue): continue
            if re.match(r'^[a-zñáéíóú]', lo_que_sigue): continue

            # --- CONVERSIÓN ---
            raiz_nueva = LATINO_A_AMERICANO.get(raiz_orig, raiz_orig)
            
            # UNIMOS TODO PRIMERO: Raíz + Resto (Ej: F + m#)
            nuevo_acorde = f"{raiz_nueva}{resto_acorde}"
            
            # AHORA AÑADIMOS EL APÓSTROFE AL FINAL DEL TODO
            # Verificamos si ya tiene apóstrofe o asterisco para no duplicar
            if not (lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*")):
                nuevo_acorde += "'"

            # --- MANTENER POSICIÓN Y REEMPLAZAR ---
            # Calculamos el ancho ocupado en la línea original para sobreescribir
            ancho_a_reemplazar = len(acorde_original)
            if lo_que_sigue.startswith("'") or lo_que_sigue.startswith("*"):
                ancho_a_reemplazar += 1
            
            sustitucion = nuevo_acorde.ljust(ancho_a_reemplazar)

            for i, char in enumerate(sustitucion):
                if inicio + i < len(linea_lista):
                    linea_lista[inicio + i] = char
                    
        resultado_final.append("".join(linea_lista))
    return '\n'.join(resultado_final)
