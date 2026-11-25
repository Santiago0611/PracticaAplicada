import { useEffect, useState } from "react";
import { api } from "./api";

export default function Mascotas({ usuario }) {
  const [mascotas, setMascotas] = useState([]);
  const [error, setError] = useState("");
  const [form, setForm] = useState({ nombre: "", especie: "", raza: "", fecha_nacimiento: "", peso_kg: "", sexo: "" });

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
      setForm({ nombre: "", especie: "", raza: "", fecha_nacimiento: "", peso_kg: "" , sexo: ""});
      cargar();
    } catch (err) {
      setError(err.message);
    }
  }

  async function eliminar(id) {
    if (!window.confirm("¿Eliminar esta mascota?")) return;
    try {
      await api(`/mascotas/${id}`, { method: "DELETE" });
      cargar();
    } catch (err) {
      setError(err.message);
    }
  }

  const esPropietario = usuario.rol === "propietario";

  return (
    <section>
      <h2>Mascotas</h2>
      {error && <p className="error">{error}</p>}

      {esPropietario && (
        <form onSubmit={crear} className="formulario">
          <input name="nombre" placeholder="Nombre" value={form.nombre} onChange={cambiar} required />
          <input name="especie" placeholder="Especie (ej: PERRO)" value={form.especie} onChange={cambiar} required />
          <input name="raza" placeholder="Raza" value={form.raza} onChange={cambiar} />
          <input name="fecha_nacimiento" type="date" value={form.fecha_nacimiento} onChange={cambiar} />
          <input name="peso_kg" type="number" step="0.01" placeholder="Peso (kg)" value={form.peso_kg} onChange={cambiar} />
          <select name="sexo" value={form.sexo} onChange={cambiar}>
  <option value="">Sexo (opcional)</option>
  <option value="macho">Macho</option>
  <option value="hembra">Hembra</option>
</select>
          <button type="submit">Agregar mascota</button>
        </form>
      )}

      {mascotas.length === 0 && <p>No hay mascotas registradas.</p>}
      <ul className="lista">
        {mascotas.map((m) => (
          <li key={m.id}>
          <div>
  <strong>{m.nombre}</strong> · {m.especie}
  {m.raza && ` · ${m.raza}`}
  {m.sexo && ` · ${m.sexo}`}
  {(m.peso_kg ?? m.peso) && ` · ${m.peso_kg ?? m.peso} kg`}
</div>
            {esPropietario && (
              <button className="peligro" onClick={() => eliminar(m.id)}>Eliminar</button>
        )}
          </li>
        ))}
      </ul>
    </section>
  );
}