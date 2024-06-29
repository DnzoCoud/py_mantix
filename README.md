# Proyecto Mantix
Esto es un proyecto basado en Django. A continuacion se detallan los paso a paso para su instalacion

## Requisitos Previos
Asegurate de tener instlaado las siguientes versiones de programas en tu sistema
- Python (version 3.12.3 o superior)
- pip (gestion de paquetes de python)
- virtualenv (para crear entornos virtuales)

## Instrucciones de instalacion
### 1. Clonar el repositorio

Clona este repositorio en tu maquina local usando git:

```bash
git clone https://github.com/DnzoCode/MantixBack.git
cd MantixBack
```

### 2. Crear el entorno virtual
Crea un entorno virtual para aislar las dependencias del proyecto:
En Windows:

```bash
python -m venv venv
```

En macOS y Linux:
```bash
python3 -m venv venv
```
### 3. Activar el entorno virtual
Activa el entorno virtual para trabajar dentro de él:

En Windows:
```bash
venv\Scripts\activate
```

En macOS y Linux:
```bash
source venv/bin/activate
```

Cuando el entorno virtual esté activo, verás el nombre del entorno en la línea de comandos.

### 4. Instalar las dependencias
Instala las dependencias del proyecto desde el archivo requirements.txt dentro de la carpeta mantix:

```bash
cd mantix
```

```bash
pip install -r requirements.txt
```

### 6. Copiar el .env en la carpeta mantix
Una vezx hechos los pasos anteriores yo les proporcionare un archivo .env para que lo pegen en la carpeta donde se encuentran actualmente

### 5. Ejecutar el servidor de desarrollo
Inicia el servidor de desarrollo de Django:
```bash
python manage.py runserver
```
### 6. Licencia y Uso
Por favor, tener en cuenta que este código está sujeto a licencias internas de la empresa donde fue desplegado. Yo, y solo yo como desarrollador, tengo todos los derechos sobre este proyecto. Cualquier uso o copia del mismo sin autorización será legalmente sancionado.