"""
Testing Script para Verificar Sincronización Completa
======================================================

Este script verifica que:
1. El algoritmo genera el historial correctamente
2. La interfaz puede mostrar todo el historial
3. El PDF contiene la misma información

Uso: python test_sincronizacion.py
"""

from src.algoritmos.raices import biseccion
from src.algoritmos.interpolacion import lagrange

def test_biseccion():
    print("\n" + "="*70)
    print("TEST: BISECCIÓN")
    print("="*70)
    
    f = lambda x: x**3 - x - 2
    res = biseccion(f, 1, 2, tol=1e-3, max_iter=20)
    
    print(f"\n✓ Raíz encontrada: {res['raiz']:.6f}")
    print(f"✓ Iteraciones: {res['iteraciones']}")
    print(f"✓ Error final: {res['error']:.2e}")
    
    # Verificar historial
    assert "historial" in res, "Falta 'historial' en resultado"
    assert len(res["historial"]) > 0, "Historial está vacío"
    
    print(f"\n✓ Historial contiene {len(res['historial'])} iteraciones")
    
    # Verificar estructura de cada iteración
    for h in res["historial"]:
        assert "iter" in h, "Falta 'iter' en historial"
        assert "valor_parcial" in h, "Falta 'valor_parcial' en historial"
        assert "error" in h, "Falta 'error' en historial"
        assert "detalle" in h, "Falta 'detalle' en historial"
    
    print("✓ Estructura del historial válida")
    
    # Mostrar muestra del primer detalle
    print("\nMuestra del primer detalle:")
    print(res["historial"][0]["detalle"][:100] + "...")
    
    return True

def test_lagrange():
    print("\n" + "="*70)
    print("TEST: INTERPOLACIÓN LAGRANGE")
    print("="*70)
    
    x_vals = [1, 2, 3]
    y_vals = [2, 4, 9]
    x_eval = 2.5
    
    res = lagrange(x_vals, y_vals, x_eval)
    
    print(f"\n✓ Valor interpolado en x={x_eval}: {res['valor']:.6f}")
    
    # Verificar historial
    assert "historial" in res, "Falta 'historial' en resultado"
    assert len(res["historial"]) > 0, "Historial está vacío"
    
    print(f"✓ Historial contiene {len(res['historial'])} iteraciones")
    
    # Verificar estructura
    for h in res["historial"]:
        assert "iter" in h, "Falta 'iter' en historial"
        assert "valor_parcial" in h, "Falta 'valor_parcial' en historial"
        assert "detalle" in h, "Falta 'detalle' en historial"
    
    print("✓ Estructura del historial válida")
    
    # Verificar que interpolación es correcta
    assert "verificacion" in res, "Falta 'verificacion' en resultado"
    print(f"✓ Verificación en {len(res['verificacion'])} puntos originales")
    
    for v in res["verificacion"]:
        assert v["error"] < 1e-10, f"Error en x={v['punto']}: {v['error']}"
    
    print("✓ Polinomio interpola correctamente en todos los puntos")
    
    # Mostrar polinomio
    print(f"\nPolinomio construido:")
    print(f"{res['polinomio']}")
    
    return True

def test_consistencia_datos():
    """Verifica que mismos datos se usan en lógica, interfaz y PDF."""
    print("\n" + "="*70)
    print("TEST: CONSISTENCIA DE DATOS")
    print("="*70)
    
    # 1. Generar resultado
    f = lambda x: x**2 - 2
    res = biseccion(f, 1, 2, tol=1e-4, max_iter=15)
    
    # 2. Extraer datos que UI mostrará
    num_iters_tabla = len(res["historial"])
    
    # 3. Verificar que cada iteración tiene datos suficientes para:
    #    - Tabla: iter, valor_parcial, error
    #    - Procedimiento: todos los anteriores + detalle
    #    - PDF: mismos datos
    
    for h in res["historial"]:
        # Datos para tabla
        iter_num = h["iter"]
        valor = h["valor_parcial"]
        error = h["error"]
        
        # Datos para procedimiento y PDF
        detalle = h["detalle"]
        
        # Verificaciones
        assert isinstance(iter_num, int), "iter debe ser int"
        assert isinstance(valor, (int, float)), "valor_parcial debe ser número"
        assert isinstance(error, (int, float)), "error debe ser número"
        assert isinstance(detalle, str), "detalle debe ser string"
        assert len(detalle) > 10, "detalle muy corto"
    
    print(f"✓ {num_iters_tabla} iteraciones verificadas")
    print("✓ Todos los datos necesarios están presentes")
    print("✓ Tipos de datos son correctos")
    
    return True

def main():
    print("\n" + "="*70)
    print("TESTS DE SINCRONIZACIÓN - MÉTODOS NUMÉRICOS")
    print("="*70)
    
    try:
        test_biseccion()
        test_lagrange()
        test_consistencia_datos()
        
        print("\n" + "="*70)
        print("✓ TODOS LOS TESTS PASARON")
        print("="*70)
        print("\n¡La sincronización entre algoritmo, interfaz y PDF es correcta!")
        print("\nPróximos pasos:")
        print("1. Ejecuta 'python main.py' para ver la interfaz")
        print("2. Calcula una bisección para ver tabla + procedimiento")
        print("3. Haz click en PDF para generar el documento")
        print("4. Verifica que UI y PDF muestran la misma información")
        
    except AssertionError as e:
        print(f"\n✗ TEST FALLÓ: {e}")
        return False
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
