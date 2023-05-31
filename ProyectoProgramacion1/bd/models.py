from django.db import models

# Create your models here.
class LoginAdmin(models.Model):
    Nombre = models.CharField(max_length=200)
    Password = models.CharField(max_length=64)

class Intentos(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    intentos = models.PositiveIntegerField()
    fecha_ultimo_intento = models.DateTimeField()


class OTP(models.Model):
    id_telegram = models.CharField(max_length = 64)
    otp = models.CharField(max_length=10)
    tiempo_exp = models.DateTimeField()

class RegistroAdmin(models.Model):
    nombre = models.CharField(max_length = 200)
    correo = models.CharField(max_length = 200)
    id_telegram = models.CharField(max_length = 64)
    contraseña = models.CharField(max_length = 64)
    ip_server = models.CharField(max_length = 40)


