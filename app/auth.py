import bcrypt
import jwt
import datetime
import os

def crear_token(usuario_id, rol):
    payload = {
        "usuario_id": usuario_id,
        "rol": rol,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")


def hashear_contrasena(contrasena):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(contrasena.encode("utf-8"), salt).decode("utf-8")

def verificar_contrasena(contrasena_plana, hash_guardado):
    return bcrypt.checkpw(contrasena_plana.encode("utf-8"), hash_guardado.encode("utf-8"))
import re

from flask import Blueprint, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)

from app import db
from app.models import Usuario

auth_bp = Blueprint("auth", __name__)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@auth_bp.route("/registro", methods=["POST"])
def registro():
    data = request.get_json(silent=True) or {}

    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    rol = (data.get("rol") or Usuario.ROL_PROPIETARIO).upper()

    errores = {}
    if not username:
        errores["username"] = "El nombre de usuario es obligatorio."
    if not EMAIL_REGEX.match(email):
        errores["email"] = "El correo electrónico no es válido."
    if len(password) < 8:
        errores["password"] = "La contraseña debe tener al menos 8 caracteres."
    if rol not in Usuario.ROLES_VALIDOS:
        errores["rol"] = f"Rol inválido. Debe ser uno de: {Usuario.ROLES_VALIDOS}."

    if errores:
        return jsonify({"detalle": "Datos inválidos.", "errores": errores}), 400

    if Usuario.query.filter(
        (Usuario.username == username) | (Usuario.email == email)
    ).first():
        return jsonify({"detalle": "El usuario o el correo ya están registrados."}), 409

    usuario = Usuario(username=username, email=email, rol=rol)
    usuario.set_password(password)

    db.session.add(usuario)
    db.session.commit()

    return jsonify(usuario.to_dict()), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    usuario = Usuario.query.filter_by(username=username).first()

    if usuario is None or not usuario.check_password(password):
        return jsonify({"detalle": "Usuario o contraseña incorrectos."}), 401

    claims_extra = {"rol": usuario.rol}
    access_token = create_access_token(
        identity=str(usuario.id), additional_claims=claims_extra
    )
    refresh_token = create_refresh_token(identity=str(usuario.id))

    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "usuario": usuario.to_dict(),
        }
    ), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refrescar_token():
    identidad = get_jwt_identity()
    usuario = Usuario.query.get(int(identidad))
    if usuario is None:
        return jsonify({"detalle": "Usuario no encontrado."}), 404

    nuevo_access = create_access_token(
        identity=str(usuario.id), additional_claims={"rol": usuario.rol}
    )
    return jsonify({"access_token": nuevo_access}), 200