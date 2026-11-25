import { useState } from "react";
import Login from "./Login";
import { api } from "./api";

function leerUsuario() {
  try {
    return JSON.parse(localStorage.getItem("usuario"));
  } catch {
    return null;
  }
}

export default function App() {
  const [usuario, setUsuario] = useState(leerUsuario());

  async function cerrarSesion() {
    try {
      await api("/logout", { method: "POST" });
    } catch {
      // si falla, igual cerramos la sesión en el navegador
    }
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setUsuario(null);
  }

  if (!usuario) return <Login onLogin={setUsuario} />;

  return (
    <div className="tarjeta">
      <h1>Hola, {usuario.nombre}</h1>
      <p>Rol: {usuario.rol}</p>
      <button onClick={cerrarSesion}>Cerrar sesión</button>
    </div>
  );
}