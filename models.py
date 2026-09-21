from . import db

class Usuario(db.Model):
    __tablename__ = "usuario"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum("propietario", "veterinario", name="rol_usuario"), nullable=False)
    estado = db.Column(db.Enum("activo", "inactivo", name="estado_usuario"), default="activo")
    fecha_registro = db.Column(db.TIMESTAMP, server_default=db.func.now())


class Mascota(db.Model):
    __tablename__ = "mascota"

    id = db.Column(db.Integer, primary_key=True)
    propietario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(100), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    peso = db.Column(db.Numeric(5, 2), nullable=True)
    foto = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, default=True)


class CatalogoProducto(db.Model):
    __tablename__ = "catalogo_producto"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Enum(
        "vacuna", "desparasitante_interno", "desparasitante_externo", "desparasitante_ambos",
        name="tipo_producto"
    ), nullable=False)
    intervalo_dias = db.Column(db.Integer, nullable=True)


class RegistroAplicacion(db.Model):
    __tablename__ = "registro_aplicacion"

    id = db.Column(db.Integer, primary_key=True)
    mascota_id = db.Column(db.Integer, db.ForeignKey("mascota.id"), nullable=False)
    catalogo_id = db.Column(db.Integer, db.ForeignKey("catalogo_producto.id"), nullable=False)
    veterinario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    fecha_aplicacion = db.Column(db.Date, nullable=False)
    fecha_proxima = db.Column(db.Date, nullable=True)
    dosis = db.Column(db.String(50), nullable=True)
    observaciones = db.Column(db.String(255), nullable=True)
    fecha_creacion = db.Column(db.TIMESTAMP, server_default=db.func.now())