def procesar_texto_selectivo(texto_bruto, lineas_a_procesar):
    # Convertimos a mayúsculas para estandarizar, pero manejaremos la 'm' después
    lineas = texto_bruto.upper().replace('\r\n', '\n').split('\n')
    
    # El patrón ahora busca específicamente variaciones de menor
    # Capturamos la raíz, luego si es menor (m), y luego el resto (7, maj7, etc.)
    patron_latino = r'\b(DO|RE|MI|FA|SOL|LA|SI)([#B])?(M|MAJ|MIN|AUG|DIM|SUS|ADD)?([0-9]*)'
    
    def traducir_acorde(match):
        raiz_lat = match.group(1)
        alteracion = match.group(2) or ""
        cualidad = match.group(3) or ""
        numero = match.group(4) or ""
        
        raiz_amer = LATINO_A_AMERICANO.get(raiz_lat, raiz_lat)
        
        # Lógica para la 'm' minúscula:
        # Si la cualidad es 'M' sola o empieza por 'MIN', la convertimos en 'm'
        if cualidad == "M":
            cualidad = "m"
        elif cualidad == "MIN":
            cualidad = "m"
            
        return f"{raiz_amer}{alteracion}{cualidad}{numero}"

    resultado_traduccion = []
    for i, linea in enumerate(lineas):
        if i in lineas_a_procesar:
            # Traducimos y aplicamos la m minúscula
            linea_traducida = re.sub(patron_latino, traducir_acorde, linea)
            resultado_traduccion.append(linea_traducida)
        else:
            resultado_traduccion.append(linea)

    # 2. Paso final: Colocar el apóstrofe
    resultado_final = []
    # Actualizamos el regex americano para que también reconozca la 'm' minúscula
    patron_americano = r'\b([A-G][#B]?(?:m|MAJ|MIN|AUG|DIM|SUS|ADD)?[0-9]*(?:/[A-G][#B]?)?)\b'

    for i, linea in enumerate(resultado_traduccion):
        if i not in lineas_a_procesar:
            resultado_final.append(linea)
            continue
            
        linea_lista = list(linea)
        ajuste = 0
        for m in re.finditer(patron_americano, linea):
            fin = m.end() + ajuste
            if fin < len(linea_lista):
                if linea_lista[fin] not in ["'", "*"]:
                    linea_lista.insert(fin, "'")
                    ajuste += 1
            else:
                linea_lista.append("'")
                ajuste += 1
        resultado_final.append("".join(linea_lista))

    return '\n'.join(resultado_final)
