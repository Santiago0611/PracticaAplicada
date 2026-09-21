from datetime import datetime

from . import db

class Usuario(db.Model):
    __tablename__ = "usuario"

    ROL_PROPIETARIO = "propietario"
    ROL_VETERINARIO = "veterinario"
    ROLES_VALIDOS = (ROL_PROPIETARIO, ROL_VETERINARIO)

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.Enum(ROL_PROPIETARIO, ROL_VETERINARIO, name="rol_usuario"), nullable=False)
    estado = db.Column(db.Enum("activo", "inactivo", name="estado_usuario"), default="activo")
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=datetime.utcnow
    )

    mascotas = db.relationship(
        "Mascota", back_populates="propietario", cascade="all, delete-orphan"
    )

    def es_propietario(self) -> bool:
        return self.rol == self.ROL_PROPIETARIO

    def es_veterinario(self) -> bool:
        return self.rol == self.ROL_VETERINARIO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "rol": self.rol,
            "estado": self.estado,
            "actualizado_en": self.actualizado_en.isoformat() if self.actualizado_en else None,
        }


class Mascota(db.Model):
    __tablename__ = "mascota"

    id = db.Column(db.Integer, primary_key=True)
    propietario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(50), nullable=False)
    raza = db.Column(db.String(100), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    peso = db.Column(db.Numeric(5, 2), nullable=True)
    foto = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=datetime.utcnow
    )

    propietario = db.relationship("Usuario", back_populates="mascotas")
    registros = db.relationship(
        "RegistroAplicacion", back_populates="mascota", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "propietario_id": self.propietario_id,
            "nombre": self.nombre,
            "especie": self.especie,
            "raza": self.raza,
            "fecha_nacimiento": (
                self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None
            ),
            "peso": float(self.peso) if self.peso is not None else None,
            "foto": self.foto,
            "activo": self.activo,
            "actualizado_en": self.actualizado_en.isoformat() if self.actualizado_en else None,
        }


class CatalogoProducto(db.Model):
    __tablename__ = "catalogo_producto"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.Enum(
        "vacuna", "desparasitante_interno", "desparasitante_externo", "desparasitante_ambos",
        name="tipo_producto"
    ), nullable=False)
    intervalo_dias = db.Column(db.Integer, nullable=True)

    registros = db.relationship("RegistroAplicacion", back_populates="producto")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "intervalo_dias": self.intervalo_dias,
        }


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

    mascota = db.relationship("Mascota", back_populates="registros")
    producto = db.relationship("CatalogoProducto", back_populates="registros")
    veterinario = db.relationship("Usuario")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "mascota_id": self.mascota_id,
            "catalogo_id": self.catalogo_id,
            "veterinario_id": self.veterinario_id,
            "fecha_aplicacion": (
                self.fecha_aplicacion.isoformat() if self.fecha_aplicacion else None
            ),
            "fecha_proxima": (
                self.fecha_proxima.isoformat() if self.fecha_proxima else None
            ),
            "dosis": self.dosis,
            "observaciones": self.observaciones,
        }
    
class Usuario(db.Model):
    __tablename__ = "usuarios"

    ROL_PROPIETARIO = "PROPIETARIO"
    ROL_VETERINARIO = "VETERINARIO"
    ROLES_VALIDOS = (ROL_PROPIETARIO, ROL_VETERINARIO)

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default=ROL_PROPIETARIO)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)

    mascotas = db.relationship(
        "Mascota", back_populates="propietario", cascade="all, delete-orphan"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def es_propietario(self) -> bool:
        return self.rol == self.ROL_PROPIETARIO

    def es_veterinario(self) -> bool:
        return self.rol == self.ROL_VETERINARIO

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "rol": self.rol,
        }


class Mascota(db.Model):
    __tablename__ = "mascotas"

    ESPECIES_VALIDAS = ("PERRO", "GATO", "OTRO")

    id = db.Column(db.Integer, primary_key=True)
    propietario_id = db.Column(
        db.Integer, db.ForeignKey("usuarios.id"), nullable=False, index=True
    )
    nombre = db.Column(db.String(100), nullable=False)
    especie = db.Column(db.String(10), nullable=False)
    raza = db.Column(db.String(100), nullable=True)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    peso_kg = db.Column(db.Numeric(5, 2), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    propietario = db.relationship("Usuario", back_populates="mascotas")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "propietario_id": self.propietario_id,
            "nombre": self.nombre,
            "especie": self.especie,
            "raza": self.raza,
            "fecha_nacimiento": (
                self.fecha_nacimiento.isoformat() if self.fecha_nacimiento else None
            ),
            "peso_kg": float(self.peso_kg) if self.peso_kg is not None else None,
            "activo": self.activo,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }