import { useState } from "react";
import { api } from "./api";
import DetalleMascota from "./DetalleMascota";

const ESPECIES = ["PERRO", "GATO", "AVE", "CONEJO", "REPTIL", "OTRO"];
const AVATARES = { PERRO: "🐶", GATO: "🐱", AVE: "🐦", CONEJO: "🐰", REPTIL: "🦎" };
const VACIO = {
  nombre: "", especie: "", raza: "", fecha_nacimiento: "", peso_kg: "", sexo: "",
};

export default function Mascotas({
  usuario, mascotas, errorCarga, version, onCambio, onHistorial,
}) {
  const [error, setError] = useState("");
  const [form, setForm] = useState(VACIO);
  const [detalleId, setDetalleId] = useState(null);
  const [ocupado, setOcupado] = useState(false);
  const esPropietario = usuario.rol === "propietario";

  function cambiar(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function crear(e) {
    e.preventDefault();
    setError("");
    setOcupado(true);
    try {
      const mascota = await api("/mascotas", { method: "POST", body: form });
      setForm(VACIO);
      setDetalleId(mascota.id);
      onCambio();
    } catch (err) {
      setError(err.message);
    } finally {
      setOcupado(false);
    }
  }

  async function eliminar(mascota) {
    if (!window.confirm(`¿Eliminar a ${mascota.nombre}?`)) return;
    setError("");
    setOcupado(true);
    try {
      await api(`/mascotas/${mascota.id}`, { method: "DELETE" });
      if (detalleId === mascota.id) setDetalleId(null);
      onCambio();
    } catch (err) {
      setError(err.message);
    } finally {
      setOcupado(false);
    }
  }

  return (
    <section>
      <h2>🐶 {esPropietario ? "Mascotas" : "Pacientes"}</h2>
      {(error || errorCarga) && <p className="error" role="alert">{error || errorCarga}</p>}

      {esPropietario && (
        <form onSubmit={crear} className="formulario">
          <label>
            Nombre
            <input name="nombre" value={form.nombre} onChange={cambiar} maxLength={100} required />
          </label>
          <label>
            <span id="etiqueta-especie">Especie</span>
            <select name="especie" aria-labelledby="etiqueta-especie" value={form.especie} onChange={cambiar} required>
              <option value="">Selecciona una especie</option>
              {ESPECIES.map((especie) => <option key={especie}>{especie}</option>)}
            </select>
          </label>
          <label>
            Raza (opcional)
            <input name="raza" value={form.raza} onChange={cambiar} maxLength={100} />
          </label>
          <label>
            Fecha de nacimiento (opcional)
            <input name="fecha_nacimiento" type="date" value={form.fecha_nacimiento} onChange={cambiar} />
          </label>
          <label>
            Peso en kg (opcional)
            <input
              name="peso_kg" type="number" min="0.01" max="999.99" step="0.01"
              value={form.peso_kg} onChange={cambiar}
            />
          </label>
          <label>
            <span id="etiqueta-sexo">Sexo (opcional)</span>
            <select name="sexo" aria-labelledby="etiqueta-sexo" value={form.sexo} onChange={cambiar}>
              <option value="">Selecciona el sexo</option>
              <option value="macho">Macho</option>
              <option value="hembra">Hembra</option>
            </select>
          </label>
          <button type="submit" disabled={ocupado}>Agregar mascota</button>
        </form>
      )}

      {mascotas === null && !errorCarga && <p className="vacio">Cargando mascotas…</p>}
      {mascotas?.length === 0 && (
        <p className="vacio">
          {esPropietario ? "Aún no tienes mascotas registradas." : "Aún no tienes pacientes autorizados."}
        </p>
      )}

      <ul className="lista lista-mascotas">
        {mascotas?.map((mascota) => (
          <li key={mascota.id}>
            <div className="mascota-item">
              <span className="mascota-avatar" aria-hidden="true">{AVATARES[mascota.especie] || "🐾"}</span>
              <div>
                <strong>{mascota.nombre}</strong>
                <div className="detalle">
                  {[mascota.especie, mascota.raza, mascota.sexo, mascota.peso != null && `${mascota.peso} kg`]
                    .filter(Boolean).join(" · ")}
                </div>
              </div>
            </div>
            <div className="acciones">
              <button
                type="button"
                className="fantasma"
                aria-expanded={detalleId === mascota.id}
                aria-controls={detalleId === mascota.id ? "detalle-mascota" : undefined}
                onClick={() => setDetalleId(detalleId === mascota.id ? null : mascota.id)}
              >
                {detalleId === mascota.id ? "Cerrar ficha" : "Consultar"}
              </button>
              {esPropietario && (
                <button type="button" className="peligro" disabled={ocupado} onClick={() => eliminar(mascota)}>
                  Eliminar
                </button>
              )}
            </div>
            {detalleId === mascota.id && (
              <DetalleMascota
                id={mascota.id}
                esPropietario={esPropietario}
                version={version}
                onCambio={onCambio}
                onHistorial={onHistorial}
              />
            )}
          </li>
        ))}
      </ul>
    </section>
  );
}
