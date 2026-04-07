document.addEventListener('DOMContentLoaded', function() {
    console.debug('Proveedor ID: ' + proveedorId);
    console.debug('Inicializando Select2');

    $('#id_item').select2({
        ajax: {
            url: autocompleteUrl,
            dataType: 'json',
            delay: 250,
            data: function (params) {
                return {
                    q: params.term,  // término de búsqueda
                    page: params.page,
                    proveedor_id: proveedorId
                };
            },
            processResults: function (data, params) {
                params.page = params.page || 1;
                console.debug('Autocomplete items', data.items);
                return {
                    results: data.items,
                    pagination: {
                        more: (params.page * 30) < data.total_count
                    }
                };
            },
            cache: true
        },
        minimumInputLength: 3
    });
});
