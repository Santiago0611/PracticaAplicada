import { useEffect, useState } from "react";
import { api } from "./api";

export default function EditarAplicacion({ registro, ruta, onCancelar, onGuardado }) {
  const [catalogo, setCatalogo] = useState(null);
  const [error, setError] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [fechaProxima, setFechaProxima] = useState(undefined);
  const [form, setForm] = useState({
    catalogo_id: String(registro.catalogo_id),
    fecha_aplicacion: registro.fecha_aplicacion,
    dosis: registro.dosis || "",
    observaciones: registro.observaciones || "",
  });

  useEffect(() => {
    let vigente = true;
    api("/catalogo")
      .then((datos) => {
        if (vigente) setCatalogo(datos);
      })
      .catch((err) => {
        if (vigente) setError(err.message);
      });
    return () => { vigente = false; };
  }, []);

  const esVacuna = registro.tipo === "vacuna";
  const productos = catalogo?.filter((producto) => (producto.tipo === "vacuna") === esVacuna);
  const cambioAplicacion = Number(form.catalogo_id) !== registro.catalogo_id
    || form.fecha_aplicacion !== registro.fecha_aplicacion;

  function cambiar(e) {
    setForm({ ...form, [e.target.name]: e.target.value });
  }

  async function guardar(e) {
    e.preventDefault();
    setError("");
    setGuardando(true);
    try {
      const cuerpo = { ...form, catalogo_id: Number(form.catalogo_id) };
      if (fechaProxima !== undefined) cuerpo.fecha_proxima = fechaProxima;
      await api(ruta, { method: "PUT", body: cuerpo });
      onGuardado();
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <div className="edicion-aplicacion">
      <h3>Editar aplicación de {registro.producto}</h3>
      <form className="formulario" onSubmit={guardar}>
        <label>
          <span id="etiqueta-producto-edicion">Producto</span>
          <select
            name="catalogo_id" aria-labelledby="etiqueta-producto-edicion" value={form.catalogo_id}
            onChange={cambiar} disabled={!productos} required
          >
            {!productos && <option value={registro.catalogo_id}>{registro.producto}</option>}
            {productos?.map((producto) => <option key={producto.id} value={producto.id}>{producto.nombre}</option>)}
          </select>
        </label>
        <label>
          Fecha de aplicación
          <input type="date" name="fecha_aplicacion" value={form.fecha_aplicacion} onChange={cambiar} required />
        </label>
        <label>
          Próxima dosis (opcional)
          <input type="date" value={fechaProxima ?? (cambioAplicacion ? "" : registro.fecha_proxima || "")}
            onChange={(e) => setFechaProxima(e.target.value)}
          />
        </label>
        <label>
          Dosis (opcional)
          <input name="dosis" value={form.dosis} onChange={cambiar} maxLength={50} />
        </label>
        <label>
          Observaciones (opcional)
          <input name="observaciones" value={form.observaciones} onChange={cambiar} maxLength={255} />
        </label>
        <div className="acciones">
          <button type="submit" disabled={!productos || guardando}>Guardar cambios</button>
          <button type="button" className="fantasma" disabled={guardando} onClick={onCancelar}>Cancelar</button>
        </div>
      </form>
      {error && <p className="error" role="alert">{error}</p>}
    </div>
  );
}
