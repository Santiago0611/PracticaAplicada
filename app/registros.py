from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy.orm import contains_eager

from . import db
from .acceso import obtener_mascota_autorizada
from .calculos import calcular_proxima_dosis
from .decorators import requiere_rol
from .models import CatalogoProducto, RegistroAplicacion, Usuario

registros_bp = Blueprint("registros", __name__)

TIPOS_VACUNA = ("vacuna",)
TIPOS_DESPARASITANTE = (
    "desparasitante_interno",
    "desparasitante_externo",
    "desparasitante_ambos",
)
FILTROS_TIPO = {
    "vacuna": TIPOS_VACUNA,
    "desparasitante": TIPOS_DESPARASITANTE,
    **{tipo: (tipo,) for tipo in TIPOS_DESPARASITANTE},
}


def _parsear_fecha(valor):
    try:
        fecha = date.fromisoformat(valor)
        return fecha if fecha.isoformat() == valor else None
    except (TypeError, ValueError):
        return None


def _datos_aplicacion(datos, mascota_id, tipos, registro=None):
    if not isinstance(datos, dict):
        return None, "Envía los datos de la aplicación en formato JSON."

    producto_id = datos.get("catalogo_id", registro.catalogo_id if registro else None)
    if isinstance(producto_id, str) and producto_id.isascii() and producto_id.isdecimal():
        producto_id = int(producto_id) if len(producto_id) <= 10 else None
    if type(producto_id) is not int or not 1 <= producto_id <= 2147483647:
        return None, "Selecciona un producto del catálogo."
    producto = db.session.get(CatalogoProducto, producto_id)
    if producto is None or producto.tipo not in tipos:
        return None, "El producto seleccionado no pertenece a esta categoría."

    fecha_aplicacion = registro.fecha_aplicacion if registro else None
    if "fecha_aplicacion" in datos or registro is None:
        fecha_aplicacion = _parsear_fecha(datos.get("fecha_aplicacion"))
    if fecha_aplicacion is None:
        return None, "Ingresa la fecha de aplicación en formato AAAA-MM-DD."
    if fecha_aplicacion > date.today():
        return None, "La fecha de aplicación no puede ser posterior a hoy."

    cambio_aplicacion = (
        registro is None
        or producto.id != registro.catalogo_id
        or fecha_aplicacion != registro.fecha_aplicacion
    )
    if "fecha_proxima" in datos and datos["fecha_proxima"] not in (None, ""):
        fecha_proxima = _parsear_fecha(datos["fecha_proxima"])
        if fecha_proxima is None or fecha_proxima <= fecha_aplicacion:
            return None, "La próxima dosis debe ser una fecha posterior a la aplicación."
    elif "fecha_proxima" in datos or cambio_aplicacion:
        try:
            fecha_proxima = calcular_proxima_dosis(fecha_aplicacion, producto)
        except OverflowError:
            return None, "La próxima dosis calculada supera el rango de fechas permitido."
    else:
        fecha_proxima = registro.fecha_proxima

    limpios = {
        "catalogo_id": producto.id,
        "fecha_aplicacion": fecha_aplicacion,
        "fecha_proxima": fecha_proxima,
    }
    for campo, limite, etiqueta in (("dosis", 50, "dosis"), ("observaciones", 255, "observaciones")):
        if campo not in datos:
            continue
        valor = datos[campo]
        if valor is not None and (not isinstance(valor, str) or len(valor.strip()) > limite):
            return None, f"Ingresa un texto de hasta {limite} caracteres para {etiqueta}."
        limpios[campo] = (valor or "").strip() or None

    if cambio_aplicacion and RegistroAplicacion.query.filter_by(
        mascota_id=mascota_id, catalogo_id=producto.id, fecha_aplicacion=fecha_aplicacion
    ).with_for_update().first():
        return None, "Ya existe una aplicación del mismo producto en esa fecha."

    return limpios, None


def _registrar_aplicacion(mascota_id, usuario, tipos):
    mascota = obtener_mascota_autorizada(mascota_id, usuario, para_escritura=True)
    limpios, error = _datos_aplicacion(request.get_json(silent=True), mascota.id, tipos)
    if error:
        return jsonify({"error": error}), 400

    registro = RegistroAplicacion(mascota_id=mascota.id, veterinario_id=usuario.id, **limpios)
    db.session.add(registro)
    db.session.commit()
    return jsonify(registro.to_dict()), 201


@registros_bp.route("/mascotas/<int:mascota_id>/vacunas", methods=["POST"])
@requiere_rol(Usuario.ROL_VETERINARIO)
def registrar_vacuna(mascota_id, usuario_actual):
    return _registrar_aplicacion(mascota_id, usuario_actual, TIPOS_VACUNA)


@registros_bp.route("/mascotas/<int:mascota_id>/desparasitaciones", methods=["POST"])
@requiere_rol(Usuario.ROL_VETERINARIO)
def registrar_desparasitacion(mascota_id, usuario_actual):
    return _registrar_aplicacion(mascota_id, usuario_actual, TIPOS_DESPARASITANTE)


@registros_bp.route("/mascotas/<int:mascota_id>/historial", methods=["GET"])
@requiere_rol(*Usuario.ROLES_VALIDOS)
def historial_mascota(mascota_id, usuario_actual):
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual)
    consulta = (
        RegistroAplicacion.query.join(RegistroAplicacion.producto)
        .outerjoin(RegistroAplicacion.veterinario)
        .options(contains_eager(RegistroAplicacion.producto), contains_eager(RegistroAplicacion.veterinario))
        .filter(RegistroAplicacion.mascota_id == mascota.id)
    )

    tipo = request.args.get("tipo")
    if tipo:
        if tipo not in FILTROS_TIPO:
            return jsonify({"error": "Selecciona un tipo de aplicación válido."}), 400
        consulta = consulta.filter(CatalogoProducto.tipo.in_(FILTROS_TIPO[tipo]))

    desde_raw = request.args.get("desde")
    hasta_raw = request.args.get("hasta")
    desde, hasta = _parsear_fecha(desde_raw), _parsear_fecha(hasta_raw)
    if (desde_raw and desde is None) or (hasta_raw and hasta is None):
        return jsonify({"error": "Usa el formato AAAA-MM-DD para filtrar por fecha."}), 400
    if desde and hasta and desde > hasta:
        return jsonify({"error": "La fecha inicial debe ser anterior o igual a la final."}), 400
    if desde:
        consulta = consulta.filter(RegistroAplicacion.fecha_aplicacion >= desde)
    if hasta:
        consulta = consulta.filter(RegistroAplicacion.fecha_aplicacion <= hasta)

    busqueda = request.args.get("q", "").strip()
    if busqueda:
        consulta = consulta.filter(db.or_(
            CatalogoProducto.nombre.icontains(busqueda, autoescape=True),
            Usuario.nombre.icontains(busqueda, autoescape=True),
            RegistroAplicacion.observaciones.icontains(busqueda, autoescape=True),
            RegistroAplicacion.dosis.icontains(busqueda, autoescape=True),
        ))

    registros = consulta.order_by(
        RegistroAplicacion.fecha_aplicacion.desc(), RegistroAplicacion.id.desc()
    ).all()
    historial = [
        {
            **registro.to_dict(),
            "tipo": registro.producto.tipo,
            "producto": registro.producto.nombre,
            "veterinario": registro.veterinario.nombre if registro.veterinario else None,
            "puede_modificar": usuario_actual.es_veterinario()
            and registro.veterinario_id == usuario_actual.id,
        }
        for registro in registros
    ]
    return jsonify({
        "mascota": {"id": mascota.id, "nombre": mascota.nombre, "especie": mascota.especie},
        "historial": historial,
    })


@registros_bp.route("/mascotas/<int:mascota_id>/registros/<int:registro_id>", methods=["PUT", "DELETE"])
@requiere_rol(Usuario.ROL_VETERINARIO)
def modificar_registro(mascota_id, registro_id, usuario_actual):
    mascota = obtener_mascota_autorizada(mascota_id, usuario_actual, para_escritura=True)
    registro = RegistroAplicacion.query.filter_by(
        id=registro_id, mascota_id=mascota.id
    ).with_for_update().first()
    if registro is None:
        return jsonify({"error": "El registro de aplicación no existe."}), 404
    if registro.veterinario_id != usuario_actual.id:
        return jsonify({"error": "Solo el veterinario que registró la aplicación puede modificarla."}), 403

    if request.method == "DELETE":
        db.session.delete(registro)
        db.session.commit()
        return "", 204

    tipos = TIPOS_VACUNA if registro.producto.tipo == "vacuna" else TIPOS_DESPARASITANTE
    limpios, error = _datos_aplicacion(request.get_json(silent=True), mascota.id, tipos, registro)
    if error:
        return jsonify({"error": error}), 400

    for campo, valor in limpios.items():
        setattr(registro, campo, valor)
    db.session.commit()
    return jsonify(registro.to_dict())
