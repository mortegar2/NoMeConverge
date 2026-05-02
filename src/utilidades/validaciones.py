from .excepciones import IntervaloInvalidoError, ParametrosInvalidosError

def validar_parametros_numericos(tol: float, max_iter: int):
    if tol <= 0:
        raise ParametrosInvalidosError("La tolerancia debe ser mayor que 0.")
    if max_iter <= 0:
        raise ParametrosInvalidosError("El número de iteraciones debe ser mayor que 0.")
    
def validar_intervalo(a: float, b: float, f):
    if a >= b:
        raise IntervaloInvalidoError("El valor de 'a' debe ser menor que 'b'.")
    
    if f(a) * f(b) >= 0:
        raise IntervaloInvalidoError(
            "La función debe cambiar de signo en el intervalo [a, b]."
        )