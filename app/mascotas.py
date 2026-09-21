from datetime import date, datetime

from flask import Blueprint, jsonify, request

from app import db
from app.decorators import requiere_rol
from app.models import Mascota, Usuario

mascotas_bp = Blueprint("mascotas", __name__)


def _validar_payload_mascota(data: dict) -> dict:
    errores = {}

    nombre = (data.get("nombre") or "").strip()
    if not nombre:
        errores["nombre"] = "El nombre de la mascota es obligatorio."

    especie = (data.get("especie") or "").upper()
    if especie not in Mascota.ESPECIES_VALIDAS:
        errores["especie"] = f"Especie inválida. Opciones: {Mascota.ESPECIES_VALIDAS}."

    fecha_nacimiento = None
    fecha_raw = data.get("fecha_nacimiento")
    if fecha_raw:
        try:
            fecha_nacimiento = datetime.strptime(fecha_raw, "%Y-%m-%d").date()
            if fecha_nacimiento > date.today():
                errores["fecha_nacimiento"] = "La fecha de nacimiento no puede ser futura."
        except ValueError:
            errores["fecha_nacimiento"] = "Formato de fecha inválido. Usa AAAA-MM-DD."

    peso_kg = data.get("peso_kg")
    if peso_kg is not None:
        try:
            peso_kg = float(peso_kg)
            if peso_kg <= 0:
                errores["peso_kg"] = "El peso debe ser mayor que 0."
        except (TypeError, ValueError):
            errores["peso_kg"] = "El peso debe ser un número."

    return {
        "errores": errores,
        "datos_limpios": {
            "nombre": nombre,
            "especie": especie,
            "raza": (data.get("raza") or "").strip(),
            "fecha_nacimiento": fecha_nacimiento,
            "peso_kg": peso_kg,
        },
    }


@mascotas_bp.route("/mascotas", methods=["POST"])
@requiere_rol(Usuario.ROL_PROPIETARIO)
def registrar_mascota(usuario_actual: Usuario):
    data = request.get_json(silent=True) or {}
    validacion = _validar_payload_mascota(data)

    if validacion["errores"]:
        return jsonify({"detalle": "Datos inválidos.", "errores": validacion["errores"]}), 400

    limpio = validacion["datos_limpios"]

    duplicado = Mascota.query.filter_by(
        propietario_id=usuario_actual.id,
        nombre=limpio["nombre"],
        especie=limpio["especie"],
        activo=True,
    ).first()
    if duplicado:
        return (
            jsonify({"detalle": "Ya tienes una mascota registrada con ese nombre y especie."}),
            409,
        )

    mascota = Mascota(
        propietario_id=usuario_actual.id,
        nombre=limpio["nombre"],
        especie=limpio["especie"],
        raza=limpio["raza"],
        fecha_nacimiento=limpio["fecha_nacimiento"],
        peso_kg=limpio["peso_kg"],
    )

    db.session.add(mascota)
    db.session.commit()

    return jsonify(mascota.to_dict()), 201


@mascotas_bp.route("/mascotas", methods=["GET"])
@requiere_rol(Usuario.ROL_PROPIETARIO, Usuario.ROL_VETERINARIO)
def listar_mascotas(usuario_actual: Usuario):
    query = Mascota.query.filter_by(activo=True)

    if usuario_actual.es_propietario():
        query = query.filter_by(propietario_id=usuario_actual.id)

    mascotas = query.order_by(Mascota.creado_en.desc()).all()
    return jsonify([m.to_dict() for m in mascotas]), 200


@mascotas_bp.route("/mascotas/<int:mascota_id>", methods=["GET"])
@requiere_rol(Usuario.ROL_PROPIETARIO, Usuario.ROL_VETERINARIO)
def obtener_mascota(mascota_id: int, usuario_actual: Usuario):
    mascota = Mascota.query.filter_by(id=mascota_id, activo=True).first()

    if mascota is None:
        return jsonify({"detalle": "La mascota solicitada no existe o fue eliminada."}), 404

    if usuario_actual.es_propietario() and mascota.propietario_id != usuario_actual.id:
        return jsonify({"detalle": "No tienes permiso para consultar esta mascota."}), 403

    return jsonify(mascota.to_dict()), 200