import { useState } from "react";
import { api } from "./api";

export default function Registro({ onLogin, onIrALogin }) {
  const [form, setForm] = useState({
    nombre: "",
    correo: "",
    contrasena: "",
    rol: "propietario",
  });
  const [error, setError] = useState("");

  function cambiar(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function enviar(e) {
    e.preventDefault();
    setError("");
    try {
      await api("/usuarios", { method: "POST", body: form });
      const data = await api("/login", {
        method: "POST",
        body: { correo: form.correo, contrasena: form.contrasena },
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
          <div className="auth-icono">🐶</div>
          <h1>Crear cuenta</h1>
          <p className="auth-subtitulo">Regístrate como propietario o veterinario</p>
        </div>

        <label>Nombre</label>
        <input
          name="nombre"
          placeholder="Ej: Nicol Herrera"
          value={form.nombre}
          onChange={cambiar}
          required
        />

        <label>Correo</label>
        <input
          name="correo"
          type="email"
          placeholder="tu@correo.com"
          value={form.correo}
          onChange={cambiar}
          required
        />

        <label>Contraseña</label>
        <input
          name="contrasena"
          type="password"
          placeholder="Mínimo 8 caracteres"
          minLength={8}
          value={form.contrasena}
          onChange={cambiar}
          required
        />

        <label>Rol</label>
        <select name="rol" value={form.rol} onChange={cambiar}>
          <option value="propietario">Propietario</option>
          <option value="veterinario">Veterinario</option>
        </select>

        <button type="submit">Crear cuenta</button>

        {error && <p className="error">{error}</p>}

        <p className="cambio">
          ¿Ya tienes cuenta?{" "}
          <button type="button" className="enlace" onClick={onIrALogin}>
            Inicia sesión
          </button>
        </p>
      </form>
    </div>
  );
}