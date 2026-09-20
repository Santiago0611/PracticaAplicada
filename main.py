from flask import request, jsonify
from . import app, db, models, auth
@app.route("/login", methods=["POST"])
def login():
    datos = request.get_json()

    usuario = models.Usuario.query.filter(
        models.Usuario.correo == datos["correo"]
    ).first()

    if not usuario or not auth.verificar_contrasena(datos["contrasena"], usuario.contrasena_hash):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = auth.crear_token(usuario.id, usuario.rol)

    return jsonify({
        "token": token,
        "usuario": {
            "id": usuario.id,
            "nombre": usuario.nombre,
            "rol": usuario.rol
        }
    }), 200

@app.route("/usuarios", methods=["POST"])
def registrar_usuario():
    datos = request.get_json()

    usuario_existente = models.Usuario.query.filter(
        models.Usuario.correo == datos["correo"]
    ).first()

    if usuario_existente:
        return jsonify({"error": "Ya existe un usuario registrado con este correo"}), 400

    hash_generado = auth.hashear_contrasena(datos["contrasena"])

    nuevo_usuario = models.Usuario(
        nombre=datos["nombre"],
        correo=datos["correo"],
        contrasena_hash=hash_generado,
        rol=datos["rol"]
    )

    db.session.add(nuevo_usuario)
    db.session.commit()

    return jsonify({
        "id": nuevo_usuario.id,
        "nombre": nuevo_usuario.nombre,
        "correo": nuevo_usuario.correo,
        "rol": nuevo_usuario.rol
    }), 201


if __name__ == "__main__":
    app.run(debug=True)