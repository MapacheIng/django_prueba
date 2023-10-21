from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Verificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre_completo = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    telefono = models.CharField(max_length=10) # por que un numero tiene solo 10 digitos
    programa_academico = models.CharField(max_length=255)
    contrasena = models.CharField(max_length=10, unique=True)
    rfid = models.CharField(max_length=50, null=True, blank=True)
    lab_vision = models.BooleanField(default=False)
    lab_robotica = models.BooleanField(default=False)
    
    def __str__(self):
        return f'{self.usuario.username} \n {self.nombre_completo} \n {self.programa_academico}'