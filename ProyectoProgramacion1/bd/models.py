from django.db import models

# Create your models here.
class LoginAdmin(models.Model):
    Nombre = models.CharField(max_length=200)
    Password = models.CharField(max_length=64)

class Intentos(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    intentos = models.PositiveIntegerField()
    fecha_ultimo_intento = models.DateTimeField()
