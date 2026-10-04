import { useState } from 'react'
import { peticion, guardarSesion } from './api'
import './Auth.css'

const ESPECIALES = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

function calcularRequisitos(contrasena) {
  return [
    { texto: 'Mínimo 8 caracteres', ok: contrasena.length >= 8 },
    { texto: 'Al menos una mayúscula', ok: /[A-Z]/.test(contrasena) },
    { texto: 'Al menos un número', ok: /\d/.test(contrasena) },
    {
      texto: 'Al menos un carácter especial',
      ok: [...contrasena].some((c) => ESPECIALES.includes(c)),
    },
  ]
}

function Auth({ alIniciarSesion }) {
  const [modo, setModo] = useState('login')
  const [nombre, setNombre] = useState('')
  const [correo, setCorreo] = useState('')
  const [contrasena, setContrasena] = useState('')
  const [confirmacion, setConfirmacion] = useState('')
  const [rol, setRol] = useState('propietario')
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  const requisitos = calcularRequisitos(contrasena)

  async function enviar(evento) {
    evento.preventDefault()
    setError('')

    if (modo === 'registro') {
      const faltan = requisitos.filter((r) => !r.ok).map((r) => r.texto.toLowerCase())
      if (faltan.length > 0) {
        setError('La contraseña no cumple los requisitos. Falta: ' + faltan.join(', ') + '.')
        return
      }
      if (contrasena !== confirmacion) {
        setError('Las contraseñas no coinciden.')
        return
      }
    }

    setCargando(true)
    try {
      if (modo === 'registro') {
        await peticion('/usuarios', {
          metodo: 'POST',
          cuerpo: { nombre, correo, contrasena, rol },
        })
      }
      const datos = await peticion('/login', {
        metodo: 'POST',
        cuerpo: { correo, contrasena },
      })
      guardarSesion(datos.token, datos.usuario)
      alIniciarSesion()
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  function cambiarModo() {
    setError('')
    setConfirmacion('')
    setModo(modo === 'login' ? 'registro' : 'login')
  }

  return (
    <div className="tarjeta auth">
      <div className="logo">🐾</div>
      <h1>{modo === 'login' ? 'Iniciar sesión' : 'Crear cuenta'}</h1>
      {error && <div className="error">{error}</div>}
      <form onSubmit={enviar}>
        {modo === 'registro' && (
          <label>
            Nombre
            <input value={nombre} onChange={(e) => setNombre(e.target.value)} required />
          </label>
        )}
        <label>
          Correo
          <input type="email" value={correo} onChange={(e) => setCorreo(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={contrasena} onChange={(e) => setContrasena(e.target.value)} required />
        </label>
        {modo === 'registro' && (
          <>
            <ul className="requisitos">
              {requisitos.map((r) => (
                <li key={r.texto} className={r.ok ? 'cumple' : 'falta'}>
                  {r.ok ? '✓' : '✗'} {r.texto}
                </li>
              ))}
            </ul>
            <label>
              Confirmar contraseña
              <input
                type="password"
                value={confirmacion}
                onChange={(e) => setConfirmacion(e.target.value)}
                required
              />
            </label>
            {confirmacion && contrasena !== confirmacion && (
              <div className="aviso">Las contraseñas no coinciden.</div>
            )}
            <label>
              Rol
              <select value={rol} onChange={(e) => setRol(e.target.value)}>
                <option value="propietario">Propietario</option>
                <option value="veterinario">Veterinario</option>
              </select>
            </label>
          </>
        )}
        <button type="submit" disabled={cargando}>
          {cargando ? 'Enviando...' : modo === 'login' ? 'Entrar' : 'Registrarme'}
        </button>
      </form>
      <p>
        {modo === 'login' ? '¿No tiene cuenta? ' : '¿Ya tiene cuenta? '}
        <button type="button" className="enlace" onClick={cambiarModo}>
          {modo === 'login' ? 'Regístrese' : 'Inicie sesión'}
        </button>
      </p>
    </div>
  )
}

export default Auth