from flask import abort, jsonify

from . import db
from .models import Mascota, PacienteVeterinario


def filtro_mascotas_visibles(usuario):
    if usuario.es_propietario():
        return Mascota.propietario_id == usuario.id
    if usuario.es_veterinario():
        return Mascota.id.in_(
            db.select(PacienteVeterinario.mascota_id).where(
                PacienteVeterinario.veterinario_id == usuario.id
            )
        )
    return db.false()


def mascotas_visibles(usuario):
    return Mascota.query.filter(Mascota.activo.is_(True), filtro_mascotas_visibles(usuario))


def obtener_mascota_autorizada(mascota_id, usuario, *, para_escritura=False):
    consulta = Mascota.query.filter_by(id=mascota_id, activo=True)
    if para_escritura:
        consulta = consulta.with_for_update()
    mascota = consulta.first()
    if mascota is None:
        abort(404, description="La mascota solicitada no existe o fue eliminada.")

    if usuario.es_propietario():
        autorizado = mascota.propietario_id == usuario.id
    else:
        autorizado = usuario.es_veterinario() and db.session.get(
            PacienteVeterinario,
            (mascota_id, usuario.id),
            with_for_update=para_escritura,
        ) is not None
    if not autorizado:
        abort(403, description="No tienes acceso a esta mascota.")
    return mascota


def respuesta_acceso(error):
    return jsonify({"detalle": error.description}), error.code
