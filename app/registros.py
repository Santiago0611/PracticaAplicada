from datetime import date, datetime

from flask import Blueprint, jsonify, request

from . import db
from .decorators import requiere_rol
from .models import CatalogoProducto, Mascota, RegistroAplicacion
from .calculos import calcular_proxima_dosis
registros_bp = Blueprint("registros", __name__)

TIPOS_VACUNA = ("vacuna",)
TIPOS_DESPARASITANTE = (
    "desparasitante_interno",
    "desparasitante_externo",
    "desparasitante_ambos",
)


def _parsear_fecha(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def _registrar_aplicacion(mascota_id, usuario, tipos_validos, categoria):
    datos = request.get_json(silent=True) or {}

    mascota = Mascota.query.filter_by(id=mascota_id, activo=True).first()
    if not mascota:
        return jsonify({"error": "Mascota no encontrada"}), 404

    if not datos.get("catalogo_id"):
        return jsonify({"error": f"El tipo de {categoria} es obligatorio."}), 400

    producto = CatalogoProducto.query.get(datos["catalogo_id"])
    if not producto or producto.tipo not in tipos_validos:
        return jsonify({"error": f"El producto seleccionado no existe en el catálogo de {categoria}s."}), 400

    fecha_aplicacion = _parsear_fecha(datos.get("fecha_aplicacion"))
    if fecha_aplicacion is None:
        return jsonify({"error": "La fecha de aplicación es obligatoria (formato AAAA-MM-DD)."}), 400
    if fecha_aplicacion > date.today():
        return jsonify({"error": "La fecha de aplicación no puede ser posterior a hoy."}), 400

    if datos.get("fecha_proxima"):
        fecha_proxima = _parsear_fecha(datos["fecha_proxima"])
        if fecha_proxima is None or fecha_proxima <= fecha_aplicacion:
            return jsonify({"error": "La próxima dosis debe ser una fecha posterior a la aplicación."}), 400
    else:
        fecha_proxima = calcular_proxima_dosis(fecha_aplicacion, producto)

    duplicado = RegistroAplicacion.query.filter_by(
        mascota_id=mascota.id,
        catalogo_id=producto.id,
        fecha_aplicacion=fecha_aplicacion,
    ).first()
    if duplicado:
        return jsonify({"error": "Ya existe un registro con estos mismos datos."}), 400

    registro = RegistroAplicacion(
        mascota_id=mascota.id,
        catalogo_id=producto.id,
        veterinario_id=usuario.id,
        fecha_aplicacion=fecha_aplicacion,
        fecha_proxima=fecha_proxima,
        dosis=datos.get("dosis"),
        observaciones=datos.get("observaciones"),
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify(registro.to_dict()), 201


@registros_bp.route("/mascotas/<int:mascota_id>/vacunas", methods=["POST"])
@requiere_rol("veterinario")
def registrar_vacuna(mascota_id, usuario_actual):
    return _registrar_aplicacion(mascota_id, usuario_actual, TIPOS_VACUNA, "vacuna")


@registros_bp.route("/mascotas/<int:mascota_id>/desparasitaciones", methods=["POST"])
@requiere_rol("veterinario")
def registrar_desparasitacion(mascota_id, usuario_actual):
    return _registrar_aplicacion(mascota_id, usuario_actual, TIPOS_DESPARASITANTE, "desparasitante")