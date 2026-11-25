import { useEffect, useState } from "react";
import Login from "./Login";
import Registro from "./Registro";
import Mascotas from "./Mascotas";
import Dosis from "./Dosis";
import RegistrarAplicacion from "./RegistrarAplicacion";
import EnviarRecordatorios from "./EnviarRecordatorios";
import Historial from "./Historial";
import { api, EVENTO_SESION_INVALIDA } from "./api";

const METRICAS = [
  ["mascotas", "Mascotas"],
  ["vacunas", "Vacunas aplicadas"],
  ["desparasitaciones", "Desparasitaciones"],
  ["vigentes", "Dosis vigentes"],
  ["proximas", "Dosis próximas", "proxima"],
  ["vencidas", "Dosis vencidas", "vencida"],
];

function leerUsuario() {
  try {
    return localStorage.getItem("token") && JSON.parse(localStorage.getItem("usuario"));
  } catch {
    return null;
  }
}

function Panel({ usuario, onCerrarSesion }) {
  const [version, setVersion] = useState(0);
  const [mascotas, setMascotas] = useState(null);
  const [mascotaId, setMascotaId] = useState("");
  const [estadisticas, setEstadisticas] = useState(null);
  const [errorMascotas, setErrorMascotas] = useState("");
  const [errorEstadisticas, setErrorEstadisticas] = useState("");

  useEffect(() => {
    let vigente = true;
    api("/mascotas")
      .then((datos) => {
        if (vigente) {
          setMascotas(datos);
          setErrorMascotas("");
        }
      })
      .catch((error) => {
        if (vigente) {
          setMascotas(null);
          setErrorMascotas(error.message);
        }
      });
    api("/estadisticas")
      .then((datos) => {
        if (vigente) {
          setEstadisticas(datos);
          setErrorEstadisticas("");
        }
      })
      .catch((error) => {
        if (vigente) {
          setEstadisticas(null);
          setErrorEstadisticas(error.message);
        }
      });
    return () => { vigente = false; };
  }, [version]);

  function actualizarPanel() {
    setVersion((actual) => actual + 1);
  }

  const seleccion = mascotas?.some((mascota) => String(mascota.id) === mascotaId)
    ? mascotaId
    : "";

  return (
    <div className="contenedor">
      <header className="barra">
        <h1 className="marca">Control de vacunación</h1>
        <div className="sesion">
          <span>{usuario.nombre}</span>
          <span className="rol">{usuario.rol}</span>
          <button className="fantasma" onClick={onCerrarSesion}>Cerrar sesión</button>
        </div>
      </header>

      {errorEstadisticas && <p className="error" role="alert">{errorEstadisticas}</p>}
      <div className="metricas" aria-label="Estadísticas de seguimiento">
        {METRICAS.map(([clave, etiqueta, clase = ""]) => (
          <div className={`metrica-card ${clase}`} key={clave}>
            <span className="metrica-valor">{estadisticas?.[clave] ?? "—"}</span>
            <span className="metrica-etiqueta">{etiqueta}</span>
          </div>
        ))}
      </div>

      <EnviarRecordatorios usuario={usuario} />
      <RegistrarAplicacion usuario={usuario} mascotas={mascotas ?? []} onRegistrado={actualizarPanel} />
      <Dosis version={version} />
      <Historial
        mascotas={mascotas ?? []}
        mascotaId={seleccion}
        onSeleccionar={setMascotaId}
        version={version}
        onCambio={actualizarPanel}
      />
      <Mascotas
        usuario={usuario}
        mascotas={mascotas}
        errorCarga={errorMascotas}
        version={version}
        onCambio={actualizarPanel}
        onHistorial={(id) => setMascotaId(String(id))}
      />
    </div>
  );
}

export default function App() {
  const [usuario, setUsuario] = useState(leerUsuario);
  const [pantalla, setPantalla] = useState("login");
  const [aviso, setAviso] = useState("");

  useEffect(() => {
    function sesionInvalida(evento) {
      setUsuario(null);
      setPantalla("login");
      setAviso(evento.detail);
    }
    window.addEventListener(EVENTO_SESION_INVALIDA, sesionInvalida);
    return () => window.removeEventListener(EVENTO_SESION_INVALIDA, sesionInvalida);
  }, []);

  function iniciarSesion(cuenta) {
    setAviso("");
    setUsuario(cuenta);
  }

  async function cerrarSesion() {
    try {
      await api("/logout", { method: "POST" });
    } catch {
      // Se retiran también las credenciales locales cuando el servidor no responde.
    }
    localStorage.removeItem("token");
    localStorage.removeItem("usuario");
    setUsuario(null);
    setPantalla("login");
    setAviso("");
  }

  if (!usuario) {
    return pantalla === "registro" ? (
      <Registro onLogin={iniciarSesion} onIrALogin={() => setPantalla("login")} />
    ) : (
      <Login aviso={aviso} onLogin={iniciarSesion} onIrARegistro={() => setPantalla("registro")} />
    );
  }

  return <Panel key={usuario.id} usuario={usuario} onCerrarSesion={cerrarSesion} />;
}
