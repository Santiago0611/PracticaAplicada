import { useState } from "react";
import { api } from "./api";

export default function EnviarRecordatorios({ usuario }) {
  const [incluirVencidas, setIncluirVencidas] = useState(true);
  const [enviando, setEnviando] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState("");

  if (usuario.rol !== "veterinario") return null;

  async function enviar(e) {
    e.preventDefault();
    setError("");
    setResultado(null);
    setEnviando(true);
    try {
      const data = await api("/recordatorios/enviar", {
        method: "POST",
        body: { incluir_vencidas: incluirVencidas },
      });
      setResultado(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <section>
      <h2>✉️ Recordatorios por correo</h2>
      <form onSubmit={enviar} className="recordatorios-form">
        <label className="check-label">
          <input
            type="checkbox"
            checked={incluirVencidas}
            onChange={(e) => setIncluirVencidas(e.target.checked)}
          />
          <span>Incluir dosis vencidas además de las próximas</span>
        </label>

        <button type="submit" disabled={enviando}>
          {enviando ? "Enviando correos..." : "Enviar recordatorios"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {resultado && (
        <div className="resumen-envio">
          <p className="exito">
            Enviados: <strong>{resultado.enviados ?? 0}</strong> · Sin correo:{" "}
            <strong>{resultado.sin_correo ?? 0}</strong> · Fallidos:{" "}
            <strong>{resultado.fallidos ?? 0}</strong>
          </p>
          {Array.isArray(resultado.detalle) && resultado.detalle.length > 0 && (
            <ul className="detalle-lista">
              {resultado.detalle.map((item, idx) => (
                <li key={idx}>{item}</li>
              ))}
            </ul>
          )}
        </div>
      )}
    </section>
  );
}