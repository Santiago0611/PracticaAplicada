import os
from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import contains_eager, joinedload

from .acceso import filtro_mascotas_visibles
from .calculos import calcular_proxima_dosis
from .decorators import requiere_rol
from .models import Mascota, RegistroAplicacion

dosis_bp = Blueprint("dosis", __name__)

DIAS_ALERTA = int(os.getenv("DIAS_ALERTA_DOSIS", "30"))
ESTADOS_VALIDOS = ("vigente", "proxima", "vencida")


def _fecha_vencimiento(registro):
    if registro.fecha_proxima:
        return registro.fecha_proxima
    return calcular_proxima_dosis(registro.fecha_aplicacion, registro.producto)


def _clasificar(fecha_vencimiento, hoy):
    if fecha_vencimiento < hoy:
        return "vencida"
    if fecha_vencimiento <= hoy + timedelta(days=DIAS_ALERTA):
        return "proxima"
    return "vigente"


def obtener_dosis(usuario, hoy=None):
    """Devuelve el estado de la última aplicación por producto y mascota visible."""
    hoy = hoy or date.today()

    consulta = (
        RegistroAplicacion.query.join(RegistroAplicacion.mascota)
        .options(contains_eager(RegistroAplicacion.mascota), joinedload(RegistroAplicacion.producto))
        .filter(Mascota.activo.is_(True), filtro_mascotas_visibles(usuario))
    )

    registros = consulta.order_by(
        RegistroAplicacion.fecha_aplicacion.asc(), RegistroAplicacion.id.asc()
    ).all()

    # Se queda con la aplicación más reciente de cada mascota y producto.
    ultimos = {}
    for registro in registros:
        ultimos[(registro.mascota_id, registro.catalogo_id)] = registro

    resultado = []
    for registro in ultimos.values():
        vencimiento = _fecha_vencimiento(registro)
        if vencimiento is None:
            continue
        resultado.append(
            {
                "mascota_id": registro.mascota_id,
                "mascota": registro.mascota.nombre,
                "propietario_id": registro.mascota.propietario_id,
                "producto": registro.producto.nombre,
                "tipo": registro.producto.tipo,
                "fecha_aplicacion": registro.fecha_aplicacion.isoformat(),
                "fecha_vencimiento": vencimiento.isoformat(),
                "dias_restantes": (vencimiento - hoy).days,
                "estado": _clasificar(vencimiento, hoy),
            }
        )

    resultado.sort(key=lambda d: d["fecha_vencimiento"])
    return resultado


@dosis_bp.route("/dosis", methods=["GET"])
@requiere_rol("propietario", "veterinario")
def listar_dosis(usuario_actual):
    estado = request.args.get("estado")
    if estado and estado not in ESTADOS_VALIDOS:
        return jsonify({"error": "El estado debe ser vigente, proxima o vencida."}), 400

    dosis = obtener_dosis(usuario_actual)
    if estado:
        dosis = [d for d in dosis if d["estado"] == estado]
    else:
        dosis = [d for d in dosis if d["estado"] != "vigente"]

    return jsonify(dosis), 200
