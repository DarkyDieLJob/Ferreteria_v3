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

// Delegación de eventos (sin inline handlers en templates)
document.addEventListener('DOMContentLoaded', function () {
    document.body.addEventListener('click', function (e) {
        const llego = e.target.closest('.js-llego');
        if (llego) {
            const articuloId = llego.getAttribute('data-articulo-id');
            const proveedorId = llego.getAttribute('data-proveedor-id');
            const itemId = llego.getAttribute('data-item-id');
            if (articuloId && proveedorId && itemId) {
                agregarAlStock(articuloId, proveedorId, itemId);
            }
            return;
        }

        const devolver = e.target.closest('.js-devolver');
        if (devolver) {
            const articuloId = devolver.getAttribute('data-articulo-id');
            const proveedorId = devolver.getAttribute('data-proveedor-id');
            const itemId = devolver.getAttribute('data-item-id');
            if (articuloId && proveedorId && itemId) {
                agregarDevolucion(articuloId, proveedorId, itemId);
            }
        }
    });
});

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