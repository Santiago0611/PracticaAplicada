import { useEffect, useState } from "react";
import { api } from "./api";

const VACIO = {
  mascota_id: "",
  catalogo_id: "",
  fecha_aplicacion: "",
  fecha_proxima: "",
  dosis: "",
  observaciones: "",
};

export default function RegistrarAplicacion({ usuario, mascotas, onRegistrado }) {
  const [categoria, setCategoria] = useState("vacuna");
  const [catalogo, setCatalogo] = useState([]);
  const [form, setForm] = useState(VACIO);
  const [error, setError] = useState("");
  const [ok, setOk] = useState("");

  const esVeterinario = usuario.rol === "veterinario";

  useEffect(() => {
    if (!esVeterinario) return;
    async function cargar() {
      try {
        setCatalogo(await api("/catalogo"));
      } catch (err) {
        setError(err.message);
      }
    }
    cargar();
  }, [esVeterinario]);

  if (!esVeterinario) return null;

  const productos = catalogo.filter((p) =>
    categoria === "vacuna" ? p.tipo === "vacuna" : p.tipo.startsWith("desparasitante")
  );

  function cambiar(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  function cambiarCategoria(c) {
    setCategoria(c);
    setForm({ ...form, catalogo_id: "" });
  }

  async function enviar(e) {
    e.preventDefault();
    setError("");
    setOk("");
    const { mascota_id, ...resto } = form;
    const body = { ...resto, catalogo_id: Number(resto.catalogo_id) };
    if (!body.fecha_proxima) delete body.fecha_proxima;
    if (!body.dosis) delete body.dosis;
    if (!body.observaciones) delete body.observaciones;

    const ruta = categoria === "vacuna" ? "vacunas" : "desparasitaciones";
    try {
      await api(`/mascotas/${mascota_id}/${ruta}`, { method: "POST", body });
      setOk("Registro guardado correctamente.");
      setForm(VACIO);
      if (onRegistrado) onRegistrado();
    } catch (err) {
      setError(err.message);
    }
  }

  const hoy = new Date().toISOString().slice(0, 10);

  return (
    <section>
      <h2>💉 Registrar aplicación</h2>
      <div className="pestanas">
        <button
          type="button"
          className={categoria === "vacuna" ? "activa" : ""}
          onClick={() => cambiarCategoria("vacuna")}
        >
          Vacuna
        </button>
        <button
          type="button"
          className={categoria === "desparasitante" ? "activa" : ""}
          onClick={() => cambiarCategoria("desparasitante")}
        >
          Desparasitación
        </button>
      </div>

      <form onSubmit={enviar} className="formulario">
        <select name="mascota_id" value={form.mascota_id} onChange={cambiar} required>
          <option value="">Mascota</option>
          {mascotas.map((m) => (
            <option key={m.id} value={m.id}>
              {m.nombre} ({m.especie})
            </option>
          ))}
        </select>

        <select name="catalogo_id" value={form.catalogo_id} onChange={cambiar} required>
          <option value="">Producto</option>
          {productos.map((p) => (
            <option key={p.id} value={p.id}>
              {p.nombre}
            </option>
          ))}
        </select>

        <label>Fecha de aplicación</label>
        <input
          name="fecha_aplicacion"
          type="date"
          max={hoy}
          value={form.fecha_aplicacion}
          onChange={cambiar}
          required
        />

        <label>Próxima dosis (opcional)</label>
        <input
          name="fecha_proxima"
          type="date"
          value={form.fecha_proxima}
          onChange={cambiar}
        />

        <input
          name="dosis"
          placeholder="Dosis (opcional)"
          value={form.dosis}
          onChange={cambiar}
        />
        <input
          name="observaciones"
          placeholder="Observaciones (opcional)"
          value={form.observaciones}
          onChange={cambiar}
        />

        <button type="submit">Guardar registro</button>
      </form>

      {error && <p className="error">{error}</p>}
      {ok && <p className="exito">{ok}</p>}
    </section>
  );
}
