from flask import Blueprint, jsonify, request

from . import db
from .decorators import requiere_rol
from .models import CatalogoProducto

catalogo_bp = Blueprint("catalogo", __name__)

TIPOS_VALIDOS = (
    "vacuna",
    "desparasitante_interno",
    "desparasitante_externo",
    "desparasitante_ambos",
)


def _validar(datos, parcial=False):
    """Devuelve (valores_limpios, mensaje_de_error)."""
    limpios = {}

    if "nombre" in datos or not parcial:
        nombre = datos.get("nombre")
        if not isinstance(nombre, str) or not nombre.strip():
            return None, "El nombre del producto es obligatorio."
        limpios["nombre"] = nombre.strip()

    if "tipo" in datos or not parcial:
        if datos.get("tipo") not in TIPOS_VALIDOS:
            return None, "El tipo debe ser uno de: " + ", ".join(TIPOS_VALIDOS) + "."
        limpios["tipo"] = datos["tipo"]

    if "intervalo_dias" in datos:
        intervalo = datos["intervalo_dias"]
        if intervalo is not None:
            if isinstance(intervalo, bool) or not isinstance(intervalo, int) or intervalo <= 0:
                return None, "El intervalo debe ser un número entero de días mayor que cero."
        limpios["intervalo_dias"] = intervalo

    return limpios, None


def _existe_duplicado(nombre, tipo, excluir_id=None):
    consulta = CatalogoProducto.query.filter(
        db.func.lower(CatalogoProducto.nombre) == nombre.lower(),
        CatalogoProducto.tipo == tipo,
    )
    if excluir_id is not None:
        consulta = consulta.filter(CatalogoProducto.id != excluir_id)
    return consulta.first() is not None


@catalogo_bp.route("/catalogo", methods=["GET"])
@requiere_rol("propietario", "veterinario")
def listar_catalogo(usuario_actual):
    tipo = request.args.get("tipo")
    consulta = CatalogoProducto.query

    if tipo:
        if tipo not in TIPOS_VALIDOS:
            return jsonify({"error": "El tipo debe ser uno de: " + ", ".join(TIPOS_VALIDOS) + "."}), 400
        consulta = consulta.filter_by(tipo=tipo)

    productos = consulta.order_by(CatalogoProducto.nombre.asc()).all()
    return jsonify([p.to_dict() for p in productos]), 200


@catalogo_bp.route("/catalogo", methods=["POST"])
@requiere_rol("veterinario")
def crear_producto(usuario_actual):
    datos = request.get_json(silent=True) or {}

    limpios, error = _validar(datos)
    if error:
        return jsonify({"error": error}), 400

    if _existe_duplicado(limpios["nombre"], limpios["tipo"]):
        return jsonify({"error": "Ya existe un producto con ese nombre y tipo."}), 400

    producto = CatalogoProducto(**limpios)
    db.session.add(producto)
    db.session.commit()

    return jsonify(producto.to_dict()), 201


@catalogo_bp.route("/catalogo/<int:producto_id>", methods=["PUT"])
@requiere_rol("veterinario")
def editar_producto(producto_id, usuario_actual):
    producto = CatalogoProducto.query.get(producto_id)
    if not producto:
        return jsonify({"error": "Producto no encontrado"}), 404

    datos = request.get_json(silent=True) or {}

    limpios, error = _validar(datos, parcial=True)
    if error:
        return jsonify({"error": error}), 400

    nombre = limpios.get("nombre", producto.nombre)
    tipo = limpios.get("tipo", producto.tipo)

    if tipo != producto.tipo and producto.registros:
        return jsonify({"error": "No se puede cambiar el tipo de un producto que ya tiene aplicaciones registradas."}), 400

    if _existe_duplicado(nombre, tipo, excluir_id=producto.id):
        return jsonify({"error": "Ya existe un producto con ese nombre y tipo."}), 400

    for campo, valor in limpios.items():
        setattr(producto, campo, valor)
    db.session.commit()

    return jsonify(producto.to_dict()), 200