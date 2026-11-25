from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request

from . import db
from .acceso import mascotas_visibles, obtener_mascota_autorizada
from .decorators import requiere_rol
from .models import Mascota, PacienteVeterinario, Usuario

mascotas_bp = Blueprint("mascotas", __name__)


def _validar_payload_mascota(data, *, parcial=False):
    errores = {}
    datos = {}

    for campo, limite in (("nombre", 100), ("especie", 50), ("raza", 100), ("sexo", 10), ("foto", 255)):
        if campo not in data and (parcial or campo == "foto"):
            continue
        valor = data.get(campo)
        if valor is not None and not isinstance(valor, str):
            errores[campo] = "Ingresa un texto válido."
            continue
        valor = (valor or "").strip()
        if len(valor) > limite:
            errores[campo] = f"Usa como máximo {limite} caracteres."
        elif campo == "nombre" and not valor:
            errores[campo] = "El nombre de la mascota es obligatorio."
        elif campo == "especie" and valor.upper() not in Mascota.ESPECIES_VALIDAS:
            errores[campo] = f"Especie inválida. Opciones: {', '.join(Mascota.ESPECIES_VALIDAS)}."
        elif campo == "sexo" and valor.lower() not in ("", "macho", "hembra"):
            errores[campo] = "El sexo debe ser macho o hembra."
        elif campo == "especie":
            datos[campo] = valor.upper()
        elif campo == "sexo":
            datos[campo] = valor.lower() or None
        else:
            datos[campo] = valor or None

    if "fecha_nacimiento" in data:
        valor = data["fecha_nacimiento"]
        try:
            fecha = date.fromisoformat(valor) if valor not in (None, "") else None
            if fecha and fecha > date.today():
                errores["fecha_nacimiento"] = "La fecha de nacimiento no puede ser futura."
            else:
                datos["fecha_nacimiento"] = fecha
        except (TypeError, ValueError):
            errores["fecha_nacimiento"] = "Formato de fecha inválido. Usa AAAA-MM-DD."

    if "peso_kg" in data or "peso" in data:
        valor = data.get("peso_kg", data.get("peso"))
        try:
            peso = Decimal(str(valor)) if valor not in (None, "") else None
            if peso is not None and (
                not peso.is_finite() or not Decimal("0.01") <= peso <= Decimal("999.99")
            ):
                errores["peso_kg"] = "El peso debe estar entre 0,01 y 999,99 kg."
            else:
                datos["peso"] = peso
        except InvalidOperation:
            errores["peso_kg"] = "El peso debe ser un número."

    return datos, errores


def _validar_solicitud_mascota(*, parcial=False):
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return None, (jsonify({"detalle": "Envía los datos de la mascota en formato JSON."}), 400)
    limpios, errores = _validar_payload_mascota(datos, parcial=parcial)
    if errores:
        return None, (jsonify({"detalle": "Datos inválidos.", "errores": errores}), 400)
    return limpios, None


def _hay_duplicado(propietario_id, nombre, especie, sexo, excluir_id=None):
    consulta = Mascota.query.filter_by(
        propietario_id=propietario_id, nombre=nombre, especie=especie, sexo=sexo, activo=True
    )
    if excluir_id is not None:
        consulta = consulta.filter(Mascota.id != excluir_id)
    return consulta.with_for_update().first() is not None


@mascotas_bp.route("/mascotas", methods=["POST"])
@requiere_rol(Usuario.ROL_PROPIETARIO)
def registrar_mascota(usuario_actual):
    limpio, error = _validar_solicitud_mascota()
    if error:
        return error

    db.session.get(Usuario, usuario_actual.id, with_for_update=True)
    if _hay_duplicado(usuario_actual.id, limpio["nombre"], limpio["especie"], limpio["sexo"]):
        return jsonify({"detalle": "Ya tienes una mascota con ese nombre, especie y sexo."}), 409

    mascota = Mascota(propietario_id=usuario_actual.id, **limpio)
    db.session.add(mascota)
    db.session.commit()

    return jsonify(mascota.to_dict()), 201


@mascotas_bp.route("/mascotas", methods=["GET"])
@requiere_rol(*Usuario.ROLES_VALIDOS)
def listar_mascotas(usuario_actual):
    mascotas = mascotas_visibles(usuario_actual).order_by(Mascota.id.desc()).all()
    return jsonify([mascota.to_dict() for mascota in mascotas])


@mascotas_bp.route("/mascotas/<int:mascota_id>", methods=["GET"])
@requiere_rol(*Usuario.ROLES_VALIDOS)
def obtener_mascota(mascota_id, usuario_actual):
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual)
    return jsonify(mascota.to_dict())


@mascotas_bp.route("/mascotas/<int:mascota_id>", methods=["PUT"])
@requiere_rol(Usuario.ROL_PROPIETARIO)
def editar_mascota(mascota_id, usuario_actual):
    limpio, error = _validar_solicitud_mascota(parcial=True)
    if error:
        return error

    db.session.get(Usuario, usuario_actual.id, with_for_update=True)
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual, para_escritura=True)
    campos = ("nombre", "especie", "sexo")
    actual = tuple(getattr(mascota, campo) for campo in campos)
    nuevo = tuple(limpio.get(campo, valor) for campo, valor in zip(campos, actual))
    if nuevo != actual and _hay_duplicado(usuario_actual.id, *nuevo, excluir_id=mascota.id):
        return jsonify({"detalle": "Ya tienes una mascota con ese nombre, especie y sexo."}), 409

    for campo, valor in limpio.items():
        setattr(mascota, campo, valor)
    db.session.commit()
    return jsonify(mascota.to_dict())


@mascotas_bp.route("/mascotas/<int:mascota_id>", methods=["DELETE"])
@requiere_rol(Usuario.ROL_PROPIETARIO)
def eliminar_mascota(mascota_id, usuario_actual):
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual, para_escritura=True)
    mascota.activo = False
    db.session.commit()

    return jsonify({"detalle": "Mascota eliminada correctamente."})


@mascotas_bp.route("/mascotas/<int:mascota_id>/veterinarios", methods=["GET"])
@requiere_rol(Usuario.ROL_PROPIETARIO)
def listar_veterinarios(mascota_id, usuario_actual):
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual)
    veterinarios = (
        Usuario.query.join(PacienteVeterinario, PacienteVeterinario.veterinario_id == Usuario.id)
        .filter(PacienteVeterinario.mascota_id == mascota.id)
        .order_by(Usuario.nombre, Usuario.id)
    )
    return jsonify([_datos_veterinario(veterinario) for veterinario in veterinarios])


def _datos_veterinario(veterinario):
    return {"id": veterinario.id, "nombre": veterinario.nombre, "correo": veterinario.correo}


@mascotas_bp.route("/mascotas/<int:mascota_id>/veterinarios", methods=["POST"])
@requiere_rol(Usuario.ROL_PROPIETARIO)
def autorizar_veterinario(mascota_id, usuario_actual):
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual, para_escritura=True)
    datos = request.get_json(silent=True)
    correo = datos.get("correo") if isinstance(datos, dict) else None
    if not isinstance(correo, str) or not correo.strip() or len(correo.strip()) > 150:
        return jsonify({"detalle": "Ingresa el correo registrado del veterinario."}), 400

    veterinario = Usuario.query.filter(
        db.func.lower(Usuario.correo) == correo.strip().lower(),
        Usuario.rol == Usuario.ROL_VETERINARIO,
        Usuario.estado == "activo",
    ).first()
    if veterinario is None:
        return jsonify({"detalle": "No hay un veterinario activo registrado con ese correo."}), 404

    if db.session.get(PacienteVeterinario, (mascota.id, veterinario.id), with_for_update=True) is not None:
        return jsonify(_datos_veterinario(veterinario))

    db.session.add(PacienteVeterinario(mascota_id=mascota.id, veterinario_id=veterinario.id))
    db.session.commit()
    return jsonify(_datos_veterinario(veterinario)), 201


@mascotas_bp.route("/mascotas/<int:mascota_id>/veterinarios/<int:veterinario_id>", methods=["DELETE"])
@requiere_rol(Usuario.ROL_PROPIETARIO)
def retirar_veterinario(mascota_id, veterinario_id, usuario_actual):
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual, para_escritura=True)
    enlace = db.session.get(PacienteVeterinario, (mascota.id, veterinario_id), with_for_update=True)
    if enlace is not None:
        db.session.delete(enlace)
        db.session.commit()
    return "", 204
