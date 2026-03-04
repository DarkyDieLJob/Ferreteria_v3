# App Pedido - Guía de Arquitectura y Estilo

## 1. Propósito
Gestión del ciclo de pedidos a proveedores: creación/edición, control de recepción, listados, faltantes y devoluciones.

## 2. Modelos clave (pedido/models.py)
- Vendido
  - proveedor(FK Proveedor), item(FK Item), cantidad(float), umbral(float), pedido(bool)
- ArticuloPedido
  - proveedor(FK Proveedor), item(FK Item), cantidad(float), llego(bool), fecha(date)
- Pedido
  - fecha(date auto), proveedor(FK Proveedor)
  - articulo_pedido(M2M ArticuloPedido), total(float), fecha_entrega(date)
  - estado(choices: Pendiente/Enviado/Entregado/Controlado)
- ArticuloDevolucion
  - fecha(auto), proveedor(FK), item(FK), cantidad(float)

Relaciones externas:
- Item, Proveedor, Lista_Pedidos (desde bdd.models) se usan en varias vistas/acciones.

## 3. Formularios (pedido/forms.py)
- ArticuloPedidoForm
  - Campos: item (ModelSelect2 autocomplete), cantidad
  - Depende de dal_select2 (Select2QuerySetView en views/base.py)

## 4. Vistas (pedido/views)
- base.py
  - GeneralPedidoView(TemplateView): arma `barra_de_navegacion`
  - ItemAutocomplete(Select2QuerySetView): filtra Item por código y abreviatura de proveedor
  - agregar_al_stock(request): actualiza ArticuloPedido, Item.stock y Lista_Pedidos (bdd)
- controlar.py, editar.py, devoluciones.py, detalles.py, faltantes.py, home.py, externo.py
  - Implementan las pantallas específicas para: controlar pedidos, editar pedidos, gestionar devoluciones, ver detalles, listar faltantes y home de pedidos.

## 5. Templates (pedido/templates/pedido)
- base_pedido.html
  - Layout base de la app (incluye Bootstrap local, Select2 CDN, Navbar)
- nav_bar.html
  - Usa `barra_de_navegacion` del contexto; contiene dropdowns y enlaces
- Vistas (subcarpetas por pantalla)
  - vistas/home: base.html, tabla_content.html
  - vistas/editar_pedido: base.html, form_content.html, table_content_articulos_*
  - vistas/controlar_pedido: base.html, form_content.html, table_content.html
  - vistas/detalle_pedido: base.html, table_content.html
  - vistas/devoluciones: base.html, table_content.html
  - vistas/listar_pedido: base.html, table_content.html
- Reutilizables
  - elementos/elemento_tabla.html, listar_faltantes.html

## 6. JavaScript (pedido/static/js)
- pedido/nuevo_stock.js
- pedido/vistas/controlar_pedido.js
- pedido/vistas/devoluciones.js
- pedido/vistas/editar_pedido.js

## 7. Dependencias Front
- Bootstrap (CSS/JS desde static)
- jQuery (hay carga local y CDN en base_pedido.html; se recomienda unificar a una sola fuente)
- Select2 (CDN) para autocomplete
- Quagga (lector de códigos)
- admin/css/widgets.css

## 8. Flujo resumido
- Home pedidos: acceso a listados y acciones comunes
- Editar pedido: agregar/editar artículos de pedido por proveedor (autocomplete)
- Listar/Controlar pedido: marcar llegadas, actualizar stock y faltantes
- Detalle pedido: vista focalizada de un pedido
- Devoluciones: registro y listado de devoluciones
- Faltantes: listado consolidado desde Lista_Pedidos (bdd)

## 9. Guía de Estilo (base)
- Usar `base_pedido.html` como layout heredable
- Evitar CSS inline; preferir `static/css/pedido.css` (a crear) para reglas comunes:
  - Tipografía, espaciado, `box-sizing: border-box` global
  - Componentes: `.btn`, `.form-control`, `.table.table-striped.table-hover`
  - Navbar: asegurar `navbar-light` o `navbar-dark` según fondo; toggler-icon visible
- No duplicar jQuery (usar una sola fuente); alinear versión de Bootstrap/Select2

## 10. Roadmap UI / Cross-browser
- Normalizar librerías: una sola jQuery, Bootstrap 5 estable, Select2 compatible
- Extraer inline CSS de `base_pedido.html` a `static/css/pedido.css`
- Revisar plantillas más usadas (home, editar, controlar) y aplicar clases Bootstrap de forma consistente
- Probar en Chrome/Firefox/Edge, ajustar contrastes y espaciados

## 11. Puntos sensibles
- ItemAutocomplete: requiere `proveedor_id` válido y filtra `codigo__endswith` por abreviatura (Proveedor.identificador.abreviatura)
- agregar_al_stock: toca `Item.stock` y `Lista_Pedidos`; revisar transacciones si se hace masivo

## 12. Convenciones
- Prefijo de rutas de template: `pedido/...` para evitar colisiones
- Nombrado de archivos por pantalla en `templates/pedido/vistas/<pantalla>/`
- JS por pantalla en `static/js/pedido/vistas/<pantalla>.js`
