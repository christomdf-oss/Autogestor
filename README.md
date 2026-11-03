# 🚗 AutoGestor — Sistema de Gestión de Vehículos

**Aplicación web Full-Stack desarrollada con Python, FastAPI y PostgreSQL, con autenticación JWT, control de acceso por roles, gestión de vehículos y almacenamiento de imágenes en la nube.**

🌐 **[Ver aplicación en línea](https://autogestor-lkyy.onrender.com)**

## 📌 Descripción

AutoGestor es una aplicación web diseñada para administrar un inventario de vehículos mediante una interfaz sencilla y una API REST.

El proyecto fue desarrollado para poner en práctica conceptos de desarrollo Backend, arquitectura por capas, bases de datos relacionales, autenticación, autorización, almacenamiento de archivos y despliegue en la nube.

El sistema permite gestionar información de vehículos, consultar inventarios y administrar imágenes, con restricciones de acceso según el rol del usuario.

## 🚀 Funcionalidades principales

- Autenticación de usuarios mediante JWT.
- Almacenamiento seguro de contraseñas mediante hashing.
- Control de acceso basado en roles: administrador y usuario.
- Registro, consulta, actualización y eliminación de vehículos.
- Búsqueda y filtrado por marca, modelo, precio y estado.
- Paginación de resultados.
- Gestión de fotografías por vehículo.
- Selección de imagen principal.
- Validación de datos y manejo de errores HTTP.
- Documentación interactiva de la API mediante Swagger.
- Pruebas automatizadas de autenticación con Pytest.
- Despliegue de la aplicación y servicios de datos en la nube.

## 🛠️ Tecnologías utilizadas

| Categoría | Tecnologías |
|---|---|
| Lenguaje principal | Python |
| Framework Backend | FastAPI |
| Base de datos | PostgreSQL |
| ORM | SQLAlchemy |
| Validación | Pydantic |
| Autenticación | JWT |
| Seguridad de contraseñas | Argon2 / pwdlib |
| Frontend | HTML, CSS y JavaScript |
| Almacenamiento de imágenes | Cloudinary |
| Base de datos en la nube | Neon |
| Hosting | Render |
| Contenedores | Docker |
| Pruebas | Pytest |
| Control de versiones | Git y GitHub |

## 🏗️ Arquitectura del proyecto

AutoGestor utiliza una organización por capas para separar responsabilidades y facilitar el mantenimiento del código.

```text
AutoGestor/
├── main.py
├── database.py
├── models.py
├── security.py
├── routes/
│   ├── vehiculos.py
│   └── usuarios.py
├── services/
│   ├── vehiculos.py
│   └── usuarios.py
├── Repository/
│   ├── vehiculos.py
│   └── usuarios.py
├── tests/
│   └── test_seguridad.py
└── README.md
```

**Responsabilidades principales:**

- **Routes:** define los endpoints y recibe las solicitudes HTTP.
- **Services:** contiene la lógica de negocio.
- **Repository:** administra las operaciones de acceso a datos.
- **Models:** representa las entidades de la base de datos.
- **Security:** gestiona los tokens JWT, contraseñas y permisos.
- **Database:** configura la conexión con PostgreSQL.

Esta separación permite mantener un código más organizado, reutilizable y sencillo de ampliar.

## 🔐 Autenticación y autorización

La aplicación implementa autenticación mediante JSON Web Tokens (JWT).

Los usuarios deben iniciar sesión para acceder a las rutas protegidas.

El sistema contempla dos niveles de acceso:

**Administrador**

- Registrar vehículos.
- Modificar información.
- Eliminar vehículos.
- Administrar fotografías.
- Gestionar usuarios.

**Usuario**

- Iniciar sesión.
- Consultar el inventario.
- Buscar y filtrar vehículos.
- Consultar su perfil.

Las operaciones administrativas están protegidas mediante dependencias de autorización en FastAPI.

## 🚘 Gestión de vehículos

Cada vehículo puede almacenar información como:

- Marca y modelo.
- Año de fabricación.
- Precio.
- Kilometraje.
- Color.
- Descripción.
- Estado de disponibilidad.
- Fotografías asociadas.

El sistema permite consultar el inventario mediante filtros y paginación, facilitando la búsqueda de registros.

## 🖼️ Almacenamiento de imágenes

Las imágenes de los vehículos se gestionan mediante Cloudinary.

La aplicación permite cargar varias fotografías, seleccionar una imagen principal y eliminar imágenes asociadas.

Se implementaron validaciones de formato y tamaño para controlar los archivos recibidos por la API.

## ☁️ Despliegue en la nube

La aplicación utiliza tres servicios principales:

- **Render:** alojamiento y ejecución del Backend.
- **Neon:** base de datos PostgreSQL administrada.
- **Cloudinary:** almacenamiento y entrega de imágenes.

El despliegue permite acceder a AutoGestor desde internet sin depender de que el entorno de desarrollo local permanezca encendido.

**Aplicación:** https://autogestor-lkyy.onrender.com

*Nota: el servicio gratuito de Render puede suspenderse por inactividad y tardar un poco en responder a la primera solicitud.*

## 🧪 Pruebas automatizadas

Se implementaron pruebas de seguridad con Pytest y FastAPI TestClient.

Actualmente se han validado los siguientes escenarios:

| Escenario | Resultado |
|---|---|
| Consultar vehículos sin autenticación | Aprobado |
| Crear vehículo sin autenticación | Aprobado |
| Consultar usuarios sin autenticación | Aprobado |
| Consultar perfil sin autenticación | Aprobado |

**Resultado de la ejecución: 4 pruebas aprobadas.**

Las pruebas verifican que las rutas protegidas rechacen solicitudes sin autenticación. No representan una auditoría completa de seguridad.

Para ejecutarlas:

```bash
python -m pytest tests/test_seguridad.py -v
```

## 📚 Aprendizajes obtenidos

Durante el desarrollo de AutoGestor se trabajaron conceptos fundamentales del desarrollo Backend:

- Diseño e implementación de APIs REST.
- Operaciones CRUD.
- Modelado de bases de datos relacionales.
- Consultas mediante SQLAlchemy.
- Validación con Pydantic.
- Autenticación JWT y autorización por roles.
- Gestión de archivos e integración con servicios externos.
- Uso de variables de entorno.
- Contenedores con Docker.
- Despliegue y configuración de servicios en la nube.
- Pruebas automatizadas.
- Control de versiones con Git.

## 🔮 Posibles mejoras futuras

- Ampliar la cobertura de pruebas automatizadas.
- Incorporar pruebas de integración.
- Implementar migraciones con Alembic.
- Agregar monitoreo y registros de auditoría.
- Mejorar la experiencia de usuario.
- Incorporar recuperación de contraseñas.

## 👨‍💻 Autor

**Christopher — Ingeniería en Sistemas Computacionales**

Proyecto de portafolio enfocado en desarrollo Backend con Python, FastAPI, PostgreSQL y tecnologías de despliegue en la nube.

**GitHub:** https://github.com/christomdf-oss/Autogestor

---

*AutoGestor es un proyecto de aprendizaje y portafolio desarrollado para demostrar conocimientos prácticos en construcción, seguridad y despliegue de aplicaciones web.*
