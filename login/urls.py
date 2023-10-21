from django.urls import path
from . import views


urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('home/', views.inicio, name='inicio'),
    path('registro/', views.registro, name='registro'),
    path('cerrar_sesion', views.cerrar_sesion, name='cerrar_sesion'),
    path('iniciar_sesion', views.logear, name='iniciar_sesion'),
    path('clave_puerta', views.crear_clave_puerta, name='clave_puerta'),
    path('lista_perta', views.ClaveLista.as_view(), name='lista_puerta'),
    # path('clave_puerta/editar/<int:pk>/', views.ActualizarClave.as_view(), name='actualizar_clave'),
]