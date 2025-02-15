function eliminarDevolucion(articulo_id, proveedor_id, item_id){
    var devolver = document.getElementById('devolver-devolver' + articulo_id).checked;
    var url = '/pedidos/eliminar_devolucion/';
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'devolucion_id': articulo_id,
        'csrfmiddlewaretoken': csrftoken
    };
    $.post(url, data, function(response){
        if (response.status == 'ok'){
            location.reload();
        } else {
            alert('Error al eliminar la devolucion');
        }
    });
}