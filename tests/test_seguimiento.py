import os
import unittest
from datetime import date, timedelta
from unittest.mock import patch

with patch.dict(os.environ, {
    "DATABASE_URL": "sqlite://",
    "SECRET_KEY": "clave-de-prueba-para-seguimiento-mascotas",
    "DIAS_ALERTA_DOSIS": "30",
}):
    from app.main import app, db
    from app.models import CatalogoProducto, Usuario


class SeguimientoTest(unittest.TestCase):
    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.engine.dispose()

    def setUp(self):
        self.assertEqual(app.config["SQLALCHEMY_DATABASE_URI"], "sqlite://")
        app.config["TESTING"] = True
        self.contexto = app.app_context()
        self.contexto.push()
        self.addCleanup(self.contexto.pop)
        db.create_all()
        self.addCleanup(db.drop_all)
        self.addCleanup(db.session.remove)
        self.cliente = app.test_client()
        self.cuentas = {}

    def crear_cuenta(self, nombre, rol):
        correo = f"{nombre.lower()}@ejemplo.com"
        credenciales = {"correo": correo, "contrasena": "Mascota123!"}
        registro = self.cliente.post("/usuarios", json={**credenciales, "nombre": nombre, "rol": rol})
        self.assertEqual(registro.status_code, 201, registro.json)
        respuesta = self.cliente.post("/login", json=credenciales)
        self.assertEqual(respuesta.status_code, 200, respuesta.json)
        self.cuentas[nombre] = {"Authorization": f"Bearer {respuesta.json['token']}"}
        return registro.json["id"]

    def pedir(self, metodo, ruta, cuenta=None, datos=None):
        return self.cliente.open(
            ruta, method=metodo, headers=self.cuentas.get(cuenta, {}), json=datos
        )

    def mascota(self, cuenta, nombre="Luna"):
        respuesta = self.pedir("POST", "/mascotas", cuenta, {"nombre": nombre, "especie": "gato"})
        self.assertEqual(respuesta.status_code, 201, respuesta.json)
        return f"/mascotas/{respuesta.json['id']}"

    def autorizar(self, ruta, propietario, veterinario):
        respuesta = self.pedir(
            "POST", ruta + "/veterinarios", propietario, {"correo": f"{veterinario.lower()}@ejemplo.com"}
        )
        self.assertEqual(respuesta.status_code, 201, respuesta.json)

    def producto(self, nombre, tipo="vacuna", intervalo=30):
        producto = CatalogoProducto(nombre=nombre, tipo=tipo, intervalo_dias=intervalo)
        db.session.add(producto)
        db.session.commit()
        return producto.id

    def aplicacion(self, ruta, cuenta, producto, fecha, *, tipo="vacunas", **campos):
        respuesta = self.pedir("POST", f"{ruta}/{tipo}", cuenta, {
            "catalogo_id": producto, "fecha_aplicacion": fecha.isoformat(), **campos,
        })
        self.assertEqual(respuesta.status_code, 201, respuesta.json)
        return respuesta.json

    def test_acceso_por_mascota_y_revocacion(self):
        propietario = self.crear_cuenta("Ana", "propietario")
        otro = self.crear_cuenta("Beto", "propietario")
        vet = self.crear_cuenta("Carla", "veterinario")
        ruta = self.mascota("Ana")
        otra = self.mascota("Beto")
        self.assertEqual(self.pedir("GET", ruta).status_code, 401)
        self.assertEqual(self.pedir("GET", ruta, "Beto").status_code, 403)
        self.assertEqual(self.pedir("PUT", otra, "Ana", {"nombre": "Sol"}).status_code, 403)
        self.assertEqual(self.pedir("PUT", f"/usuarios/{otro}", "Ana", {"nombre": "Sol"}).status_code, 403)
        self.assertEqual(self.pedir("PUT", f"/usuarios/{propietario}", "Ana", {"rol": "veterinario"}).json["rol"], "propietario")
        self.assertEqual(self.pedir("GET", "/mascotas", "Carla").json, [])
        self.assertEqual(self.pedir("POST", "/mascotas", "Carla", {"nombre": "Sol", "especie": "GATO"}).status_code, 403)

        self.autorizar(ruta, "Ana", "Carla")
        self.assertEqual(self.pedir("GET", ruta, "Carla").json["nombre"], "Luna")
        self.assertEqual(len(self.pedir("GET", "/mascotas", "Carla").json), 1)
        self.assertEqual(self.pedir("GET", otra + "/historial", "Carla").status_code, 403)
        self.assertEqual(self.pedir("POST", otra + "/vacunas", "Carla", {}).status_code, 403)
        self.assertEqual(self.pedir("GET", ruta + "/veterinarios", "Ana").json[0]["id"], vet)

        retiro = self.pedir("DELETE", ruta + f"/veterinarios/{vet}", "Ana")
        self.assertEqual(retiro.status_code, 204)
        self.assertEqual(self.pedir("GET", ruta + "/historial", "Carla").status_code, 403)
        self.assertEqual(self.pedir("GET", "/estadisticas", "Carla").json["mascotas"], 0)
        self.assertEqual(self.pedir("POST", "/logout", "Ana").status_code, 200)
        self.assertEqual(self.pedir("GET", "/mascotas", "Ana").status_code, 401)
        self.assertEqual(self.pedir("GET", "/mascotas", "Beto").status_code, 200)

    def test_historial_y_edicion_recalculan_el_seguimiento(self):
        self.crear_cuenta("Ana", "propietario")
        self.crear_cuenta("Carla", "veterinario")
        self.crear_cuenta("Diego", "veterinario")
        ruta = self.mascota("Ana")
        self.autorizar(ruta, "Ana", "Carla")
        self.autorizar(ruta, "Ana", "Diego")
        vacuna = self.producto("Antirrábica")
        antiparasitario = self.producto("Desparasitación Oral", "desparasitante_interno", 90)
        hoy = date.today()

        anterior = self.aplicacion(ruta, "Carla", vacuna, hoy - timedelta(days=60))
        registro = self.aplicacion(ruta, "Carla", vacuna, hoy, dosis="1 ml", observaciones="Control 100%")
        registro_desparasitacion = self.aplicacion(
            ruta, "Diego", antiparasitario, hoy, tipo="desparasitaciones"
        )
        historial = ruta + "/historial"
        edicion = ruta + f"/registros/{registro['id']}"
        self.assertEqual(
            [item["id"] for item in self.pedir("GET", historial, "Ana").json["historial"]],
            [registro_desparasitacion["id"], registro["id"], anterior["id"]],
        )
        filtros = f"?q=CONTROL&tipo=vacuna&desde={hoy}&hasta={hoy}"
        coincidencias = self.pedir("GET", historial + filtros, "Carla").json["historial"]
        self.assertEqual([item["id"] for item in coincidencias], [registro["id"]])
        self.assertTrue(coincidencias[0]["puede_modificar"])
        self.assertFalse(self.pedir("GET", historial + "?q=%25", "Ana").json["historial"][0]["puede_modificar"])
        self.assertEqual(self.pedir("GET", historial + "?q=%25", "Ana").json["historial"][0]["dosis"], "1 ml")
        self.assertEqual(self.pedir("GET", historial + "?tipo=desparasitante_interno", "Ana").json["historial"][0]["id"], registro_desparasitacion["id"])
        self.assertEqual(self.pedir("GET", historial + "?desde=sin-fecha", "Ana").status_code, 400)
        self.assertEqual(self.pedir("PUT", edicion, "Ana", {}).status_code, 403)
        self.assertEqual(self.pedir("DELETE", edicion, "Diego").status_code, 403)

        resumen = self.pedir("GET", "/estadisticas", "Ana").json
        self.assertEqual(resumen, {
            "mascotas": 1, "vacunas": 2, "desparasitaciones": 1,
            "vigentes": 1, "proximas": 1, "vencidas": 0,
        })
        self.assertEqual(self.pedir("PUT", edicion, "Carla", {
            "fecha_aplicacion": anterior["fecha_aplicacion"],
        }).status_code, 400)

        fecha = hoy - timedelta(days=40)
        editado = self.pedir("PUT", edicion, "Carla", {"fecha_aplicacion": fecha.isoformat()})
        self.assertEqual(editado.status_code, 200, editado.json)
        self.assertEqual(editado.json["fecha_proxima"], (fecha + timedelta(days=30)).isoformat())
        self.assertEqual(self.pedir("GET", "/estadisticas", "Carla").json["vencidas"], 1)

        fecha_manual = (hoy + timedelta(days=45)).isoformat()
        self.assertEqual(self.pedir("PUT", edicion, "Carla", {"fecha_proxima": fecha_manual}).status_code, 200)
        self.assertEqual(
            self.pedir("PUT", edicion, "Carla", {"observaciones": "Revisada"}).json["fecha_proxima"],
            fecha_manual,
        )
        self.assertEqual(self.pedir("DELETE", edicion, "Carla").status_code, 204)
        self.assertEqual(self.pedir("GET", "/estadisticas", "Ana").json["vacunas"], 1)
        self.assertEqual(
            self.pedir("GET", "/dosis?estado=vencida", "Diego").json[0]["fecha_aplicacion"],
            anterior["fecha_aplicacion"],
        )

        desparasitacion = ruta + f"/registros/{registro_desparasitacion['id']}"
        self.assertEqual(self.pedir("PUT", desparasitacion, "Diego", {"dosis": "2 ml"}).json["dosis"], "2 ml")
        self.assertEqual(self.pedir("DELETE", desparasitacion, "Diego").status_code, 204)
        self.assertEqual(self.pedir("GET", "/estadisticas", "Ana").json["desparasitaciones"], 0)

    def test_alertas_y_recordatorios_solo_de_pacientes_autorizados(self):
        self.crear_cuenta("Ana", "propietario")
        self.crear_cuenta("Beto", "propietario")
        self.crear_cuenta("Carla", "veterinario")
        self.crear_cuenta("Diego", "veterinario")
        luna = self.mascota("Ana")
        sol = self.mascota("Beto", "Sol")
        self.autorizar(luna, "Ana", "Carla")
        self.autorizar(sol, "Beto", "Diego")
        vacuna = self.producto("Antirrábica")
        fecha = date.today() - timedelta(days=2)
        self.aplicacion(luna, "Carla", vacuna, fecha)
        self.aplicacion(sol, "Diego", vacuna, fecha)

        dosis = self.pedir("GET", "/dosis", "Carla").json
        self.assertEqual([item["mascota"] for item in dosis], ["Luna"])
        self.assertEqual(self.pedir("GET", "/estadisticas", "Carla").json["vacunas"], 1)
        with (
            patch("app.notificaciones._config_correo", return_value=("smtp", 465, "remitente", "clave")),
            patch("app.notificaciones.smtplib.SMTP_SSL"),
            patch("app.notificaciones.enviar_correo") as enviar,
        ):
            respuesta = self.pedir("POST", "/recordatorios/enviar", "Carla", {})
            self.assertEqual(respuesta.json["enviados"], 1)
            self.assertEqual(enviar.call_args.args[2], "ana@ejemplo.com")

    def test_mascota_sin_opcionales_y_borrado_logico(self):
        self.crear_cuenta("Ana", "propietario")
        self.crear_cuenta("Carla", "veterinario")
        ruta = self.mascota("Ana")
        self.autorizar(ruta, "Ana", "Carla")
        datos = self.pedir("GET", ruta, "Ana").json
        self.assertIsNone(datos["peso"])
        self.assertIsNone(datos["sexo"])
        self.assertEqual(self.pedir("GET", ruta, "Carla").status_code, 200)
        self.assertEqual(self.pedir("DELETE", ruta, "Ana").status_code, 200)
        self.assertEqual(self.pedir("GET", ruta, "Carla").status_code, 404)
        self.assertEqual(self.pedir("GET", "/mascotas", "Carla").json, [])

    def test_migracion_conserva_mascotas_existentes(self):
        self.crear_cuenta("Ana", "propietario")
        self.crear_cuenta("Carla", "veterinario")
        ruta = self.mascota("Ana")
        self.autorizar(ruta, "Ana", "Carla")
        registro = self.aplicacion(ruta, "Carla", self.producto("Antirrábica"), date.today())
        db.session.remove()
        with db.engine.begin() as conexion:
            for instruccion in (
                "DROP TABLE paciente_veterinario",
                "DROP TABLE token_revocado",
                "ALTER TABLE usuario DROP COLUMN actualizado_en",
                "ALTER TABLE mascota DROP COLUMN actualizado_en",
                "ALTER TABLE mascota DROP COLUMN sexo",
            ):
                conexion.exec_driver_sql(instruccion)

        for _ in range(2):
            resultado = app.test_cli_runner().invoke(args=["actualizar-esquema"])
            self.assertEqual(resultado.exit_code, 0, resultado.output)

        self.assertEqual(self.pedir("GET", ruta, "Ana").json["nombre"], "Luna")
        self.assertEqual(self.pedir("GET", ruta + "/veterinarios", "Ana").json, [])
        historial = self.pedir("GET", ruta + "/historial", "Ana").json["historial"]
        self.assertEqual([aplicacion["id"] for aplicacion in historial], [registro["id"]])
        self.assertEqual(self.pedir("GET", "/mascotas", "Carla").json, [])

    def test_cuenta_inactiva_no_puede_usar_token(self):
        usuario_id = self.crear_cuenta("Ana", "propietario")
        usuario = db.session.get(Usuario, usuario_id)
        usuario.estado = "inactivo"
        db.session.commit()
        self.assertEqual(self.pedir("GET", "/mascotas", "Ana").status_code, 401)
        self.assertEqual(self.cliente.post("/login", json={
            "correo": "ana@ejemplo.com", "contrasena": "Mascota123!",
        }).status_code, 401)
