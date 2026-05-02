"""
Prueba de métodos de interpolación
"""

from src.algoritmos.interpolacion import lagrange, newton_interpolacion

def probar_interpolacion():
    # Datos de prueba
    x_vals = [1, 2, 3, 4]
    y_vals = [1, 4, 9, 16]  # x^2

    print("=== DATOS DE PRUEBA ===")
    print(f"x: {x_vals}")
    print(f"y: {y_vals}")
    print()

    # Punto a interpolar
    x_interp = 2.5

    print(f"=== INTERPOLACIÓN EN x = {x_interp} ===")
    print()

    # Lagrange
    print("--- LAGRANGE ---")
    try:
        res_lagrange = lagrange(x_vals, y_vals, x_interp)
        print(f"Valor interpolado: {res_lagrange['valor']}")
        print(f"Valor esperado (x^2): {x_interp**2}")
        print(f"Error: {abs(res_lagrange['valor'] - x_interp**2)}")
        print(f"Pasos: {len(res_lagrange['historial'])}")
        print("Historial de pasos:")
        for h in res_lagrange['historial']:
            print(f"  Paso {h['iter']}: {h['valor_parcial']:.6f} (error: {h['error']:.6f})")
        print()
    except Exception as e:
        print(f"ERROR en Lagrange: {e}")
        print()

    # Newton
    print("--- NEWTON ---")
    try:
        res_newton = newton_interpolacion(x_vals, y_vals, x_interp)
        print(f"Valor interpolado: {res_newton['valor']}")
        print(f"Valor esperado (x^2): {x_interp**2}")
        print(f"Error: {abs(res_newton['valor'] - x_interp**2)}")
        print(f"Pasos: {len(res_newton['historial'])}")
        print("Historial de pasos:")
        for h in res_newton['historial']:
            print(f"  Paso {h['iter']}: {h['valor_parcial']:.6f} (error: {h['error']:.6f})")
        print()
    except Exception as e:
        print(f"ERROR en Newton: {e}")
        print()

    # Verificación en puntos originales
    print("=== VERIFICACIÓN EN PUNTOS ORIGINALES ===")
    print("Lagrange:")
    if 'res_lagrange' in locals():
        for v in res_lagrange['verificacion']:
            print(f"  x={v['punto']}: esperado={v['esperado']:.6f}, calculado={v['calculado']:.6f}, error={v['error']:.6f}")

    print("\nNewton:")
    if 'res_newton' in locals():
        for v in res_newton['verificacion']:
            print(f"  x={v['punto']}: esperado={v['esperado']:.6f}, calculado={v['calculado']:.6f}, error={v['error']:.6f}")

def probar_caso_dificil():
    """Prueba con puntos no equiespaciados"""
    print("\n" + "="*50)
    print("=== PRUEBA CON PUNTOS NO EQUIESPACIADOS ===")

    x_vals = [0, 1, 4, 9]
    y_vals = [0, 1, 2, 3]  # sqrt(x)

    x_interp = 2.5

    print(f"x: {x_vals}")
    print(f"y: {y_vals} (sqrt(x))")
    print(f"Interpolando en x = {x_interp}")
    print()

    # Lagrange
    try:
        res_lagrange = lagrange(x_vals, y_vals, x_interp)
        esperado = x_interp ** 0.5
        print(f"Lagrange: {res_lagrange['valor']:.6f} (esperado: {esperado:.6f}, error: {abs(res_lagrange['valor'] - esperado):.6f})")
    except Exception as e:
        print(f"ERROR Lagrange: {e}")

    # Newton
    try:
        res_newton = newton_interpolacion(x_vals, y_vals, x_interp)
        esperado = x_interp ** 0.5
        print(f"Newton: {res_newton['valor']:.6f} (esperado: {esperado:.6f}, error: {abs(res_newton['valor'] - esperado):.6f})")
    except Exception as e:
        print(f"ERROR Newton: {e}")

if __name__ == "__main__":
    probar_interpolacion()
    probar_caso_dificil()