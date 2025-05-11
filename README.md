# ingesta-gest (Variables de Entorno)

Estas son las variables de entorno necesarias para configurar la conexión a la base de datos cuando se ejecute la aplicación Python en un contenedor Docker:

| Variable | Descripción |
|----------|-------------|
| `DB_HOST` | Dirección del servidor de la base de datos |
| `DB_USER` | Usuario para la conexión a la base de datos |
| `DB_PASSWORD` | Contraseña del usuario de la base de datos |
| `DB_NAME` | Nombre de la base de datos a la que conectarse |
| `DB_PORT` | Puerto para la conexión a la base de datos |

## Cómo configurar estas variables

### Opción 1: Al ejecutar el contenedor con Docker run

```bash
docker run -e DB_HOST=mi-servidor \
           -e DB_USER=usuario \
           -e DB_PASSWORD=contraseña \
           -e DB_NAME=mi_db \
           -e DB_PORT=5432 \
           nombre-imagen
```

### Opción 2: Usando un archivo .env

Crea un archivo `.env` con el siguiente contenido:

```
DB_HOST=mi-servidor
DB_USER=usuario
DB_PASSWORD=contraseña
DB_NAME=mi_db
DB_PORT=5432
```

Y luego ejecuta:

```bash
docker run --env-file .env nombre-imagen
```

### Opción 3: En docker-compose.yml

```yaml
version: '3'
services:
  app:
    image: nombre-imagen
    environment:
      - DB_HOST=mi-servidor
      - DB_USER=usuario
      - DB_PASSWORD=contraseña
      - DB_NAME=mi_db
      - DB_PORT=5432
```
