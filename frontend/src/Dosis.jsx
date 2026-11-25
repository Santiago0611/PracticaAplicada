import { useEffect, useState } from "react";
import { api } from "./api";

const ETIQUETAS = { vencida: "Vencida", proxima: "Próxima", al_dia: "Al día" };

function leyendaSello(dias) {
  if (dias < 0) return "días de atraso";
  if (dias === 0) return "vence hoy";
  return dias === 1 ? "día" : "días";
}

function resumenDias(dias) {
  const n = Math.abs(dias);
  const plural = n === 1 ? "" : "s";
  if (dias < 0) return `venció hace ${n} día${plural}`;
  if (dias === 0) return "vence hoy";
  return `faltan ${n} día${plural}`;
}

export default function Dosis({ version }) {
  const [dosis, setDosis] = useState([]);
  const [estado, setEstado] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function cargar() {
      try {
        setError("");
        const ruta = estado ? `/dosis?estado=${estado}` : "/dosis";
        setDosis(await api(ruta));
      } catch (err) {
        setError(err.message);
      }
    }
    cargar();
  }, [estado, version]);

  return (
    <section>
      <h2>🔔 Alertas de dosis</h2>
      <select value={estado} onChange={(e) => setEstado(e.target.value)}>
        <option value="">Todas</option>
        <option value="vencida">Vencidas</option>
        <option value="proxima">Próximas</option>
      </select>

      {error && <p className="error">{error}</p>}
      {!error && dosis.length === 0 && (
        <p className="vacio">No hay dosis pendientes por ahora.</p>
      )}

      <ul className="lista">
        {dosis.map((d, i) => (
          <li key={i} className={`dosis ${d.estado}`}>
            <div className="sello" aria-hidden="true">
              <strong>{Math.abs(d.dias_restantes)}</strong>
              <span>{leyendaSello(d.dias_restantes)}</span>
            </div>
            <div className="dosis-info">
              <strong>{d.mascota}</strong>
              <span>{d.producto}</span>
              <span className="detalle">
                Aplicada el {d.fecha_aplicacion}. Vence el {d.fecha_vencimiento}.
              </span>
              <span className="estado">
                {ETIQUETAS[d.estado] || d.estado}: {resumenDias(d.dias_restantes)}
              </span>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}