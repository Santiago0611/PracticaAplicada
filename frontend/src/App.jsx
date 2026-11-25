import { useEffect, useState } from "react";
import Login from "./Login";
import Registro from "./Registro";
import Mascotas from "./Mascotas";
import Dosis from "./Dosis";
import RegistrarAplicacion from "./RegistrarAplicacion";
import EnviarRecordatorios from "./EnviarRecordatorios";
import Historial from "./Historial";
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
  const [pantalla, setPantalla] = useState("login");
  const [version, setVersion] = useState(0);
  const [resumen, setResumen] = useState({
    mascotas: 0,
    proximas: 0,
    vencidas: 0,
  });

  useEffect(() => {
    if (!usuario) return;
    Promise.all([api("/mascotas").catch(() => []), api("/dosis").catch(() => [])])
      .then(([listaMascotas, listaDosis]) => {
        const mascotasArr = Array.isArray(listaMascotas) ? listaMascotas : [];
        const dosisArr = Array.isArray(listaDosis) ? listaDosis : [];
        setResumen({
          mascotas: mascotasArr.length,
          proximas: dosisArr.filter((d) => d.estado === "proxima").length,
          vencidas: dosisArr.filter((d) => d.estado === "vencida").length,
        });
      });
  }, [usuario, version]);

  async function cerrarSesion() {
    try {
      await api("/logout", { method: "POST" });
    } catch {
      // si falla, igual cerramos la sesión en el navegador
    }
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setUsuario(null);
    setPantalla("login");
  }

  if (!usuario) {
    return pantalla === "registro" ? (
      <Registro onLogin={setUsuario} onIrALogin={() => setPantalla("login")} />
    ) : (
      <Login onLogin={setUsuario} onIrARegistro={() => setPantalla("registro")} />
    );
  }

  return (
    <div className="contenedor">
      <header className="barra">
        <h1 className="marca">Control de vacunación</h1>
        <div className="sesion">
          <span>{usuario.nombre}</span>
          <span className="rol">{usuario.rol}</span>
          <button className="fantasma" onClick={cerrarSesion}>
            Cerrar sesión
          </button>
        </div>
      </header>

      <div className="metricas">
        <div className="metrica-card">
          <span className="metrica-valor">{resumen.mascotas}</span>
          <span className="metrica-etiqueta">Mascotas</span>
        </div>
        <div className="metrica-card proxima">
          <span className="metrica-valor">{resumen.proximas}</span>
          <span className="metrica-etiqueta">Dosis próximas</span>
        </div>
        <div className="metrica-card vencida">
          <span className="metrica-valor">{resumen.vencidas}</span>
          <span className="metrica-etiqueta">Dosis vencidas</span>
        </div>
      </div>

      <EnviarRecordatorios usuario={usuario} />
      <RegistrarAplicacion
        usuario={usuario}
        onRegistrado={() => setVersion((v) => v + 1)}
      />
      <Dosis version={version} />
      <Historial version={version} />
      <Mascotas
        usuario={usuario}
        onCambio={() => setVersion((v) => v + 1)}
      />
    </div>
  );
}