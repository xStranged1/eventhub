# Makefile tiene como objetivo facilitar la gestión de tareas comunes en el proyecto Django.
# Se asocicia un comando, o una serie de comandos a un comando personalizado.
# Se pueden ejecutar comandos específicos con `make <target>`

# Instalar dependencias de Python
install:
	pip install -r requirements.txt

# Instalar dependencias de Playwright
play:
	playwright install

# Aplicar migraciones de la base de datos
migrate:
	python manage.py migrate

# Crear un superusuario
superuser:
	python manage.py createsuperuser

# Cargar datos iniciales
loaddata:
	python manage.py loaddata fixtures/events.json

# Iniciar el servidor de desarrollo
run:
	python manage.py runserver

# Ejecutar todos los tests
test:
	python manage.py test app.test

# Tests unitarios
unit:
	python manage.py test app.test.test_unit

# Tests de integración
int:
	python manage.py test app.test.test_integration

# Tests end-to-end
e2e:
	python manage.py test app.test.test_e2e
