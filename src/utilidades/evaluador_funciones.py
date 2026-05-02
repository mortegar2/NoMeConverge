from typing import Callable
import numpy as np
import math


class EvaluadorFunciones:
    """
    Convierte una expresión matemática en una función f(x) evaluable.

    La evaluación se realiza de forma controlada usando un entorno seguro
    para evitar ejecución de código no permitido.
    """

    # =========================================================
    # ENTORNO SEGURO DE EVALUACIÓN
    # =========================================================
    # Solo se permiten funciones matemáticas controladas
    NAMESPACE_SEGURO = {
        "np": np,
        "math": math,

        # Funciones matemáticas permitidas
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "log10": np.log10,
        "sqrt": np.sqrt,
        "abs": abs,

        # Constantes matemáticas
        "pi": np.pi,
        "e": np.e
    }

    # =========================================================
    # NORMALIZACIÓN DE EXPRESIONES
    # =========================================================
    @staticmethod
    def _normalizar_expresion(expresion: str) -> str:
        """
        Adapta la expresión ingresada por el usuario a sintaxis Python válida.
        """

        # Conversión de notación matemática común a Python
        expresion = expresion.replace("^", "**")

        # Soporte para entradas en español
        expresion = expresion.replace("sen", "sin")
        expresion = expresion.replace("raiz", "sqrt")

        return expresion

    # =========================================================
    # CREACIÓN DE FUNCIÓN f(x)
    # =========================================================
    @staticmethod
    def crear_funcion_univariable(expresion: str) -> Callable[[float], float]:
        """
        Convierte una expresión matemática en una función evaluable f(x).

        Ejemplo:
            "x**2 + sin(x)" → función f(x)

        Parameters
        ----------
        expresion : str
            Expresión matemática ingresada por el usuario.

        Returns
        -------
        Callable
            Función f(x) evaluable.
        
        Raises
        ------
        ValueError
            Si la expresión contiene sintaxis inválida.
        """

        # Normaliza la expresión del usuario
        expresion = EvaluadorFunciones._normalizar_expresion(expresion)

        # Entorno seguro de ejecución
        namespace = EvaluadorFunciones.NAMESPACE_SEGURO.copy()

        # Valida la expresión con un valor de prueba
        try:
            eval(
                expresion,
                {"__builtins__": {}},
                {**namespace, "x": 1.0}
            )
        except Exception as e:
            raise ValueError(f"Expresión inválida: {str(e)}")

        def f(x_val: float) -> float:
            """
            Evalúa la expresión en un valor x específico.
            """
            try:
                return eval(
                    expresion,
                    {"__builtins__": {}},  # bloqueo de funciones peligrosas
                    {**namespace, "x": x_val}
                )
            except Exception as e:
                # Retorna NaN si hay error (para que el filtrado lo maneje)
                return float('nan')

        return f