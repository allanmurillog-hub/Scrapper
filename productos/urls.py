from django.urls import path
from . import views

app_name = 'productos'
urlpatterns = [
    path(
        '<int:producto_id>/',
        views.detalle,
        name='producto_detalle'),
    path('formulario', views.formulario, name='formulario'),
    path('<int:producto_id>/',
         views.detalle,
         name='detalle'),  # detalle
]
