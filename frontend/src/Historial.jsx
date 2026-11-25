import { useEffect, useState } from "react";
import { api } from "./api";
import EditarAplicacion from "./EditarAplicacion";

const SIN_FILTROS = { q: "", tipo: "", desde: "", hasta: "" };
const TIPOS = {
  vacuna: "Vacuna",
  desparasitante_interno: "Desparasitación interna",
  desparasitante_externo: "Desparasitación externa",
  desparasitante_ambos: "Desparasitación interna y externa",
};

export default function Historial({ mascotas, mascotaId, onSeleccionar, version, onCambio }) {
  return (
    <section id="historial">
      <h2>📋 Historial de la mascota</h2>
      <label>
        <span id="etiqueta-mascota-historial">Mascota</span>
        <select aria-labelledby="etiqueta-mascota-historial" value={mascotaId} onChange={(e) => onSeleccionar(e.target.value)}>
          <option value="">Selecciona una mascota</option>
          {mascotas.map((mascota) => (
            <option key={mascota.id} value={mascota.id}>{mascota.nombre} ({mascota.especie})</option>
          ))}
        </select>
      </label>
      {mascotaId && (
        <HistorialMascota key={mascotaId} mascotaId={mascotaId} version={version} onCambio={onCambio} />
      )}
    </section>
  );
}

function HistorialMascota({ mascotaId, version, onCambio }) {
  const [form, setForm] = useState(SIN_FILTROS);
  const [filtros, setFiltros] = useState(SIN_FILTROS);
  const [resultado, setResultado] = useState(null);
  const [editando, setEditando] = useState(null);
  const [eliminando, setEliminando] = useState(false);
  const [errorAccion, setErrorAccion] = useState("");
  const [mensaje, setMensaje] = useState("");

  const params = new URLSearchParams(Object.entries(filtros).filter(([, valor]) => valor));
  const rutaMascota = `/mascotas/${mascotaId}`;
  const ruta = `${rutaMascota}/historial${params.size ? `?${params}` : ""}`;

  useEffect(() => {
    let vigente = true;
    api(ruta)
      .then((datos) => {
        if (vigente) setResultado({ ruta, version, datos });
      })
      .catch((err) => {
        if (vigente) setResultado({ ruta, version, error: err.message });
      });
    return () => { vigente = false; };
  }, [ruta, version]);

  const resultadoActual = resultado?.ruta === ruta && resultado.version === version ? resultado : null;
  const historial = resultadoActual?.datos?.historial;
  const hayAcciones = historial?.some((registro) => registro.puede_modificar);
  const registroActual = historial?.find((registro) => registro.id === editando);

  function cambiar(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function aplicarFiltros(nuevos) {
    setFiltros(nuevos);
    setEditando(null);
    setErrorAccion("");
    setMensaje("");
  }

  async function eliminar(registro) {
    if (!window.confirm(`¿Eliminar la aplicación de ${registro.producto} del ${registro.fecha_aplicacion}?`)) return;
    setErrorAccion("");
    setMensaje("");
    setEliminando(true);
    try {
      await api(`${rutaMascota}/registros/${registro.id}`, { method: "DELETE" });
      setEditando(null);
      setMensaje("Aplicación eliminada.");
      onCambio();
    } catch (err) {
      setErrorAccion(err.message);
    } finally {
      setEliminando(false);
    }
  }

  return (
    <>
      <form className="filtros filtros-historial" onSubmit={(e) => {
        e.preventDefault();
        aplicarFiltros({ ...form, q: form.q.trim() });
      }}>
        <label>
          Buscar en el historial
          <input type="search" name="q" value={form.q} onChange={cambiar} placeholder="Producto, veterinario, dosis o notas" />
        </label>
        <label>
          <span id="etiqueta-tipo-historial">Tipo de aplicación</span>
          <select name="tipo" aria-labelledby="etiqueta-tipo-historial" value={form.tipo} onChange={cambiar}>
            <option value="">Todos los tipos</option>
            <option value="vacuna">Vacunas</option>
            <option value="desparasitante">Todas las desparasitaciones</option>
            {Object.entries(TIPOS).filter(([tipo]) => tipo !== "vacuna").map(([tipo, etiqueta]) => (
              <option value={tipo} key={tipo}>{etiqueta}</option>
            ))}
          </select>
        </label>
        <label>
          Desde
          <input type="date" name="desde" value={form.desde} max={form.hasta || undefined} onChange={cambiar} />
        </label>
        <label>
          Hasta
          <input type="date" name="hasta" value={form.hasta} min={form.desde || undefined} onChange={cambiar} />
        </label>
        <button type="submit">Aplicar filtros</button>
        <button type="button" className="fantasma" onClick={() => {
          setForm(SIN_FILTROS);
          aplicarFiltros(SIN_FILTROS);
        }}>Limpiar</button>
      </form>

      {(resultadoActual?.error || errorAccion) && (
        <p className="error" role="alert">{resultadoActual?.error || errorAccion}</p>
      )}
      {mensaje && <p className="exito" role="status">{mensaje}</p>}
      {!resultadoActual && <p className="vacio">Cargando historial…</p>}
      {historial?.length === 0 && (
        <p className="vacio">
          {params.size ? "No hay registros que coincidan con los filtros." : "Esta mascota aún no tiene registros."}
        </p>
      )}

      {historial?.length > 0 && (
        <div className="tabla-contenedor" tabIndex={0} role="region" aria-label="Aplicaciones del historial">
          <table className="tabla">
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Producto</th>
                <th>Dosis</th>
                <th>Próxima dosis</th>
                <th>Veterinario</th>
                <th>Notas</th>
                {hayAcciones && <th>Acciones</th>}
              </tr>
            </thead>
            <tbody>
              {historial.map((registro) => (
                <tr key={registro.id}>
                  <td>{registro.fecha_aplicacion}</td>
                  <td>
                    <strong>{registro.producto}</strong>
                    <div className="detalle">{TIPOS[registro.tipo]}</div>
                  </td>
                  <td>{registro.dosis || "—"}</td>
                  <td>{registro.fecha_proxima || "—"}</td>
                  <td>{registro.veterinario || "—"}</td>
                  <td>{registro.observaciones || "—"}</td>
                  {hayAcciones && (
                    <td>
                      {registro.puede_modificar && (
                        <div className="acciones">
                          <button type="button" className="fantasma" disabled={eliminando} onClick={() => {
                            setEditando(registro.id);
                            setMensaje("");
                            setErrorAccion("");
                          }}>Editar</button>
                          <button type="button" className="peligro" disabled={eliminando} onClick={() => eliminar(registro)}>
                            Eliminar
                          </button>
                        </div>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {registroActual && (
        <EditarAplicacion
          key={registroActual.id}
          registro={registroActual}
          ruta={`${rutaMascota}/registros/${registroActual.id}`}
          onCancelar={() => setEditando(null)}
          onGuardado={() => {
            setEditando(null);
            setMensaje("Aplicación actualizada.");
            onCambio();
          }}
        />
      )}
    </>
  );
}
