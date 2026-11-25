from collections import Counter

from flask import Blueprint, jsonify

from . import db
from .acceso import mascotas_visibles
from .decorators import requiere_rol
from .dosis import obtener_dosis
from .models import CatalogoProducto, Mascota, RegistroAplicacion, Usuario
from .registros import TIPOS_DESPARASITANTE

estadisticas_bp = Blueprint("estadisticas", __name__)


@estadisticas_bp.route("/estadisticas", methods=["GET"])
@requiere_rol(*Usuario.ROLES_VALIDOS)
def estadisticas(usuario_actual):
    mascotas = mascotas_visibles(usuario_actual)
    aplicaciones = dict(
        db.session.query(CatalogoProducto.tipo, db.func.count(RegistroAplicacion.id))
        .join(RegistroAplicacion.producto)
        .filter(RegistroAplicacion.mascota_id.in_(mascotas.with_entities(Mascota.id).statement))
        .group_by(CatalogoProducto.tipo)
        .all()
    )
    dosis = Counter(d["estado"] for d in obtener_dosis(usuario_actual))

    return jsonify({
        "mascotas": mascotas.count(),
        "vacunas": aplicaciones.get("vacuna", 0),
        "desparasitaciones": sum(aplicaciones.get(tipo, 0) for tipo in TIPOS_DESPARASITANTE),
        "vigentes": dosis["vigente"],
        "proximas": dosis["proxima"],
        "vencidas": dosis["vencida"],
    })
