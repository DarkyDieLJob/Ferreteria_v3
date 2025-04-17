# -*- coding: utf-8 -*-
from .classes import ComandoFiscal, TicketFactura
from bdd.models import Carrito, Articulo, ArticuloSinRegistro
from .models import Cliente, MetodoPago, Transaccion, ArticuloVendido
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse # Added JsonResponse for potential error returns
from django.db import transaction # Import transaction for atomic operations
# Import the configured logger
from .log_config import logger


# ======================================
# Helper Functions / Business Logic
# ======================================

# Note: These cycle functions seem designed for the older ComandoFiscal class.
# Ensure they are still relevant if you are primarily using TicketFactura.
def ciclo(fiscal=None):
    """Executes a standard fiscal command cycle (no overflow)."""
    if not isinstance(fiscal, ComandoFiscal):
        logger.error("Ciclo: Se requiere una instancia válida de ComandoFiscal.")
        return # Or raise error

    logger.info("Iniciando ciclo de comandos fiscales estándar.")
    # Assuming 'i' was meant to be ticket index 0 for a single ticket
    ticket_index = 0
    fiscal.set_encabezado(ticket_index)
    fiscal.set_tipo_cliente()
    fiscal.set_articulos() # Uses the method without factor calculation
    fiscal.set_cierre()
    logger.info("Ciclo de comandos fiscales estándar completado.")


def ciclo_desborde(fiscal=None):
    """Executes a fiscal command cycle handling potential ticket overflow."""
    if not isinstance(fiscal, ComandoFiscal):
        logger.error("Ciclo desborde: Se requiere una instancia válida de ComandoFiscal.")
        return # Or raise error

    # Log the number of tickets once before the loop
    num_tickets = getattr(fiscal, 'cantidad_tickets', 0) # Safely get attribute
    if num_tickets <= 0:
         logger.warning("Ciclo desborde: cantidad_tickets es inválido o cero. No se generarán tickets.")
         return

    logger.info(f"Iniciando ciclo de comandos fiscales con desborde: {num_tickets} tickets a generar.")
    for i in range(num_tickets):
        logger.debug(f"--- Generando Ticket {i+1}/{num_tickets} ---")
        fiscal.set_encabezado(i)
        fiscal.set_tipo_cliente()
        fiscal.set_articulos_desborde() # Uses the method WITH factor calculation
        fiscal.set_cierre()
        logger.debug(f"--- Ticket {i+1}/{num_tickets} completado ---")
    logger.info(f"Ciclo de comandos fiscales con desborde ({num_tickets} tickets) completado.")


def cliente_to_dict(cliente):
    """Converts a Cliente object to a dictionary."""
    if not isinstance(cliente, Cliente):
        logger.warning("cliente_to_dict recibió un objeto que no es Cliente.")
        return {} # Return empty dict or None
    data = {
        'id': cliente.id,
        "razon_social": cliente.razon_social,
        "cuit_dni": cliente.cuit_dni,
        "domicilio": cliente.domicilio,
        "telefono": cliente.telefono,
        # Consider adding other relevant fields like 'responsabilidad_iva', 'tipo_documento'
    }
    # logger.debug(f"Cliente {cliente.id} convertido a diccionario: {data}") # Optional: Log if needed
    return data


def request_on_procesar_transaccion_to_dict(request):
    """Extracts relevant data from a POST request for transaction processing."""
    # Consider adding default values or error handling if keys might be missing
    data = {
        "nombre_usuario": request.POST.get('usuario'),
        "carrito_id": request.POST.get('carrito_id'),
        "id_cliente": request.POST.get('cliente_id'), # Can be empty string or None
        "total": request.POST.get('total'),
        "total_efectivo": request.POST.get('total_efectivo'), # Might be missing if not cash
        "articulos_vendidos": request.POST.get('articulos_vendidos'), # Usage of this field seems unclear later
        "id_metodo_de_pago": request.POST.get('metodo_de_pago'),
    }
    logger.debug(f"Datos extraídos del request para procesar transacción: {data}")
    return data


@transaction.atomic # Ensure all DB operations succeed or fail together
def registrar_articulos_vendidos(request_dict):
    """
    Creates a Transaccion, associates sold items (ArticuloVendido),
    and prepares the JSON for fiscal ticket generation (if applicable).

    Args:
        request_dict (dict): Dictionary containing data extracted from the request.

    Returns:
        dict: A dictionary containing 'json' (for websocket), 'articulos' (queryset),
              'articulos_sin_registro' (queryset), and 'transaccion' (object).
              Returns None or raises an exception on critical error.
    """
    logger.info("Iniciando registro de artículos vendidos y creación de transacción.")
    logger.debug(f"Datos recibidos: {request_dict}")

    # --- 1. Fetch related objects ---
    try:
        usuario = User.objects.get(username=request_dict.get('nombre_usuario'))
        metodo_de_pago = MetodoPago.objects.get(id=request_dict.get('id_metodo_de_pago'))
        carrito = Carrito.objects.get(id=request_dict.get('carrito_id'))
        # Prefetch related items for efficiency when iterating later
        articulos = Articulo.objects.filter(carrito=carrito).select_related('item')
        articulos_sin_registro = ArticuloSinRegistro.objects.filter(carrito=carrito)
        logger.debug(f"Objetos relacionados encontrados: Usuario='{usuario.username}', MetodoPago ID={metodo_de_pago.id}, Carrito ID={carrito.id}")

    except User.DoesNotExist:
        logger.error(f"Usuario '{request_dict.get('nombre_usuario')}' no encontrado.")
        # Return a dictionary indicating failure, or raise a specific exception
        # return {"error": "Usuario no encontrado", "status": 404}
        raise ValueError(f"Usuario '{request_dict.get('nombre_usuario')}' no encontrado.")
    except MetodoPago.DoesNotExist:
        logger.error(f"Método de pago con ID '{request_dict.get('id_metodo_de_pago')}' no encontrado.")
        raise ValueError(f"Método de pago ID '{request_dict.get('id_metodo_de_pago')}' inválido.")
    except Carrito.DoesNotExist:
        logger.error(f"Carrito con ID '{request_dict.get('carrito_id')}' no encontrado.")
        raise ValueError(f"Carrito ID '{request_dict.get('carrito_id')}' inválido.")
    except Exception as e:
        logger.error(f"Error inesperado al buscar objetos relacionados: {e}", exc_info=True)
        raise # Re-raise unexpected errors

    # --- 2. Determine Amount Paid ---
    metodo_de_pago_display = metodo_de_pago.display.lower() if metodo_de_pago.display else ""
    total_request = request_dict.get('total', '0')
    total_efectivo_request = request_dict.get('total_efectivo') # Can be None

    logger.debug(f"Determinando monto abonado: metodo='{metodo_de_pago_display}', total_req={total_request}, total_efectivo_req={total_efectivo_request}")

    monto_abonado_str = total_request # Default to total from request
    # Use efectivo total only if method is cash AND efectivo total is provided
    if metodo_de_pago_display in ["efectivo con ticket", "efectivo s/ticket"] and total_efectivo_request is not None:
        monto_abonado_str = total_efectivo_request
        logger.debug("Usando total_efectivo como monto abonado.")
    else:
         logger.debug("Usando total normal como monto abonado.")

    try:
         # Convert final amount to float, handle potential errors
         monto_abonado_float = float(monto_abonado_str or 0.0)
         logger.info(f"Monto abonado determinado: {monto_abonado_float:.2f}")
    except (ValueError, TypeError):
         logger.error(f"Monto abonado inválido: '{monto_abonado_str}'. No se puede crear transacción.")
         raise ValueError(f"Monto abonado inválido: '{monto_abonado_str}'.")


    # --- 3. Create Transaction ---
    try:
        transaccion = Transaccion.objects.create(
            usuario=usuario,
            metodo_de_pago=metodo_de_pago,
            total=monto_abonado_float,
            # cliente field will be set later if applicable
        )
        logger.info(f"Transacción ID {transaccion.id} creada exitosamente.")
    except Exception as e:
        logger.error("Error al crear la instancia de Transaccion.", exc_info=True)
        raise # Re-raise critical error

    # --- 4. Create and Associate Sold Items ---
    logger.debug("Creando y asociando ArticuloVendido a la transacción...")
    articulos_vendidos_creados = []
    try:
        # Combine lists for iteration
        items_en_carrito = list(articulos) + list(articulos_sin_registro)
        if not items_en_carrito:
             logger.warning(f"Carrito ID {carrito.id} está vacío. No se crearán ArticuloVendido.")

        for articulo_carrito in items_en_carrito:
            # Create ArticuloVendido instance
            if isinstance(articulo_carrito, Articulo):
                articulo_vendido = ArticuloVendido(
                    item=articulo_carrito.item, # Use related item
                    cantidad=articulo_carrito.cantidad,
                    # Add precio_unitario_momento_venta if needed
                    # precio_unitario = articulo_carrito.item.final_efectivo if self.pago_efectivo else articulo_carrito.item.final
                )
                logger.debug(f"Creando ArticuloVendido para Item ID {articulo_carrito.item.id} (Cant: {articulo_carrito.cantidad})")
            else: # ArticuloSinRegistro
                articulo_vendido = ArticuloVendido(
                    sin_registrar=articulo_carrito, # Link to the ArticuloSinRegistro instance
                    cantidad=articulo_carrito.cantidad
                    # Add precio_unitario_momento_venta if needed
                    # precio_unitario = articulo_carrito.precio
                )
                logger.debug(f"Creando ArticuloVendido para ArticuloSinRegistro ID {articulo_carrito.id} (Cant: {articulo_carrito.cantidad})")

            # Save the ArticuloVendido instance first
            articulo_vendido.save()
            articulos_vendidos_creados.append(articulo_vendido)

        # Associate all created ArticuloVendido instances to the Transaccion at once
        if articulos_vendidos_creados:
            transaccion.articulos_vendidos.set(articulos_vendidos_creados)
            logger.info(f"{len(articulos_vendidos_creados)} ArticuloVendido asociados a la transacción ID {transaccion.id}.")
        else:
            logger.info(f"No se asociaron ArticuloVendido a la transacción ID {transaccion.id} (carrito vacío).")


    except Exception as e:
        logger.error("Error al crear o asociar ArticuloVendido.", exc_info=True)
        # Depending on policy, you might want to delete the created Transaccion here
        # transaccion.delete()
        raise # Re-raise critical error


    # --- 5. Prepare Fiscal Ticket JSON (if applicable) ---
    json_para_websocket = [] # Initialize as empty list (as TicketFactura returns a list)

    # Check conditions for generating a fiscal ticket
    # MetodoPago ID 1 assumed to be "No generar comprobante" or similar
    id_metodo_pago_int = int(metodo_de_pago.id)
    id_cliente_str = request_dict.get('id_cliente') # Can be None or empty string ''

    if id_metodo_pago_int != 1 and id_cliente_str is not None: # Need client info (even if empty for Consumidor Final)
        logger.info("Preparando JSON para ticket fiscal.")
        cliente_id_para_ticket = None
        if not id_cliente_str: # Handle empty string as Consumidor Final default (ID 1)
            cliente_id_para_ticket = 1
            logger.debug("ID Cliente vacío, usando ID 1 (Consumidor Final) para ticket.")
        else:
            try:
                cliente_id_para_ticket = int(id_cliente_str)
                logger.debug(f"ID Cliente para ticket: {cliente_id_para_ticket}")
            except (ValueError, TypeError):
                logger.error(f"ID de cliente inválido ('{id_cliente_str}') para generar ticket. Abortando generación de JSON.")
                # Decide how to handle this: skip JSON, raise error?
                # For now, we'll just skip JSON generation.
                cliente_id_para_ticket = None # Ensure it stays None

        # Assign Client to Transaction and generate JSON if ID is valid
        if cliente_id_para_ticket is not None:
            try:
                cliente_obj = Cliente.objects.get(id=cliente_id_para_ticket)
                transaccion.cliente = cliente_obj
                transaccion.save(update_fields=['cliente']) # Save only the updated field
                logger.info(f"Cliente ID {cliente_id_para_ticket} asignado a la transacción ID {transaccion.id}.")

                # Generate the ticket JSON using the updated transaction
                ticket_factura = TicketFactura(transaccion)
                json_para_websocket = ticket_factura.get_ticket_json()
                logger.info("JSON para ticket fiscal generado.")

            except Cliente.DoesNotExist:
                logger.error(f"Cliente con ID {cliente_id_para_ticket} no encontrado al intentar asignar a transacción. No se generará JSON.")
                # JSON remains empty list
            except Exception as e:
                logger.error("Error al generar TicketFactura JSON.", exc_info=True)
                # JSON remains empty list or handle error differently
    else:
        logger.info("No se requiere ticket fiscal (Método de pago ID 1 o ID Cliente no proporcionado).")


    # --- 6. Return Results ---
    logger.info("Registro de artículos vendidos completado.")
    return {
        "json": json_para_websocket,
        "articulos": articulos, # Original queryset from carrito
        "articulos_sin_registro": articulos_sin_registro, # Original queryset from carrito
        "transaccion": transaccion, # The created transaction object
    }