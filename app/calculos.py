from datetime import timedelta


def calcular_proxima_dosis(fecha_aplicacion, producto):
    """fecha_proxima = fecha_aplicacion + intervalo_dias del producto.

    Devuelve None si el producto no tiene un intervalo definido.
    """
    if not producto.intervalo_dias:
        return None
    return fecha_aplicacion + timedelta(days=producto.intervalo_dias)