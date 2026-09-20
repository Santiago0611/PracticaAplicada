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