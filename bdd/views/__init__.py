# Importa las vistas que necesitas exponer para urls.py
from .main import (
    Inicio,
    Prueba,
    Imprimir,
    ListadoPedidos,
    ListarCarteles,
    BusquedaView,
    ItemsView,
)
from .ajax import (
    crear_modificar_lista_pedidos,
    seleccionar_proveedor,
    cambiar_cantidad_pedido,
    editar_item,
    agregar_articulo_a_carrito,
    carrito,
    consultar_carrito,
    usuarios_caja,
    eliminar_articulo_pedido,
    descargar_archivo,
    reportar_item,
    enviar_reporte,
)