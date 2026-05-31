from src.utilidades.excepciones import ParametrosInvalidosError


def _validar_parametros(t0, tf, n):
    if tf <= t0:
        raise ParametrosInvalidosError("El tiempo final tf debe ser mayor que t0.")
    if n <= 0:
        raise ParametrosInvalidosError("El número de pasos n debe ser un entero positivo.")


def euler(f, t0, y0, tf, n):
    """Método de Euler para ecuaciones diferenciales ordinarias."""
    _validar_parametros(t0, tf, n)

    h = (tf - t0) / n
    t = t0
    y = y0

    historial = []
    tabla = []

    for i in range(1, n + 1):
        f_val = f(t, y)
        y_next = y + h * f_val
        detalle = (f"----------------------------------------\n"
                   f"PASO {i}\n"
                   f"----------------------------------------\n"
                   f"t = {t}\n"
                   f"y = {y}\n"
                   f"f(t,y) = {f_val}\n"
                   f"h = {h}\n"
                   f"y_next = {y} + {h} * {f_val} = {y_next}\n"
                   f"\n")

        historial.append({
            "iter": i,
            "t": t,
            "y": y,
            "f": f_val,
            "y_next": y_next,
            "detalle": detalle
        })

        tabla.append({
            "i": i,
            "t": t,
            "y": y,
            "f(t,y)": f_val,
            "y_next": y_next
        })

        t += h
        y = y_next

    return {
        "metodo": "Euler",
        "t0": t0,
        "y0": y0,
        "tf": tf,
        "n": n,
        "h": h,
        "ts": [row["t"] for row in tabla] + [tf],
        "ys": [row["y"] for row in tabla] + [y],
        "tabla": tabla,
        "historial": historial,
        "valor": y
    }


def runge_kutta_4(f, t0, y0, tf, n):
    """Método de Runge-Kutta de cuarto orden para ecuaciones diferenciales."""
    _validar_parametros(t0, tf, n)

    h = (tf - t0) / n
    t = t0
    y = y0

    historial = []
    tabla = []

    for i in range(1, n + 1):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h * k1 / 2)
        k3 = f(t + h / 2, y + h * k2 / 2)
        k4 = f(t + h, y + h * k3)

        y_next = y + (h / 6) * (k1 + 2 * k2 + 2 * k3 + k4)

        detalle = (f"----------------------------------------\n"
                   f"PASO {i}\n"
                   f"----------------------------------------\n"
                   f"t = {t}\n"
                   f"y = {y}\n"
                   f"k1 = f(t, y) = {k1}\n"
                   f"k2 = f(t + h/2, y + h*k1/2) = {k2}\n"
                   f"k3 = f(t + h/2, y + h*k2/2) = {k3}\n"
                   f"k4 = f(t + h, y + h*k3) = {k4}\n"
                   f"y_next = {y} + (h/6)*({k1} + 2*{k2} + 2*{k3} + {k4}) = {y_next}\n")

        historial.append({
            "iter": i,
            "t": t,
            "y": y,
            "k1": k1,
            "k2": k2,
            "k3": k3,
            "k4": k4,
            "y_next": y_next,
            "detalle": detalle
        })

        tabla.append({
            "i": i,
            "t": t,
            "y": y,
            "k1": k1,
            "k2": k2,
            "k3": k3,
            "k4": k4,
            "y_next": y_next
        })

        t += h
        y = y_next

    return {
        "metodo": "Runge-Kutta 4",
        "t0": t0,
        "y0": y0,
        "tf": tf,
        "n": n,
        "h": h,
        "ts": [row["t"] for row in tabla] + [tf],
        "ys": [row["y"] for row in tabla] + [y],
        "tabla": tabla,
        "historial": historial,
        "valor": y
    }
