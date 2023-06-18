from django.db import models
from datetime import datetime

class LoginAdmin(models.Model):
    Nombre = models.CharField(max_length=200)
    Password = models.CharField(max_length=106)


class Intentos(models.Model):
    ip = models.GenericIPAddressField(primary_key=True)
    intentos = models.PositiveIntegerField()
    fecha_ultimo_intento = models.DateTimeField()


class OTP(models.Model):
    id_telegram = models.CharField(max_length = 64)
    otp = models.CharField(max_length=10)
    tiempo_exp = models.DateTimeField(default = datetime.now)

class RegistroAdmin(models.Model):
    nombre = models.CharField(max_length=200)
    correo = models.CharField(max_length=200)
    id_telegram = models.CharField(max_length=64)
    contraseña = models.CharField(max_length=106)

class Servidores(models.Model):
    ip = models.CharField(max_length=40)
    server_name = models.CharField(max_length=200)
    ram = models.CharField(max_length=10, default='0')
    cpu = models.CharField(max_length=10, default='0')
    disco = models.CharField(max_length=10, default='10')

class Asociado(models.Model):
    registro_admin = models.ForeignKey(RegistroAdmin, null=True, blank=True, on_delete=models.CASCADE)
    servidor = models.ForeignKey(Servidores, on_delete=models.CASCADE)
    nombre_registro_admin = models.CharField(max_length=200, blank=True)
    ip_servidor = models.CharField(max_length=40, blank=True)

