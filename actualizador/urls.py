from django.urls import path

from .views import Actualizar, Reckup, ActualizarAhora, MarcarDescargado

urlpatterns = [
    path("actualizar/", Actualizar.as_view(), name="actualizar"),
    path("reckup/", Reckup.as_view(), name="reckup"),
    path("actualizar/ahora/", ActualizarAhora.as_view(), name="actualizar_ahora"),
    path(
        "actualizador/marcar_descargado/",
        MarcarDescargado.as_view(),
        name="marcar_descargado",
    ),
]
