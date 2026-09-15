import os
from celery import Celery

# Le dice a Celery dónde está la configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('facturapro')

# Lee la configuración de Celery desde settings.py (las variables que empiezan con CELERY_)
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descubre tareas automáticamente en cada app instalada (busca archivos tasks.py)
app.autodiscover_tasks()