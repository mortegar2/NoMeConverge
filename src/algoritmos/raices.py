"""
Módulo: Cálculo de Raíces

Incluye:
- Resultado numérico
- Historial
- Procedimiento paso a paso (detalle)
"""

from typing import Callable, Dict, List, Any

from src.utilidades.excepciones import (
    DerivadaCeroError,
    NoConvergeError
)

from src.utilidades.validaciones import (
    validar_intervalo,
    validar_parametros_numericos
)


# =========================================================
# MÉTODO DE BISECCIÓN
# =========================================================
def biseccion(f, a, b, tol=1e-6, max_iter=100):

    validar_parametros_numericos(tol, max_iter)
    validar_intervalo(a, b, f)

    historial = []
    fa, fb = f(a), f(b)

    for i in range(1, max_iter + 1):

        c = (a + b) / 2
        fc = f(c)
        error = abs(b - a) / 2

        detalle = f"""
----------------------------------------
ITERACIÓN {i}
----------------------------------------
a = {a}
b = {b}

c = (a + b)/2 = {c}

f(c) = {fc}

Error = {error}
"""

        historial.append({
            "iter": i,
            "valor_parcial": c,
            "error": error,
            "detalle": detalle
        })

        if abs(fc) < tol or error < tol:
            return {
                "raiz": c,
                "iteraciones": i,
                "error": error,
                "historial": historial
            }

        if fa * fc < 0:
            b, fb = c, fc
        else:
            a, fa = c, fc

    raise NoConvergeError("Bisección no convergió")


# =========================================================
# MÉTODO DE NEWTON-RAPHSON
# =========================================================
def newton_raphson(f, x0, tol=1e-6, max_iter=100, df=None):

    validar_parametros_numericos(tol, max_iter)

    historial = []
    x = x0

    for i in range(1, max_iter + 1):

        fx = f(x)

        if df is None:
            h = 1e-8
            dfx = (f(x + h) - f(x - h)) / (2 * h)
        else:
            dfx = df(x)

        if abs(dfx) < 1e-12:
            raise DerivadaCeroError("Derivada cercana a cero")

        x_new = x - fx / dfx
        error = abs(x_new - x)

        detalle = f"""
----------------------------------------
ITERACIÓN {i}
----------------------------------------
x = {x}
f(x) = {fx}
f'(x) = {dfx}

x_nuevo = {x} - ({fx}/{dfx})
x_nuevo = {x_new}

Error = {error}
"""

        historial.append({
            "iter": i,
            "valor_parcial": x_new,
            "error": error,
            "detalle": detalle
        })

        if error < tol:
            return {
                "raiz": x_new,
                "iteraciones": i,
                "error": error,
                "historial": historial
            }

        x = x_new

    raise NoConvergeError("Newton no convergió")


# =========================================================
# MÉTODO DE SECANTE
# =========================================================
def secante(f, x0, x1, tol=1e-6, max_iter=100):

    validar_parametros_numericos(tol, max_iter)

    historial = []

    for i in range(1, max_iter + 1):

        f_x0 = f(x0)
        f_x1 = f(x1)

        denom = f_x1 - f_x0

        if denom == 0:
            raise DerivadaCeroError("División por cero")

        x2 = x1 - f_x1 * (x1 - x0) / denom
        error = abs(x2 - x1)

        detalle = f"""
----------------------------------------
ITERACIÓN {i}
----------------------------------------
x0 = {x0}
x1 = {x1}

x2 = {x1} - ({f_x1} * ({x1} - {x0})) / ({f_x1} - {f_x0})
x2 = {x2}

Error = {error}
"""

        historial.append({
            "iter": i,
            "valor_parcial": x2,
            "error": error,
            "detalle": detalle
        })

        if error < tol:
            return {
                "raiz": x2,
                "iteraciones": i,
                "error": error,
                "historial": historial
            }

        x0, x1 = x1, x2

    raise NoConvergeError("Secante no convergió")