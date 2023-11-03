from django.urls import path
from . import views


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('home/', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('cerrar_sesion', views.cerrar_sesion, name='cerrar_sesion'),
    path('iniciar_sesion', views.logear, name='iniciar_sesion'),
    path('clave_puerta', views.crear_clave_puerta, name='clave_puerta'),
    path('lista_puerta', views.lista_usuarios, name='lista_puerta'),
    path('actualizacion_clave/<int:id>', views.actualizar_clave, name='actualizar_clave'),
    path('verificacion_clave/', views.verificacion_clave, name='verificacion_clave'),
    path('verificacion', views.lista_registro, name='verificacion'),
]