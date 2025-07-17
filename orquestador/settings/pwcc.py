from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]  # o el dominio de BuenCapital

# Puedes sobreescribir lo que quieras del base
# por ejemplo, un logo personalizado, idioma, email, etc.
INSTALLED_APPS += [
        'apps.pwcc',
]