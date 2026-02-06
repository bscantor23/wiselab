# Wiselab

![Dashboard Mobile](./public/README_PICTURE_1.png)
![Workspace List](./public/README_PICTURE_3.png)
![Login Interface](./public/README_PICTURE_2.png)

Wiselab es una API backend construida con FastAPI diseñada para la gestión financiera colaborativa. Permite a los usuarios crear espacios de trabajo, administrar presupuestos, categorías y realizar seguimiento de movimientos financieros de manera eficiente y segura.

## Módulos

El sistema está compuesto por los siguientes módulos principales:

- **Auth**: Manejo de autenticación, autorización y gestión de usuarios.
- **Workspace**: Gestión de espacios de trabajo, miembros y roles.
- **Budget**: Núcleo financiero para la administración de presupuestos, categorías y control de gastos.

## Acceso Local

Una vez que los servicios estén arriba, puedes acceder a la aplicación en las siguientes direcciones:

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API (Backend)**: [http://localhost:8000/api](http://localhost:8000/api)
- **Documentación API (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

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

## Datos de Prueba (Seeder)

El sistema incluye un script de semillas para facilitar las pruebas. Al ejecutar el comando con `RESET_DB=true` o `SEED_DB=true`, se crearán los siguientes datos:

- **Usuarios**: Se crean 5 usuarios de prueba con el formato `usuario${X}@example.com` (donde X es de 1 a 5).
- **Credenciales**:
  - **Email**: `usuario1@example.com` (hasta `usuario5@example.com`)
  - **Password**: `password123`
- **Estructura**:
  - 10 Espacios de trabajo (Workspaces) con nombres y descripciones realistas enfocadas en finanzas.
  - 20 Miembros distribuidos entre los espacios.
  - 10 Presupuestos iniciales para conectar con el frontend.

## Pruebas (Tests)

Para ejecutar las pruebas del backend y verificar la integridad del código:

```bash
# Ejecutar todos los tests
docker-compose exec backend pytest

# Ejecutar con reporte de cobertura
docker-compose exec backend pytest --cov=src --cov-report=term-missing
```

## Estado del Proyecto

Actualmente, el proyecto se encuentra en desarrollo activo:
- **Frontend**: Se sigue trabajando en los módulos debido al tiempo implementado para la prueba, donde actualmente se encuentra disponible el auth y workspaces, pero faltaría una página para visualizar y enlazar miembros, y otra para presupuestos y movimientos
- **Movimientos**: La funcionalidad de movimientos financieros dentro de los presupuestos está en proceso de implementación dado que tecnicamente es un módulo distinto a presupuestos.