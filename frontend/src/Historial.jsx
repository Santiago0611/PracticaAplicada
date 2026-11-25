import { useEffect, useState } from "react";
import { api } from "./api";

export default function Historial({ version }) {
  const [mascotas, setMascotas] = useState([]);
  const [mascotaId, setMascotaId] = useState("");
  const [tipo, setTipo] = useState("");
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api("/mascotas").then(setMascotas).catch((e) => setError(e.message));
  }, [version]);

  useEffect(() => {
    if (!mascotaId) {
      setDatos(null);
      return;
    }
    const ruta = `/mascotas/${mascotaId}/historial${tipo ? `?tipo=${tipo}` : ""}`;
    api(ruta)
      .then((d) => {
        setError("");
        setDatos(d);
      })
      .catch((e) => setError(e.message));
  }, [mascotaId, tipo, version]);

  return (
    <section>
      <h2>📋 Historial de la mascota</h2>
      <div className="filtros">
        <select value={mascotaId} onChange={(e) => setMascotaId(e.target.value)}>
          <option value="">Selecciona una mascota</option>
          {mascotas.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre} ({m.especie})
            </option>
          ))}
        </select>
        <select value={tipo} onChange={(e) => setTipo(e.target.value)}>
          <option value="">Todo</option>
          <option value="vacuna">Vacunas</option>
          <option value="desparasitante">Desparasitaciones</option>
        </select>
      </div>

      {error && <p className="error">{error}</p>}
      {datos && datos.historial.length === 0 && (
        <p className="vacio">Esta mascota aún no tiene registros.</p>
      )}

      {datos && datos.historial.length > 0 && (
        <table className="tabla">
          <thead>
            <tr>
              <th>Fecha</th>
              <th>Producto</th>
              <th>Próxima dosis</th>
              <th>Veterinario</th>
              <th>Notas</th>
            </tr>
          </thead>
          <tbody>
            {datos.historial.map((h) => (
              <tr key={h.id}>
                <td>{h.fecha_aplicacion}</td>
                <td>
                  <strong>{h.producto}</strong>
                </td>
                <td>{h.fecha_proxima || "—"}</td>
                <td>{h.veterinario || "—"}</td>
                <td>{h.observaciones || "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  );
}