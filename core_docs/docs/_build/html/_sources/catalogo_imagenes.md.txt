# Catálogo de Imágenes

Este catálogo contiene una lista de todas las imágenes utilizadas en la documentación, organizadas por sección y con su descripción correspondiente.

## Sistema de Pedidos

| Nombre | Ruta | Descripción | Fecha |
|--------|------|-------------|--------|
| proceso_pedido_20250531.png | /_static/images/sistema_pedidos/proceso_pedido_20250531.png | Interfaz principal del sistema de pedidos, mostrando la lista de pedidos y las opciones de acción disponibles | 2025-05-31 |

## Facturación

| Nombre | Ruta | Descripción | Fecha |
|--------|------|-------------|--------|

## Inventario

| Nombre | Ruta | Descripción | Fecha |
|--------|------|-------------|--------|

## Configuración

| Nombre | Ruta | Descripción | Fecha |
|--------|------|-------------|--------|

## Notas

1. **Formato de Nombres**
   - Usa nombres descriptivos y en minúsculas
   - Incluye la fecha en YYYYMMDD si es necesario
   - Ejemplo: `proceso_pedido_20250531.png`

2. **Actualización Automática**
   - Este catálogo debe actualizarse manualmente cada vez que se agregue una nueva imagen
   - Incluye la fecha de creación/modificación en el formato YYYY-MM-DD

3. **Mantenimiento**
   - Verifica periódicamente que las rutas de las imágenes sean correctas
   - Elimina entradas de imágenes que ya no se utilicen
   - Mantén la descripción actualizada con los cambios en la interfaz

4. **Uso en Documentación**
   ```markdown
   ![Descripción](/_static/images/sistema_pedidos/proceso_pedido_20250531.png)
   ```

## Proceso de Actualización

1. **Agregar Nueva Imagen**
   1. Crea la imagen y guárdala en el directorio correspondiente
   2. Agrega una nueva entrada en la tabla correspondiente
   3. Incluye:
      - Nombre del archivo
      - Ruta completa
      - Descripción breve
      - Fecha de creación

2. **Actualizar Documentación**
   1. Modifica el archivo que utilizará la imagen
   2. Usa la sintaxis correcta: `![Descripción](/_static/images/...)`
   3. Reconstruye la documentación: `python manage.py rebuild_docs`

3. **Eliminar Imagen**
   1. Elimina la imagen del directorio
   2. Elimina la entrada del catálogo
   3. Actualiza cualquier referencia en la documentación

## Validación

1. **Verifica que**
   - La imagen existe en el directorio indicado
   - La ruta en el markdown es correcta
   - La descripción es clara y precisa
   - La fecha está actualizada
   - No hay duplicados en el catálogo

2. **Herramientas de Validación**
   - Usa `ls -la` para verificar la existencia de archivos
   - Usa `grep` para buscar referencias en la documentación
   - Usa `diff` para comparar versiones anteriores
