"""
Módulo: Interpolación

Métodos:
- Lagrange
- Newton (diferencias divididas)
"""

from typing import List, Dict, Any
import numpy as np


def _formatear_polinomio(coefs, grado_max=None):
    """
    Convierte coeficientes polinomiales a una expresión legible.
    """
    if grado_max is None:
        grado_max = len(coefs) - 1

    # Redondear coeficientes muy pequeños a cero
    umbral = 1e-10
    coefs_redondeados = []
    for coef in coefs:
        if abs(coef) < umbral:
            coefs_redondeados.append(0.0)
        else:
            coefs_redondeados.append(round(coef, 6))  # Redondear a 6 decimales

    terminos = []
    for i, coef in enumerate(coefs_redondeados):
        if coef == 0:  # Ahora comparar con cero exacto
            continue

        grado = grado_max - i
        coef_str = f"{coef:.3f}" if abs(coef - round(coef)) > 1e-10 else f"{int(round(coef))}"

        if coef_str == "1" and grado > 0:
            coef_str = ""
        elif coef_str == "-1" and grado > 0:
            coef_str = "-"

        if grado == 0:
            terminos.append(coef_str)
        elif grado == 1:
            terminos.append(f"{coef_str}x")
        else:
            terminos.append(f"{coef_str}x^{grado}")

    if not terminos:
        return "0"

    # Unir términos con signos correctos
    resultado = terminos[0]
    for term in terminos[1:]:
        if term.startswith("-"):
            resultado += f" {term}"
        else:
            resultado += f" + {term}"

    return resultado


# =========================================================
# LAGRANGE
# =========================================================
def lagrange(x_vals: List[float], y_vals: List[float], x: float = None) -> Dict[str, Any]:
    """
    Interpolación de Lagrange.
    
    Args:
        x_vals: Lista de puntos x
        y_vals: Lista de puntos y
        x: Punto donde evaluar el polinomio (opcional)
    
    Returns:
        Diccionario con:
        - valor: Valor evaluado (None si x no se proporciona)
        - historial: Pasos del cálculo
        - polinomio: Expresión del polinomio interpolante
        - verificacion: Evaluación en puntos originales
    """
    if len(x_vals) != len(y_vals):
        raise ValueError("X e Y deben tener la misma longitud.")
    if len(x_vals) == 0:
        raise ValueError("Debe ingresar al menos un punto X e Y.")
    if len(set(x_vals)) != len(x_vals):
        raise ValueError("Los valores de X deben ser únicos; no se permiten repeticiones.")

    n = len(x_vals)
    historial = []
    polinomio_expr = ""

    # Construir expresión del polinomio (siempre se hace)
    for i in range(n):
        polinomio_expr += f" + {y_vals[i]} * L{i}(x)"

    polinomio_expr = polinomio_expr.lstrip(" + ")

    # Calcular coeficientes del polinomio para mostrar forma legible
    polinomio_legible = polinomio_expr  # Default

    if n <= 4:
        try:
            # Usar polyfit para obtener los coeficientes del polinomio
            coefs = np.polyfit(x_vals, y_vals, n-1)
            polinomio_legible = _formatear_polinomio(coefs)  # polyfit ya devuelve coefs de mayor a menor grado
        except:
            # Si falla, usar la expresión simbólica
            polinomio_legible = polinomio_expr

    # Generar historial: si hay x_eval, mostrar evaluación; si no, mostrar construcción
    resultado = None
    if x is not None:
        resultado = 0
        for i in range(n):
            termino = y_vals[i]
            detalle = f"""
----------------------------------------
ITERACIÓN {i + 1}: Término L{i}(x)
----------------------------------------
Calculando L{i}(x) = y{i} * ∏(j≠i) [(x - xj)/(xi - xj)]

y{i} = {y_vals[i]}
x{i} = {x_vals[i]}
x = {x}

Producto de términos:
"""

            producto = 1.0
            for j in range(n):
                if i != j:
                    factor = (x - x_vals[j]) / (x_vals[i] - x_vals[j])
                    producto *= factor
                    detalle += f"(x - x{j}) / (x{i} - x{j}) = ({x} - {x_vals[j]}) / ({x_vals[i]} - {x_vals[j]}) = {factor}\n"

            termino = y_vals[i] * producto
            detalle += f"\nProducto total = {producto}"
            detalle += f"\nTérmino completo = y{i} * producto = {y_vals[i]} * {producto} = {termino}"

            resultado_anterior = resultado
            resultado += termino

            detalle += f"\n\nResultado acumulado = {resultado_anterior} + {termino} = {resultado}"

            historial.append({
                "iter": i + 1,
                "valor_parcial": resultado,
                "error": abs(resultado - resultado_anterior),
                "detalle": detalle
            })
    else:
        # Sin evaluación, mostrar construcción de funciones base
        for i in range(n):
            detalle = f"""
----------------------------------------
ITERACIÓN {i + 1}: Función base de Lagrange L{i}(x)
----------------------------------------
L{i}(x) = Producto(j≠{i}) [(x - x_j)/(x{i} - x_j)]

Punto base: x{i} = {x_vals[i]}, y{i} = {y_vals[i]}

Factores de la función base:
"""
            for j in range(n):
                if i != j:
                    denom = x_vals[i] - x_vals[j]
                    detalle += f"\nFactor j={j}: (x - x{j})/(x{i} - x{j}) = (x - {x_vals[j]})/({x_vals[i]} - {x_vals[j]}) = (x - {x_vals[j]})/{denom}"
            
            detalle += f"\n\nFunción base final: L{i}(x) = Producto[(x - x_j)/(x{i} - x_j)] para todo j ≠ {i}"
            detalle += f"\nContribución al polinomio: {y_vals[i]} * L{i}(x)"
            
            historial.append({
                "iter": i + 1,
                "valor_parcial": y_vals[i],
                "error": 0,
                "detalle": detalle
            })
        
        # Agregar paso final mostrando el polinomio completo
        detalle_final = f"""
----------------------------------------
POLINOMIO INTERPOLANTE FINAL
----------------------------------------
P(x) = {polinomio_expr}

O en forma estándar:
P(x) = {polinomio_legible}

Este polinomio pasa por todos los {n} puntos dados:
"""
        for i in range(n):
            detalle_final += f"\nP({x_vals[i]}) = {y_vals[i]}"
        
        historial.append({
            "iter": n + 1,
            "valor_parcial": None,
            "error": 0,
            "detalle": detalle_final
        })

    # Verificación: Evaluar en puntos originales
    verificacion = []
    for i in range(n):
        # Calcular directamente el valor en x_vals[i]
        val_calc = 0
        for j in range(n):
            term = y_vals[j]
            for k in range(n):
                if k != j:
                    term *= (x_vals[i] - x_vals[k]) / (x_vals[j] - x_vals[k])
            val_calc += term
        error_verif = abs(val_calc - y_vals[i])
        verificacion.append({
            "punto": x_vals[i],
            "esperado": y_vals[i],
            "calculado": val_calc,
            "error": error_verif
        })

    return {
        "valor": resultado,
        "valor_evaluado": x,  # Nuevo campo para saber en qué punto se evaluó
        "historial": historial,
        "polinomio": polinomio_legible,
        "verificacion": verificacion
    }


# =========================================================
# NEWTON (DIFERENCIAS DIVIDIDAS)
# =========================================================
def newton_interpolacion(x_vals: List[float], y_vals: List[float], x: float = None) -> Dict[str, Any]:
    """
    Interpolación de Newton (diferencias divididas).
    
    Args:
        x_vals: Lista de puntos x
        y_vals: Lista de puntos y
        x: Punto donde evaluar el polinomio (opcional)
    
    Returns:
        Diccionario con:
        - valor: Valor evaluado (None si x no se proporciona)
        - historial: Pasos del cálculo
        - polinomio: Expresión del polinomio interpolante
        - verificacion: Evaluación en puntos originales
    """
    n = len(x_vals)
    tabla = [y_vals.copy()]
    historial = []
    polinomio_expr = f"{y_vals[0]}"

    # Construcción de tabla de diferencias divididas
    for i in range(1, n):
        fila = []
        for j in range(n - i):
            denom = x_vals[j+i] - x_vals[j]
            if abs(denom) < 1e-12:
                raise ValueError(f"División por cero en diferencias divididas: x{j+i} ≈ x{j}")
            val = (tabla[i-1][j+1] - tabla[i-1][j]) / denom
            fila.append(val)

            detalle = f"""
----------------------------------------
ITERACIÓN {len(historial) + 1}: Diferencia dividida de orden {i}
----------------------------------------
Calculando f[x{j}, x{j+i}] = (f[x{j+1}, x{j+i-1}] - f[x{j}, x{j+i-1}]) / (x{j+i} - x{j})

f[x{j+1}, x{j+i-1}] = {tabla[i-1][j+1]}
f[x{j}, x{j+i-1}] = {tabla[i-1][j]}
x{j+i} = {x_vals[j+i]}
x{j} = {x_vals[j]}

f[x{j}, x{j+i}] = ({tabla[i-1][j+1]} - {tabla[i-1][j]}) / ({x_vals[j+i]} - {x_vals[j]}) = {val}
"""

            historial.append({
                "iter": len(historial) + 1,
                "valor_parcial": val,
                "error": 0,  # No error directo aquí
                "detalle": detalle
            })

        tabla.append(fila)

    polinomio_expr = f"P(x) = {y_vals[0]}"
    for i in range(1, n):
        polinomio_expr += f" + {tabla[i][0]} * ∏(x - x{j} for j=0 to {i-1})"

    # Convertir a forma polinomial estándar para mostrar
    polinomio_legible = polinomio_expr  # Default

    if n <= 4:
        try:
            # Usar polyfit para obtener los coeficientes del polinomio
            coefs = np.polyfit(x_vals, y_vals, n-1)
            polinomio_legible = _formatear_polinomio(coefs)  # polyfit ya devuelve coefs de mayor a menor grado
        except:
            # Si falla, usar la expresión simbólica
            polinomio_legible = polinomio_expr

    # Evaluación del polinomio (si se proporciona x)
    resultado = None
    if x is not None:
        resultado = tabla[0][0]
        producto = 1
        historial_eval = []

        detalle_eval = f"""
----------------------------------------
EVALUACIÓN DEL POLINOMIO EN x = {x}
----------------------------------------
Polinomio: P(x) = {y_vals[0]}"""

        for i in range(1, n):
            producto_anterior = producto
            producto *= (x - x_vals[i-1])

            detalle_eval += f" + {tabla[i][0]} * ∏(x - x{j} for j=0 to {i-1})"
            detalle_eval += f"\n\nTérmino {i}: {tabla[i][0]} * ∏(x - x{j} for j=0 to {i-1})"
            detalle_eval += f"\n∏(x - x{j} for j=0 to {i-1}) = {producto_anterior} * (x - x{i-1}) = {producto_anterior} * ({x} - {x_vals[i-1]}) = {producto}"
            detalle_eval += f"\nTérmino completo = {tabla[i][0]} * {producto} = {tabla[i][0] * producto}"

            resultado_anterior = resultado
            incremento = tabla[i][0] * producto
            resultado += incremento

            detalle_eval += f"\nResultado acumulado = {resultado_anterior} + {incremento} = {resultado}"

            historial_eval.append({
                "iter": len(historial) + len(historial_eval) + 1,
                "valor_parcial": resultado,
                "error": abs(incremento),
                "detalle": detalle_eval
            })

            detalle_eval = ""  # Reset para el siguiente término

        historial.extend(historial_eval)

    # Verificación: Evaluar en puntos originales
    verificacion = []
    for i in range(n):
        # Evaluar el polinomio completo en x_vals[i]
        val_calc = tabla[0][0]
        producto_verif = 1
        for j in range(1, n):
            producto_verif *= (x_vals[i] - x_vals[j-1])
            val_calc += tabla[j][0] * producto_verif
        error_verif = abs(val_calc - y_vals[i])
        verificacion.append({
            "punto": x_vals[i],
            "esperado": y_vals[i],
            "calculado": val_calc,
            "error": error_verif
        })

    return {
        "valor": resultado,
        "valor_evaluado": x,  # Nuevo campo para saber en qué punto se evaluó
        "historial": historial,
        "polinomio": polinomio_legible,
        "verificacion": verificacion
    }