# PracticaAplicada — Control de Vacunación de Mascotas

Plataforma digital para el registro y control de vacunación y desparasitación de mascotas, con gestión de propietarios y veterinarios.

## Stack

- **Backend:** Python + Flask + Flask-SQLAlchemy
- **Base de datos:** MySQL (probado con XAMPP)
- **Autenticación:** JWT (PyJWT) + hashing de contraseñas con bcrypt

## Cómo levantar el proyecto en tu computador

### 1. Clona el repositorio y entra a la carpeta

```bash
git clone https://github.com/Santiago0611/PracticaAplicada.git
cd PracticaAplicada
```

### 2. Crea y activa el entorno virtual

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux
```

### 3. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 4. Crea la base de datos

1. Prende MySQL (por ejemplo con XAMPP).
2. Abre phpMyAdmin y crea una base de datos llamada `control_vacunacion_mascotas`.
3. Ve a la pestaña **Importar**, selecciona el archivo `database/control_vacunacion_mascotas.sql` de este repositorio, y dale a **Continuar**.


Ajusta el usuario/contraseña de MySQL según tu instalación.

### 6. Corre el servidor

```bash
python -m app.main
```

El servidor queda disponible en `http://127.0.0.1:5000`.

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/usuarios` | Registra un nuevo usuario (propietario o veterinario) |
| POST | `/login` | Inicia sesión y devuelve un token JWT |

## Equipo

- Valeria Álvarez
- Mauro Santiago Sánchez Zambrano
- Nicolle Castro Delgado

### 5. Crea tu archivo `.env`

En la raíz del proyecto, crea un archivo `.env` (no se sube a GitHub) con:
