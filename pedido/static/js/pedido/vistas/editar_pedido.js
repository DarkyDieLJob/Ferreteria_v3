function actualizarLlego(id){
    var llego = document.getElementById('llego-' + id).checked;
    var url = '/pedidos/actualizar_llego/'+id;
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'id': id,
        'llego': llego,
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
        console.log(data);
    });
}

function actualizarCantidad(id, cantidad){
    var url = '/pedidos/actualizar_cantidad/'+id;
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'id': id,
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
        if (data.status === 'ok'){
            location.reload();
        }
    });
}

function agregarAlPedido(articulo_id, proveedor_id, item_id) {
    var url = '/pedidos/agregar_al_pedido/';
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'articulo_id': articulo_id,
        'item_id': item_id,
        'proveedor_id': proveedor_id,
        'cantidad': document.querySelector('[data-id="pedir-' + articulo_id + '"]').value,
        'pedido_id': pedidoId,
        'csrfmiddlewaretoken': csrftoken
    };
    console.log(data);
    //si data cantidad es <= 0, salta un alert y el check se setea en unquecked
    if (data.cantidad <= 0){
        alert('La cantidad debe ser mayor a 0');
        document.getElementById('agregar-al-pedido-' + articulo_id).checked = false;
        return;
    }

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
        if (data.status === 'ok'){
            location.reload();
        }
    });
}

function enviarPedido(pedido_id) {
    var url = '/pedidos/enviar_pedido/';
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'csrfmiddlewaretoken': csrftoken,
        'pedido_id': pedido_id
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
        //si {'status': 'error', 'message': 'El pedido no tiene artículos'} salta un alert
        if (data.status === 'ok'){
            //redirije a la vista de detalle pedido como ruta absoluta y no relativa
            window.location.href = urlEnviarPedido;
        }
        if (data.status === 'error'){
            alert(data.message);
        }
    });
}

function cancelarArticuloPedido(articulo_id, proveedor_id, item_id) {
    var url = '/pedidos/cancelar_articulo_pedido/';
    var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var data = {
        'articulo_id': articulo_id,
        'item_id': item_id,
        'proveedor_id': proveedor_id,
        'pedido_id': pedidoId,
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
        if (data.status === 'ok'){
            location.reload();
        }
    });
}