import { useEffect, useState } from "react";
import { api } from "./api";

function iconoEspecie(especie = "") {
  const e = especie.toLowerCase();
  if (e.includes("perro") || e.includes("can")) return "🐶";
  if (e.includes("gato") || e.includes("fel")) return "🐱";
  if (e.includes("conejo")) return "🐰";
  if (e.includes("ave") || e.includes("pájaro") || e.includes("pajaro") || e.includes("loro")) return "🐦";
  return "🐾";
}

function calcularEdad(fechaStr) {
  if (!fechaStr) return null;
  const nacimiento = new Date(`${fechaStr}T00:00:00`);
  if (Number.isNaN(nacimiento.getTime())) return null;

  const hoy = new Date();
  let meses =
    (hoy.getFullYear() - nacimiento.getFullYear()) * 12 +
    (hoy.getMonth() - nacimiento.getMonth());
  if (hoy.getDate() < nacimiento.getDate()) meses -= 1;
  if (meses < 0) return null;

  if (meses < 12) {
    return meses === 1 ? "1 mes" : `${meses} meses`;
  }
  const años = Math.floor(meses / 12);
  const restoMeses = meses % 12;
  const textoAnos = años === 1 ? "1 año" : `${años} años`;
  return restoMeses > 0 ? `${textoAnos} ${restoMeses}m` : textoAnos;
}

export default function Mascotas({ usuario, onCambio }) {
  const [mascotas, setMascotas] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    nombre: "",
    especie: "",
    raza: "",
    fecha_nacimiento: "",
    peso_kg: "",
    sexo: "",
  });

  async function cargar() {
    try {
      setMascotas(await api("/mascotas"));
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    cargar();
  }, []);

  function cambiar(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function crear(e) {
    e.preventDefault();
    setError("");
    const body = { ...form };
    if (!body.sexo) delete body.sexo;
    if (!body.fecha_nacimiento) delete body.fecha_nacimiento;
    if (body.peso_kg === "") delete body.peso_kg;
    try {
      await api("/mascotas", { method: "POST", body });
      setForm({
        nombre: "",
        especie: "",
        raza: "",
        fecha_nacimiento: "",
        peso_kg: "",
        sexo: "",
      });
      cargar();
      if (onCambio) onCambio();
    } catch (err) {
      setError(err.message);
    }
  }

  async function eliminar(id) {
    if (!window.confirm("¿Eliminar esta mascota?")) return;
    try {
      await api(`/mascotas/${id}`, { method: "DELETE" });
      cargar();
      if (onCambio) onCambio();
    } catch (err) {
      setError(err.message);
    }
  }

  const esPropietario = usuario.rol === "propietario";

  return (
    <section>
      <h2>🐶 Mascotas</h2>
      {error && <p className="error">{error}</p>}

      {esPropietario && (
        <form onSubmit={crear} className="formulario">
          <input
            name="nombre"
            placeholder="Nombre"
            value={form.nombre}
            onChange={cambiar}
            required
          />
          <input
            name="especie"
            placeholder="Especie (ej: PERRO)"
            value={form.especie}
            onChange={cambiar}
            required
          />
          <input
            name="raza"
            placeholder="Raza"
            value={form.raza}
            onChange={cambiar}
          />
          <input
            name="fecha_nacimiento"
            type="date"
            value={form.fecha_nacimiento}
            onChange={cambiar}
          />
          <input
            name="peso_kg"
            type="number"
            step="0.01"
            placeholder="Peso (kg)"
            value={form.peso_kg}
            onChange={cambiar}
          />
          <select name="sexo" value={form.sexo} onChange={cambiar}>
            <option value="">Sexo (opcional)</option>
            <option value="macho">Macho</option>
            <option value="hembra">Hembra</option>
          </select>
          <button type="submit">+ Agregar mascota</button>
        </form>
      )}

      {mascotas.length === 0 && (
        <p className="vacio">No hay mascotas registradas todavía.</p>
      )}

      <ul className="lista">
        {mascotas.map((m) => {
          const edad = calcularEdad(m.fecha_nacimiento);
          return (
            <li key={m.id}>
              <div className="mascota-item">
                <span className="mascota-avatar" aria-hidden="true">
                  {iconoEspecie(m.especie)}
                </span>
                <div>
                  <strong>{m.nombre}</strong>
                  <div className="detalle">
                    {m.especie}
                    {m.raza && ` · ${m.raza}`}
                    {edad && ` · ${edad}`}
                    {m.sexo && ` · ${m.sexo}`}
                    {(m.peso_kg ?? m.peso) && ` · ${m.peso_kg ?? m.peso} kg`}
                  </div>
                </div>
              </div>
              {esPropietario && (
                <button className="peligro" onClick={() => eliminar(m.id)}>
                  Eliminar
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}