from django.shortcuts import render, redirect
from .forms import RegisterForm, VerificacionForm
from .models import Verificacion
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.db import IntegrityError
from django.contrib.auth.forms import AuthenticationForm
from django.views.generic import UpdateView, ListView
from django.urls import reverse_lazy



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


#listado de usuarios
class ClaveLista(ListView):
    model = Verificacion
    template_name = 'pagina/lista_clave.html'
    

def band_update(request, id):
    band = Band.objects.get(id=id)
    if request.method == "POST":
        form = BandForm(request.POST, instance=band)
        if form.is_valid():
            form.save()
            return redirect("band_detail", band.id)
    else:
        form = BandForm(instance=band)
    return render(request, "listings/band_update.html", {"form": form})


# # vamos hacer la parte de editar la clave.
# # buscar updateview django form
# class ActualizarClave(UpdateView):
#     model = Verificacion
#     form_class = VerificacionForm
#     template_name = 'pagina/actualizacion_clave.html'
#     success_url = reverse_lazy('inicio')