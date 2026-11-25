import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.getenv("SECRET_KEY")
CORS(app)
db = SQLAlchemy(app)
jwt = JWTManager(app)


@jwt.token_in_blocklist_loader
def verificar_token_revocado(_jwt_header, jwt_payload):
    from .models import TokenRevocado

    return TokenRevocado.query.filter_by(jti=jwt_payload["jti"]).first() is not None


@jwt.revoked_token_loader
def respuesta_token_revocado(_jwt_header, _jwt_payload):
    return jsonify({"detalle": "La sesión fue cerrada. Inicia sesión de nuevo."}), 401


@jwt.expired_token_loader
def respuesta_token_expirado(_jwt_header, _jwt_payload):
    return jsonify({"detalle": "La sesión venció. Inicia sesión de nuevo."}), 401


@jwt.unauthorized_loader
def respuesta_sin_token(_motivo):
    return jsonify({"detalle": "Inicia sesión para continuar."}), 401


@jwt.invalid_token_loader
def respuesta_token_invalido(_motivo):
    return jsonify({"detalle": "La sesión no es válida. Inicia sesión de nuevo."}), 401
