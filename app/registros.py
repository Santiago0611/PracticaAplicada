from datetime import date, datetime

from flask import Blueprint, jsonify, request

from . import db
from .decorators import requiere_rol
from .models import CatalogoProducto, Mascota, RegistroAplicacion

registros_bp = Blueprint("registros", __name__)


def _parsear_fecha(valor):
    try:
        return datetime.strptime(valor, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@registros_bp.route("/mascotas/<int:mascota_id>/vacunas", methods=["POST"])
@requiere_rol("veterinario")
def registrar_vacuna(mascota_id, usuario_actual):
    datos = request.get_json(silent=True) or {}

    mascota = Mascota.query.filter_by(id=mascota_id, activo=True).first()
    if not mascota:
        return jsonify({"error": "Mascota no encontrada"}), 404

    if not datos.get("catalogo_id"):
        return jsonify({"error": "El tipo de vacuna es obligatorio."}), 400

    producto = CatalogoProducto.query.get(datos["catalogo_id"])
    if not producto or producto.tipo != "vacuna":
        return jsonify({"error": "La vacuna seleccionada no existe en el catálogo."}), 400

    fecha_aplicacion = _parsear_fecha(datos.get("fecha_aplicacion"))
    if fecha_aplicacion is None:
        return jsonify({"error": "La fecha de aplicación es obligatoria (formato AAAA-MM-DD)."}), 400
    if fecha_aplicacion > date.today():
        return jsonify({"error": "La fecha de aplicación no puede ser posterior a hoy."}), 400

    fecha_proxima = None
    if datos.get("fecha_proxima"):
        fecha_proxima = _parsear_fecha(datos["fecha_proxima"])
        if fecha_proxima is None or fecha_proxima <= fecha_aplicacion:
            return jsonify({"error": "La próxima dosis debe ser una fecha posterior a la aplicación."}), 400

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
        veterinario_id=usuario_actual.id,
        fecha_aplicacion=fecha_aplicacion,
        fecha_proxima=fecha_proxima,
        dosis=datos.get("dosis"),
        observaciones=datos.get("observaciones"),
    )
    db.session.add(registro)
    db.session.commit()

    return jsonify(registro.to_dict()), 201