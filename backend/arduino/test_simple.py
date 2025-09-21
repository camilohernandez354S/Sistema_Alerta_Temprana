#!/usr/bin/env python3
"""
Script de prueba simple para verificar el manejo de formatos de datos
"""

import re

def validar_formato(dato):
    """Validar el formato de los datos crudos del Arduino"""
    # Verificar que el formato sea "nivel_agua: [número]cm" o "Distancia: [número]cm"
    if not re.match(r"^(nivel_agua|Distancia):\s*\d+(?:\.\d+)?\scm$", dato):
        return False, "Formato de datos inválido. Debe ser 'nivel_agua: [número]cm' o 'Distancia: [número]cm'"
    return True, "Formato válido"

def extraer_nivel_agua(dato):
    """Extraer el valor numérico del nivel del agua de la lectura cruda"""
    try:
        # Manejar tanto "nivel_agua:" como "Distancia:"
        nivel_agua_str = dato.replace("nivel_agua:", "").replace("Distancia:", "").replace("cm", "").strip()
        nivel_agua = float(nivel_agua_str)
        return nivel_agua
    except ValueError:
        raise ValueError("No se pudo extraer un número válido del nivel del agua")

def test_formato_nivel_agua():
    """Probar formato 'nivel_agua: [número]cm'"""
    print("🧪 Probando formato 'nivel_agua: [número]cm'")
    
    datos_correctos = [
        "nivel_agua: 10.5 cm",
        "nivel_agua: 125.19 cm",
        "nivel_agua: 0 cm",
        "nivel_agua: 1000 cm"
    ]
    
    for dato in datos_correctos:
        try:
            es_valido, mensaje = validar_formato(dato)
            if es_valido:
                valor = extraer_nivel_agua(dato)
                print(f"✅ {dato} -> {valor}")
            else:
                print(f"❌ {dato} -> {mensaje}")
        except Exception as e:
            print(f"❌ {dato} -> Error: {e}")

def test_formato_distancia():
    """Probar formato 'Distancia: [número]cm'"""
    print("\n🧪 Probando formato 'Distancia: [número]cm'")
    
    datos_correctos = [
        "Distancia: 10.5 cm",
        "Distancia: 125.19 cm",
        "Distancia: 0 cm",
        "Distancia: 1000 cm"
    ]
    
    for dato in datos_correctos:
        try:
            es_valido, mensaje = validar_formato(dato)
            if es_valido:
                valor = extraer_nivel_agua(dato)
                print(f"✅ {dato} -> {valor}")
            else:
                print(f"❌ {dato} -> {mensaje}")
        except Exception as e:
            print(f"❌ {dato} -> Error: {e}")

def test_formatos_invalidos():
    """Probar formatos inválidos"""
    print("\n🧪 Probando formatos inválidos")
    
    datos_invalidos = [
        "nivel_agua 10.5 cm",  # Sin dos puntos
        "Distancia 10.5 cm",   # Sin dos puntos
        "nivel_agua: 10.5",    # Sin cm
        "Distancia: 10.5",     # Sin cm
        "nivel_agua: abc cm",  # No es número
        "Distancia: abc cm",   # No es número
        "random: 10.5 cm",     # Formato desconocido
        "",                    # Vacío
        "10.5 cm"              # Sin prefijo
    ]
    
    for dato in datos_invalidos:
        try:
            es_valido, mensaje = validar_formato(dato)
            if not es_valido:
                print(f"✅ {dato} -> Correctamente rechazado: {mensaje}")
            else:
                valor = extraer_nivel_agua(dato)
                print(f"❌ {dato} -> Debería haber fallado pero devolvió: {valor}")
        except Exception as e:
            print(f"✅ {dato} -> Correctamente rechazado: {e}")

def main():
    """Función principal"""
    print("🔍 Pruebas de formato de datos del Arduino")
    print("=" * 50)
    
    test_formato_nivel_agua()
    test_formato_distancia()
    test_formatos_invalidos()
    
    print("\n" + "=" * 50)
    print("✅ Pruebas completadas")

if __name__ == "__main__":
    main()
