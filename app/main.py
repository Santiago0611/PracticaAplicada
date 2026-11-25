import re

from flask import jsonify, request
from flask_jwt_extended import get_jwt, jwt_required
from sqlalchemy.exc import IntegrityError

from . import app, auth, db, esquema
from .acceso import respuesta_acceso
from .catalogo import catalogo_bp
from .decorators import requiere_rol
from .dosis import dosis_bp
from .estadisticas import estadisticas_bp
from .mascotas import mascotas_bp
from .models import TokenRevocado, Usuario
from .notificaciones import notificaciones_bp
from .registros import registros_bp

app.register_blueprint(mascotas_bp)
app.register_blueprint(registros_bp)
app.register_blueprint(dosis_bp)
app.register_blueprint(notificaciones_bp)
app.register_blueprint(catalogo_bp)
app.register_blueprint(estadisticas_bp)
app.register_error_handler(403, respuesta_acceso)
app.register_error_handler(404, respuesta_acceso)


def _correo_valido(valor):
    return isinstance(valor, str) and len(valor.strip()) <= 150 and re.fullmatch(
        r"[^@\s]+@[^@\s]+\.[^@\s]+", valor.strip()
    )


def _datos_cuenta(datos, *, parcial=False):
    limpios = {}
    if not isinstance(datos, dict):
        return None, "Envía los datos de la cuenta en formato JSON."

    if "nombre" in datos or not parcial:
        nombre = datos.get("nombre")
        if not isinstance(nombre, str) or not 1 <= len(nombre.strip()) <= 100:
            return None, "Ingresa un nombre de 1 a 100 caracteres."
        limpios["nombre"] = nombre.strip()

    if "correo" in datos or not parcial:
        correo = datos.get("correo")
        if not _correo_valido(correo):
            return None, "Ingresa un correo válido."
        limpios["correo"] = correo.strip().lower()

    if "contrasena" in datos or not parcial:
        contrasena = datos.get("contrasena")
        if not isinstance(contrasena, str) or len(contrasena) < 8 or len(contrasena.encode("utf-8")) > 72:
            return None, "La contraseña debe tener al menos 8 caracteres y ocupar como máximo 72 bytes."
        limpios["contrasena_hash"] = auth.hashear_contrasena(contrasena)

    return limpios, None


def _guardar_usuario():
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Ya existe un usuario registrado con este correo."}), 400
    return None


@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Ingresa tu correo y contraseña."}), 400

    correo = datos.get("correo")
    contrasena = datos.get("contrasena")
    if (
        not isinstance(correo, str)
        or not isinstance(contrasena, str)
        or len(contrasena.encode("utf-8")) > 72
    ):
        return jsonify({"error": "Credenciales inválidas."}), 401

    usuario = Usuario.query.filter(db.func.lower(Usuario.correo) == correo.strip().lower()).first()
    if (
        not usuario
        or usuario.estado == "inactivo"
        or usuario.rol not in Usuario.ROLES_VALIDOS
        or not auth.verificar_contrasena(contrasena, usuario.contrasena_hash)
    ):
        return jsonify({"error": "Credenciales inválidas."}), 401

    return jsonify({
        "token": auth.crear_token(usuario.id, usuario.rol),
        "usuario": {"id": usuario.id, "nombre": usuario.nombre, "rol": usuario.rol},
    })


@app.route("/usuarios", methods=["POST"])
def registrar_usuario():
    datos = request.get_json(silent=True)
    limpios, error = _datos_cuenta(datos)
    if error:
        return jsonify({"error": error}), 400
    if datos.get("rol") not in Usuario.ROLES_VALIDOS:
        return jsonify({"error": "Selecciona el rol propietario o veterinario."}), 400
    if Usuario.query.filter(db.func.lower(Usuario.correo) == limpios["correo"]).first():
        return jsonify({"error": "Ya existe un usuario registrado con este correo."}), 400

    usuario = Usuario(**limpios, rol=datos["rol"])
    db.session.add(usuario)
    error_guardado = _guardar_usuario()
    if error_guardado:
        return error_guardado
    return jsonify({
        "id": usuario.id, "nombre": usuario.nombre, "correo": usuario.correo, "rol": usuario.rol,
    }), 201


@app.route("/usuarios/<int:usuario_id>", methods=["PUT"])
@requiere_rol(*Usuario.ROLES_VALIDOS)
def editar_usuario(usuario_id, usuario_actual):
    if usuario_actual.id != usuario_id:
        return jsonify({"detalle": "No tienes permiso para editar otra cuenta."}), 403

    limpios, error = _datos_cuenta(request.get_json(silent=True), parcial=True)
    if error:
        return jsonify({"error": error}), 400

    if "correo" in limpios and Usuario.query.filter(
        db.func.lower(Usuario.correo) == limpios["correo"],
        Usuario.id != usuario_actual.id,
    ).first():
        return jsonify({"error": "Ya existe un usuario registrado con ese correo."}), 400

    for campo, valor in limpios.items():
        setattr(usuario_actual, campo, valor)
    error_guardado = _guardar_usuario()
    if error_guardado:
        return error_guardado

    return jsonify({
        "id": usuario_actual.id, "nombre": usuario_actual.nombre,
        "correo": usuario_actual.correo, "rol": usuario_actual.rol,
    })


@app.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    db.session.add(TokenRevocado(jti=get_jwt()["jti"]))
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        if not TokenRevocado.query.filter_by(jti=get_jwt()["jti"]).first():
            raise
    return jsonify({"mensaje": "Sesión cerrada correctamente."})


if __name__ == "__main__":
    app.run()
