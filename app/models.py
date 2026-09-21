from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


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