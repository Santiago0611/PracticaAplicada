import { useState } from "react";
import Login from "./Login";
import { api } from "./api";
import Mascotas from "./Mascotas";
import Dosis from "./Dosis";
import RegistrarAplicacion from "./RegistrarAplicacion";

function leerUsuario() {
  try {
    return JSON.parse(localStorage.getItem("usuario"));
  } catch {
    return null;
  }
}

export default function App() {
  const [usuario, setUsuario] = useState(leerUsuario());
  const [version, setVersion] = useState(0);

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
    <div className="contenedor">
      <header className="barra">
        <span>Hola, {usuario.nombre} ({usuario.rol})</span>
        <button onClick={cerrarSesion}>Cerrar sesión</button>
      </header>
      <RegistrarAplicacion usuario={usuario} onRegistrado={() => setVersion((v) => v + 1)} />
      <Dosis version={version} />
      <Mascotas usuario={usuario} />
    </div>
  );
}