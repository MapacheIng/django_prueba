from django.shortcuts import render, redirect
from .forms import RegisterForm, VerificacionForm, VerificacionClave
from .models import Verificacion, RegistroAcceso
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import ListView
from django.core.paginator import Paginator

# Create your views here.
def inicio(request):
    return render(request, 'pagina/pagina_inicio.html')


# registro de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            #un try para manejo de errores por si hay repetidos
            try:
                user = form.save()
                login(request, user)
                return redirect('inicio')
            except IntegrityError:
                return render(request, 'pagina/registro.html', {
                    'form': form,
                    'error': 'este usuario ya existe'
                })
        else:
            #manejo de errores cuando el formulario no es valido
            for msg in form.error_messages:
                messages.error(request, form.error_messages[msg])
            return render(request, 'pagina/registro.html', {'form':form})
    else:
        # cuando el metodo no es post (osea get) no crear el formulario vacio para luego mostrarlo
        form = RegisterForm()
    
    return render(request, 'pagina/registro.html', {'form':form})

# cerrado de sesion
def cerrar_sesion(request):
    # se importa la funcion para quitar el loggin
    logout(request)
    return redirect('inicio')

def logear(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            nombre_usuario = form.cleaned_data.get('username')
            contra=form.cleaned_data.get('password')
            usuario = authenticate(username=nombre_usuario, password=contra)
            if usuario is not None:
                login(request, usuario)
                return redirect('inicio')
            else:
                messages.error(request, 'Usuario no valido')
        else:
            messages.error(request, 'informacion incorrecta')
        
        
    form=AuthenticationForm()
    return render(request, 'pagina/login.html', {'form':form})


# este codigo es propenso a mejoras y a modificaciones, pero por lo pronto sirve como esta.
def crear_clave_puerta(request):
    if request.method == 'GET':
        return render(request, 'pagina/clave_puerta.html', {'form': VerificacionForm()})
    else:
        try:
            form = VerificacionForm(request.POST)
            clave_perta = form.save(commit=False)
            clave_perta.usuario = request.user
            # hacer mostrar mensaje 
            clave_perta.save()
            return redirect('inicio')
        except ValueError:
            return render(request, 'pagina/clave_puerta.html', {
                'form': VerificacionForm(),
                'error':'Please provide valida data'
            })


# #listado de usuarios
# class ClaveLista(ListView):
#     model = Verificacion
#     template_name = 'pagina/lista_clave.html'


def lista_usuarios(request):
    registros = Verificacion.objects.all()
    
    # configuracion de la paginacion
    paginacion = Paginator(Verificacion.objects.all().order_by('-id'), 10)
    page = request.GET.get('page')
    registro_acceso = paginacion.get_page(page)
    # num_paginas = 'a' * registro_acceso.paginator.num_pages
    num_paginas = registro_acceso.paginator.page_range
    
    parametros = {'registros':registros,
                    'paginacion':registro_acceso,
                    'num_paginas':num_paginas}
    return render(request, 'pagina/lista_clave.html', parametros)


# actualizacion de datos
def actualizar_clave(request, id):
    clave = Verificacion.objects.get(id=id)
    if request.method == 'POST':
        form = VerificacionForm(request.POST, instance=clave)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = VerificacionForm(instance=clave)
    return render(request, 'pagina/actualizacion_clave.html', {'form':form})

def verificacion_clave(request):
    if request.method == 'POST':
        form = VerificacionClave(request.POST)
        if form.is_valid():
            valor = form.cleaned_data['clave']
            existe_db = Verificacion.objects.filter(contrasena=valor).exists()
            if existe_db:
                persona = Verificacion.objects.filter(contrasena=valor).first()
                registro = RegistroAcceso(verificacion=persona)
                registro.save()
                datos = {
                    'form':form,
                    'validacion': 'Valor valido',
                    'persona':persona
                }
                return render(request, 'pagina/validacion_clave.html', datos)
            else:
                return render(request, 'pagina/verificacion_clave.html', {
                    'form':form,
                    'error':'Valor no validos',
                })
    else:
        form = VerificacionClave()
    
    return render(request, 'pagina/verificacion_clave.html', {'form':form})



def lista_registro(request):
    registros = RegistroAcceso.objects.all()
    
    # configuracion de la paginacion
    paginacion = Paginator(RegistroAcceso.objects.all().order_by('-id'), 10)
    page = request.GET.get('page')
    registro_acceso = paginacion.get_page(page)
    # num_paginas = 'a' * registro_acceso.paginator.num_pages
    num_paginas = registro_acceso.paginator.page_range
    
    parametros = {'registros':registros,
                    'paginacion':registro_acceso,
                    'num_paginas':num_paginas}
    return render(request, 'pagina/verificacion.html', parametros)