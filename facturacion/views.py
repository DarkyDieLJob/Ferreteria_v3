# -*- coding: utf-8 -*-
from django.shortcuts import redirect
#viejo archivo
from bdd.views_old import Inicio
from bdd.views.main import Inicio
from bdd.models import Carrito, Articulo, ArticuloSinRegistro, Item, Lista_Pedidos, NavBar
from boletas.models import Boleta
from facturacion.forms import ClienteForm
from .models import Cliente, CierreZ, Transaccion
from .funtions import cliente_to_dict, request_on_procesar_transaccion_to_dict
from django.http import JsonResponse, HttpResponse
from .models import MetodoPago
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
# from bdd.models import ArticuloSinRegistro, Carrito # Redundant import
# import json # Redundant import
from .funtions import registrar_articulos_vendidos
from .cliente import conectar_a_websocket
import asyncio
from django.views.generic import TemplateView
# from django.shortcuts import redirect # Redundant import
from actualizador.task import ejecutar_cola_tareas
# Import the configured logger
import logging

logger = logging.getLogger(__name__)

from utils.ordenar_query import agrupar_transacciones_por_fecha
from django.db.models import Sum, Count
from datetime import datetime, date
from dateutil.relativedelta import relativedelta

# ========================
# API/Utility Views
# ========================

def obtener_metodos_pago(request):
    """Returns available payment methods."""
    metodos_pago = MetodoPago.objects.all()
    data = [{"id": metodo_pago.id, "display": metodo_pago.display} for metodo_pago in metodos_pago]
    return JsonResponse(data, safe=False)

def obtener_cliente(request):
    """Returns a list of all clients."""
    clientes = Cliente.objects.all()
    data = {'clientes': [cliente_to_dict(cliente) for cliente in clientes]}
    return JsonResponse(data, safe=False)

@csrf_exempt # Consider security implications, use Session or Token Auth if possible
@require_POST
def procesar_transaccion(request):
    """Processes a transaction, registers sold items, generates fiscal documents via websocket."""
    if request.method == 'POST': # require_POST decorator makes this check redundant
        logger.info("Iniciando procesar_transaccion")

        try:
            request_dict = request_on_procesar_transaccion_to_dict(request)
            logger.debug(f"Request Dict procesar_transaccion: {request_dict}")

            registro_dic = registrar_articulos_vendidos(request_dict)
            boletas_json = registro_dic["json"]
            logger.debug(f"JSON para boletas: {boletas_json}")

            numero_cbte = None
            tipo_cbte = None

            for boleta in boletas_json:
                try:
                    rta = asyncio.run(conectar_a_websocket(boleta))
                    logger.info(f"Respuesta Websocket (tipo {type(rta)}): {rta}")

                    respuesta = rta.get("rta")
                    if respuesta and isinstance(respuesta, list) and len(respuesta) > 0:
                        rta_interno = respuesta[0]
                        # logger.debug(f"rta_interno (tipo {type(rta_interno)}): {rta_interno}")
                        numero_cbte_str = rta_interno.get("rta")
                        numero_cbte = int(numero_cbte_str) if numero_cbte_str else None
                        # logger.debug(f"numero_cbte (tipo {type(numero_cbte)}): {numero_cbte}")
                        tipo_cbte = boleta.get('printTicket', {}).get('cabecera', {}).get('tipo_cbte')
                        logger.info(f"Boleta generada: Tipo={tipo_cbte}, Número={numero_cbte}")
                    else:
                         logger.warning("Formato de respuesta inesperado o vacío de websocket.")

                except asyncio.CancelledError as e:
                    logger.warning("La conexión websocket fue cancelada.", exc_info=True)
                    return HttpResponse("Ticket cancelado", status=500)
                except asyncio.TimeoutError as e:
                    logger.warning("Timeout esperando respuesta del websocket.", exc_info=True)
                    return HttpResponse("Tiempo de respuesta excedido", status=500)
                except ValueError as e:
                    logger.error(f"Error al convertir número de comprobante a entero: {numero_cbte_str}", exc_info=True)
                    return HttpResponse("Error en formato de número de comprobante", status=500)
                except Exception as e:
                    logger.error("Error inesperado durante la comunicación websocket o procesamiento de respuesta.", exc_info=True)
                    return HttpResponse("Error procesando boleta", status=500)

            # Cleanup cart items
            articulos = registro_dic.get("articulos")
            if articulos:
                articulos.delete()
                logger.info("Artículos del carrito eliminados.")
            articulos_sin_registro = registro_dic.get("articulos_sin_registro")
            if articulos_sin_registro:
                articulos_sin_registro.delete()
                logger.info("Artículos sin registro del carrito eliminados.")

            # Update transaction with fiscal document info
            transaccion = registro_dic.get("transaccion")
            if transaccion:
                try:
                    if tipo_cbte:
                        transaccion.tipo_cbte = tipo_cbte
                    if numero_cbte is not None:
                        transaccion.numero_cbte = numero_cbte
                    transaccion.save()
                    logger.info(f"Transacción ID {transaccion.id} actualizada con Tipo Cbte: {tipo_cbte}, Número Cbte: {numero_cbte}")
                except Exception as e:
                    logger.warning(f"No se pudo asignar tipo_cbte o numero_cbte a la transacción {transaccion.id}.", exc_info=True)
            else:
                 logger.warning("No se encontró objeto de transacción en registro_dic.")

            logger.info("procesar_transaccion completada exitosamente.")
            return HttpResponse(status=200)

        except Exception as e:
            logger.error("Error general en procesar_transaccion.", exc_info=True)
            return HttpResponse("Error interno del servidor", status=500)

    # This part might be unreachable due to @require_POST
    # else:
    #     logger.warning(f"Método {request.method} no permitido para procesar_transaccion.")
    #     return HttpResponse("Método no permitido", status=405)


@csrf_exempt # Consider security
@require_POST
def agregar_articulo_sin_registro(request):
    """Adds an item not present in the main inventory to the cart."""
    try:
        data = json.loads(request.body)
        logger.debug(f"Datos recibidos para agregar_articulo_sin_registro: {data}")

        descripcion = data.get('descripcion')
        cantidad_str = data.get('cantidad')
        precio_str = data.get('precio')
        carrito_id = data.get('carrito_id')

        if not all([descripcion, cantidad_str, precio_str, carrito_id]):
            logger.warning("Datos incompletos para agregar_articulo_sin_registro.")
            return JsonResponse({'error': 'Faltan datos'}, status=400)

        try:
            cantidad = float(cantidad_str) # Use DecimalField in model?
            precio = float(precio_str)     # Use DecimalField in model?
            carrito = Carrito.objects.get(id=carrito_id)
        except ValueError:
            logger.warning(f"Error al convertir cantidad ({cantidad_str}) o precio ({precio_str}) a número.")
            return JsonResponse({'error': 'Cantidad o precio inválido'}, status=400)
        except Carrito.DoesNotExist:
             logger.warning(f"Intento de agregar artículo a carrito inexistente ID: {carrito_id}")
             return JsonResponse({'error': 'Carrito no encontrado'}, status=404)

        # Handle potential duplicate descriptions within the same cart
        contador = ArticuloSinRegistro.objects.filter(carrito=carrito, descripcion__iexact=descripcion).count()
        descripcion_final = descripcion
        if contador > 0:
            # Find the highest existing number if any
            existing_suffixes = ArticuloSinRegistro.objects.filter(
                carrito=carrito,
                descripcion__startswith=descripcion + " " # Check for "Item X"
            ).values_list('descripcion', flat=True)

            max_num = 0
            for suffix_desc in existing_suffixes:
                 try:
                     num_part = suffix_desc.split(" ")[-1]
                     if num_part.isdigit():
                         max_num = max(max_num, int(num_part))
                 except:
                     pass # Ignore if suffix is not a number

            descripcion_final = f"{descripcion} {max_num + 1}"
            logger.debug(f"Descripción duplicada encontrada. Nueva descripción: {descripcion_final}")


        # Create or update the ArticuloSinRegistro
        # Using update_or_create is often cleaner for this pattern
        articulo_sin_registro, created = ArticuloSinRegistro.objects.update_or_create(
            descripcion=descripcion_final, # Use the potentially modified description
            carrito=carrito,
            defaults={'cantidad': cantidad, 'precio': precio}
        )

        if created:
            logger.info(f"Artículo sin registro '{descripcion_final}' creado en carrito {carrito_id}.")
        else:
             logger.info(f"Artículo sin registro '{descripcion_final}' actualizado en carrito {carrito_id}.")


        return JsonResponse({'articulo_sin_registro': articulo_sin_registro.id}, status=201 if created else 200)

    except json.JSONDecodeError:
        logger.error("Error al decodificar JSON en agregar_articulo_sin_registro.", exc_info=True)
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error("Error inesperado en agregar_articulo_sin_registro.", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@csrf_exempt # Consider security
@require_POST
def eliminar_articulo(request):
    """Removes a registered item from the cart and updates related order list."""
    try:
        data = json.loads(request.body)
        articulo_id = data.get('id')
        logger.info(f"Solicitud para eliminar artículo ID: {articulo_id}")

        if not articulo_id:
            logger.warning("ID de artículo faltante en solicitud de eliminación.")
            return JsonResponse({'error': 'ID de artículo requerido'}, status=400)

        try:
            articulo = Articulo.objects.select_related('item').get(id=articulo_id) # Optimize query
        except Articulo.DoesNotExist:
            logger.warning(f"Intento de eliminar artículo inexistente ID: {articulo_id}")
            return JsonResponse({'error': 'Artículo no encontrado'}, status=404)

        item_relacionado = articulo.item
        cantidad_articulo = articulo.cantidad

        # Update related Lista_Pedidos if exists
        try:
            # Use update to avoid race conditions if possible, or select_for_update
            pedido = Lista_Pedidos.objects.get(item=item_relacionado)
            pedido.cantidad -= cantidad_articulo
            pedido.save()
            logger.info(f"Actualizada cantidad en Lista_Pedidos para item {item_relacionado.id}. Nueva cantidad: {pedido.cantidad}")
        except Lista_Pedidos.DoesNotExist:
            logger.info(f"No se encontró Lista_Pedidos para item {item_relacionado.id}. No se requiere actualización.")
        except Exception as e:
            # Catching broad exception here might hide issues, be more specific if possible
            logger.error(f"Error actualizando Lista_Pedidos para item {item_relacionado.id}", exc_info=True)
            # Decide if this error should prevent article deletion or just be logged

        # Delete the Articulo
        descripcion_articulo = articulo.item.descripcion # Get description before deleting
        articulo.delete()
        logger.info(f"Artículo '{descripcion_articulo}' (ID: {articulo_id}) eliminado del carrito.")

        return JsonResponse({'status': 'success'}, status=200)

    except json.JSONDecodeError:
        logger.error("Error al decodificar JSON en eliminar_articulo.", exc_info=True)
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error("Error inesperado en eliminar_articulo.", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@csrf_exempt # Consider security
@require_POST
def actualizar_cantidad_articulo(request):
    """Updates the quantity of a registered item in the cart and related order list."""
    try:
        data = json.loads(request.body)
        articulo_id = data.get('id')
        cantidad_nueva_str = data.get('cantidad')
        logger.info(f"Solicitud para actualizar cantidad del artículo ID: {articulo_id} a: {cantidad_nueva_str}")

        if not articulo_id or cantidad_nueva_str is None:
             logger.warning("ID de artículo o nueva cantidad faltante en solicitud de actualización.")
             return JsonResponse({'error': 'ID y cantidad requeridos'}, status=400)

        try:
            cantidad_nueva = float(cantidad_nueva_str) # Use DecimalField in model?
            if cantidad_nueva < 0: # Add validation
                logger.warning(f"Intento de actualizar artículo ID {articulo_id} con cantidad negativa: {cantidad_nueva}")
                return JsonResponse({'error': 'La cantidad no puede ser negativa'}, status=400)
        except ValueError:
            logger.warning(f"Error al convertir nueva cantidad '{cantidad_nueva_str}' a número para artículo ID {articulo_id}.")
            return JsonResponse({'error': 'Cantidad inválida'}, status=400)

        try:
            # Use select_for_update to lock rows during transaction if high concurrency is expected
            articulo = Articulo.objects.select_related('item').get(id=articulo_id)
        except Articulo.DoesNotExist:
            logger.warning(f"Intento de actualizar cantidad de artículo inexistente ID: {articulo_id}")
            return JsonResponse({'error': 'Artículo no encontrado'}, status=404)

        cantidad_anterior = articulo.cantidad
        diferencia_cantidad = cantidad_nueva - cantidad_anterior

        # Update related Lista_Pedidos if exists
        try:
            pedido = Lista_Pedidos.objects.get(item=articulo.item)
            pedido.cantidad += diferencia_cantidad # Adjust based on the difference
            pedido.save()
            logger.info(f"Actualizada cantidad en Lista_Pedidos para item {articulo.item.id} por diferencia {diferencia_cantidad}. Nueva cantidad: {pedido.cantidad}")
        except Lista_Pedidos.DoesNotExist:
             logger.info(f"No se encontró Lista_Pedidos para item {articulo.item.id}. No se requiere actualización.")
        except Exception as e:
             logger.error(f"Error actualizando Lista_Pedidos para item {articulo.item.id}", exc_info=True)
             # Decide if this error should prevent article update or just be logged


        # Update the quantity of the Articulo
        articulo.cantidad = cantidad_nueva
        articulo.save()
        logger.info(f"Cantidad del artículo '{articulo.item.descripcion}' (ID: {articulo_id}) actualizada de {cantidad_anterior} a {cantidad_nueva}.")

        return JsonResponse({'status': 'success'}, status=200)

    except json.JSONDecodeError:
        logger.error("Error al decodificar JSON en actualizar_cantidad_articulo.", exc_info=True)
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error("Error inesperado en actualizar_cantidad_articulo.", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)

@csrf_exempt # Consider security
@require_POST
def eliminar_articulo_sin_registro(request):
    """Removes an unregistered item from the cart."""
    try:
        data = json.loads(request.body)
        articulo_sr_id = data.get('id')
        logger.info(f"Solicitud para eliminar artículo sin registro ID: {articulo_sr_id}")

        if not articulo_sr_id:
            logger.warning("ID de artículo sin registro faltante en solicitud de eliminación.")
            return JsonResponse({'error': 'ID de artículo sin registro requerido'}, status=400)

        try:
            articulo_sin_registro = ArticuloSinRegistro.objects.get(id=articulo_sr_id)
        except ArticuloSinRegistro.DoesNotExist:
            logger.warning(f"Intento de eliminar artículo sin registro inexistente ID: {articulo_sr_id}")
            return JsonResponse({'error': 'Artículo sin registro no encontrado'}, status=404)

        descripcion_articulo = articulo_sin_registro.descripcion # Get description before deleting
        articulo_sin_registro.delete()
        logger.info(f"Artículo sin registro '{descripcion_articulo}' (ID: {articulo_sr_id}) eliminado.")

        return JsonResponse({'status': 'success'}, status=200)

    except json.JSONDecodeError:
        logger.error("Error al decodificar JSON en eliminar_articulo_sin_registro.", exc_info=True)
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error("Error inesperado en eliminar_articulo_sin_registro.", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


@csrf_exempt # Consider security
@require_POST
def actualizar_cantidad_articulo_sin_registro(request):
    """Updates the quantity of an unregistered item in the cart."""
    try:
        data = json.loads(request.body)
        articulo_sr_id = data.get('id')
        cantidad_nueva_str = data.get('cantidad')
        logger.info(f"Solicitud para actualizar cantidad del artículo sin registro ID: {articulo_sr_id} a: {cantidad_nueva_str}")


        if not articulo_sr_id or cantidad_nueva_str is None:
             logger.warning("ID de artículo sin registro o nueva cantidad faltante en solicitud de actualización.")
             return JsonResponse({'error': 'ID y cantidad requeridos'}, status=400)

        try:
            cantidad_nueva = float(cantidad_nueva_str) # Use DecimalField in model?
            if cantidad_nueva < 0: # Add validation
                logger.warning(f"Intento de actualizar artículo sin registro ID {articulo_sr_id} con cantidad negativa: {cantidad_nueva}")
                return JsonResponse({'error': 'La cantidad no puede ser negativa'}, status=400)
        except ValueError:
            logger.warning(f"Error al convertir nueva cantidad '{cantidad_nueva_str}' a número para artículo sin registro ID {articulo_sr_id}.")
            return JsonResponse({'error': 'Cantidad inválida'}, status=400)

        try:
            articulo_sin_registro = ArticuloSinRegistro.objects.get(id=articulo_sr_id)
        except ArticuloSinRegistro.DoesNotExist:
            logger.warning(f"Intento de actualizar cantidad de artículo sin registro inexistente ID: {articulo_sr_id}")
            return JsonResponse({'error': 'Artículo sin registro no encontrado'}, status=404)

        cantidad_anterior = articulo_sin_registro.cantidad
        articulo_sin_registro.cantidad = cantidad_nueva
        articulo_sin_registro.save()
        logger.info(f"Cantidad del artículo sin registro '{articulo_sin_registro.descripcion}' (ID: {articulo_sr_id}) actualizada de {cantidad_anterior} a {cantidad_nueva}.")


        return JsonResponse({'status': 'success'}, status=200)

    except json.JSONDecodeError:
        logger.error("Error al decodificar JSON en actualizar_cantidad_articulo_sin_registro.", exc_info=True)
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        logger.error("Error inesperado en actualizar_cantidad_articulo_sin_registro.", exc_info=True)
        return JsonResponse({'error': 'Error interno del servidor'}, status=500)


# ========================
# Template Views
# ========================

class FacturacionMensual(TemplateView):
    """Displays monthly aggregated billing information."""
    template_name = 'facturacion/facturacion_mensual.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["barra_de_navegacion"] = NavBar.objects.all() # Cache this if possible

        transacciones = Transaccion.objects.all()
        # logger.debug(f"Query para transacciones mensuales: {transacciones.query}") # Log query if needed

        datos_agrupados = agrupar_transacciones_por_fecha(transacciones)
        context['datos_agrupados'] = datos_agrupados
        logger.debug(f"Datos agrupados por fecha para facturación mensual: {datos_agrupados}")


        return context

class Facturacion(TemplateView):
    """Displays daily billing information for a specific date."""
    template_name = 'facturacion/facturacion.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["barra_de_navegacion"] = NavBar.objects.all() # Cache this if possible

        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        day = self.kwargs.get('day')

        try:
            if all([year, month, day]):
                fecha_seleccionada = date(int(year), int(month), int(day))
            else:
                fecha_seleccionada = datetime.now().date() # Use today if no date is provided
        except ValueError:
             logger.warning(f"Fecha inválida recibida: año={year}, mes={month}, día={day}. Usando fecha actual.")
             # return HttpResponse("Fecha inválida") # Or redirect, or show error in template
             fecha_seleccionada = datetime.now().date() # Fallback to today

        logger.info(f"Obteniendo datos de facturación para fecha: {fecha_seleccionada}")
        transacciones = Transaccion.objects.filter(fecha__date=fecha_seleccionada)

        context["datos"] = transacciones
        context["fecha_actual"] = fecha_seleccionada # Pass date to template for display

        # Aggregate totals per payment method
        context["totales"] = []
        metodos_pago = MetodoPago.objects.all() # Fetch once
        for metodo in metodos_pago:
            ventas = transacciones.filter(metodo_de_pago=metodo) # Filter the already filtered queryset
            total_sum = ventas.aggregate(Sum("total"))["total__sum"] or 0 # Handle None if no sales
            count = ventas.count()

            if count > 0: # Only add payment methods with sales for that day
                data = {
                    "nombre": metodo.display,
                    "total": total_sum,
                    "cantidad": count,
                    "datos": ventas # Pass filtered transactions if needed in template
                }
                context["totales"].append(data)

        logger.debug(f"Totales calculados por método de pago: {context['totales']}")
        return context

    # get and post methods are inherited from TemplateView, defining them here
    # without adding functionality is usually unnecessary unless overriding.
    # def get(self, request, *args, **kwargs):
    #     return super().get(request, *args, **kwargs)

    # def post(self, request, *args, **kwargs):
    #     # Handle POST if needed, otherwise remove
    #     return super().post(request, *args, **kwargs)


class CierreZVieW(TemplateView):
    """Handles viewing past Z Closures and initiating a new one."""
    template_name = 'facturacion/cierre_z.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['barra_de_navegacion'] = NavBar.objects.all() # Cache this if possible
        return context

    def get(self, request, *args, **kwargs):
        """Displays the page with past Z closures."""
        context = self.get_context_data(**kwargs)
        context["cierres_fiscales"] = CierreZ.objects.order_by('-fecha') # Show newest first
        logger.info("Accediendo a la vista de Cierre Z (GET).")
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Initiates a new Z Closure via websocket."""
        context = self.get_context_data(**kwargs)
        logger.info("Iniciando proceso de Cierre Z (POST).")
        cierre_z_comando = {
            "dailyClose": "Z",
            "printerName": "IMPRESORA_FISCAL" # Make this configurable?
        }

        try:
            respuesta_ws_str = asyncio.run(conectar_a_websocket(cierre_z_comando))
            logger.info(f"Respuesta cruda del websocket para Cierre Z: {respuesta_ws_str}")

            # Safely parse the response string (assuming it looks like a dict)
            import ast
            try:
                # Using ast.literal_eval is safer than eval() but still assumes a Python literal structure
                data = ast.literal_eval(respuesta_ws_str)
                logger.debug(f"Respuesta parseada (tipo {type(data)}): {data}")

                if isinstance(data, dict) and "rta" in data and isinstance(data["rta"], list) and len(data["rta"]) > 0:
                    rta = data["rta"][0].get("rta")
                    if rta and isinstance(rta, dict):
                        logger.info(f"Datos RTA extraídos para Cierre Z: {rta}")

                        # Create and save CierreZ instance
                        # Add validation and default values for robustness
                        cierre_z_obj = CierreZ(
                            RESERVADO_SIEMPRE_CERO=int(rta.get("RESERVADO_SIEMPRE_CERO", 0)),
                            cant_doc_fiscales=int(rta.get("cant_doc_fiscales", 0)),
                            cant_doc_nofiscales_homologados=int(rta.get("cant_doc_nofiscales_homologados", 0)),
                            ultima_nc_a=int(rta.get("ultima_nc_a", 0)),
                            ultima_nc_b=int(rta.get("ultima_nc_b", 0)),
                            monto_percepciones=float(rta.get("monto_percepciones", 0.0)),
                            monto_percepciones_nc=float(rta.get("monto_percepciones_nc", 0.0)),
                            monto_credito_nc=float(rta.get("monto_credito_nc", 0.0)),
                            ultimo_doc_a=int(rta.get("ultimo_doc_a", 0)),
                            ultimo_doc_b=int(rta.get("ultimo_doc_b", 0)),
                            zeta_numero=rta.get("zeta_numero", "N/A"),
                            monto_imp_internos_nc=float(rta.get("monto_imp_internos_nc", 0.0)),
                            cant_doc_fiscales_cancelados=int(rta.get("cant_doc_fiscales_cancelados", 0)),
                            monto_iva_doc_fiscal=float(rta.get("monto_iva_doc_fiscal", 0.0)),
                            monto_imp_internos=float(rta.get("monto_imp_internos", 0.0)),
                            status_fiscal=rta.get("status_fiscal", "N/A"),
                            status_impresora=rta.get("status_impresora", "N/A"),
                            monto_iva_nc=float(rta.get("monto_iva_nc", 0.0)),
                            monto_ventas_doc_fiscal=float(rta.get("monto_ventas_doc_fiscal", 0.0)),
                            cant_doc_nofiscales=int(rta.get("cant_doc_nofiscales", 0))
                            # fecha_hora is usually auto_now_add=True in the model
                        )
                        cierre_z_obj.save()
                        logger.info(f"Nuevo Cierre Z guardado con ID: {cierre_z_obj.id} y número Z: {cierre_z_obj.zeta_numero}")
                        context['cierre_exitoso'] = True # Add flag for template feedback
                        context['nuevo_cierre'] = cierre_z_obj # Pass the new object if needed

                        # Trigger background tasks after successful closure
                        try:
                             ejecutar_cola_tareas()
                             logger.info("Cola de tareas ejecutada después del Cierre Z.")
                        except Exception as task_err:
                             logger.error("Error al ejecutar la cola de tareas después del Cierre Z.", exc_info=True)

                    else:
                        logger.error("Formato inesperado en la clave 'rta' interna de la respuesta del Cierre Z.")
                        context['error_procesamiento'] = "Formato de respuesta interna inválido."
                else:
                     logger.error("Formato inesperado en la respuesta principal del Cierre Z.")
                     context['error_procesamiento'] = "Formato de respuesta principal inválido."

            except (ValueError, SyntaxError, TypeError) as parse_err:
                 logger.error(f"Error al parsear la respuesta del websocket para Cierre Z: {parse_err}", exc_info=True)
                 context['error_procesamiento'] = f"Error al interpretar respuesta: {parse_err}"
            except Exception as db_err: # Catch potential DB errors during save
                 logger.error(f"Error al guardar el objeto CierreZ en la base de datos.", exc_info=True)
                 context['error_procesamiento'] = "Error al guardar el cierre en la base de datos."


        except asyncio.TimeoutError:
            logger.warning("Timeout esperando respuesta del websocket para Cierre Z.")
            context['error_websocket'] = "Tiempo de espera agotado conectando con impresora."
        except Exception as ws_err:
            logger.error("Error durante la comunicación websocket para Cierre Z.", exc_info=True)
            context['error_websocket'] = f"Error de conexión: {ws_err}"

        # Always re-fetch the list for the template after POST
        context["cierres_fiscales"] = CierreZ.objects.order_by('-fecha')
        return self.render_to_response(context)


class Clientes(TemplateView):
    """Handles adding new clients via a form."""
    template_name = 'facturacion/add_client.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["barra_de_navegacion"] = NavBar.objects.all() # Already in base template? If not, add it.
        return context

    def get(self, request, *args, **kwargs):
        """Displays the client creation form."""
        context = self.get_context_data(**kwargs)
        form = ClienteForm()
        context['form'] = form
        logger.info("Accediendo a la vista de agregar cliente (GET).")
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Processes the submitted client form."""
        logger.info("Procesando formulario de nuevo cliente (POST).")
        form = ClienteForm(request.POST)
        if form.is_valid():
            try:
                cliente = form.save()  # Guarda el cliente en la base de datos
                logger.info(f"Cliente '{cliente.razon_social}' (ID: {cliente.id}) guardado exitosamente.")
                # Add success message? messages.success(request, 'Cliente agregado correctamente.')
                return redirect('/buscador/') # Redirect on success
            except Exception as e:
                 logger.error("Error al guardar el nuevo cliente.", exc_info=True)
                 # Add error message? messages.error(request, 'Error al guardar el cliente.')
                 context = self.get_context_data(**kwargs)
                 context['form'] = form # Show form again with error flag maybe
                 return self.render_to_response(context)
        else:
            logger.warning(f"Formulario de cliente inválido: {form.errors}")
            context = self.get_context_data(**kwargs)
            context['form'] = form # Show form again with validation errors
            return self.render_to_response(context)

# ========================
# Fiscal Printer Commands (Generic)
# ========================

@csrf_exempt # Consider security, maybe internal API only?
def consulta_impresora_fiscal_generica(request):
    """Sends a generic command (GET/SET config) to the fiscal printer via websocket."""
    # Using GET for a configuration query is acceptable here.
    # If it were modifying state (like setConfigurationData), POST would be better.
    if request.method == 'GET':
        logger.info("Recibida solicitud GET para consulta_impresora_fiscal_generica.")
        # Example command - Get Configuration Data (0x96)
        # You might want to pass the command type via query parameters for flexibility
        comando = {
            "getConfigurationData": 0x96, # Hex value for Get Configuration
            "printerName": "IMPRESORA_FISCAL" # Make configurable?
        }
        # Example command - Set Configuration Data (0x65)
        # NUEVO_VALOR_MAXIMO = 999999999.00 # Use Decimal for currency
        # parametros_set = ("1000.00", "999999999.00", "0.00", "2", "P", "P", "P", "N", "P", "Cuenta Corriente", "P", "M", "M", "T", "M", "P", "N", "N", "P")
        # comando_set = {
        #     "setConfigurationData": [0x65, parametros_set],
        #     "printerName": "IMPRESORA_FISCAL",
        # }
        # Choose which command to send based on request or keep it fixed like this:
        comando_a_enviar = comando # Sending GET command by default

        logger.debug(f"Enviando comando a websocket: {comando_a_enviar}")
        try:
            respuesta_ws_str = asyncio.run(conectar_a_websocket(comando_a_enviar))
            logger.info(f"Respuesta cruda del websocket para consulta genérica: {respuesta_ws_str}")

            try:
                # Attempt to parse as JSON first, as many APIs return JSON
                data = json.loads(respuesta_ws_str)
                logger.debug("Respuesta parseada como JSON.")
                return JsonResponse(data, safe=False)
            except json.JSONDecodeError:
                # If not JSON, maybe it's the Python literal string format seen before?
                logger.warning("Respuesta no es JSON, intentando parsear como Python literal.")
                try:
                    import ast
                    data = ast.literal_eval(respuesta_ws_str)
                    logger.debug("Respuesta parseada como Python literal.")
                    # Decide if you want to return this dict as JSON
                    return JsonResponse(data, safe=False)
                except (ValueError, SyntaxError, TypeError):
                     logger.warning("Respuesta no pudo ser parseada como JSON ni Python literal. Devolviendo cruda.")
                     # Return the raw string if parsing fails completely
                     return JsonResponse({"respuesta_cruda": respuesta_ws_str})

        except asyncio.TimeoutError:
            logger.warning("Timeout esperando respuesta del websocket para consulta genérica.")
            return JsonResponse({"error": "Tiempo de espera agotado"}, status=504) # Gateway Timeout
        except Exception as e:
            logger.error(f"Error durante la comunicación websocket para consulta genérica.", exc_info=True)
            return JsonResponse({"error": f"Error al ejecutar el comando: {e}"}, status=500)
    else:
        logger.warning(f"Método {request.method} no permitido para consulta_impresora_fiscal_generica.")
        # Consider adding POST support if needed for SET commands
        return JsonResponse({"error": "Método no permitido"}, status=405)