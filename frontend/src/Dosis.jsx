import { useEffect, useState } from "react";
import { api } from "./api";

const ETIQUETAS = {
  vencida: "Vencida",
  proxima: "Próxima",
  al_dia: "Al día",
};

function textoDias(d) {
  if (d < 0) return `Venció hace ${Math.abs(d)} día${Math.abs(d) === 1 ? "" : "s"}`;
  if (d === 0) return "Vence hoy";
  return `Faltan ${d} día${d === 1 ? "" : "s"}`;
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
      <h2>Alertas de dosis</h2>
      <select value={estado} onChange={(e) => setEstado(e.target.value)}>
        <option value="">Todas</option>
        <option value="vencida">Vencidas</option>
        <option value="proxima">Próximas</option>
      </select>

      {error && <p className="error">{error}</p>}
      {!error && dosis.length === 0 && <p>No hay dosis para mostrar.</p>}

      <ul className="lista">
        {dosis.map((d, i) => (
          <li key={i} className={`dosis ${d.estado}`}>
            <div>
              <strong>{d.mascota}</strong> · {d.producto}
              <div className="detalle">
                {d.tipo} · aplicada {d.fecha_aplicacion} · vence {d.fecha_vencimiento}
              </div>
            </div>
            <span className="etiqueta">
              {ETIQUETAS[d.estado] || d.estado} · {textoDias(d.dias_restantes)}
            </span>
          </li>
        ))}
      </ul>
    </section>
  );
}