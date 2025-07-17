import os
from celery import Celery

# Establece el settings module adecuado
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'orquestador.settings.base')

app = Celery('orquestador')

# Configura desde settings de Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre tareas automáticamente dentro de INSTALLED_APPS
app.autodiscover_tasks()

# Opcional: útil para debug
@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
