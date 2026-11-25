import { useState } from "react";
import { api } from "./api";

export default function Login({ onLogin, onIrARegistro }) {
  const [correo, setCorreo] = useState("");
  const [contrasena, setContrasena] = useState("");
  const [error, setError] = useState("");

  async function enviar(e) {
    e.preventDefault();
    setError("");
    try {
      const data = await api("/login", {
        method: "POST",
        body: { correo, contrasena },
      });
      localStorage.setItem("token", data.token);
      localStorage.setItem("usuario", JSON.stringify(data.usuario));
      onLogin(data.usuario);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="auth-fondo">
      <form className="tarjeta" onSubmit={enviar}>
        <div className="auth-cabecera">
          <div className="auth-icono">🐾</div>
          <h1>Control de vacunación</h1>
          <p className="auth-subtitulo">Cuida el calendario médico de tus mascotas</p>
        </div>

        <label>Correo</label>
        <input
          type="email"
          placeholder="tu@correo.com"
          value={correo}
          onChange={(e) => setCorreo(e.target.value)}
          required
        />

        <label>Contraseña</label>
        <input
          type="password"
          placeholder="••••••••"
          value={contrasena}
          onChange={(e) => setContrasena(e.target.value)}
          required
        />

        <button type="submit">Iniciar sesión</button>

        <p className="cambio">
          ¿No tienes cuenta?{" "}
          <button type="button" className="enlace" onClick={onIrARegistro}>
            Crear cuenta
          </button>
        </p>

        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}