from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

# Si querés agregar más apps específicas para esta instancia, lo hacés acá:
INSTALLED_APPS += [
    'apps.tropicfeel'
]