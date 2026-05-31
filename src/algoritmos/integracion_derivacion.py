"""
Módulo: Integración y Derivación Numérica

Implementa métodos numéricos para:
- Aproximación de derivadas mediante diferencias finitas
- Integración numérica mediante trapecio compuesto y Simpson compuesto

Cada función devuelve un diccionario con el resultado final, historial de pasos
y datos intermedios para mostrar el procedimiento completo.
"""

from typing import Callable, Dict, Any, List
import numpy as np


def formatear_numero(valor: float) -> str:
    return f"{valor:.6f}"


def diferencias_finitas(
    f: Callable[[float], float],
    a: float,
    b: float,
    n: int = 10,
    h: float = 1e-3,
    method: str = "central"
) -> Dict[str, Any]:
    """
    Aproxima la derivada de f en n puntos equiespaciados entre a y b.
    """
    if n < 2:
        raise ValueError("n debe ser al menos 2 para diferencias finitas")
    if h <= 0:
        raise ValueError("h debe ser mayor que 0")
    if method not in ("forward", "backward", "central"):
        raise ValueError("method debe ser 'forward', 'backward' o 'central'")

    xs = np.linspace(a, b, n).tolist()
    historial: List[Dict[str, Any]] = []
    resultados: List[Dict[str, Any]] = []

    for i, x in enumerate(xs):
        fx = f(x)
        if method == "forward":
            fx_h = f(x + h)
            derivada = (fx_h - fx) / h
            detalle = (
                f"ITERACIÓN {i + 1}: x = {x}\n"
                f"f(x) = {fx}\n"
                f"f(x + h) = {fx_h}\n"
                f"Diferencia adelante = (f(x+h) - f(x)) / h = ({fx_h} - {fx}) / {h} = {derivada}\n"
            )
        elif method == "backward":
            fx_h = f(x - h)
            derivada = (fx - fx_h) / h
            detalle = (
                f"ITERACIÓN {i + 1}: x = {x}\n"
                f"f(x) = {fx}\n"
                f"f(x - h) = {fx_h}\n"
                f"Diferencia atrás = (f(x) - f(x-h)) / h = ({fx} - {fx_h}) / {h} = {derivada}\n"
            )
        else:
            fx_forward = f(x + h)
            fx_backward = f(x - h)
            derivada = (fx_forward - fx_backward) / (2 * h)
            detalle = (
                f"ITERACIÓN {i + 1}: x = {x}\n"
                f"f(x + h) = {fx_forward}\n"
                f"f(x - h) = {fx_backward}\n"
                f"Diferencia central = (f(x+h) - f(x-h)) / (2*h) = ({fx_forward} - {fx_backward}) / ({2 * h}) = {derivada}\n"
            )

        resultados.append({
            "i": i + 1,
            "x": x,
            "f(x)": fx,
            "derivada_aprox": derivada,
            "detalle": detalle
        })
        historial.append({
            "iter": i + 1,
            "x": x,
            "detalle": detalle
        })

    return {
        "metodo": "Diferencias finitas",
        "submetodo": method,
        "a": a,
        "b": b,
        "h": h,
        "n": n,
        "resultados": resultados,
        "historial": historial
    }


def derivada_en_punto(f: Callable[[float], float], x0: float, h: float = 1e-6, method: str = "central") -> Dict[str, Any]:
    """
    Aproxima la derivada de f en el punto x0 usando el método indicado.

    Retorna un diccionario con el valor aproximado, los valores evaluados
    (f(x0), f(x0+h), f(x0-h) según corresponda) y el detalle paso a paso.
    """
    if h <= 0:
        raise ValueError("h debe ser mayor que 0")
    if method not in ("forward", "backward", "central"):
        raise ValueError("method debe ser 'forward', 'backward' o 'central'")

    fx0 = f(x0)
    historial = []
    resultados = []

    def num(valor: float) -> str:
        return formatear_numero(valor)

    # Construir representación legible de entradas y fórmula
    datos_entrada = {
        "funcion": None,
        "x0": x0,
        "h": h,
    }

    if method == "forward":
        fxh = f(x0 + h)
        derivada = (fxh - fx0) / h
        formula = "f'(x) ≈ (f(x+h) - f(x)) / h"
        evaluaciones = [
            {"x": x0, "expr": f"f({num(x0)})", "valor": num(fx0)},
            {"x": x0 + h, "expr": f"f({num(x0 + h)})", "valor": num(fxh)}
        ]
        sustitucion = f"({num(fxh)} - {num(fx0)}) / {num(h)} = {num(derivada)}"
        resultados.append({"etiqueta": "f(x0)", "valor": num(fx0)})
        resultados.append({"etiqueta": "f(x0+h)", "valor": num(fxh)})
        detalle = (
            f"Cálculo en x0={num(x0)}:\n"
            f"Formula usada: {formula}\n"
            f"Evaluaciones:\n"
            f"  {evaluaciones[0]['expr']} = {evaluaciones[0]['valor']}\n"
            f"  {evaluaciones[1]['expr']} = {evaluaciones[1]['valor']}\n"
            f"Sustitución: {sustitucion}\n"
        )

    elif method == "backward":
        fxh = f(x0 - h)
        derivada = (fx0 - fxh) / h
        formula = "f'(x) ≈ (f(x) - f(x-h)) / h"
        evaluaciones = [
            {"x": x0 - h, "expr": f"f({num(x0 - h)})", "valor": num(fxh)},
            {"x": x0, "expr": f"f({num(x0)})", "valor": num(fx0)}
        ]
        sustitucion = f"({num(fx0)} - {num(fxh)}) / {num(h)} = {num(derivada)}"
        resultados.append({"etiqueta": "f(x0-h)", "valor": num(fxh)})
        resultados.append({"etiqueta": "f(x0)", "valor": num(fx0)})
        detalle = (
            f"Cálculo en x0={num(x0)}:\n"
            f"Formula usada: {formula}\n"
            f"Evaluaciones:\n"
            f"  {evaluaciones[0]['expr']} = {evaluaciones[0]['valor']}\n"
            f"  {evaluaciones[1]['expr']} = {evaluaciones[1]['valor']}\n"
            f"Sustitución: {sustitucion}\n"
        )

    else:
        fx_forward = f(x0 + h)
        fx_backward = f(x0 - h)
        derivada = (fx_forward - fx_backward) / (2 * h)
        formula = "f'(x) ≈ (f(x+h) - f(x-h)) / (2*h)"
        evaluaciones = [
            {"x": x0 - h, "expr": f"f({num(x0 - h)})", "valor": num(fx_backward)},
            {"x": x0, "expr": f"f({num(x0)})", "valor": num(fx0)},
            {"x": x0 + h, "expr": f"f({num(x0 + h)})", "valor": num(fx_forward)}
        ]
        sustitucion = f"({num(fx_forward)} - {num(fx_backward)}) / {num(2*h)} = {num(derivada)}"
        resultados.append({"etiqueta": "f(x0-h)", "valor": num(fx_backward)})
        resultados.append({"etiqueta": "f(x0)", "valor": num(fx0)})
        resultados.append({"etiqueta": "f(x0+h)", "valor": num(fx_forward)})
        detalle = (
            f"Cálculo en x0={num(x0)}:\n"
            f"Formula usada: {formula}\n"
            f"Evaluaciones:\n"
            f"  {evaluaciones[0]['expr']} = {evaluaciones[0]['valor']}\n"
            f"  {evaluaciones[1]['expr']} = {evaluaciones[1]['valor']}\n"
            f"  {evaluaciones[2]['expr']} = {evaluaciones[2]['valor']}\n"
            f"Sustitución: {sustitucion}\n"
        )

    # construir tabla de evaluaciones (x, f(x))
    tabla = [{"x": eval["x"], "f(x)": eval["valor"]} for eval in evaluaciones]

    # historial con índice para compatibilidad con exportación PDF
    historial.append({"iter": 1, "detalle": detalle})

    return {
        "metodo": "Derivación en punto",
        "submetodo": method,
        "x0": x0,
        "h": h,
        "valor": derivada,
        "resultados": resultados,
        "historial": historial,
        "datos_entrada": datos_entrada,
        "formula": formula,
        "evaluaciones": evaluaciones,
        "sustitucion": sustitucion,
        "tabla": tabla
    }


def trapecio_compuesto(
    f: Callable[[float], float],
    a: float,
    b: float,
    n: int = 10
) -> Dict[str, Any]:
    """
    Calcula la integral de f en [a,b] usando la regla del trapecio compuesta.
    Retorna un diccionario con datos de entrada, fórmula, tabla, sustitución y valor.
    """
    if n < 1:
        raise ValueError("n debe ser mayor que 0")

    h = (b - a) / n
    def num(valor: float) -> str:
        return formatear_numero(valor)

    xs = np.linspace(a, b, n + 1).tolist()
    fs = [f(x) for x in xs]

    # Construir tabla con i, x, f(x)
    tabla = []
    for i, (x, fx) in enumerate(zip(xs, fs)):
        tabla.append({"i": i, "x": num(x), "f(x)": num(fx)})

    # Construcción de suma
    suma_str_parts = [f"f({tabla[0]['x']})"]
    for i in range(1, len(tabla) - 1):
        suma_str_parts.append(f"2f({tabla[i]['x']})")
    suma_str_parts.append(f"f({tabla[-1]['x']})")
    sustitucion = "S = " + " + ".join(suma_str_parts)

    # Suma efectiva para cálculo
    suma = fs[0] + fs[-1]
    for i in range(1, n):
        suma += 2 * fs[i]

    valor = (h / 2) * suma

    formula = (
        "∫ f(x)dx ≈ (h/2) * [f(x₀) + 2f(x₁) + 2f(x₂) + ... + 2f(xₙ₋₁) + f(xₙ)]"
    )

    historial = [{
        "iter": 1,
        "detalle": (
            f"Regla del Trapecio\n"
            f"Intervalo: [{num(a)}, {num(b)}]\n"
            f"Paso h = {num(h)}\n"
            f"Número de subintervalos: {n}\n\n"
            f"Fórmula: {formula}\n\n"
            f"Tabla de evaluaciones:\n"
            f"{sustitucion}\n\n"
            f"Resultado: Integral ≈ (h/2) * S = {num(valor)}\n"
        )
    }]

    return {
        "metodo": "Trapecio compuesto",
        "a": a,
        "b": b,
        "n": n,
        "h": num(h),
        "valor": valor,
        "resultados": tabla,
        "historial": historial,
        "formula": formula,
        "tabla": tabla,
        "sustitucion": sustitucion
    }


def simpson_compuesto(
    f: Callable[[float], float],
    a: float,
    b: float,
    n: int = 10
) -> Dict[str, Any]:
    """
    Calcula la integral de f en [a,b] usando Simpson compuesto.
    Retorna un diccionario con datos de entrada, fórmula, tabla con pesos, sustitución y valor.
    """
    if n < 2 or n % 2 == 1:
        raise ValueError("n debe ser par y mayor que 1 para Simpson compuesto")

    h = (b - a) / n
    def num(valor: float) -> str:
        return formatear_numero(valor)

    xs = np.linspace(a, b, n + 1).tolist()
    fs = [f(x) for x in xs]

    # Construir tabla con i, x, f(x), peso
    tabla = []
    suma = fs[0] + fs[-1]
    for i, (x, fx) in enumerate(zip(xs, fs)):
        if 0 < i < n:
            peso = 4 if i % 2 == 1 else 2
            suma += peso * fx
        else:
            peso = 1
        tabla.append({"i": i, "x": num(x), "f(x)": num(fx), "peso": peso})

    # Construcción de suma (sustitución)
    suma_str_parts = [f"f({tabla[0]['x']})"]
    for i in range(1, len(tabla) - 1):
        peso = tabla[i]["peso"]
        suma_str_parts.append(f"{peso}f({tabla[i]['x']})")
    suma_str_parts.append(f"f({tabla[-1]['x']})")
    sustitucion = "S = " + " + ".join(suma_str_parts)

    valor = (h / 3) * suma

    formula = (
        "∫ f(x)dx ≈ (h/3) * [f(x₀) + 4f(x₁) + 2f(x₂) + 4f(x₃) + ... + 4f(xₙ₋₁) + f(xₙ)]"
    )

    historial = [{
        "iter": 1,
        "detalle": (
            f"Regla de Simpson\n"
            f"Intervalo: [{num(a)}, {num(b)}]\n"
            f"Paso h = {num(h)}\n"
            f"Número de subintervalos: {n} (par)\n\n"
            f"Fórmula: {formula}\n\n"
            f"Tabla de evaluaciones (con pesos):\n"
            f"{sustitucion}\n\n"
            f"Resultado: Integral ≈ (h/3) * S = {num(valor)}\n"
        )
    }]

    return {
        "metodo": "Simpson compuesto",
        "a": a,
        "b": b,
        "n": n,
        "h": num(h),
        "valor": valor,
        "resultados": tabla,
        "historial": historial,
        "formula": formula,
        "tabla": tabla,
        "sustitucion": sustitucion
    }
