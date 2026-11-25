import { useEffect, useState } from "react";
import { api } from "./api";

function calcularEdad(fechaNacimiento) {
  const nacimiento = new Date(`${fechaNacimiento}T00:00:00`);
  const hoy = new Date();
  const meses = (hoy.getFullYear() - nacimiento.getFullYear()) * 12
    + hoy.getMonth() - nacimiento.getMonth() - Number(hoy.getDate() < nacimiento.getDate());
  if (!Number.isFinite(meses) || meses < 0) return "";
  const anios = Math.floor(meses / 12);
  const resto = meses % 12;
  const edadMeses = resto === 1 ? "1 mes" : `${resto} meses`;
  if (!anios) return edadMeses;
  const edadAnios = anios === 1 ? "1 año" : `${anios} años`;
  return resto ? `${edadAnios} y ${edadMeses}` : edadAnios;
}

export default function DetalleMascota({ id, esPropietario, version, onCambio, onHistorial }) {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState("");
  const [errorAccion, setErrorAccion] = useState("");
  const [correo, setCorreo] = useState("");
  const [ocupado, setOcupado] = useState(false);
  const ruta = `/mascotas/${id}`;

  useEffect(() => {
    let vigente = true;
    Promise.all([api(ruta), esPropietario ? api(`${ruta}/veterinarios`) : []])
      .then(([mascota, veterinarios]) => {
        if (vigente) {
          setError("");
          setDatos({ mascota, veterinarios });
        }
      })
      .catch((err) => {
        if (vigente) {
          setDatos(null);
          setError(err.message);
        }
      });
    return () => { vigente = false; };
  }, [ruta, esPropietario, version]);

  async function actualizarAcceso(rutaAccion, opciones) {
    setErrorAccion("");
    setOcupado(true);
    try {
      await api(rutaAccion, opciones);
      if (opciones.method === "POST") setCorreo("");
      onCambio();
    } catch (err) {
      setErrorAccion(err.message);
    } finally {
      setOcupado(false);
    }
  }

  if (!datos) {
    return <p id="detalle-mascota" className={error ? "error" : "vacio"}>{error || "Cargando ficha…"}</p>;
  }
  const { mascota, veterinarios } = datos;
  const edad = mascota.fecha_nacimiento && calcularEdad(mascota.fecha_nacimiento);

  return (
    <div className="ficha-mascota" id="detalle-mascota">
      <dl>
        <div><dt>Especie</dt><dd>{mascota.especie}</dd></div>
        <div><dt>Raza</dt><dd>{mascota.raza || "—"}</dd></div>
        <div><dt>Sexo</dt><dd>{mascota.sexo || "—"}</dd></div>
        <div><dt>Peso</dt><dd>{mascota.peso != null ? `${mascota.peso} kg` : "—"}</dd></div>
        <div><dt>Nacimiento</dt><dd>{mascota.fecha_nacimiento || "—"}{edad && ` (${edad})`}</dd></div>
      </dl>
      <a href="#historial" onClick={() => onHistorial(id)}>Ver historial</a>
      {esPropietario && (
        <div>
          <h3>Veterinarios autorizados</h3>
          {veterinarios.length === 0 && <p className="detalle">Aún no has autorizado a ningún veterinario.</p>}
          {veterinarios.length > 0 && (
            <ul className="lista-veterinarios">
              {veterinarios.map((vet) => (
                <li key={vet.id}>
                  <span>{vet.nombre} ({vet.correo})</span>
                  <button
                    type="button" className="peligro" disabled={ocupado}
                    onClick={() => actualizarAcceso(`${ruta}/veterinarios/${vet.id}`, { method: "DELETE" })}
                  >
                    Retirar acceso
                  </button>
                </li>
              ))}
            </ul>
          )}
          <form className="filtros" onSubmit={(e) => {
            e.preventDefault();
            actualizarAcceso(`${ruta}/veterinarios`, { method: "POST", body: { correo } });
          }}>
            <label>
              Correo registrado del veterinario
              <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} maxLength={150} required />
            </label>
            <button type="submit" disabled={ocupado}>Autorizar</button>
          </form>
          {errorAccion && <p className="error" role="alert">{errorAccion}</p>}
        </div>
      )}
    </div>
  );
}
