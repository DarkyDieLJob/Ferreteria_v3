// Delegación de eventos para eliminar devoluciones
document.addEventListener('DOMContentLoaded', function () {
  document.body.addEventListener('click', function (e) {
    const trigger = e.target.closest('.js-eliminar-devolucion');
    if (trigger) {
      e.preventDefault(); // evita navegación si es un <a> o <button type="submit">
      const devolucionId = trigger.getAttribute('data-devolucion-id');
      if (devolucionId) {
        eliminarDevolucion(devolucionId);
      }
    }
  });
});

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function eliminarDevolucion(devolucionId) {
  var url = '/pedidos/eliminar_devolucion/';
  var csrftoken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || getCookie('csrftoken');
  var data = {
    'devolucion_id': devolucionId,
    'csrfmiddlewaretoken': csrftoken
  };
  $.post(url, data, function (response) {
    if (response.status == 'ok') {
      location.reload();
    } else {
      alert('Error al eliminar la devolucion');
    }
  });
}