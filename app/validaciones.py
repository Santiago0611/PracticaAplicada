import re
import string

PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_correo(correo):
    if not isinstance(correo, str) or not PATRON_CORREO.match(correo.strip()):
        return 'El correo no tiene un formato válido (debe contener "@" y un dominio válido).'
    return None


def validar_contrasena(contrasena):
    if not isinstance(contrasena, str) or not contrasena:
        return "La contraseña es obligatoria."

    faltan = []
    if len(contrasena) < 8:
        faltan.append("mínimo 8 caracteres")
    if not re.search(r"[A-Z]", contrasena):
        faltan.append("al menos una letra mayúscula")
    if not re.search(r"\d", contrasena):
        faltan.append("al menos un número")
    if not any(c in string.punctuation for c in contrasena):
        faltan.append("al menos un carácter especial")

    if faltan:
        return "La contraseña no cumple los requisitos. Falta: " + ", ".join(faltan) + "."
    return None