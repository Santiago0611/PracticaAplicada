from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import Usuario


def usuario_actual() -> Usuario | None:
    identidad = get_jwt_identity()
    if identidad is None:
        return None
    return Usuario.query.get(int(identidad))


def requiere_rol(*roles_permitidos):
    def decorador(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            usuario = usuario_actual()

            if usuario is None:
                return jsonify({"detalle": "Usuario no encontrado o token inválido."}), 401

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