# Wiselab

Wiselab es una API backend construida con FastAPI diseñada para la gestión financiera colaborativa. Permite a los usuarios crear espacios de trabajo, administrar presupuestos, categorías y realizar seguimiento de movimientos financieros de manera eficiente y segura.

## Módulos

El sistema está compuesto por los siguientes módulos principales:

- **Auth**: Manejo de autenticación, autorización y gestión de usuarios.
- **Workspace**: Gestión de espacios de trabajo, miembros y roles.
- **Budget**: Núcleo financiero para la administración de presupuestos, categorías y control de gastos.

## Documentación API

Puedes consultar la documentación interactiva de la API y probar los endpoints a través de Swagger UI en el siguiente enlace:

[http://localhost:8000/docs](http://localhost:8000/docs)

## Comandos

A continuación se detallan los comandos necesarios para gestionar el ciclo de vida de la aplicación usando Docker Compose.

### Levantar servicios
Inicia la aplicación y la base de datos normalmente.

```bash
docker-compose up --build
```

### Alimentar con el seeder
Levanta los servicios y ejecuta el seeder para poblar la base de datos con datos iniciales (si no existen).

```bash
SEED_DB=true docker-compose up --build
```

### Resetear y alimentar con el seeder
Levanta los servicios, borra todos los datos existentes en la base de datos y la vuelve a poblar desde cero. Útil para entornos de desarrollo.

```bash
RESET_DB=true docker-compose up --build
```