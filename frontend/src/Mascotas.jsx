import { useEffect, useState } from 'react'
import { peticion } from './api'
import './Mascotas.css'

const ESPECIES = ['PERRO', 'GATO', 'AVE', 'CONEJO', 'REPTIL', 'OTRO']
const VACIO = { nombre: '', especie: 'PERRO', raza: '', fecha_nacimiento: '', peso: '' }
const EMOJIS = { PERRO: '🐶', GATO: '🐱', AVE: '🐦', CONEJO: '🐰', REPTIL: '🦎', OTRO: '🐾' }

function Mascotas({ sesion, alExpirar }) {
  const { token, usuario } = sesion
  const esPropietario = usuario.rol === 'propietario'

  const [mascotas, setMascotas] = useState([])
  const [cargando, setCargando] = useState(true)
  const [error, setError] = useState('')
  const [exito, setExito] = useState('')
  const [formulario, setFormulario] = useState(null)
  const [editandoId, setEditandoId] = useState(null)
  const [guardando, setGuardando] = useState(false)
  const [porEliminar, setPorEliminar] = useState(null)

  const hoy = new Date().toLocaleDateString('en-CA')

  function manejarError(e) {
    if (e.status === 401) {
      alExpirar()
    } else {
      setError(e.message)
    }
  }

  useEffect(() => {
    let activo = true
    peticion('/mascotas', { token })
      .then((datos) => {
        if (activo) setMascotas(datos)
      })
      .catch((e) => {
        if (!activo) return
        if (e.status === 401) alExpirar()
        else setError(e.message)
      })
      .finally(() => {
        if (activo) setCargando(false)
      })
    return () => {
      activo = false
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token])

  function abrirNuevo() {
    setError('')
    setExito('')
    setEditandoId(null)
    setFormulario({ ...VACIO })
  }

  function abrirEditar(m) {
    setError('')
    setExito('')
    setEditandoId(m.id)
    setFormulario({
      nombre: m.nombre,
      especie: m.especie,
      raza: m.raza || '',
      fecha_nacimiento: m.fecha_nacimiento || '',
      peso: m.peso ?? '',
    })
  }

  function cerrarFormulario() {
    setFormulario(null)
    setEditandoId(null)
  }

  function cambiar(campo, valor) {
    setFormulario({ ...formulario, [campo]: valor })
  }

  async function guardar(evento) {
    evento.preventDefault()
    setError('')
    setExito('')

    if (!formulario.nombre.trim()) {
      setError('El nombre de la mascota es obligatorio.')
      return
    }
    const peso = formulario.peso === '' ? null : Number(formulario.peso)
    if (peso !== null && (Number.isNaN(peso) || peso <= 0)) {
      setError('El peso debe ser mayor que 0.')
      return
    }

    setGuardando(true)
    try {
      if (editandoId) {
        const actualizada = await peticion(`/mascotas/${editandoId}`, {
          metodo: 'PUT',
          token,
          cuerpo: {
            nombre: formulario.nombre.trim(),
            especie: formulario.especie,
            raza: formulario.raza.trim(),
            peso,
          },
        })
        setMascotas(mascotas.map((m) => (m.id === editandoId ? actualizada : m)))
        setExito('Mascota actualizada correctamente.')
      } else {
        const creada = await peticion('/mascotas', {
          metodo: 'POST',
          token,
          cuerpo: {
            nombre: formulario.nombre.trim(),
            especie: formulario.especie,
            raza: formulario.raza.trim(),
            fecha_nacimiento: formulario.fecha_nacimiento || null,
            peso_kg: peso,
          },
        })
        setMascotas([creada, ...mascotas])
        setExito('Mascota registrada correctamente.')
      }
      cerrarFormulario()
    } catch (e) {
      manejarError(e)
    } finally {
      setGuardando(false)
    }
  }

  async function confirmarEliminar() {
    setError('')
    setExito('')
    const id = porEliminar.id
    try {
      await peticion(`/mascotas/${id}`, { metodo: 'DELETE', token })
      setMascotas(mascotas.filter((m) => m.id !== id))
      setExito('Mascota eliminada correctamente.')
    } catch (e) {
      manejarError(e)
    } finally {
      setPorEliminar(null)
    }
  }

  return (
    <div>
      <div className="encabezado-seccion">
        <h2>{esPropietario ? 'Mis mascotas' : 'Mascotas registradas'}</h2>
        {esPropietario && !formulario && (
          <button onClick={abrirNuevo}>+ Registrar mascota</button>
        )}
      </div>

      {error && <div className="error">{error}</div>}
      {exito && <div className="exito">{exito}</div>}

      {formulario && (
        <form className="tarjeta formulario" onSubmit={guardar}>
          <h3>{editandoId ? 'Editar mascota' : 'Registrar mascota'}</h3>
          <label>
            Nombre
            <input value={formulario.nombre} onChange={(e) => cambiar('nombre', e.target.value)} />
          </label>
          <label>
            Especie
            <select value={formulario.especie} onChange={(e) => cambiar('especie', e.target.value)}>
              {ESPECIES.map((e) => (
                <option key={e} value={e}>
                  {e.charAt(0) + e.slice(1).toLowerCase()}
                </option>
              ))}
            </select>
          </label>
          <label>
            Raza (opcional)
            <input value={formulario.raza} onChange={(e) => cambiar('raza', e.target.value)} />
          </label>
          {!editandoId && (
            <label>
              Fecha de nacimiento (opcional)
              <input
                type="date"
                max={hoy}
                value={formulario.fecha_nacimiento}
                onChange={(e) => cambiar('fecha_nacimiento', e.target.value)}
              />
            </label>
          )}
          <label>
            Peso en kg (opcional)
            <input
              type="number"
              step="0.1"
              min="0"
              value={formulario.peso}
              onChange={(e) => cambiar('peso', e.target.value)}
            />
          </label>
          <div className="acciones">
            <button type="submit" disabled={guardando}>
              {guardando ? 'Guardando...' : 'Guardar'}
            </button>
            <button type="button" className="secundario" onClick={cerrarFormulario}>
              Cancelar
            </button>
          </div>
        </form>
      )}

      {cargando ? (
        <p>Cargando mascotas...</p>
      ) : mascotas.length === 0 ? (
        <div className="tarjeta">
          <p>{esPropietario ? 'Aún no tiene mascotas registradas.' : 'No hay mascotas registradas.'}</p>
        </div>
      ) : (
        <div className="lista">
          {mascotas.map((m) => (
                        <div key={m.id} className="tarjeta mascota">
              <div className="avatar">{EMOJIS[m.especie] || '🐾'}</div>
              <div className="info">
                <h3>{m.nombre}</h3>
                <p>
                  <span className="etiqueta">{m.especie}</span>
                  {m.raza ? ` ${m.raza}` : ''}
                </p>
                <p className="detalle">
                  Nacimiento: {m.fecha_nacimiento || 'No registrada'} · Peso:{' '}
                  {m.peso != null ? `${m.peso} kg` : 'No registrado'}
                </p>
                {!esPropietario && <p className="detalle">Propietario n.º {m.propietario_id}</p>}
              </div>
              {esPropietario && (
                <div className="acciones">
                  <button className="secundario" onClick={() => abrirEditar(m)}>
                    Editar
                  </button>
                  <button className="peligro" onClick={() => setPorEliminar(m)}>
                    Eliminar
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {porEliminar && (
        <div className="fondo-modal">
          <div className="modal tarjeta">
            <h3>¿Eliminar a {porEliminar.nombre}?</h3>
            <p>¿Está seguro? Esta acción no se puede deshacer.</p>
            <div className="acciones">
              <button className="peligro" onClick={confirmarEliminar}>
                Sí, eliminar
              </button>
              <button className="secundario" onClick={() => setPorEliminar(null)}>
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Mascotas