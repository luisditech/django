![Python](https://img.shields.io/badge/Python-3.13-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-success)
![License](https://img.shields.io/badge/license-MIT-green.svg)
---
[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=sysazure_Orquestador&token=132b96f3e735260ee6446906a6a5448201ed70b9)](https://sonarcloud.io/summary/new_code?id=sysazure_Orquestador)
---
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=sysazure_Orquestador&metric=alert_status&token=132b96f3e735260ee6446906a6a5448201ed70b9)](https://sonarcloud.io/summary/new_code?id=sysazure_Orquestador)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=sysazure_Orquestador&metric=bugs&token=132b96f3e735260ee6446906a6a5448201ed70b9)](https://sonarcloud.io/summary/new_code?id=sysazure_Orquestador)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=sysazure_Orquestador&metric=code_smells&token=132b96f3e735260ee6446906a6a5448201ed70b9)](https://sonarcloud.io/summary/new_code?id=sysazure_Orquestador)
[![Coverage](https://sonarcloud.io/api/project_badges/measure?project=sysazure_Orquestador&metric=coverage&token=132b96f3e735260ee6446906a6a5448201ed70b9)](https://sonarcloud.io/summary/new_code?id=sysazure_Orquestador)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=sysazure_Orquestador&metric=duplicated_lines_density&token=132b96f3e735260ee6446906a6a5448201ed70b9)](https://sonarcloud.io/summary/new_code?id=sysazure_Orquestador)

# 🐍 Proyecto Django - Base

Este es un proyecto base construido con [Django](https://www.djangoproject.com/) para desarrollo web en Python. Está organizado para permitir una arquitectura escalable, modular y lista para ambientes de desarrollo, staging y producción.

---

## 🚀 Requisitos

- Python 3.8+
- pip
- virtualenv (opcional, pero recomendado)
- PostgreSQL (o el motor de base de datos que uses)

---

## ⚙️ Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/tu_proyecto.git
cd tu_proyecto
```

### 2. Crear y activar entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Crear archivo `.env`

Crea un archivo `.env` en la raíz del proyecto y define tus variables:

```env
DEBUG=True
SECRET_KEY=tu_clave_secreta
DB_NAME=nombre_bd
DB_USER=usuario
DB_PASSWORD=contraseña
ALLOWED_HOSTS=localhost,127.0.0.1
```

> Asegúrate de tener `.env` en tu `.gitignore`.

---

## 🗃️ Migraciones de base de datos

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🧪 Ejecutar servidor de desarrollo

```bash
python manage.py runserver
```

---

## 🧰 Comandos útiles

- Crear superusuario:

```bash
python manage.py createsuperuser
```

- Ejecutar pruebas:

```bash
python manage.py test
```

- Generar requerimientos:

```bash
pip freeze > requirements.txt
```

---

## 📄 Licencia

Este proyecto está bajo la licencia MIT.


