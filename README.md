# Eventhub

Aplicación web para venta de entradas utilizada en la cursada 2025 de Ingeniería y Calidad de Software. UTN-FRLP

## Integrantes

- Valentín Augusto Garzaniti
- Romeo Lorenzo Monfroglio
- Gonzalo Martín Perez
- Manuel Rebol
- Facundo Serra
- Federico Nahuel Valle



## Dependencias

- python 3
- Django
- sqlite
- playwright
- ruff

## Instalar dependencias
```
pip install -r requirements.txt
```

## Makefile
`Makefile` tiene como objetivo facilitar la gestión de tareas comunes en el proyecto Django. 

Para poder ejecutar `Makefile` en Windows es necesario instalar [Chocolatly](https://chocolatey.org/install#individual) y correr

```bash
choco install make
```

Se asocicia un comando, o una serie de comandos a un comando personalizado. Se pueden ejecutar comandos específicos con `make <target>`

| Comando           | Descripción                                              |
|-------------------|----------------------------------------------------------|
| `make install`    | Instala las dependencias desde `requirements.txt`        |
| `make playwright-install` | Instala las dependencias de Playwright                |
| `make migrate`     | Aplica las migraciones a la base de datos                |
| `make superuser`   | Crea un usuario administrador interactivo                |
| `make loaddata`    | Carga los datos iniciales desde `fixtures/events.json`  |
| `make run`         | Inicia el servidor de desarrollo (`runserver`)          |
| `make test`        | Ejecuta todos los tests definidos en `app.test`         |
| `make test-class CLASS=...` | Ejecuta una clase de tests específica (`ClaseTest`)     |
| `make test-unit`   | Ejecuta los tests unitarios en `app.test.test_unit`     |
| `make test-integration` | Ejecuta los tests de integración en `app.test.test_integration` |
| `make test-e2e`    | Ejecuta los tests end-to-end en `app.test.test_e2e`     |
