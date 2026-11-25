import os
import smtplib
from email.message import EmailMessage

from flask import Blueprint, jsonify, request

from .decorators import requiere_rol
from .dosis import obtener_dosis
from .models import Usuario

notificaciones_bp = Blueprint("notificaciones", __name__)


def _config_correo():
    servidor = os.getenv("MAIL_SERVER")
    puerto = os.getenv("MAIL_PORT")
    usuario = os.getenv("MAIL_USER")
    clave = os.getenv("MAIL_PASSWORD")
    if not (servidor and puerto and usuario and clave):
        return None
    return servidor, int(puerto), usuario, clave


def enviar_correo(smtp, remitente, destino, asunto, texto):
    msg = EmailMessage()
    msg["From"] = remitente
    msg["To"] = destino
    msg["Subject"] = asunto
    msg.set_content(texto)
    smtp.send_message(msg)


def _armar_mensaje(dosis):
    if dosis["estado"] == "vencida":
        situacion = f"venció el {dosis['fecha_vencimiento']}"
    elif dosis["dias_restantes"] == 0:
        situacion = "vence hoy"
    else:
        situacion = f"vence el {dosis['fecha_vencimiento']} (en {dosis['dias_restantes']} días)"
    return (
        f"Hola,\n\nLa dosis de {dosis['producto']} de {dosis['mascota']} {situacion}.\n"
        "Agenda una cita con tu veterinario.\n\nControl de vacunación de mascotas"
    )


@notificaciones_bp.route("/recordatorios/enviar", methods=["POST"])
@requiere_rol("veterinario")
def enviar_recordatorios(usuario_actual):
    datos = request.get_json(silent=True) or {}
    estados = ["proxima"]
    if datos.get("incluir_vencidas"):
        estados.append("vencida")

    config = _config_correo()
    if config is None:
        return jsonify({"error": "El servicio de correo no está configurado."}), 500
    servidor, puerto, remitente, clave = config

    pendientes = [d for d in obtener_dosis() if d["estado"] in estados]
    resumen = {"enviados": 0, "sin_correo": 0, "fallidos": 0, "detalle": []}

    try:
        with smtplib.SMTP_SSL(servidor, puerto, timeout=15) as smtp:
            smtp.login(remitente, clave)
            for dosis in pendientes:
                propietario = Usuario.query.get(dosis["propietario_id"])
                if not propietario or not propietario.correo:
                    resumen["sin_correo"] += 1
                    continue
                try:
                    enviar_correo(smtp, remitente, propietario.correo,
                                  f"Recordatorio de vacuna: {dosis['mascota']}",
                                  _armar_mensaje(dosis))
                    resumen["enviados"] += 1
                except smtplib.SMTPException:
                    resumen["fallidos"] += 1
                    resumen["detalle"].append(f"{dosis['mascota']}: no se pudo enviar.")

    except smtplib.SMTPAuthenticationError:
        return jsonify({"error": "Usuario o contraseña de aplicación incorrectos."}), 500
    
    except Exception:
        return jsonify({"error": "No se pudo conectar con el servidor de correo."}), 500
    
    return jsonify(resumen),200
    