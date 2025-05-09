# tu_app/views/ajax.py
import json
import os
from django.conf import settings
from django.http import FileResponse, JsonResponse, HttpResponse
from django.shortcuts import render # Usado en seleccionar_proveedor
from django.db.models import F
from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core import serializers # Usado en editar_item
from django.views.decorators.csrf import csrf_exempt # Usado en enviar_reporte

# Importa modelos y utils
from ..models import Lista_Pedidos, Item, ListaProveedores, Proveedor, Carrito, Articulo, Cajon, ArticuloSinRegistro
from .utils import articulo_to_dict, calcular_total, carrito_to_dict # Importa desde utils en el mismo módulo


import logging

logger = logging.getLogger(__name__)


def crear_modificar_lista_pedidos(request, proveedor_id=None): # Permitir None si no siempre se usa
    if request.method == 'GET':
        logger.info(f"GET request para lista de pedidos, proveedor_id={proveedor_id}")
        # Filtrar por proveedor si se proporciona un ID válido
        try:
            proveedor_filter = {}
            if proveedor_id is not None:
                proveedor_id = int(proveedor_id) # Asegurar que sea int
                proveedor_filter['proveedor_id'] = proveedor_id
            items = Lista_Pedidos.objects.filter(**proveedor_filter).select_related('proveedor', 'item')
            logger.debug(f"Encontrados {items.count()} pedidos para el filtro {proveedor_filter}.")
            data = [{
                'id': item.id,
                'proveedor': {
                    'id': item.proveedor.id,
                    'text_display': getattr(item.proveedor, 'text_display', str(item.proveedor)), # Usar un campo real o str
                },
                'item': {
                    'id': item.item.id,
                    'codigo': item.item.codigo, # Añadir código
                    'descripcion': item.item.descripcion,
                },
                'cantidad': item.cantidad,
                'pedido': item.pedido, # Añadir estado de pedido
            } for item in items]
            return JsonResponse(data, safe=False)
        except ValueError:
             logger.warning(f"Proveedor ID inválido recibido en GET: {proveedor_id}")
             return JsonResponse({'error': 'ID de proveedor inválido'}, status=400)
        except Exception as e:
             logger.error(f"Error obteniendo lista de pedidos (GET, proveedor_id={proveedor_id}): {e}", exc_info=True)
             return JsonResponse({'error': 'Error interno'}, status=500)


    elif request.method == 'POST':
        logger.info("POST request para crear/modificar lista de pedidos.")
        try:
            data = json.loads(request.body)
            codigo = data.get('codigo')
            if not codigo:
                 logger.warning("Solicitud POST sin 'codigo' en el body.")
                 return JsonResponse({'error': 'Código del item es requerido'}, status=400)

            logger.debug(f"Código recibido: {codigo}")
            item = Item.objects.get(codigo=codigo)

            # Determinar proveedor (lógica original basada en abreviatura)
            # Esta lógica parece frágil. ¿No debería el item tener ya un proveedor principal?
            # O pasar el proveedor_id en el POST?
            # Usando la lógica original:
            try:
                abreviatura = '/' + codigo.split('/')[-1]
                lista_proveedores = ListaProveedores.objects.get(abreviatura=abreviatura)
                proveedor = Proveedor.objects.get(identificador=lista_proveedores)
                logger.debug(f"Proveedor determinado por abreviatura '{abreviatura}': {proveedor.nombre}")
            except (ListaProveedores.DoesNotExist, Proveedor.DoesNotExist, IndexError) as e:
                 logger.error(f"No se pudo determinar el proveedor para el código '{codigo}' basado en abreviatura: {e}")
                 # Fallback: Usar el proveedor asignado al Item si existe?
                 if item.proveedor:
                      proveedor = item.proveedor
                      logger.warning(f"Usando proveedor asignado al Item como fallback: {proveedor.nombre}")
                 else:
                      return JsonResponse({'error': 'No se pudo determinar el proveedor para este item'}, status=400)


            # Buscar o crear entrada en Lista_Pedidos
            lista_pedido, created = Lista_Pedidos.objects.get_or_create(
                 item=item,
                 proveedor=proveedor, # Usar el proveedor determinado
                 defaults={'cantidad': 1, 'pedido': False} # Valor inicial si se crea
            )

            if created:
                logger.info(f"Creado nuevo registro en Lista_Pedidos para Item ID {item.id}, Proveedor ID {proveedor.id}.")
            else:
                # Si ya existe, incrementar cantidad
                lista_pedido.cantidad = F('cantidad') + 1
                lista_pedido.save()
                logger.info(f"Incrementada cantidad en Lista_Pedidos para ID {lista_pedido.id}.")

            # Marcar item como trabajado y asignar proveedor si no lo tiene o es diferente?
            # Esta lógica podría ser problemática si un item puede venir de varios proveedores.
            if not item.trabajado or item.proveedor != proveedor:
                 item.trabajado = True
                 item.proveedor = proveedor # Sobreescribe proveedor actual del item?
                 item.save(update_fields=['trabajado', 'proveedor'])
                 logger.info(f"Item ID {item.id} marcado como trabajado y proveedor actualizado a {proveedor.nombre}.")

            return JsonResponse({'success': True, 'lista_pedido_id': lista_pedido.id, 'created': created})

        except Item.DoesNotExist:
             logger.warning(f"Intento de añadir a pedido un item inexistente con código: {codigo}")
             return JsonResponse({'error': 'Item no encontrado'}, status=404)
        except json.JSONDecodeError:
             logger.error("Error decodificando JSON en POST a crear_modificar_lista_pedidos.")
             return JsonResponse({'error': 'JSON inválido'}, status=400)
        except Exception as e:
             logger.error(f"Error en POST a crear_modificar_lista_pedidos: {e}", exc_info=True)
             return JsonResponse({'error': 'Error interno'}, status=500)
    else:
        logger.warning(f"Método {request.method} no permitido para crear_modificar_lista_pedidos.")
        return JsonResponse({'error': 'Método no permitido'}, status=405)


# --- Otras vistas AJAX ---

def seleccionar_proveedor(request):
    # Esta vista parece renderizar HTML, ¿debería estar en main.py?
    # Si es solo para obtener la lista y poblar un select, podría ser AJAX.
    logger.info("Accediendo a seleccionar_proveedor.")
    if request.accepts('application/json'): # Chequear si el cliente prefiere JSON
         try:
              proveedores = Proveedor.objects.all().values('id', 'nombre') # Enviar solo lo necesario
              return JsonResponse(list(proveedores), safe=False)
         except Exception as e:
              logger.error(f"Error obteniendo proveedores para JSON: {e}", exc_info=True)
              return JsonResponse({'error':'Error interno'}, status=500)
    else: # Renderizar HTML si no se pide JSON
         try:
              proveedores = Proveedor.objects.all()
              return render(request, 'seleccionar_proveedor.html', {'proveedores': proveedores})
         except Exception as e:
              logger.error(f"Error renderizando seleccionar_proveedor.html: {e}", exc_info=True)
              # Considera renderizar una página de error o retornar HttpResponseServerError
              return HttpResponse("Error al cargar la página", status=500)


def cambiar_cantidad_pedido(request, id_articulo, cantidad):
    # Asume POST, aunque la URL sugiere GET. Mejor usar POST para cambios.
    if request.method == 'POST':
        logger.info(f"POST para cambiar cantidad de pedido: id_articulo={id_articulo}, cantidad={cantidad}")
        try:
            # Validar cantidad
            try:
                 nueva_cantidad = int(cantidad)
                 if nueva_cantidad < 0: # No permitir negativos? O 0 para eliminar?
                      raise ValueError("Cantidad no puede ser negativa")
            except ValueError:
                 logger.warning(f"Cantidad inválida recibida: {cantidad}")
                 return JsonResponse({'error': 'Cantidad inválida'}, status=400)

            pedido = Lista_Pedidos.objects.get(id=id_articulo)

            # Si la cantidad es 0, ¿eliminar el pedido?
            if nueva_cantidad == 0:
                 pedido_id = pedido.id
                 pedido.delete()
                 logger.info(f"Eliminado registro de Lista_Pedidos ID {pedido_id} por cantidad 0.")
                 return JsonResponse({'status': 'deleted', 'id': pedido_id})
            else:
                 pedido.cantidad = nueva_cantidad
                 # No resetear 'pedido' a False automáticamente?
                 # pedido.pedido = False # Desmarcar como pedido si cambia cantidad?
                 pedido.save(update_fields=['cantidad']) # Solo guardar cantidad
                 logger.info(f"Actualizada cantidad de Lista_Pedidos ID {pedido.id} a {nueva_cantidad}.")
                 # Devuelve la cantidad actualizada por si el frontend la necesita
                 return JsonResponse({'status': 'ok', 'nueva_cantidad': pedido.cantidad}) # Devuelve la cantidad guardada

        except Lista_Pedidos.DoesNotExist:
             logger.warning(f"Intento de cambiar cantidad de pedido inexistente (ID: {id_articulo}).")
             return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
        except Exception as e:
             logger.error(f"Error cambiando cantidad de pedido (ID: {id_articulo}): {e}", exc_info=True)
             return JsonResponse({'error': 'Error interno'}, status=500)
    else:
        logger.warning(f"Método {request.method} no permitido para cambiar_cantidad_pedido.")
        return JsonResponse({'error': 'Método no permitido, usa POST'}, status=405)


def editar_item(request, id_articulo):
    logger.info(f"Accediendo a editar_item para ID: {id_articulo}, Método: {request.method}")
    try:
         articulo = Item.objects.select_related('cajon').get(id=id_articulo) # Optimizar FK
    except Item.DoesNotExist:
         logger.warning(f"Intento de editar item inexistente (ID: {id_articulo}).")
         # Si es AJAX, devolver error. Si es una página, renderizar 404.
         return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
    except Exception as e: # Otros errores al buscar
         logger.error(f"Error buscando Item ID {id_articulo} para editar: {e}", exc_info=True)
         return JsonResponse({'error': 'Error interno al buscar artículo'}, status=500)


    if request.method == 'GET':
        logger.debug("Procesando GET para editar_item.")
        try:
            cajon_dict = model_to_dict(articulo.cajon) if articulo.cajon else None
            logger.debug(f"Cajón actual del item: {cajon_dict}")

            # Crear lista de cajones para el select (incluyendo opción vacía)
            # Serializar directamente puede ser pesado si hay muchos cajones.
            # Enviar solo IDs y códigos podría ser más eficiente.
            # cajon_vacio = {'id': None, 'codigo': "------"}
            # cajones_list = [cajon_vacio] + list(Cajon.objects.all().values('id', 'codigo'))
            # Usando el serialize original:
            cajon_vacio_obj = Cajon(id=None, codigo="------") # Objeto temporal
            cajones_qs = [cajon_vacio_obj] + list(Cajon.objects.all())
            cajones_serialized = serializers.serialize('json', cajones_qs)
            logger.debug("Lista de cajones serializada para el modal.")


            return JsonResponse({
                'status': 'ok',
                'modal_stock': articulo.stock, # Renombrar 'modal_cantidad' a 'modal_stock'
                'modal_barras': articulo.barras,
                'modal_tiene_cartel': articulo.tiene_cartel,
                'modal_cajon': cajon_dict, # Cajón actual
                'cajones': cajones_serialized, # Lista completa para el select
            })
        except Exception as e:
             logger.error(f"Error preparando datos GET para editar_item (ID: {id_articulo}): {e}", exc_info=True)
             return JsonResponse({'error': 'Error preparando datos del modal'}, status=500)

    elif request.method == 'POST':
         logger.debug("Procesando POST para editar_item.")
         try:
             data = json.loads(request.body)
             logger.debug(f"Datos recibidos en POST: {data}")

             # Validar y actualizar campos
             try:
                  articulo.stock = int(data.get('stock', articulo.stock)) # Mantener stock si no se envía
             except (ValueError, TypeError):
                  logger.warning(f"Valor de stock inválido recibido: {data.get('stock')}. Se mantiene el anterior.")
                  # return JsonResponse({'error': 'Stock inválido'}, status=400) # Opcional: devolver error

             barras_recibido = data.get('barras', articulo.barras) # Mantener barras si no se envía
             articulo.barras = barras_recibido if barras_recibido else '0' # Default a '0' si es vacío

             # Asegurarse que tiene_cartel sea booleano
             tiene_cartel_recibido = data.get('tiene_cartel')
             if tiene_cartel_recibido is not None: # Solo actualizar si se envía
                 articulo.tiene_cartel = bool(tiene_cartel_recibido)


             # Actualizar cajón
             cajon_id = data.get('cajon')
             if cajon_id == 'null' or cajon_id is None:
                  articulo.cajon = None
                  logger.debug("Cajón asignado a None.")
             elif cajon_id: # Si no es None o 'null'
                  try:
                       cajon_nuevo = Cajon.objects.get(id=int(cajon_id))
                       articulo.cajon = cajon_nuevo
                       logger.debug(f"Cajón actualizado a ID: {cajon_id}")
                  except (Cajon.DoesNotExist, ValueError, TypeError):
                       logger.warning(f"ID de cajón inválido o no encontrado recibido: {cajon_id}. No se actualiza el cajón.")
                       # return JsonResponse({'error': 'Cajón seleccionado inválido'}, status=400) # Opcional

             # Guardar cambios
             # Especificar los campos a actualizar es más seguro
             update_fields = ['stock', 'barras', 'tiene_cartel', 'cajon']
             articulo.save(update_fields=update_fields)
             logger.info(f"Item ID {articulo.id} actualizado correctamente.")

             return JsonResponse({'status': 'ok', 'message': 'Artículo actualizado'})

         except json.JSONDecodeError:
              logger.error("Error decodificando JSON en POST a editar_item.")
              return JsonResponse({'error': 'JSON inválido'}, status=400)
         except Exception as e:
              logger.error(f"Error procesando POST para editar_item (ID: {id_articulo}): {e}", exc_info=True)
              return JsonResponse({'error': 'Error interno al actualizar'}, status=500)
    else:
        logger.warning(f"Método {request.method} no permitido para editar_item.")
        return JsonResponse({'error': 'Método no permitido'}, status=405)


def agregar_articulo_a_carrito(request, id_articulo):
     if request.method == 'POST':
          logger.info(f"POST para agregar artículo ID {id_articulo} al carrito.")
          if not request.user.is_authenticated:
               logger.warning("Intento de agregar al carrito por usuario no autenticado.")
               return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

          try:
               data = json.loads(request.body)
               cantidad_a_agregar = data.get('cantidad')
               usuario_caja_id = data.get('usuario_caja') # Para agregar a carrito de otro usuario
               logger.debug(f"Datos recibidos: cantidad={cantidad_a_agregar}, usuario_caja_id={usuario_caja_id}")

               try:
                    cantidad_a_agregar = int(cantidad_a_agregar)
                    if cantidad_a_agregar <= 0:
                         logger.warning("Intento de agregar cantidad no positiva al carrito.")
                         return JsonResponse({'error': 'La cantidad debe ser positiva'}, status=400)
               except (ValueError, TypeError):
                    logger.warning(f"Cantidad inválida recibida: {cantidad_a_agregar}")
                    return JsonResponse({'error': 'Cantidad inválida'}, status=400)

               item = Item.objects.get(id=id_articulo)

               # Determinar el usuario objetivo del carrito
               if usuario_caja_id:
                    # Validar permisos: solo ciertos usuarios pueden agregar a carritos ajenos?
                    if not request.user.is_staff: # Ejemplo: solo staff puede agregar a otros carritos
                         logger.error(f"Usuario {request.user} intentó agregar a carrito ajeno (ID: {usuario_caja_id}) sin permisos.")
                         return JsonResponse({'error': 'No tienes permiso para agregar a este carrito'}, status=403)
                    try:
                         usuario_objetivo = User.objects.get(id=usuario_caja_id)
                         logger.info(f"Agregando al carrito del usuario: {usuario_objetivo.username}")
                    except User.DoesNotExist:
                         logger.warning(f"Usuario caja ID {usuario_caja_id} no encontrado.")
                         return JsonResponse({'error': 'Usuario caja no encontrado'}, status=404)
               else:
                    usuario_objetivo = request.user
                    logger.info(f"Agregando al carrito del usuario actual: {usuario_objetivo.username}")


               # Obtener o crear carrito y artículo en carrito
               carrito, _ = Carrito.objects.get_or_create(usuario=usuario_objetivo)
               articulo_en_carrito, created = Articulo.objects.get_or_create(
                    item=item,
                    carrito=carrito,
                    defaults={
                         'cantidad': cantidad_a_agregar,
                         'precio': item.final, # Precio actual al agregar
                         'precio_efectivo': item.final_efectivo # Precio actual al agregar
                    }
               )

               if created:
                    logger.info(f"Item ID {item.id} agregado al carrito ID {carrito.id} con cantidad {cantidad_a_agregar}.")
               else:
                    # Si ya existe, sumar cantidad
                    articulo_en_carrito.cantidad = F('cantidad') + cantidad_a_agregar
                    # Actualizar precios si han cambiado? O mantener el original?
                    # articulo_en_carrito.precio = item.final # Descomentar para actualizar precio
                    # articulo_en_carrito.precio_efectivo = item.final_efectivo # Descomentar
                    articulo_en_carrito.save(update_fields=['cantidad']) # Actualizar solo cantidad
                    #articulo_en_carrito.refresh_from_db() # Recargar para obtener valor actualizado
                    logger.info(f"Actualizada cantidad de Item ID {item.id} en carrito ID {carrito.id}. Nueva cantidad estimada: +{cantidad_a_agregar}")


               # Actualizar Lista_Pedidos (aumentar cantidad pedida)
               # OJO: Esto asume que cada venta implica pedir más. ¿Es correcto?
               if item.proveedor:
                    pedido, pedido_created = Lista_Pedidos.objects.get_or_create(
                         proveedor=item.proveedor,
                         item=item,
                         defaults={'cantidad': cantidad_a_agregar}
                    )
                    if not pedido_created:
                         pedido.cantidad = F('cantidad') + cantidad_a_agregar
                         pedido.save(update_fields=['cantidad'])
                         logger.info(f"Incrementada cantidad en Lista_Pedidos ID {pedido.id} por venta.")
                    else:
                         logger.info(f"Creado nuevo registro en Lista_Pedidos ID {pedido.id} por venta.")
               else:
                    logger.warning(f"Item ID {item.id} no tiene proveedor asignado, no se actualizó Lista_Pedidos.")

               return JsonResponse({'status': 'ok', 'message': 'Artículo agregado al carrito'})

          except Item.DoesNotExist:
               logger.warning(f"Intento de agregar item inexistente (ID: {id_articulo}) al carrito.")
               return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
          except json.JSONDecodeError:
               logger.error("Error decodificando JSON en POST a agregar_articulo_a_carrito.")
               return JsonResponse({'error': 'JSON inválido'}, status=400)
          except Exception as e:
               logger.error(f"Error agregando artículo ID {id_articulo} al carrito: {e}", exc_info=True)
               return JsonResponse({'error': 'Error interno'}, status=500)
     else:
          logger.warning(f"Método {request.method} no permitido para agregar_articulo_a_carrito.")
          return JsonResponse({'error': 'Método no permitido'}, status=405)


def carrito(request):
     # Devuelve info básica del carrito del usuario actual
     if request.method == 'GET':
          logger.info("GET request para obtener información del carrito.")
          if not request.user.is_authenticated:
               logger.warning("Intento de ver carrito por usuario no autenticado.")
               return JsonResponse({'error': 'Usuario no autenticado'}, status=401)
          try:
               # Obtener carrito (crearlo si no existe para este usuario)
               carrito_obj, created = Carrito.objects.get_or_create(usuario=request.user)
               if created:
                    logger.info(f"Carrito creado para el usuario {request.user.username}")
               # Usar el helper para convertir a dict
               carrito_dict = carrito_to_dict(carrito_obj) # Asume que carrito_to_dict está definido en utils.py
               return JsonResponse({'status': 'ok', 'carrito': carrito_dict})
          except Exception as e:
               logger.error(f"Error obteniendo/creando carrito para usuario {request.user.username}: {e}", exc_info=True)
               return JsonResponse({'error': 'Error interno'}, status=500)
     else:
          logger.warning(f"Método {request.method} no permitido para carrito.")
          return JsonResponse({'error': 'Método no permitido'}, status=405)



def consultar_carrito(request):
     # Devuelve el contenido detallado de uno o más carritos
     if request.method == 'GET':
          logger.info("GET request para consultar contenido del carrito.")
          datos = {}
          if not request.user.is_authenticated:
               logger.warning("Intento de consultar carrito por usuario no autenticado.")
               return JsonResponse({'error': 'Usuario no autenticado'}, status=401)

          try:
               # Lógica especial para 'darkydiel' (¿admin?)
               if request.user.username == 'darkydiel': # Usar username es más fiable que str(request.user)
                    logger.info("Usuario 'darkydiel' consultando carritos de Mati y Carlos.")
                    # Obtener carritos específicos (IDs hardcodeados es mala práctica)
                    # Mejor buscar por username si es posible
                    try:
                         carrito_mati = Carrito.objects.get(usuario__username='Mati') # Asume username 'Mati'
                         articulos_mati = Articulo.objects.filter(carrito=carrito_mati).select_related('item') # Optimizar
                         articulos_sin_registro_mati = ArticuloSinRegistro.objects.filter(carrito=carrito_mati)
                         datos['Mati'] = {
                              "articulos": [articulo_to_dict(a) for a in articulos_mati],
                              "articulos_sin_registro": [articulo_to_dict(a) for a in articulos_sin_registro_mati],
                              "carrito_id": carrito_mati.id
                         }
                    except Carrito.DoesNotExist:
                         logger.warning("No se encontró el carrito para 'Mati'.")
                         datos['Mati'] = {"articulos": [], "articulos_sin_registro": [], "carrito_id": None, "error": "Carrito no encontrado"}

                    try:
                         carrito_carlos = Carrito.objects.get(usuario__username='Carlos') # Asume username 'Carlos'
                         articulos_carlos = Articulo.objects.filter(carrito=carrito_carlos).select_related('item')
                         articulos_sin_registro_carlos = ArticuloSinRegistro.objects.filter(carrito=carrito_carlos)
                         datos['Carlos'] = {
                              "articulos": [articulo_to_dict(a) for a in articulos_carlos],
                              "articulos_sin_registro": [articulo_to_dict(a) for a in articulos_sin_registro_carlos],
                              "carrito_id": carrito_carlos.id
                         }
                    except Carrito.DoesNotExist:
                         logger.warning("No se encontró el carrito para 'Carlos'.")
                         datos['Carlos'] = {"articulos": [], "articulos_sin_registro": [], "carrito_id": None, "error": "Carrito no encontrado"}

               else: # Para usuarios normales
                    logger.info(f"Usuario '{request.user.username}' consultando su propio carrito.")
                    carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
                    articulos = Articulo.objects.filter(carrito=carrito).select_related('item')
                    articulos_sin_registro = ArticuloSinRegistro.objects.filter(carrito=carrito)
                    datos[request.user.username] = {
                         "articulos": [articulo_to_dict(articulo) for articulo in articulos],
                         "articulos_sin_registro": [articulo_to_dict(articulo) for articulo in articulos_sin_registro],
                         "carrito_id": carrito.id
                    }

               # Calcular totales usando la función utilitaria
               datos_con_totales = calcular_total(datos) # Asume que calcular_total está en utils.py
               logger.debug("Totales calculados para los carritos consultados.")

               return JsonResponse(datos_con_totales)

          except Exception as e:
               logger.error(f"Error consultando carritos para usuario {request.user.username}: {e}", exc_info=True)
               return JsonResponse({'error': 'Error interno al consultar carritos'}, status=500)
     else:
          logger.warning(f"Método {request.method} no permitido para consultar_carrito.")
          return JsonResponse({'error': 'Método no permitido'}, status=405)



def usuarios_caja(request):
     # Devuelve lista de usuarios que pueden ser seleccionados como 'caja'
     if request.method == 'GET':
          logger.info("GET request para obtener usuarios caja.")
          try:
               # Definir quiénes son usuarios caja (ej: por grupo, por flag en UserProfile, etc.)
               # Ejemplo: Usuarios en el grupo 'Cajeros'
               # from django.contrib.auth.models import Group
               # try:
               #     cajeros_group = Group.objects.get(name='Cajeros')
               #     usuarios = User.objects.filter(groups=cajeros_group, is_active=True).values('id', 'username')
               # except Group.DoesNotExist:
               #     logger.warning("El grupo 'Cajeros' no existe para filtrar usuarios caja.")
               #     usuarios = []

               # Usando la lista hardcodeada original como fallback/ejemplo:
               usuarios_hardcoded = [
                    # Usar IDs reales de la BBDD, no 1 y 2 a menos que coincidan
                    {'id': User.objects.get(username='Mati').id, 'nombre': 'Mati'},
                    {'id': User.objects.get(username='Carlos').id, 'nombre': 'Carlos'},
               ]
               logger.debug(f"Devolviendo lista hardcodeada de usuarios caja: {usuarios_hardcoded}")
               return JsonResponse(usuarios_hardcoded, safe=False)

          except User.DoesNotExist as e:
               logger.error(f"Error obteniendo ID de usuario hardcodeado para usuarios_caja: {e}")
               return JsonResponse({'error': 'Error configurando usuarios caja'}, status=500)
          except Exception as e:
               logger.error(f"Error inesperado obteniendo usuarios caja: {e}", exc_info=True)
               return JsonResponse({'error': 'Error interno'}, status=500)
     else:
          logger.warning(f"Método {request.method} no permitido para usuarios_caja.")
          return JsonResponse({'error': 'Método no permitido'}, status=405)


def eliminar_articulo_pedido(request):
     # Confirma o elimina un item de la Lista_Pedidos
     if request.method == 'POST':
          # Asumiendo que los datos vienen como form-data (request.POST)
          # Si vienen como JSON, usar json.loads(request.body)
          pedido_id = request.POST.get('id')
          cantidad = request.POST.get('quantity')
          confirmado_str = request.POST.get('confirmed', 'false').lower() # Default false
          confirmado = confirmado_str == 'true'

          logger.info(f"POST para eliminar/confirmar pedido ID: {pedido_id}, Cantidad: {cantidad}, Confirmado: {confirmado}")

          if not pedido_id:
               logger.warning("Solicitud POST sin ID de pedido.")
               return JsonResponse({'error': 'ID de pedido requerido'}, status=400)

          try:
               pedido = Lista_Pedidos.objects.get(id=pedido_id)

               if confirmado:
                    # Validar cantidad antes de guardar
                    try:
                         cantidad_validada = int(cantidad)
                         if cantidad_validada <= 0: # Si confirman con 0 o menos, ¿qué hacer? Eliminar?
                              raise ValueError("Cantidad confirmada debe ser positiva.")
                    except (ValueError, TypeError):
                         logger.warning(f"Cantidad inválida recibida al confirmar pedido ID {pedido_id}: {cantidad}")
                         return JsonResponse({'error': 'Cantidad inválida'}, status=400)

                    # Marcar como pedido y actualizar cantidad
                    pedido.pedido = True
                    pedido.cantidad = cantidad_validada
                    pedido.save(update_fields=['pedido', 'cantidad'])
                    logger.info(f"Pedido ID {pedido_id} confirmado con cantidad {cantidad_validada}.")
                    return JsonResponse({'status': 'confirmed', 'id': pedido.id, 'cantidad': pedido.cantidad})
               else:
                    # Si no está confirmado, eliminar
                    pedido_id_deleted = pedido.id
                    pedido.delete()
                    logger.info(f"Pedido ID {pedido_id_deleted} eliminado (no confirmado).")
                    return JsonResponse({'status': 'deleted', 'id': pedido_id_deleted})

          except Lista_Pedidos.DoesNotExist:
               logger.warning(f"Intento de eliminar/confirmar pedido inexistente (ID: {pedido_id}).")
               return JsonResponse({'error': 'Pedido no encontrado'}, status=404)
          except Exception as e:
               logger.error(f"Error procesando eliminación/confirmación de pedido ID {pedido_id}: {e}", exc_info=True)
               return JsonResponse({'error': 'Error interno'}, status=500)
     else:
          logger.warning(f"Método {request.method} no permitido para eliminar_articulo_pedido.")
          return JsonResponse({'error': 'Método no permitido'}, status=405)


# --- Vistas de Reporte y Descarga (Podrían ir en archivos separados si crecen) ---

def descargar_archivo(request):
    # Ofrece un archivo específico para descargar
    logger.info("Solicitud GET para descargar archivo.")
    nombre_del_archivo = 'script_pyinstaller.py' # ¿Hardcodeado? Mejor desde settings o un modelo
    # Asume que MEDIA_ROOT está configurado correctamente en settings.py
    try:
         ruta_al_archivo = os.path.join(settings.MEDIA_ROOT, nombre_del_archivo)
         logger.debug(f"Intentando servir archivo desde: {ruta_al_archivo}")
         # Verificar si el archivo existe antes de intentar abrirlo
         if not os.path.exists(ruta_al_archivo):
              logger.error(f"Archivo no encontrado para descarga: {ruta_al_archivo}")
              # Devolver un 404 o un mensaje adecuado
              return HttpResponse("Archivo no encontrado.", status=404)

         # Usar FileResponse para servir archivos
         response = FileResponse(open(ruta_al_archivo, 'rb'), content_type='application/octet-stream') # Tipo genérico
         # Establecer el nombre de archivo para la descarga
         response['Content-Disposition'] = f'attachment; filename="{os.path.basename(nombre_del_archivo)}"'
         logger.info(f"Archivo '{nombre_del_archivo}' enviado para descarga.")
         return response
    except FileNotFoundError: # Capturar explícitamente por si os.path.exists falla o hay race condition
         logger.error(f"Archivo no encontrado (FileNotFoundError): {ruta_al_archivo}")
         return HttpResponse("Archivo no encontrado.", status=404)
    except Exception as e:
         logger.error(f"Error al intentar descargar archivo '{nombre_del_archivo}': {e}", exc_info=True)
         return HttpResponse("Error al descargar el archivo.", status=500)


def reportar_item(request, articulo_id):
     # Devuelve datos iniciales para un modal de reporte (GET)
     if request.method == 'GET':
          logger.info(f"GET request para reportar item ID: {articulo_id}")
          try:
               # Verificar que el artículo existe (opcional, pero bueno)
               # item = Item.objects.get(id=articulo_id)

               # Estados predefinidos (mejor desde settings o BBDD si cambian mucho)
               estados = getattr(settings, 'ESTADOS_REPORTE_ITEM', ['Cantidad mal dividida', 'Falta precio en Efectivo', 'Otros'])
               # Estado actual y detalles podrían venir del modelo si ya hay un reporte?
               # Por ahora, valores por defecto:
               estado_actual = estados[0] # Default al primero
               detalles = ""

               data = {
                    'status': 'ok',
                    'estados_posibles': estados,
                    'modal_detalles': detalles, # Para prellenar el textarea
                    'estado_actual': estado_actual, # Para preseleccionar el estado
               }
               logger.debug(f"Datos preparados para modal de reporte: {data}")
               return JsonResponse(data)

          # except Item.DoesNotExist:
          #      logger.warning(f"Intento de reportar item inexistente ID: {articulo_id}")
          #      return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
          except Exception as e:
               logger.error(f"Error preparando datos para reportar item ID {articulo_id}: {e}", exc_info=True)
               return JsonResponse({'error': 'Error interno'}, status=500)
     else:
          logger.warning(f"Método {request.method} no permitido para reportar_item (solo GET).")
          return JsonResponse({'error': 'Método no permitido'}, status=405)


@csrf_exempt # Necesario si el POST viene de JS sin token CSRF
def enviar_reporte(request, articulo_id):
     # Recibe los datos del reporte (POST)
     if request.method == 'POST':
          logger.info(f"POST request para enviar reporte de item ID: {articulo_id}")
          try:
               data = json.loads(request.body)
               estado = data.get('estado')
               detalles = data.get('detalles')
               logger.debug(f"Reporte recibido: Estado='{estado}', Detalles='{detalles}'")

               if not estado: # Validar que al menos el estado venga
                    logger.warning("Reporte recibido sin estado.")
                    return JsonResponse({'error': 'El estado es requerido'}, status=400)

               # Aquí va la lógica para guardar el reporte:
               # 1. Validar que el Item exista.
               # 2. Crear un nuevo registro en un modelo 'ReporteItem' (por ejemplo).
               # 3. Asociarlo al Item y al usuario que reporta (request.user).
               # 4. Guardar estado y detalles.
               try:
                    item_reportado = Item.objects.get(id=articulo_id)
                    # Crear modelo Reporte (ejemplo)
                    # from ..models import ReporteItem
                    # ReporteItem.objects.create(
                    #      item=item_reportado,
                    #      usuario_reporta=request.user if request.user.is_authenticated else None,
                    #      estado=estado,
                    #      detalles=detalles
                    # )
                    logger.info(f"Reporte para Item ID {articulo_id} procesado (lógica de guardado pendiente).")
                    # Simular éxito por ahora
                    return HttpResponse("Reporte enviado correctamente", status=200) # Usar 200 OK

               except Item.DoesNotExist:
                    logger.warning(f"Intento de enviar reporte para item inexistente ID: {articulo_id}")
                    return JsonResponse({'error': 'Artículo no encontrado'}, status=404)
               except Exception as e: # Error durante el guardado
                    logger.error(f"Error al guardar reporte para item ID {articulo_id}: {e}", exc_info=True)
                    return JsonResponse({'error': 'Error al guardar el reporte'}, status=500)


          except json.JSONDecodeError:
               logger.error("Error decodificando JSON en POST a enviar_reporte.")
               return JsonResponse({'error': 'JSON inválido'}, status=400)
          except Exception as e: # Otros errores inesperados
               logger.error(f"Error inesperado en enviar_reporte para item ID {articulo_id}: {e}", exc_info=True)
               return JsonResponse({'error': 'Error interno inesperado'}, status=500)
     else:
          logger.warning(f"Método {request.method} no permitido para enviar_reporte (solo POST).")
          return JsonResponse({'error': 'Método no permitido'}, status=405)