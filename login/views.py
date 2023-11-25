from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegisterForm, VerificacionForm, VerificacionClave
from .models import Verificacion, RegistroAcceso
from .decorators import groups_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.contrib.auth.models import Group, User
from django.contrib import messages

# Create your views here.

def inicio(request):
    user = request.user
    nombre_grupo = None
    if user.is_authenticated:
        group = Group.objects.filter(user=user).first()
        if group:
            nombre_grupo = group.name
    return render(request, 'pagina/pagina_inicio.html', {'nombre_grupo':nombre_grupo})
    


# registro de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                return redirect('inicio')
            except IntegrityError:
                messages.error(request, 'Este usuario ya existe.')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterForm()
    return render(request, 'pagina/registro.html', {'form': form})

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
            contra = form.cleaned_data.get('password')
            try:
                usuario = authenticate(username=nombre_usuario, password=contra)
                if usuario is not None:
                    login(request, usuario)
                    return redirect('inicio')
                else:
                    messages.error(request, 'Credenciales no válidas')
            except Exception as e:
                messages.error(request, f'Error de autenticación: {e}')
        else:
            messages.error(request, 'Credenciales no válidas')
        
    form = AuthenticationForm()
    return render(request, 'pagina/login.html', {'form': form})


# este codigo es propenso a mejoras y a modificaciones, pero por lo pronto sirve como esta.
def crear_clave_puerta(request):
    # Verifica si el usuario ya tiene una clave de puerta
    if Verificacion.objects.filter(usuario=request.user).exists():
        messages.warning(request, 'Ya has creado una clave de puerta.')
        return redirect('inicio')
    
    if request.method == 'GET':
        return render(request, 'pagina/clave_puerta.html', {'form': VerificacionForm()})
    else:
        try:
            form = VerificacionForm(request.POST)
            if form.is_valid():
                clave_puerta = form.save(commit=False)
                clave_puerta.usuario = request.user
                clave_puerta.save()

                return redirect('inicio')
            else:
                messages.error(request, 'Por favor, proporcione datos válidos')
        except ValueError as e:
            messages.error(request, f'Error al crear clave de puerta: {str(e)}')

        return render(request, 'pagina/clave_puerta.html', {'form': VerificacionForm()})



# lista de las personas que tienen clave activa.
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



# validacion de ingreso al laboratorio.
def verificacion_clave(request):
    if request.method == 'POST':
        form = VerificacionClave(request.POST)
        if form.is_valid():
            valor = form.cleaned_data['clave']
            
            existe_db_clave = Verificacion.objects.filter(contrasena=valor).exists()
            existe_db_rfid = Verificacion.objects.filter(rfid=valor).exists()
            
            if existe_db_clave:
                persona = Verificacion.objects.filter(contrasena=valor).first()
            elif existe_db_rfid:
                persona = Verificacion.objects.filter(rfid=valor).first()
            else:
                return render(request, 'pagina/verificacion_clave.html', {
                    'form':form,
                    'error':'Valor no válido',
                })
            
            # Verificar si lab_vision o lab_robotica están activados en la persona
            if not (persona.lab_vision or persona.lab_robotica):
                return render(request, 'pagina/verificacion_clave.html', {
                    'form':form,
                    'error':'Usuario no autorizado para el acceso.',
                })

            # Registrar el acceso
            registro = RegistroAcceso(verificacion=persona)
            registro.save()
            datos = {
                'form': form,
                'validacion': 'Valor válido',
                'persona': persona
            }
            return render(request, 'pagina/validacion_clave.html', datos)
    else:
        form = VerificacionClave()
        return render(request, 'pagina/verificacion_clave.html', {'form': form})



# lista de las personas que entran.
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




# actualizacion de datos del usuario logeado
def actualizar_datos(request):
    usuario = Verificacion.objects.get(usuario=request.user)
    
    if request.method == 'POST':
        form = VerificacionForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            return redirect('inicio')
    else:
        form = VerificacionForm(instance=usuario)
    return render(request, 'pagina/actualizar_datos.html', {'form':form})





@groups_required(['profesor',])
def prueba_decorador(request):
    user = request.user
    nombre_grupo = None
    if user.is_authenticated:
        group = Group.objects.filter(user=user).first()
        if group:
            nombre_grupo = group.name
    return render(request, 'pagina/pagina_inicio.html', {'nombre_grupo':nombre_grupo})


def permisos_usuarios(request):
    if request.method == 'POST':
        estudiante = request.POST.get('estudiante')
        delegado = request.POST.get('delegado')
        profesor = request.POST.get('profesor')
        
        if estudiante:
            user = User.objects.filter(id=estudiante).first()
            try:
                pass
                # eliminar de los grupos en lo que este
                for group in user.groups.all():
                    user.groups.remove(group)
                # agregarlo al grupo de estudiantes
                grupo_estudiante = Group.objects.get(name='estudiante')
                user.groups.add(grupo_estudiante)
                # Agregar mensaje de éxito
                messages.success(request, f'Usuario fue movido al grupo de estudiantes exitosamente.')
            except:
                pass
            
        if delegado:
            user = User.objects.filter(id=delegado).first()
            try:
                pass
                # eliminar de los grupos en lo que este
                for group in user.groups.all():
                    user.groups.remove(group)
                # agregarlo al grupo de estudiantes
                grupo_delegado = Group.objects.get(name='delegado')
                user.groups.add(grupo_delegado)
                messages.success(request, f'Usuario fue movido al grupo de delegado exitosamente.')
            except:
                pass
            
            
        if profesor:
            user = User.objects.filter(id=profesor).first()
            try:
                pass
                # eliminar de los grupos en lo que este
                for group in user.groups.all():
                    user.groups.remove(group)
                # agregarlo al grupo de estudiantes
                grupo_profesor = Group.objects.get(name='profesor')
                user.groups.add(grupo_profesor)
                messages.success(request, f'Usuario fue movido al grupo de profesor exitosamente.')
            except:
                pass
        
    registros = Verificacion.objects.all()
    
    paginacion = Paginator(Verificacion.objects.all().order_by('-id'), 10)
    page = request.GET.get('page')
    registro_acceso = paginacion.get_page(page)
    # num_paginas = 'a' * registro_acceso.paginator.num_pages
    num_paginas = registro_acceso.paginator.page_range
    
    parametros = {'registros':registros,
                    'paginacion':registro_acceso,
                    'num_paginas':num_paginas}
    return render(request, 'pagina/modificar_permisos.html', parametros)
    


def permisos_profesor(request):
    user = request.user
    if user.is_staff:
        if request.method == 'POST':
            estudiante = request.POST.get('estudiante')
            delegado = request.POST.get('delegado')
            profesor = request.POST.get('profesor')
            
            if estudiante:
                user = User.objects.filter(id=estudiante).first()
                try:
                    pass
                    # eliminar de los grupos en lo que este
                    for group in user.groups.all():
                        user.groups.remove(group)
                    # agregarlo al grupo de estudiantes
                    grupo_estudiante = Group.objects.get(name='estudiante')
                    user.groups.add(grupo_estudiante)
                    # Agregar mensaje de éxito
                    messages.success(request, f'Usuario fue movido al grupo de estudiantes exitosamente.')
                except:
                    pass
                
            if delegado:
                user = User.objects.filter(id=delegado).first()
                try:
                    pass
                    # eliminar de los grupos en lo que este
                    for group in user.groups.all():
                        user.groups.remove(group)
                    # agregarlo al grupo de estudiantes
                    grupo_delegado = Group.objects.get(name='delegado')
                    user.groups.add(grupo_delegado)
                    messages.success(request, f'Usuario fue movido al grupo de delegado exitosamente.')
                except:
                    pass
                
                
            if profesor:
                user = User.objects.filter(id=profesor).first()
                try:
                    pass
                    # eliminar de los grupos en lo que este
                    for group in user.groups.all():
                        user.groups.remove(group)
                    # agregarlo al grupo de estudiantes
                    grupo_profesor = Group.objects.get(name='profesor')
                    user.groups.add(grupo_profesor)
                    messages.success(request, f'Usuario fue movido al grupo de profesor exitosamente.')
                except:
                    pass
            
        registros = Verificacion.objects.all()
        
        paginacion = Paginator(Verificacion.objects.all().order_by('-id'), 10)
        page = request.GET.get('page')
        registro_acceso = paginacion.get_page(page)
        # num_paginas = 'a' * registro_acceso.paginator.num_pages
        num_paginas = registro_acceso.paginator.page_range
        
        parametros = {'registros':registros,
                        'paginacion':registro_acceso,
                        'num_paginas':num_paginas}
        return render(request, 'pagina/modificar_permisos_profesor.html', parametros)
    else:
        return render(request, 'pagina/acceso_denegado.html')