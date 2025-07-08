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
            <div id="${titulo.toLowerCase().replace(' ', '_')}"> ${valor}</div>
        </div>
    `;
}
// Obtener la lista de títulos del elemento oculto
let lista_titulos = document.getElementById('lista-titulos').dataset.listaTitulos;
window.addEventListener('load', () => {
    document.querySelectorAll('.card-row').forEach(row => {
        row.addEventListener('click', event => {
            // Obtener todos los atributos data- del elemento
            const data = row.dataset;
            // Crear un array de objetos para los precios
            const precios = [];
            // Iterar sobre los atributos data-
            for (let name in data) {
                // Si el nombre del campo está en lista_titulos, continuar con la siguiente iteración
                if (lista_titulos.includes(name)) continue;
                // name es el nombre del atributo (por ejemplo, 'precioBase')
                // data[name] es el valor del atributo
                precios.push({ titulo: name.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase()), valor: data[name] });
            }
            // Verificar si la fila ya tiene la clase "info-shown"
            if (!row.classList.contains('info-shown')) {
                // Crear un nuevo elemento tr para mostrar la información adicional
                const infoRow = document.createElement('tr');
                let html = '<td colspan="2"><div class="row"><div class="contenedor">';
                precios.forEach(precio => {
                    html += crearElementoPrecio(precio.titulo, precio.valor);
                });
                html += '</div></div></td>';
                infoRow.innerHTML = html;
                infoRow.addEventListener('click', event => {
                    // Obtener todos los atributos data- del elemento
                    const data = row.dataset;
                    // Mostrar el modal y el backdrop
                    document.getElementById('editModal').style.display = 'block';
                    // Iterar sobre los atributos data-
                    for (let name in data) {
                        // Buscar el elemento del formulario
                        let element = document.querySelector('#id_' + name);
                        // Verificar si el elemento existe antes de intentar acceder a su propiedad 'value'
                        if (element) {
                            if (element.type === "checkbox") {
                                element.checked = data[name] === "True";
                            } else {
                                element.value = data[name];
                            }
                        }
                    }
                    // Mostrar el modal
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
        let formData = new FormData(event.target);//aqui cargar el formulario con los datos de un endpoint porque sino no funciona nada carajo!
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
        // Actualizar manualmente el valor del checkbox
        var checkbox = jQuery(this).find("input[type=checkbox]");
        checkbox.each(function() {
            jQuery(this).val(jQuery(this).is(':checked'));
        });
        jQuery.ajax({
            url: '/articulos/', // La URL de tu vista que maneja el formulario
            type: 'post',
            data: jQuery(this).serialize(),
            success: function(response) {
                // Aquí puedes actualizar la tabla con los nuevos datos
                var fila = jQuery('tr[data-codigo="' + response.codigo + '"]');
                var infoRow = fila.next(); // Esto asume que la fila de información adicional está justo después de la fila original
                // Iterar sobre lista_titulos para actualizar el contenido de la fila
                for (let i = 0; i < lista_titulos.length; i++) {
                    fila.find('td:eq(' + i + ')').html('<h6>' + response[lista_titulos[i]] + '</h6>');
                    }
                // Iterar sobre los atributos data-
                for (let name in response) {
                    // Convertir el nombre del campo a snake_case
                    let snakeCaseName = name.replace(/([A-Z])/g, '_$1').toLowerCase();
                    // Buscar el elemento
                    let element = document.getElementById(snakeCaseName);
                    // Verificar si el elemento existe antes de intentar acceder a su propiedad 'textContent'
                    if (element) {
                        // Si el nombre del campo está en lista_titulos, escribir sin símbolo y en negrita
                        if (lista_titulos.includes(name)) {
                            element.innerHTML = '<b>' + response[name] + '</b>';
                        } else {
                            // Si no, escribir con símbolo
                            element.textContent = response[name];
                        }
                    }
                }
                // Ocultar el modal
                document.getElementById('editModal').style.display = 'none';
            }
        });
    });
});
