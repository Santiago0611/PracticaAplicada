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