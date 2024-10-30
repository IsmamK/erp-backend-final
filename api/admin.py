from django.contrib import admin
from .models import *
# Register your models here.
from django.apps import apps

app_models = apps.get_models()

for model in app_models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
