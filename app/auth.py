import bcrypt
import datetime

from flask_jwt_extended import create_access_token


def crear_token(usuario_id, rol):
    return create_access_token(
        identity=str(usuario_id),
        additional_claims={"rol": rol},
        expires_delta=datetime.timedelta(hours=2),
    )


def hashear_contrasena(contrasena):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(contrasena.encode("utf-8"), salt).decode("utf-8")


def verificar_contrasena(contrasena_plana, hash_guardado):
    return bcrypt.checkpw(contrasena_plana.encode("utf-8"), hash_guardado.encode("utf-8"))