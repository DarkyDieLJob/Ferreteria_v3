function agregarDevolucion(articulo_id, proveedor_id, item_id, checkboxEl){
    if (!checkboxEl) {
        checkboxEl = document.getElementById('devolver-devolver' + articulo_id);
    }
    if (!checkboxEl) return;

    if (checkboxEl.dataset.loading === '1') return; // evitar dobles envíos
    checkboxEl.dataset.loading = '1';
    checkboxEl.disabled = true;

    var devolver = checkboxEl.checked;
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
    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(resp => {
        // Remover la fila del DOM al confirmar devolución para evitar estados residuales
        var row = checkboxEl.closest('tr');
        if (row) row.remove();
    })
    .catch(() => {
        // En caso de error, re-habilitar y revertir estado visual
        checkboxEl.checked = false;
    })
    .finally(() => {
        checkboxEl.disabled = false;
        delete checkboxEl.dataset.loading;
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
            e.preventDefault();
            const articuloId = devolver.getAttribute('data-articulo-id');
            const proveedorId = devolver.getAttribute('data-proveedor-id');
            const itemId = devolver.getAttribute('data-item-id');
            if (articuloId && proveedorId && itemId) {
                agregarDevolucion(articuloId, proveedorId, itemId, devolver);
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
        // Feedback inmediato: eliminar la fila del artículo controlado sin recargar
        if (data && (data.status === 'ok' || !data.error)) {
            const qtyInput = document.querySelector(`.quantity-input[data-id="llego-${articulo_id}"]`);
            const row = qtyInput ? qtyInput.closest('tr') : null;
            if (row) row.remove();
        }
    });
}