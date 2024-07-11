# Proyecto: Paciente Virtual

## Descripción

**Versión 2** del proyecto "Paciente Virtual" introduce una interfaz intuitiva para la creación y gestión de casos, facilitando la interacción con los usuarios mediante un flujo estructurado. Este proyecto está diseñado para ser una herramienta eficiente en la simulación y manejo de casos en un entorno médico o de crisis.

## Características Principales

### Creación de Nuevos Casos

- **Inicio del Flujo:** Un formulario intuitivo donde se ingresan los datos necesarios para crear un nuevo caso.
- **Envío de Datos:** El formulario envía los datos a una ruta específica y se crea el nuevo caso automáticamente.

### Gestión de Casos Existentes

- **Listado de Casos:** Una lista completa donde se muestran todos los casos creados.
- **Acciones por Caso:** En la última fila de cada caso, se disponen tres botones con funcionalidades específicas:
  - **Copiar Antecedentes:** Este botón copia los antecedentes del caso en el formulario para facilitar la creación de un nuevo caso basado en los datos existentes.
  - **Activar Caso:** Permite enviar los datos del caso y activar la interacción, posibilitando la comunicación con el caso.
  - **Eliminar Caso:** Opción para eliminar el caso de la lista.

## Estructura del Proyecto

### Frontend

- Formulario de creación de casos.
- Lista interactiva de casos.
- Botones de acción para cada caso.

### Backend

- Rutas API para la gestión de casos (creación, activación y eliminación).
- Base de datos para almacenar y gestionar los casos.

## Tecnologías Utilizadas

### Frontend

- HTML/CSS/JavaScript para la interfaz de usuario.
- Frameworks/librerías de frontend (e.g., React, Vue.js).

### Backend

- Flask para el desarrollo del API.
- SQLAlchemy para la gestión de la base de datos SQLite.

### Integraciones

- Swagger para la documentación y pruebas de la API.
- Flask-RESTful para la gestión de rutas y recursos.
