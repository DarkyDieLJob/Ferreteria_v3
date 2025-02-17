function agregarDevolucion(articulo_id, proveedor_id, item_id){
    var devolver = document.getElementById('devolver-devolver' + articulo_id).checked;
    var url = '/pedidos/agregar_devolucion/';
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'articulo_id': articulo_id,
        'proveedor_id': proveedor_id,
        'pedido_id': pedidoId,
        'item_id': item_id,
        'devolver': devolver,
        'csrfmiddlewaretoken': csrftoken
    };
    console.log(url, csrftoken, data);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        location.reload();
    });
}

function pedidoControlado(pedido_id){
    var url = '/pedidos/marcar_controlado/';
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'pedido_id': pedido_id,
        'csrfmiddlewaretoken': csrftoken
    };
    console.log(url, csrftoken, data);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error){
            alert(data.error);
            return;
        }
        if (data.status === 'ok'){
            window.location.href = urlHome;
        }
    });
}

function agregarAlStock(articulo_id, proveedor_id, item_id){
    var llego = document.getElementById('llego-llego' + articulo_id).checked;
    var cantidad = document.querySelector('.quantity-input[data-id="llego-' + articulo_id + '"]').value;
    var url = '/pedidos/agregar_al_stock/';
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'articulo_id': articulo_id,
        'proveedor_id': proveedor_id,
        'item_id': item_id,
        'llego': llego,
        'cantidad': cantidad,
        'csrfmiddlewaretoken': csrftoken
    };
    console.log(url, csrftoken, data);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        location.reload();
    });
}