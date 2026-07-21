"""
CC3103 - Procesamiento de Lenguaje Natural
Laboratorio 1: Tokenizacion y Guardrails para LLMs

Este archivo sirve como guia practica para complementar la presentacion de
Semana 1 y 2. Incluye ejemplos, funciones base y ejercicios marcados con TODO.

Objetivos:
- Comparar diferentes formas de tokenizar texto.
- Calcular estadisticas basicas de texto.
- Detectar datos sensibles usando expresiones regulares.
- Aplicar acciones simples de guardrail: ALLOW, WARN, REDACT o BLOCK.

Ejecutar:
    python laboratorio_1_tokenizacion_guardrails_guia.py

Integrantes del equipo:
- Bianca Calderón, 22272
- Mónica gomez, 22249

"""

from collections import Counter
import re


# -----------------------------------------------------------------------------
# 1. Textos De Prueba
# -----------------------------------------------------------------------------

TEXTOS_DE_PRUEBA = [
    "Hola!!! necesito ayuda con mi cuenta :( mi correo es ana.lopez@uvg.edu.gt",
    "El modelo GPT-4.1 respondio: 'No tengo suficiente contexto.'",
    "Mi numero es +502 5555-1234 y mi sitio es https://uvg.edu.gt",
    "API_KEY=abc123-super-secreta no deberia compartirse con ningun modelo.",
    "anticonstitucionalmente, NLP, #IA, www.example.com/manual.pdf",
    "Mi DPI simulado es 1234 56789 0101 y no deberia enviarse.",
    "Por favor, no compartas la clave ni el token en el chat.",
    "Mi correo alternativo es carmen.gomez@uvg.edu.gt para soporte.",
]


# -----------------------------------------------------------------------------
# 2. Normalizacion Basica
# -----------------------------------------------------------------------------

def normalizar_espacios(texto):
    """Elimina espacios repetidos y saltos de linea innecesarios."""
    return re.sub(r"\s+", " ", texto).strip()


def normalizar_minusculas(texto):
    """Convierte texto a minusculas.

    Nota: no siempre conviene hacer esto. Por ejemplo, Apple y apple pueden
    significar cosas distintas.
    """
    return texto.lower()


# -----------------------------------------------------------------------------
# 3. Tokenizacion Clasica
# -----------------------------------------------------------------------------

def tokenizar_por_espacios(texto):
    """Tokenizacion simple usando espacios.

    Ventaja: facil de entender.
    Limitacion: conserva signos pegados a las palabras y no maneja bien URLs,
    correos o puntuacion.
    """
    return texto.split()


def tokenizar_con_regex_basico(texto):
    """Tokenizacion usando Regex para capturar palabras y numeros.

    Limitacion: puede destruir estructuras como correos, telefonos y URLs.
    """
    return re.findall(r"\b\w+\b", texto.lower())


def tokenizar_con_regex_mixto(texto):
    """Tokenizacion un poco mas cuidadosa.

    Este patron intenta conservar:
    - Correos electronicos
    - URLs
    - Palabras
    - Numeros
    - Algunos signos importantes
    """
    patron = r"https?://\S+|www\.\S+|[\w\.-]+@[\w\.-]+\.\w+|\b\w+\b|[^\w\s]"
    return re.findall(patron, texto, flags=re.UNICODE)


# -----------------------------------------------------------------------------
# 4. Estadisticas De Texto
# -----------------------------------------------------------------------------

def calcular_estadisticas(texto, tokens):
    """Calcula estadisticas basicas de un texto tokenizado."""
    frecuencias = Counter(tokens)

    return {
        "caracteres": len(texto),
        "tokens": len(tokens),
        "tokens_unicos": len(set(tokens)),
        "top_10": frecuencias.most_common(10),
    }


def imprimir_estadisticas(estadisticas):
    """Imprime estadisticas en formato legible."""
    print(f"Caracteres: {estadisticas['caracteres']}")
    print(f"Tokens: {estadisticas['tokens']}")
    print(f"Tokens unicos: {estadisticas['tokens_unicos']}")
    print("Top 10 tokens:")
    for token, frecuencia in estadisticas["top_10"]:
        print(f"  - {token}: {frecuencia}")


# -----------------------------------------------------------------------------
# 5. Patrones Regex Para Guardrails
# -----------------------------------------------------------------------------

PATRONES_SENSIBLES = {
    "EMAIL": r"\b[\w\.-]+@[\w\.-]+\.\w+\b",
    "URL": r"https?://\S+|www\.\S+",
    "PHONE": r"\+?\d[\d\s\-]{7,}\d",
    "SECRET_WORD": r"(?i)\b(password|contrasena|contraseña|clave|secret|token|api_key|apikey)\b",
    "DPI": r"\b\d{4}[\s-]?\d{5}[\s-]?\d{4}\b",
    "LONG_NUMBER": r"\b\d{8,}\b",
}


def detectar_datos_sensibles(texto):
    """Detecta datos sensibles usando los patrones definidos.

    Retorna una lista de diccionarios con tipo y valor detectado.
    """
    hallazgos = []

    for tipo, patron in PATRONES_SENSIBLES.items():
        coincidencias = re.findall(patron, texto)

        for coincidencia in coincidencias:
            # re.findall puede devolver tuplas si el patron tiene grupos.
            if isinstance(coincidencia, tuple):
                coincidencia = " ".join(filter(None, coincidencia))

            hallazgos.append({
                "tipo": tipo,
                "valor": coincidencia,
            })

    return hallazgos


# -----------------------------------------------------------------------------
# 6. Acciones De Guardrail
# -----------------------------------------------------------------------------

def decidir_accion(hallazgos):
    """Decide que accion tomar segun los datos detectados.

    Politica sugerida:
    - SECRET_WORD -> BLOCK
    - EMAIL, PHONE, DPI o LONG_NUMBER -> REDACT
    - URL -> WARN
    - Sin hallazgos -> ALLOW
    """
    tipos = {hallazgo["tipo"] for hallazgo in hallazgos}

    if "SECRET_WORD" in tipos:
        return "BLOCK"

    if tipos.intersection({"EMAIL", "PHONE", "DPI", "LONG_NUMBER"}):
        return "REDACT"

    if "URL" in tipos:
        return "WARN"

    return "ALLOW"


def redactar_texto(texto):
    """Reemplaza datos sensibles por etiquetas seguras."""
    texto_seguro = texto

    reemplazos = {
        "EMAIL": "[EMAIL_REDACTED]",
        "URL": "[URL_REDACTED]",
        "PHONE": "[PHONE_REDACTED]",
        "DPI": "[DPI_REDACTED]",
        "LONG_NUMBER": "[NUMBER_REDACTED]",
    }

    for tipo, reemplazo in reemplazos.items():
        patron = PATRONES_SENSIBLES[tipo]
        texto_seguro = re.sub(patron, reemplazo, texto_seguro)

    return texto_seguro


def aplicar_guardrail(texto):
    """Aplica deteccion, decision y posible redaccion al texto."""
    hallazgos = detectar_datos_sensibles(texto)
    accion = decidir_accion(hallazgos)

    if accion == "REDACT":
        texto_seguro = redactar_texto(texto)
    elif accion == "BLOCK":
        texto_seguro = None
    else:
        texto_seguro = texto

    return {
        "accion": accion,
        "hallazgos": hallazgos,
        "texto_seguro": texto_seguro,
    }


# -----------------------------------------------------------------------------
# 7. Pipeline Completo
# -----------------------------------------------------------------------------

def procesar_texto(texto):
    """Ejecuta el pipeline completo para un texto."""
    texto_normalizado = normalizar_espacios(texto)
    resultado_guardrail = aplicar_guardrail(texto_normalizado)

    texto_para_tokenizar = resultado_guardrail["texto_seguro"]

    if texto_para_tokenizar is None:
        tokens = []
        estadisticas = None
    else:
        tokens = tokenizar_con_regex_mixto(texto_para_tokenizar)
        estadisticas = calcular_estadisticas(texto_para_tokenizar, tokens)

    return {
        "texto_original": texto,
        "texto_normalizado": texto_normalizado,
        "guardrail": resultado_guardrail,
        "tokens": tokens,
        "estadisticas": estadisticas,
    }


def imprimir_resultado_pipeline(resultado, indice):
    """Imprime el resultado completo del pipeline."""
    print("=" * 80)
    print(f"TEXTO {indice}")
    print("=" * 80)

    print("Texto original:")
    print(resultado["texto_original"])

    print("\nTexto normalizado:")
    print(resultado["texto_normalizado"])

    print("\nDatos sensibles detectados:")
    hallazgos = resultado["guardrail"]["hallazgos"]
    if hallazgos:
        for hallazgo in hallazgos:
            print(f"  - {hallazgo['tipo']}: {hallazgo['valor']}")
    else:
        print("  No se detectaron datos sensibles.")

    print(f"\nAccion recomendada: {resultado['guardrail']['accion']}")

    print("\nTexto seguro:")
    if resultado["guardrail"]["texto_seguro"] is None:
        print("  [BLOQUEADO: no debe enviarse al modelo]")
    else:
        print(resultado["guardrail"]["texto_seguro"])

    print("\nTokens:")
    print(resultado["tokens"])

    print("\nEstadisticas:")
    if resultado["estadisticas"] is None:
        print("  No se calcularon estadisticas porque el texto fue bloqueado.")
    else:
        imprimir_estadisticas(resultado["estadisticas"])

    print()


# -----------------------------------------------------------------------------
# 8. Demos Para Clase
# -----------------------------------------------------------------------------

def demo_comparar_tokenizadores():
    """Compara tres formas de tokenizar el mismo texto."""
    texto = "Mi numero es +502 5555-1234 y mi correo es ana@uvg.edu.gt"

    print("=" * 80)
    print("DEMO: COMPARACION DE TOKENIZADORES")
    print("=" * 80)
    print("Texto:")
    print(texto)

    print("\nTokenizacion por espacios:")
    print(tokenizar_por_espacios(texto))

    print("\nTokenizacion Regex basica:")
    print(tokenizar_con_regex_basico(texto))

    print("\nTokenizacion Regex mixta:")
    print(tokenizar_con_regex_mixto(texto))
    print()


def demo_guardrails():
    """Ejecuta el pipeline completo sobre todos los textos de prueba."""
    print("=" * 80)
    print("DEMO: PIPELINE COMPLETO")
    print("=" * 80)
    print()

    for indice, texto in enumerate(TEXTOS_DE_PRUEBA, start=1):
        resultado = procesar_texto(texto)
        imprimir_resultado_pipeline(resultado, indice)


# -----------------------------------------------------------------------------
# 9. Ejercicios Para Estudiantes
# -----------------------------------------------------------------------------

def ejercicio_1_agregar_textos():
    """Agrega textos nuevos para cubrir los casos de prueba descritos."""
    nuevos = [
        "Mi correo alternativo es bianca.calderon@uvg.edu.gt para asistencia.",
        "Contactame al +502 7777-8888 cuando tengas tiempo.",
        "No compartas tu token de acceso ni la clave de API en el chat.",
    ]
    TEXTOS_DE_PRUEBA.extend(nuevos)
    return nuevos


def ejercicio_2_mejorar_regex_dpi():
    """Agrega un patron DPI al diccionario de patrones sensibles."""
    PATRONES_SENSIBLES["DPI"] = r"\b\d{4}[\s-]?\d{5}[\s-]?\d{4}\b"
    return PATRONES_SENSIBLES["DPI"]


def ejercicio_3_accion_warn():
    """Devuelve la politica de guardrail actualizada con WARN para URLs."""
    return {
        "SECRET_WORD": "BLOCK",
        "EMAIL": "REDACT",
        "PHONE": "REDACT",
        "DPI": "REDACT",
        "URL": "WARN",
        "NONE": "ALLOW",
    }


def ejercicio_4_reflexion():
    """Responde las preguntas de reflexion del laboratorio."""
    return [
        "Falsos positivos: palabras como 'token' o 'clave' en frases educativas pueden activarse aunque no sean datos reales.",
        "Falsos negativos: formatos de datos atipicos o informacion sensible embebida en texto largo no coincidente con los patrones. ",
        "Al redactar se pierde el valor original del dato sensible, lo que dificulta el analisis posterior y elimina contexto util.",
        "Regex no es suficiente para proteger informacion real porque no entiende el contexto, no cubre todos los formatos y puede evadirlo con variaciones.",
        "Una capa adicional seria analisis de entidades con modelos NER o listas de controles, y proteccion en el cliente/endpoint antes de enviar texto al modelo.",
    ]


# -----------------------------------------------------------------------------
# 10. Programa Principal
# -----------------------------------------------------------------------------

def main():
    demo_comparar_tokenizadores()
    demo_guardrails()


if __name__ == "__main__":
    main()
