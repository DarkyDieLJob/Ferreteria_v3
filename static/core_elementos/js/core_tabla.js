let csrftoken = Cookies.get('csrftoken');

// Crear un nuevo elemento div para el modal
const modal = document.createElement('div');
modal.style.display = 'none'; // Inicialmente, el modal está oculto
modal.style.position = 'fixed';
modal.style.zIndex = '1'; // El modal debe estar encima de todo lo demás
modal.style.left = '0';
modal.style.top = '0';
modal.style.width = '100%'; // El modal debe cubrir toda la pantalla
modal.style.height = '100%';
modal.style.overflow = 'auto'; // Habilitar el desplazamiento si el contenido es demasiado grande
modal.style.backgroundColor = 'rgba(0,0,0,0.4)'; // Fondo semitransparente

// Crear un nuevo elemento div para el contenido del modal
const modalContent = document.createElement('div');
modalContent.style.backgroundColor = '#fefefe';
modalContent.style.margin = '15% auto'; // Centrar el modal verticalmente
modalContent.style.padding = '20px';
modalContent.style.border = '1px solid #888';
modalContent.style.width = '80%'; // El contenido del modal debe ocupar el 80% de la pantalla

// Agregar el contenido del modal al modal
modal.appendChild(modalContent);

// Agregar el modal al cuerpo del documento
document.body.appendChild(modal);

function crearElementoPrecio(titulo, valor) {
    return `
        <div class="precio">
            <div><h5>${titulo}</h5></div>
            <div id="${titulo.replace(' ', '_')}">$ ${valor}</div>
        </div>
    `;
}

window.addEventListener('load', () => {
    document.querySelectorAll('.card-row').forEach(row => {
        row.addEventListener('click', event => {
            const codigo = row.dataset.codigo;
            const finalRollo = row.dataset.finalRollo;
            const preciobase = row.dataset.precioBase;
            const finalEfectivo = row.dataset.finalEfectivo;
            const finalRolloEfectivo = row.dataset.finalRolloEfectivo;

            // Verificar si la fila ya tiene la clase "info-shown"
            if (!row.classList.contains('info-shown')) {
                // Crear un nuevo elemento tr para mostrar la información adicional
                const infoRow = document.createElement('tr');
                const precios = [
                    { titulo: 'Precio Base', valor: preciobase },
                    { titulo: 'Efectivo', valor: finalEfectivo },
                    { titulo: 'Rollo/Caja', valor: finalRollo },
                    { titulo: 'Rollo/Caja Efectivo', valor: finalRolloEfectivo }
                ];
                
                let html = '<td colspan="2"><div class="row"><div class="contenedor">';
                
                precios.forEach(precio => {
                    html += crearElementoPrecio(precio.titulo, precio.valor);
                });
                
                html += '</div></div></td>';
                
                infoRow.innerHTML = html;

                infoRow.addEventListener('click', event => {
                    // Rellenar el formulario con los datos actuales del artículo
                    document.querySelector('#id_descripcion').value = row.dataset.descripcion;
                    document.querySelector('#id_precio_base').value = row.dataset.precioBase;
                    document.querySelector('#id_codigo').value = codigo;
                
                    // Mostrar el modal y el backdrop
                    document.getElementById('editModal').style.display = 'block';
                });

                // Insertar el nuevo elemento tr después de la fila actual
                row.parentNode.insertBefore(infoRow, row.nextSibling);

                // Agregar la clase "info-shown" a la fila para indicar que ya se ha mostrado la información adicional
                row.classList.add('info-shown');
            }
        });
    });

    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.getElementById('editModal').style.display = 'none';
        }
    });

    
    // Ocultar el modal y el fondo oscuro cuando se envía el formulario
    document.querySelector('#editForm').addEventListener('submit', event => {
        event.preventDefault();

        // Crear un objeto FormData a partir del formulario
        let formData = new FormData(event.target);

        // Enviar los datos del formulario al servidor con AJAX
        fetch('/articulos/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': Cookies.get('csrftoken')
            },
            body: formData
        }).then(response => {
            if (response.ok) {
                // Cerrar el modal
                
                document.getElementById('editModal').style.display = 'none';
                
            }
        });
    });

    jQuery("#editForm").submit(function(e) {
        e.preventDefault(); // Evita que se recargue la página
    
        jQuery.ajax({
            url: '/articulos/', // La URL de tu vista que maneja el formulario
            type: 'post',
            data: jQuery(this).serialize(),
            success: function(response) {
                // Aquí puedes actualizar la tabla con los nuevos datos
                var fila = jQuery('tr[data-codigo="' + response.codigo + '"]');
                var infoRow = fila.next(); // Esto asume que la fila de información adicional está justo después de la fila original
    
                // Actualizar el precio base en la fila de información adicional
                document.getElementById('Precio_Base').textContent = '$ ' + response.precio_base;
                fila.find('td:eq(1)').html('<h6>' + response.descripcion + '</h6>');
    
                // Ocultar el modal
                document.getElementById('editModal').style.display = 'none';
                document.querySelector('.modal-backdrop').style.display = 'none';
            }
        });
    });
    
});
