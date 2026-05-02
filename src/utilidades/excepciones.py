class MetodosNumericosError(Exception):
    """Clase base para errores de métodos numéricos."""
    pass

class NoConvergeError(MetodosNumericosError):
    """Se lanza cuando el métodos no converge."""
    pass

class DerivadaCeroError(MetodosNumericosError):
    """Se lanza cunado la derivada es cero."""
    pass

class IntervaloInvalidoError(MetodosNumericosError):
    """Intervalo no válido para bisección."""
    pass

class ParametrosInvalidosError(MetodosNumericosError):
    """Parámetros inválidos."""
    pass