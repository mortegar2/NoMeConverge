#!/usr/bin/env python
"""
CHECKLIST DE SINCRONIZACIÓN
============================

Usa este script para verificar que todo está funcionando correctamente.
Ejecuta: python checklist.py
"""

import sys
from pathlib import Path

def check_files_exist():
    """Verifica que los archivos necesarios existan."""
    print("\n" + "="*70)
    print("1. VERIFICANDO ARCHIVOS NECESARIOS")
    print("="*70)
    
    files = [
        "src/algoritmos/raices.py",
        "src/algoritmos/interpolacion.py",
        "src/interfaz/vistas/vista_raices.py",
        "src/interfaz/vistas/vista_interpolacion.py",
        "src/utilidades/validaciones.py",
        "src/utilidades/excepciones.py",
        "main.py",
    ]
    
    all_exist = True
    for f in files:
        path = Path(f)
        exists = "✓" if path.exists() else "✗"
        print(f"  {exists} {f}")
        if not path.exists():
            all_exist = False
    
    return all_exist

def check_imports():
    """Verifica que los imports funcionen."""
    print("\n" + "="*70)
    print("2. VERIFICANDO IMPORTS")
    print("="*70)
    
    try:
        print("  Testing: from src.algoritmos.raices import biseccion")
        from src.algoritmos.raices import biseccion
        print("  ✓ OK")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False
    
    try:
        print("  Testing: from src.algoritmos.interpolacion import lagrange")
        from src.algoritmos.interpolacion import lagrange
        print("  ✓ OK")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False
    
    try:
        print("  Testing: from src.interfaz.vistas.vista_raices import VistaRaices")
        from src.interfaz.vistas.vista_raices import VistaRaices
        print("  ✓ OK")
    except Exception as e:
        print(f"  ✗ ERROR: {e}")
        return False
    
    return True

def check_biseccion_historial():
    """Verifica que bisección genera historial con estructura correcta."""
    print("\n" + "="*70)
    print("3. VERIFICANDO BISECCIÓN - ESTRUCTURA DEL HISTORIAL")
    print("="*70)
    
    from src.algoritmos.raices import biseccion
    
    f = lambda x: x**2 - 2
    res = biseccion(f, 1, 2, tol=1e-3, max_iter=20)
    
    print(f"  Iteraciones: {len(res['historial'])}")
    print(f"  Raíz encontrada: {res['raiz']:.6f}")
    
    # Verificar estructura
    for i, h in enumerate(res['historial'], 1):
        required_keys = ['iter', 'valor_parcial', 'error', 'detalle']
        missing = [k for k in required_keys if k not in h]
        
        if missing:
            print(f"  ✗ Iteración {i}: Faltan campos: {missing}")
            return False
        
        if not isinstance(h['detalle'], str) or len(h['detalle']) < 10:
            print(f"  ✗ Iteración {i}: Detalle inválido")
            return False
    
    print(f"  ✓ Todas {len(res['historial'])} iteraciones tienen estructura correcta")
    return True

def check_lagrange_historial():
    """Verifica que Lagrange genera historial con estructura correcta."""
    print("\n" + "="*70)
    print("4. VERIFICANDO LAGRANGE - ESTRUCTURA DEL HISTORIAL")
    print("="*70)
    
    from src.algoritmos.interpolacion import lagrange
    
    res = lagrange([1, 2, 3], [1, 4, 9], 2.5)
    
    print(f"  Iteraciones: {len(res['historial'])}")
    print(f"  Valor interpolado: {res['valor']:.6f}")
    
    # Verificar estructura
    for i, h in enumerate(res['historial'], 1):
        required_keys = ['iter', 'valor_parcial', 'detalle']
        missing = [k for k in required_keys if k not in h]
        
        if missing:
            print(f"  ✗ Iteración {i}: Faltan campos: {missing}")
            return False
    
    # Verificar que interpola correctamente
    errors = [v['error'] for v in res['verificacion']]
    if any(e > 1e-10 for e in errors):
        print(f"  ✗ Interpolación inexacta. Errores: {errors}")
        return False
    
    print(f"  ✓ Lagrange interpola correctamente")
    print(f"  ✓ Polinomio: {res['polinomio']}")
    return True

def check_vista_raices_methods():
    """Verifica que vista_raices tiene los métodos necesarios."""
    print("\n" + "="*70)
    print("5. VERIFICANDO VISTA_RAICES - MÉTODOS")
    print("="*70)
    
    from src.interfaz.vistas.vista_raices import VistaRaices
    
    required_methods = ['_crear_ui', '_ejecutar', '_exportar_pdf', '_mostrar_procedimiento']
    
    for method in required_methods:
        has_method = hasattr(VistaRaices, method)
        status = "✓" if has_method else "✗"
        print(f"  {status} {method}")
        if not has_method:
            return False
    
    return True

def check_vista_interpolacion_methods():
    """Verifica que vista_interpolacion tiene los métodos necesarios."""
    print("\n" + "="*70)
    print("6. VERIFICANDO VISTA_INTERPOLACION - MÉTODOS")
    print("="*70)
    
    from src.interfaz.vistas.vista_interpolacion import VistaInterpolacion
    
    required_methods = ['_crear_ui', '_ejecutar', '_exportar_pdf', '_mostrar_procedimiento_interpolacion']
    
    for method in required_methods:
        has_method = hasattr(VistaInterpolacion, method)
        status = "✓" if has_method else "✗"
        print(f"  {status} {method}")
        if not has_method:
            return False
    
    return True

def check_text_widget_compatibility():
    """Verifica que pueden estar los "Text widgets" en la vistas."""
    print("\n" + "="*70)
    print("7. VERIFICANDO COMPATIBILIDAD TEXT WIDGET")
    print("="*70)
    
    # Solo verificamos que el código compile sin errores
    # No podemos crear la UI sin un displays gráfico
    
    try:
        from src.interfaz.vistas.vista_raices import VistaRaices
        print("  ✓ vista_raices puede importarse")
    except Exception as e:
        print(f"  ✗ Error en vista_raices: {e}")
        return False
    
    try:
        from src.interfaz.vistas.vista_interpolacion import VistaInterpolacion
        print("  ✓ vista_interpolacion puede importarse")
    except Exception as e:
        print(f"  ✗ Error en vista_interpolacion: {e}")
        return False
    
    return True

def main():
    print("\n" + "="*70)
    print("CHECKLIST DE SINCRONIZACIÓN")
    print("Métodos Numéricos - Proyecto Final")
    print("="*70)
    
    results = []
    
    # Ejecutar todos los checks
    results.append(("Archivos necesarios", check_files_exist()))
    results.append(("Imports", check_imports()))
    results.append(("Bisección - Historial", check_biseccion_historial()))
    results.append(("Lagrange - Historial", check_lagrange_historial()))
    results.append(("Vista Raíces - Métodos", check_vista_raices_methods()))
    results.append(("Vista Interpolación - Métodos", check_vista_interpolacion_methods()))
    results.append(("Compatibilidad Text Widget", check_text_widget_compatibility()))
    
    # Resumen
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")
    
    all_pass = all(result for _, result in results)
    
    print("\n" + "="*70)
    if all_pass:
        print("✓ TODOS LOS CHECKS PASARON")
        print("\nProximos pasos:")
        print("  1. python main.py")
        print("  2. Calcula una bisección")
        print("  3. Verifica tabla + procedimiento")
        print("  4. Exporta PDF y compara")
        print("\nDocumentación:")
        print("  - GUIA_RAPIDA.md: Uso de la aplicación")
        print("  - REFACTORIZACION.md: Detalles técnicos")
        print("  - test_sincronizacion.py: Tests adicionales")
    else:
        print("✗ ALGUNOS CHECKS FALLARON")
        print("\nRevisa los errores arriba para más detalles.")
        return False
    
    print("="*70 + "\n")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
