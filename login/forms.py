from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Verificacion

class RegisterForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        

class VerificacionForm(forms.ModelForm):
    class Meta:
        model = Verificacion
        fields = ['nombre_completo', 'email', 'telefono', 'programa_academico', 'contrasena', 'rfid', 'lab_vision', 'lab_robotica']
        widgets = {
            'nombre_completo': forms.TextInput(attrs={'placeholder': 'Nombre completo'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Correo electrónico'}),
            'telefono': forms.TextInput(attrs={'placeholder': 'Teléfono', 'maxlength': '10'}),
            'contrasena': forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
            'rfid': forms.TextInput(attrs={'placeholder': 'RFID', 'maxlength': '10'}),
            'lab_vision': forms.CheckboxInput(),
            'lab_robotica': forms.CheckboxInput(),
        }

