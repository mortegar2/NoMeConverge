"""
Módulo: Sistemas Lineales

Implementación de métodos numéricos para resolver sistemas de ecuaciones lineales.
Incluye método de Gauss-Seidel y factorización LU con procedimiento detallado.
"""

from typing import List, Dict, Any


def _validar_matriz(A: List[List[float]], b: List[float] = None):
    if len(A) == 0:
        raise ValueError("La matriz A no puede estar vacía.")

    n = len(A)
    if any(len(fila) != n for fila in A):
        raise ValueError("La matriz A debe ser cuadrada.")

    if b is not None and len(b) != n:
        raise ValueError("El vector b debe tener la misma dimensión que A.")


def gauss_seidel(
    A: List[List[float]],
    b: List[float],
    x0: List[float] = None,
    tol: float = 1e-6,
    max_iter: int = 100
) -> Dict[str, Any]:
    """Resuelve un sistema Ax = b usando el método iterativo de Gauss-Seidel."""
    _validar_matriz(A, b)

    n = len(A)
    x_old = [0.0] * n if x0 is None else list(x0)
    if len(x_old) != n:
        raise ValueError("El vector de aproximación inicial x0 debe tener la dimensión del sistema.")

    historial = []
    resultado = x_old.copy()
    error = float("inf")

    for k in range(1, max_iter + 1):
        detalle = f"ITERACIÓN {k}:\n"
        x_new = resultado.copy()

        for i in range(n):
            if abs(A[i][i]) < 1e-12:
                raise ValueError(f"Coeficiente diagonal nulo en fila {i + 1}.")

            sumatoria_anterior = sum(A[i][j] * x_new[j] for j in range(i))
            sumatoria_posterior = sum(A[i][j] * resultado[j] for j in range(i + 1, n))
            x_new[i] = (b[i] - sumatoria_anterior - sumatoria_posterior) / A[i][i]

            detalle += (
                f"  x{i+1} = (b{i+1} - ({sumatoria_anterior:.6g}) - "
                f"({sumatoria_posterior:.6g})) / {A[i][i]:.6g} = {x_new[i]:.6g}\n"
            )

        error = max(abs(x_new[i] - resultado[i]) for i in range(n))
        detalle += f"  Error máximo = {error:.6g}\n"

        resultado = x_new
        historial.append({
            "iter": k,
            "x": resultado.copy(),
            "error": error,
            "detalle": detalle
        })

        if error < tol:
            break

    return {
        "solucion": resultado,
        "iteraciones": k,
        "error": error,
        "historial": historial,
        "A": A,
        "b": b,
        "x0": x0 if x0 is not None else [0.0] * n,
        "metodo": "Gauss-Seidel"
    }


def lu_factorization(A: List[List[float]], b: List[float] = None) -> Dict[str, Any]:
    """Factoriza la matriz A en L y U y resuelve Ax = b si se proporciona b."""
    _validar_matriz(A, b)

    n = len(A)
    L = [[0.0] * n for _ in range(n)]
    U = [[0.0] * n for _ in range(n)]
    historial = []

    for i in range(n):
        L[i][i] = 1.0

        for j in range(i, n):
            suma = sum(L[i][k] * U[k][j] for k in range(i))
            U[i][j] = A[i][j] - suma

        if abs(U[i][i]) < 1e-12:
            raise ValueError(f"Pivot nulo en U[{i}][{i}]. No se puede factorizar sin pivoteo.")

        for j in range(i + 1, n):
            suma = sum(L[j][k] * U[k][i] for k in range(i))
            L[j][i] = (A[j][i] - suma) / U[i][i]

        detalle = f"ETAPA {i + 1}: factorizar fila {i + 1}\n"
        detalle += f"  U fila {i + 1}: {[round(valor, 6) for valor in U[i]]}\n"
        detalle += f"  L columna {i + 1}: {[round(L[fila][i], 6) for fila in range(n)]}\n"
        historial.append({
            "iter": i + 1,
            "detalle": detalle,
            "L": [fila.copy() for fila in L],
            "U": [fila.copy() for fila in U]
        })

    y = None
    x = None

    if b is not None:
        y = [0.0] * n
        for i in range(n):
            y[i] = (b[i] - sum(L[i][j] * y[j] for j in range(i))) / L[i][i]

        x = [0.0] * n
        for i in range(n - 1, -1, -1):
            if abs(U[i][i]) < 1e-12:
                raise ValueError(f"Pivot nulo en U[{i}][{i}] durante sustitución regresiva.")
            x[i] = (y[i] - sum(U[i][j] * x[j] for j in range(i + 1, n))) / U[i][i]

        detalle = "SOLUCIÓN mediante sustitución:\n"
        detalle += f"  y = {[round(valor, 6) for valor in y]}\n"
        detalle += f"  x = {[round(valor, 6) for valor in x]}\n"
        historial.append({
            "iter": n + 1,
            "detalle": detalle,
            "L": [fila.copy() for fila in L],
            "U": [fila.copy() for fila in U]
        })

    return {
        "L": L,
        "U": U,
        "y": y,
        "x": x,
        "historial": historial,
        "A": A,
        "b": b,
        "metodo": "LU"
    }
