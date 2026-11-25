import { useState } from "react";
import { api } from "./api";

export default function Login({ onLogin }) {
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
    <form className="tarjeta" onSubmit={enviar}>
      <h1>Control de vacunación</h1>
      <label>Correo</label>
      <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required />
      <label>Contraseña</label>
      <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required />
      <button type="submit">Iniciar sesión</button>
      {error && <p className="error">{error}</p>}
    </form>
  );
}