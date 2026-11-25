# PracticaAplicada

Plataforma para el seguimiento de vacunación y desparasitación de mascotas. El backend usa Flask y SQLAlchemy con MySQL o MariaDB, y el frontend usa React y Vite.

## Puesta en marcha

1. Desde la raíz del repositorio, crea un entorno de Python e instala las dependencias.

   ```bash
   python -m venv venv
   source venv/bin/activate
   python -m pip install -r requirements.txt
   ```

   En Windows, activa el entorno con `venv\Scripts\activate`.

2. Para una instalación nueva, crea la base `control_vacunacion_mascotas` en MySQL y carga `database/control_vacunacion_mascotas.sql` con tu cliente habitual. Crea un archivo `.env` en la raíz con los datos de tu instalación.

   ```dotenv
   DATABASE_URL=mysql+pymysql://usuario:contrasena@127.0.0.1:3306/control_vacunacion_mascotas
   SECRET_KEY=tu_clave_generada
   ```

   Genera la clave con `python -c "import secrets; print(secrets.token_hex(32))"`.

3. Si ya tienes la base de una versión anterior, actualízala con este comando. Conserva las mascotas y el historial existente. Los propietarios conceden el acceso desde la ficha de cada mascota, incluso si el veterinario ya registró aplicaciones antes de la actualización.

   ```bash
   python -m flask --app app.main actualizar-esquema
   ```

4. Inicia Flask desde la raíz del repositorio.

   ```bash
   python -m app.main
   ```

5. Abre otra terminal para iniciar el frontend y entra a la dirección que indica Vite.

   ```bash
   cd frontend
   npm ci
   npm run dev
   ```

   Por defecto la interfaz busca el backend en `http://localhost:5000`. Para usar otra dirección, define `VITE_API_URL` en el archivo `frontend/.env.local`.

## Permisos e historial

El propietario registra sus mascotas y consulta sus fichas e historiales. En **Mascotas → Consultar** puede autorizar a un veterinario con el correo registrado de su cuenta y retirar el acceso cuando lo necesite.

El veterinario ve las mascotas que le han autorizado y su historial completo. Puede registrar aplicaciones para esas mascotas, y editar o eliminar las aplicaciones que él mismo registró. Si cambia la fecha de aplicación o el producto y deja vacía la próxima dosis, se utiliza el intervalo del catálogo.

En **Historial** se puede buscar por producto, veterinario, dosis u observaciones y combinar la búsqueda con filtros de tipo y de fechas. Los totales de aplicaciones incluyen todos los registros de las mascotas visibles. Los estados de dosis se calculan a partir de la última aplicación de cada producto por mascota.

| Método | Ruta | Uso |
|---|---|---|
| POST | `/usuarios`, `/login` | Registro de cuenta e inicio de sesión |
| POST | `/logout` | Cierre de sesión y revocación del token |
| GET, POST | `/mascotas` | Lista de mascotas visibles y registro por su propietario |
| GET | `/mascotas/<id>` | Ficha de una mascota visible |
| GET, POST | `/mascotas/<id>/veterinarios` | Consulta y autorización de veterinarios por el propietario |
| DELETE | `/mascotas/<id>/veterinarios/<vet_id>` | Retiro del acceso del veterinario |
| GET | `/mascotas/<id>/historial` | Historial con filtros opcionales `q`, `tipo`, `desde` y `hasta` |
| PUT, DELETE | `/mascotas/<id>/registros/<registro_id>` | Edición y eliminación por el veterinario que registró la aplicación |
| GET | `/estadisticas` | Indicadores de las mascotas visibles para la cuenta |

## Pruebas

Ejecuta las pruebas de seguimiento con `python -m unittest discover -s tests -v`. Usan una base SQLite en memoria.

## Equipo

- Valeria Álvarez
- Mauro Santiago Sánchez Zambrano
- Nicolle Castro Delgado
