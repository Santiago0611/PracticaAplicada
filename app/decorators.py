from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from . import db
from .models import Usuario


def usuario_actual() -> Usuario | None:
    try:
        usuario_id = int(get_jwt_identity())
    except (TypeError, ValueError):
        return None
    return db.session.get(Usuario, usuario_id)


def requiere_rol(*roles_permitidos):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            usuario = usuario_actual()

            if usuario is None or usuario.estado == "inactivo":
                return jsonify({"detalle": "La cuenta no está disponible. Inicia sesión de nuevo."}), 401

            if usuario.rol not in roles_permitidos:
                return (
                    jsonify(
                        {
                            "detalle": (
                                f"No tienes permisos para esta acción. "
                                f"Rol requerido: {', '.join(roles_permitidos)}."
                            )
                        }
                    ),
                    403,
                )

            return func(*args, usuario_actual=usuario, **kwargs)

        return wrapper

    return decorador
