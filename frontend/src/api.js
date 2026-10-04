const BASE = '/api'

export function guardarSesion(token, usuario) {
  localStorage.setItem('token', token)
  localStorage.setItem('usuario', JSON.stringify(usuario))
}

export function leerSesion() {
  const token = localStorage.getItem('token')
  const usuario = localStorage.getItem('usuario')
  if (!token || !usuario) return null
  return { token, usuario: JSON.parse(usuario) }
}

export function cerrarSesion() {
  localStorage.removeItem('token')
  localStorage.removeItem('usuario')
}

export async function peticion(ruta, { metodo = 'GET', cuerpo, token } = {}) {
  const headers = {}
  if (cuerpo) headers['Content-Type'] = 'application/json'
  if (token) headers['Authorization'] = `Bearer ${token}`

  let respuesta
  try {
    respuesta = await fetch(BASE + ruta, {
      method: metodo,
      headers,
      body: cuerpo ? JSON.stringify(cuerpo) : undefined,
    })
  } catch {
    throw new Error('No se pudo conectar con el servidor. Intente nuevamente.')
  }

  let datos = null
  try {
    datos = await respuesta.json()
  } catch {
    datos = null
  }

  if (!respuesta.ok) {
    let mensaje =
      (datos && (datos.detalle || datos.error || datos.msg)) ||
      'Ocurrió un error. Intente nuevamente.'
    if (datos && datos.errores) {
      mensaje = Object.values(datos.errores).join(' ')
    }
    if (respuesta.status === 401 && token) {
      mensaje = 'Su sesión expiró. Inicie sesión de nuevo.'
    }
    const error = new Error(mensaje)
    error.status = respuesta.status
    throw error
  }
  return datos
}