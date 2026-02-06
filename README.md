# wiselab

## Ejecutar linting y tests dentro del contenedor
# 1. Reconstruir la imagen
docker-compose build backend
# 2. Ejecutar Linting
docker-compose run --rm backend flake8 src --count --max-line-length=127 --statistics
# 3. Ejecutar Tests
docker-compose run --rm -e PYTHONPATH=. -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@db/wiselab_test backend pytest

## Levantar servicios
# 1. Comando para levantar servicios
docker-compose up --build