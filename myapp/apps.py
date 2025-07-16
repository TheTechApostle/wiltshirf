from django.apps import AppConfig
from .signals import *

class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'


# apps.py
def ready(self):
    import myapp.signals
