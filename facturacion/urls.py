from django.urls import path
from facturacion.views import obtener_metodos_pago, procesar_transaccion, obtener_cliente, agregar_articulo_sin_registro
from facturacion.views import eliminar_articulo, eliminar_articulo_sin_registro, actualizar_cantidad_articulo
from facturacion.views import actualizar_cantidad_articulo_sin_registro, vista_cierre_z
from facturacion.views import Facturacion, CierreZVieW, Clientes, FacturacionMensual

urlpatterns = [
    path('obtener_metodos_pago/', obtener_metodos_pago, name='obtener_metodos_pago'),
    path('obtener_cliente/', obtener_cliente, name='obtener_cliente'),
    path('procesar_transaccion/', procesar_transaccion, name='procesar_transaccion'),
    path('agregar_articulo_sin_registro/', agregar_articulo_sin_registro, name='agregar_articulo_sin_registro'),
    path('eliminar_articulo/', eliminar_articulo, name='eliminar_articulo'),
    path('eliminar_articulo_sin_registro/', eliminar_articulo_sin_registro, name='eliminar_articulo_sin_registro'),
    path('actualizar_cantidad_articulo/', actualizar_cantidad_articulo, name='actualizar_cantidad_articulo'),
    path('actualizar_cantidad_articulo_sin_registro/', actualizar_cantidad_articulo_sin_registro, name='actualizar_cantidad_articulo_sin_registro'),
    path('vista_cierre_z/', CierreZVieW.as_view(), name='cierres-fiscales'),
    path('facturacion/clientes/', Clientes.as_view(), name='clientes'),
    path('facturacion/', Facturacion.as_view(), name='facturacion'),
    path('facturacion/mensual/', FacturacionMensual.as_view(), name='facturacion-mensual'),
    path('facturacion/<int:year>/<int:month>/<int:day>/', Facturacion.as_view(), name='facturacion_fecha'),
]