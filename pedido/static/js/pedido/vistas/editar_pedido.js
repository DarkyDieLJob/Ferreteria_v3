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
        credentials: 'same-origin',
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
        credentials: 'same-origin',
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
        credentials: 'same-origin',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        location.reload();
    });
}

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
        credentials: 'same-origin',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
}

// Delegación de eventos para inputs y botones (sin inline handlers)
document.addEventListener('DOMContentLoaded', function () {
    // Debounce por articuloId para evitar múltiples POST rápidos en Chrome
    const qtyDebounce = {};
    // Cambio de cantidad en inputs (Artículos en el pedido)
    document.body.addEventListener('change', function (e) {
        const target = e.target;
        if (target && target.classList && target.classList.contains('quantity-input')) {
            const articuloId = target.getAttribute('data-articulo-id');
            if (articuloId) {
                clearTimeout(qtyDebounce[articuloId]);
                qtyDebounce[articuloId] = setTimeout(function () {
                    actualizarCantidad(articuloId, target.value);
                }, 250);
            }
        }
    });

    // Click en botón Cancelar (Artículos en el pedido)
    document.body.addEventListener('click', function (e) {
        const btn = e.target.closest('.js-cancelar');
        if (btn) {
            if (btn.dataset.busy === '1') return;
            btn.dataset.busy = '1';
            const articuloId = btn.getAttribute('data-articulo-id');
            const proveedorId = btn.getAttribute('data-proveedor-id');
            const itemId = btn.getAttribute('data-item-id');
            if (articuloId && proveedorId && itemId) {
                cancelarArticuloPedido(articuloId, proveedorId, itemId);
            }
        }
    });

    // Click en botón Enviar pedido
    document.body.addEventListener('click', function (e) {
        const btnEnviar = e.target.closest('.js-enviar-pedido');
        if (btnEnviar) {
            e.preventDefault();
            if (btnEnviar.dataset.busy === '1') return;
            btnEnviar.dataset.busy = '1';
            enviarPedido(pedidoId);
        }
    });

    // Click en botón "Agregar al pedido" (Artículos faltantes)
    document.body.addEventListener('click', function (e) {
        const btn = e.target.closest('.js-agregar-al-pedido');
        if (btn) {
            if (btn.dataset.busy === '1') return;
            btn.dataset.busy = '1';
            const articuloId = btn.getAttribute('data-articulo-id');
            const proveedorId = btn.getAttribute('data-proveedor-id');
            const itemId = btn.getAttribute('data-item-id');
            if (articuloId && proveedorId && itemId) {
                agregarAlPedido(articuloId, proveedorId, itemId);
            }
        }
    });
});

// Flag por artículo para evitar solicitudes concurrentes que provoquen duplicados o estados inconsistentes
const _actualizarBusy = {};

function actualizarCantidad(id, cantidad){
    if (_actualizarBusy[id]) {
        return;
    }
    _actualizarBusy[id] = true;
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
        credentials: 'same-origin',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok'){
            // UI ya refleja el valor ingresado, no recargar
        }
    })
    .catch(err => {
        console.error('Error actualizando cantidad', err);
    })
    .finally(() => {
        _actualizarBusy[id] = false;
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
    // si data.cantidad es <= 0, salta un alert y el check se setea en unchecked
    if (data.cantidad <= 0){
        alert('La cantidad debe ser mayor a 0');
        const chk = document.getElementById('agregar-al-pedido-' + articulo_id);
        if (chk) chk.checked = false;
        return;
    }

    console.log(url, csrftoken, data);
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        credentials: 'same-origin',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok'){
            // mantener sin recargar
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
        credentials: 'same-origin',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // si {'status': 'error', 'message': 'El pedido no tiene artículos'} salta un alert
        if (data.status === 'ok'){
            // redirige a la vista de detalle pedido como ruta absoluta y no relativa
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
        credentials: 'same-origin',
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'ok'){
            // mantener sin recargar
        }
    });
}