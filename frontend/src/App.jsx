import { useState } from 'react'
import Auth from './Auth'
import Mascotas from './Mascotas'
import { leerSesion, cerrarSesion } from './api'

function App() {
  const [sesion, setSesion] = useState(() => leerSesion())

  function salir() {
    cerrarSesion()
    setSesion(null)
  }

  if (!sesion) {
    return <Auth alIniciarSesion={() => setSesion(leerSesion())} />
  }

  return (
    <div className="contenedor">
      <header className="barra">
        <h1>Control de Vacunación de Mascotas</h1>
        <div>
          <span>
            {sesion.usuario.nombre} ({sesion.usuario.rol}){' '}
          </span>
          <button className="secundario" onClick={salir}>
            Cerrar sesión
          </button>
        </div>
      </header>
      <Mascotas sesion={sesion} alExpirar={salir} />
    </div>
  )
}

export default App