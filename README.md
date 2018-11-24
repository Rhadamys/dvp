# Depurador visual para Python orientado al apoyo pedagógico

Este proyecto se realiza en el marco del desarrollo del trabajo de titulación para obtener el título de Ingeniero de Ejecución en Computación e Informática en la Universidad de Santiago de Chile. 

> Esta aplicación se encuentra publicada en [https://rhadamys.pythonanywhere.com](https://rhadamys.pythonanywhere.com)

## Propósito
El propósito de esta herramienta es apoyar a los estudiantes de cursos introductorios de programación en el proceso de escritura de sus códigos fuentes en el lenguaje de programación Python para que tengan un mejor entendimiento del funcionamiento de determinadas estructuras como ciclos `for` y `while` y puedan, de esta forma, desarrollar código con menos errores y en menor tiempo.

## Build

### Django
``` bash
# crear entorno virtual
python3 -m venv venv

# activar entorno virtual
. venv/bin/activate

# instalar dependencias
pip install -r requirements.txt

# iniciar servidor
python manage.py runserver
```

### Node
``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```
