# -*- coding: utf-8 -*-
from django.db.models import FloatField, ExpressionWrapper
from boletas.models import Boleta, OrdenComando, Comando
from django.db.models import F, Sum
import math
from bdd.models import Carrito, Articulo, ArticuloSinRegistro
from facturacion.models import Cliente, Transaccion
# Import the configured logger
from .log_config import logger

# ======================================
# Classes for New Ticket Generation (JSON based)
# ======================================

class FormasPago():
    """Represents payment information for a transaction."""
    ds = "Cuenta Corriente" # Default value, maybe remove if always set in init
    importe = 4924.39      # Default value, maybe remove if always set in init

    def __init__(self, transaccion):
        self.tr = transaccion
        try:
            # Ensure related object exists before accessing attributes
            self.ds = self.tr.metodo_de_pago.display
            self.importe = self.tr.total
            logger.debug(f"FormasPago inicializado: ds='{self.ds}', importe={self.importe}")
        except AttributeError as e:
            logger.error(f"Error al inicializar FormasPago para transacción {transaccion.id}: {e}", exc_info=True)
            # Set defaults or raise an error depending on desired behavior
            self.ds = "Error"
            self.importe = 0.0

    def get_importe(self):
        """Returns the payment amount as a rounded float."""
        try:
            # Convert to float robustly and round
            importe_float = float(self.importe)
            return round(importe_float, 2)
        except (ValueError, TypeError) as e:
            logger.warning(f"No se pudo convertir el importe '{self.importe}' a float en FormasPago: {e}")
            return 0.0 # Return default on conversion error

    def get_formas_pago_json(self, cant=1):
        """Generates the JSON structure for payment methods, dividing amount if needed."""
        if cant <= 0:
            logger.warning(f"Cantidad inválida ({cant}) en get_formas_pago_json. Usando 1.")
            cant = 1
        importe_dividido = round(self.get_importe() / cant, 2)
        json_data = {
            "formasPago": [
                {
                    "ds": self.ds,
                    "importe": float(importe_dividido), # Ensure it's float for JSON
                },
            ]
        }
        logger.debug(f"FormasPago JSON generado: {json_data}")
        return json_data

    def get_efectivo(self):
        """Checks if the payment method is considered 'Efectivo'."""
        # Make comparison case-insensitive and handle potential None values
        ds_lower = self.ds.lower() if self.ds else ""
        efectivo = ds_lower in ["efectivo s/ticket", "efectivo con ticket"]
        logger.debug(f"get_efectivo para '{self.ds}': {efectivo}")
        return efectivo

class TicketCabecera():
    """Represents the header information for a fiscal ticket based on client data."""
    cliente = None # Initialize as None
    tipo_cbte = "FB"
    nro_doc = '0'
    domicilio_cliente = ' '
    tipo_doc = 'DNI'
    nombre_cliente = 'M' # Default? Consider 'Consumidor Final'
    tipo_responsable = 'CONSUMIDOR_FINAL'
    cabezera_json = {}

    def __init__(self, cliente_id=None):
        logger.debug(f"TicketCabecera.__init__ - Cliente ID recibido: {cliente_id}")
        # Validate cliente_id format before querying
        valid_id = False
        if cliente_id is not None:
            try:
                cliente_id_int = int(cliente_id)
                valid_id = True
            except (ValueError, TypeError):
                logger.warning(f"TicketCabecera.__init__ - ID de cliente inválido: '{cliente_id}'. Usando consumidor final.")

        if valid_id and cliente_id_int != 1: # Assuming ID 1 is Consumidor Final default
            try:
                self.cliente = Cliente.objects.get(id=cliente_id_int)
                logger.debug(f"TicketCabecera.__init__ - Cliente encontrado: {self.cliente}")

                # Determine ticket type and client details based on fetched client
                responsabilidad = self.cliente.get_responsabilidad() # Call method once
                if responsabilidad == 'EXENTO':
                    self.tipo_cbte = "FB"
                elif responsabilidad == 'RESPONSABLE_INSCRIPTO': # Be explicit
                    self.tipo_cbte = "FA"
                else: # Other cases default to B?
                    self.tipo_cbte = "FB"
                    logger.debug(f"Cliente {cliente_id_int} con responsabilidad '{responsabilidad}', usando tipo_cbte FB.")

                self.nro_doc = (self.cliente.cuit_dni or '').replace("-", "") # Handle potential None
                self.domicilio_cliente = self.cliente.domicilio or ' '
                self.tipo_doc = self.cliente.get_tipo_documento()
                self.nombre_cliente = self.cliente.razon_social or ' '
                self.tipo_responsable = responsabilidad

                logger.debug(f"Cabecera configurada para cliente ID {cliente_id_int}: tipo_cbte={self.tipo_cbte}, tipo_resp={self.tipo_responsable}")

            except Cliente.DoesNotExist:
                logger.warning(f"TicketCabecera.__init__ - Cliente con ID {cliente_id_int} no encontrado. Usando consumidor final.")
                # Reset to default consumer final values if client not found
                self._set_consumidor_final_defaults()
            except Exception as e:
                 logger.error(f"Error al obtener datos del cliente ID {cliente_id_int}: {e}", exc_info=True)
                 self._set_consumidor_final_defaults()
        else:
            logger.debug("Usando datos de Consumidor Final por defecto.")
            self._set_consumidor_final_defaults()

    def _set_consumidor_final_defaults(self):
        """Resets attributes to default 'Consumidor Final' values."""
        self.cliente = None # Or fetch the actual default client object if ID 1 exists and is needed elsewhere
        self.tipo_cbte = "FB"
        self.nro_doc = '0'
        self.domicilio_cliente = ' '
        self.tipo_doc = 'DNI'
        self.nombre_cliente = 'Consumidor Final' # More descriptive default
        self.tipo_responsable = 'CONSUMIDOR_FINAL'

    def get_boleta_a(self):
        """Checks if the ticket type is 'FA'."""
        boleta_a = self.tipo_cbte == "FA"
        logger.debug(f"get_boleta_a para tipo_cbte '{self.tipo_cbte}': {boleta_a}")
        return boleta_a

    def get_cabezera_json(self):
        """Generates the JSON structure for the ticket header."""
        # The structure seems the same regardless of client ID 1 or not, based on code
        self.cabezera_json = {
            "cabecera": {
                "tipo_cbte": self.tipo_cbte,
                "nro_doc": self.nro_doc,
                "domicilio_cliente": self.domicilio_cliente,
                "tipo_doc": self.tipo_doc,
                "nombre_cliente": self.nombre_cliente,
                "tipo_responsable": self.tipo_responsable
            },
        }
        logger.debug(f"Cabecera JSON generada: {self.cabezera_json}")
        return self.cabezera_json

class TicketItem():
    """Represents a single item line within a fiscal ticket."""
    # Defaults - Consider removing if always set in init
    alic_iva = 21.0
    importe = 0.0
    importe_efectivo = 0.0
    ds = "Producto"
    qty = 0.0
    tasaAjusteInternos = 0.0
    efectivo = False # This seems unused within the class itself

    def __init__(self, data):
        """Initializes item from a dictionary."""
        logger.debug(f"TicketItem inicializado con datos: {data}")
        dic_item = data or {} # Ensure data is a dict

        # Assign values safely, providing defaults
        self.alic_iva = float(dic_item.get('alic_iva', 21.0)) # Assuming 21 is default IVA
        self.importe = float(dic_item.get('importe', 0.0))
        self.importe_efectivo = float(dic_item.get('importe_efectivo', self.importe)) # Default efectivo price to normal price if missing
        self.ds = str(dic_item.get('ds', 'Producto'))
        self.qty = float(dic_item.get('qty', 0.0))
        self.tasaAjusteInternos = float(dic_item.get('tasaAjusteInternos', 0.0))

    def set_div_cant(self, cantidad):
        """Divides the item quantity, typically for splitting tickets."""
        if cantidad <= 0:
             logger.warning(f"Intento de dividir cantidad por cero o negativo ({cantidad}) en set_div_cant para item '{self.ds}'. No se modifica la cantidad.")
             return
        original_qty = self.qty
        self.qty = round(self.qty / cantidad, 8) # Use high precision for division result
        logger.debug(f"Item '{self.ds}': cantidad dividida por {cantidad}. Nueva qty: {self.qty} (original: {original_qty})")


    def get_item_json(self, efectivo=False, boleta_a=False):
        """Generates the JSON structure for the item line."""
        if efectivo:
            importe_base = self.importe_efectivo
            logger.debug(f"Item '{self.ds}': Usando importe_efectivo: {importe_base}")
        else:
            importe_base = self.importe
            logger.debug(f"Item '{self.ds}': Usando importe normal: {importe_base}")

        # Adjust price for 'Boleta A' (remove VAT)
        if boleta_a:
            # The factor 0.82644 corresponds to 1 / 1.21 (removing 21% VAT)
            # Ensure this calculation is fiscally correct for your region/printer.
            precio_sin_iva = round(float(importe_base) / 1.21, 4) # Use higher precision for intermediate calc
            logger.debug(f"Item '{self.ds}': Boleta A detectada. Calculando precio sin IVA: {precio_sin_iva} (desde {importe_base})")
            importe_final = precio_sin_iva
        else:
            importe_final = importe_base

        # Final rounding for the JSON output
        importe_final_rounded = round(importe_final, 2)

        item_json = {
            'alic_iva': float(self.alic_iva), # Ensure float
            'ds': self.ds[:30] if len(self.ds) > 30 else self.ds, # Truncate description if too long (adjust limit as needed)
            'importe': float(importe_final_rounded), # Ensure float
            'qty': float(round(self.qty, 3)), # Round quantity for JSON (adjust precision as needed)
            'tasaAjusteInternos': float(self.tasaAjusteInternos) # Ensure float
        }
        logger.debug(f"Item JSON generado para '{self.ds}': {item_json}")
        return item_json

class TicketFactura():
    """Orchestrates the creation of the complete fiscal ticket JSON."""
    cantidad = 1 # Number of tickets to split into (if total exceeds limit)
    PRINTNAME = "IMPRESORA_FISCAL" # Make configurable?

    def __init__(self, transaccion):
        if not isinstance(transaccion, Transaccion):
            logger.error("TicketFactura requiere una instancia válida de Transaccion.")
            raise ValueError("Se requiere una instancia de Transaccion válida.")

        self.transaccion = transaccion
        logger.info(f"Creando TicketFactura para Transacción ID: {self.transaccion.id}")

        self.formas_pago = FormasPago(self.transaccion)

        cliente_id = self.transaccion.get_cliente_id() # Get ID once
        logger.debug(f"TicketFactura.__init__ - ID Cliente obtenido de transacción: {cliente_id}")
        self.cabecera = TicketCabecera(cliente_id)

        # Determine if splitting is needed (example limit)
        # Make the limit configurable (e.g., from settings)
        MONTO_LIMITE_TICKET = 999999999.00 # Use a more realistic limit if needed
        importe_total = self.formas_pago.get_importe()
        if importe_total > MONTO_LIMITE_TICKET and MONTO_LIMITE_TICKET > 0:
            self.cantidad = math.ceil(importe_total / MONTO_LIMITE_TICKET)
            logger.info(f"Importe total ({importe_total}) excede límite ({MONTO_LIMITE_TICKET}). Se generarán {self.cantidad} tickets.")
        else:
            self.cantidad = 1
            logger.debug(f"Importe total ({importe_total}) dentro del límite. Se generará 1 ticket.")


        # Initialize and populate items
        self.items = []
        # Use select_related or prefetch_related in the view if performance is an issue
        for articulo_vendido in self.transaccion.articulos_vendidos.all():
            try:
                item_data = articulo_vendido.get_item() # Assumes this method returns the dict needed by TicketItem
                if item_data:
                    ticket_item = TicketItem(item_data)
                    self.items.append(ticket_item)
                else:
                    logger.warning(f"ArticuloVendido ID {articulo_vendido.id} devolvió datos vacíos en get_item().")
            except Exception as e:
                 logger.error(f"Error al procesar ArticuloVendido ID {articulo_vendido.id}: {e}", exc_info=True)

        logger.debug(f"TicketFactura inicializado con {len(self.items)} items.")


    def setear_items(self):
        """Adjusts item quantities if the ticket is being split."""
        if self.cantidad > 1:
            logger.info(f"Ajustando cantidades de items para {self.cantidad} tickets.")
            for item in self.items:
                item.set_div_cant(self.cantidad)
        else:
            logger.debug("No se requiere ajuste de cantidad de items (cantidad=1).")

    def get_items_json(self, efectivo, boleta_a):
        """Generates the JSON list structure for all items."""
        items_json_list = {'items': []}
        logger.debug(f"Generando JSON de items: efectivo={efectivo}, boleta_a={boleta_a}")
        for ticket_item in self.items:
             items_json_list['items'].append(ticket_item.get_item_json(efectivo=efectivo, boleta_a=boleta_a))
        logger.debug(f"JSON de items generado: {items_json_list}")
        return items_json_list

    def get_ticket_json(self):
        """Generates the final list of JSON tickets to be sent."""
        json_list = []
        self.setear_items() # Adjust quantities first

        # Determine common flags once
        es_efectivo = self.formas_pago.get_efectivo()
        es_boleta_a = self.cabecera.get_boleta_a()

        logger.info(f"Generando {self.cantidad} ticket(s) JSON...")
        for i in range(self.cantidad):
            ticket_json = {"printTicket": {}} # Start fresh for each ticket in the list
            ticket_json["printTicket"].update(self.cabecera.get_cabezera_json())
            ticket_json["printTicket"].update(self.get_items_json(es_efectivo, es_boleta_a))
            ticket_json["printTicket"].update(self.formas_pago.get_formas_pago_json(self.cantidad))
            ticket_json.update({"printerName": self.PRINTNAME})

            # Add sequence number if splitting tickets (optional, printer might handle it)
            # if self.cantidad > 1:
            #    ticket_json["printTicket"]["observaciones"] = f"Comprobante {i+1} de {self.cantidad}"

            json_list.append(ticket_json)
            logger.debug(f"Ticket JSON {i+1}/{self.cantidad} generado.")

        logger.info(f"Generación de {len(json_list)} ticket(s) JSON completada.")
        # Log the final JSON structure only at debug level as it can be large
        logger.debug(f"TicketFactura.get_ticket_json - JSON final generado: {json_list}")

        return json_list

# ======================================
# Classes for Old Command-Based Fiscal Printer Interaction (Example)
# ======================================

class ComandoFiscal():
    """Handles creation of command sequences for older fiscal printers."""
    # Constants for commands (use descriptive names)
    CMD_GET_STATUS = "*"
    CMD_HISTORY_CAPACITY = '7'
    CMD_INFORME_Z = '9\x1cX'
    CMD_CIERRE_FISCAL_Z = '9\x1cZ'
    CMD_GET_WORKING_MEMORY = 'g'
    CMD_SENT_FIRST_IVA = 'p\x1cD'
    CMD_NEXT_IVA_TRANSMISSION = 'q'
    CMD_SUB_TOTAL = "C\x1cP\x1cSubtotal\x1c0" # Text might vary by printer
    CMD_CLOSE_FISCAL_RECEIPT = "E"
    CMD_SET_FANTASY_NAME_BASE = "_\x1c1\x1c" # Base part

    DEFAULT_FANTASY_NAME = "Pinturería y Ferretería Paoli" # Configurable?
    MONTO_LIMITE_TICKET_CMD = 25000.00 # Configurable? Example limit for command-based printers

    def __init__(self, carrito_id=None, id_cliente=None, tipo_pago=None, monto_abonado="0"):
        logger.info(f"Inicializando ComandoFiscal: carrito_id={carrito_id}, id_cliente={id_cliente}, tipo_pago='{tipo_pago}'")

        if not carrito_id:
            logger.error("ComandoFiscal requiere un carrito_id.")
            raise ValueError("carrito_id es requerido.")

        try:
            self.carrito = Carrito.objects.prefetch_related(
                'articulo_set__item', # Prefetch related items for Articulo
                'articulosinregistro_set' # Prefetch ArticuloSinRegistro
            ).get(id=carrito_id)
            # Access prefetched items directly later
            self.articulos = list(self.carrito.articulo_set.all())
            self.articulos_sin_registro = list(self.carrito.articulosinregistro_set.all())
            logger.debug(f"Carrito ID {carrito_id} cargado con {len(self.articulos)} artículos y {len(self.articulos_sin_registro)} artículos sin registro.")
        except Carrito.DoesNotExist:
            logger.error(f"Carrito con ID {carrito_id} no encontrado.")
            raise ValueError(f"Carrito con ID {carrito_id} no encontrado.")

        # Determine Client and Ticket Type
        self.cliente = None
        self.tipo_boleta = 'B' # Default to B
        if id_cliente:
            try:
                self.cliente = Cliente.objects.get(id=id_cliente)
                # Use constants or model choices for 'responsabilidad_iva'
                if self.cliente.responsabilidad_iva == 'I': # Assuming 'I' means RESPONSABLE_INSCRIPTO
                    self.tipo_boleta = 'A'
                logger.debug(f"Cliente ID {id_cliente} encontrado. Tipo de boleta: {self.tipo_boleta}")
            except Cliente.DoesNotExist:
                logger.warning(f"Cliente ID {id_cliente} no encontrado. Usando boleta tipo B.")
            except Exception as e:
                 logger.error(f"Error al obtener cliente ID {id_cliente}: {e}", exc_info=True)


        # Payment Type Handling
        self.tipo_pago = tipo_pago or "Otros Medios" # Default if None
        logger.debug(f"ComandoFiscal - Tipo de pago efectivo: {self.tipo_pago}")
        # Be explicit and case-insensitive for 'Efectivo' check
        self.pago_efectivo = isinstance(self.tipo_pago, str) and self.tipo_pago.lower() == 'efectivo con ticket'
        logger.debug(f"ComandoFiscal - pago_efectivo={self.pago_efectivo}")

        # Initialize Boleta and Command Order
        self.orden = 1
        try:
            self.boleta = Boleta.objects.create(tipo=self.tipo_boleta)
            logger.info(f"Creada nueva Boleta ID: {self.boleta.id}, Tipo: {self.tipo_boleta}")
        except Exception as e:
            logger.error("Error al crear el objeto Boleta en la base de datos.", exc_info=True)
            raise  # Re-raise the exception as this is critical

        # Calculate Total and Ticket Splitting
        self.sub_total = 0 # This will be calculated during item processing
        try:
            self.monto_abonado = float(monto_abonado or 0.0)
        except (ValueError, TypeError):
            logger.warning(f"Monto abonado inválido ('{monto_abonado}'). Usando 0.0.")
            self.monto_abonado = 0.0

        self.factor = 1.0
        self.cantidad_tickets = 1
        total_calculado = self._calcular_total_carrito() # Calculate total based on payment type

        if total_calculado > self.MONTO_LIMITE_TICKET_CMD and self.MONTO_LIMITE_TICKET_CMD > 0:
            self.cantidad_tickets = math.ceil(total_calculado / self.MONTO_LIMITE_TICKET_CMD)
            self.factor = 1.0 / self.cantidad_tickets
            logger.info(f"Total calculado ({total_calculado}) excede límite ({self.MONTO_LIMITE_TICKET_CMD}). Se generarán {self.cantidad_tickets} tickets (factor: {self.factor}).")
        else:
            logger.debug(f"Total calculado ({total_calculado}) dentro del límite. Se generará 1 ticket.")

        # Set dynamic commands based on init params
        self.CMD_OPEN_FISCAL_RECEIPT = f"@\x1c{self.tipo_boleta}\x1cS" # Command to open receipt


    def _calcular_total_carrito(self):
        """Calculates the total amount for the cart based on payment type."""
        total_acumulado = 0.0
        precio_field = 'item__final_efectivo' if self.pago_efectivo else 'item__final'
        logger.debug(f"Calculando total del carrito usando precio: '{precio_field if self.pago_efectivo else 'item__final'}'")

        # Sum for Articulo (using prefetched data)
        for art in self.articulos:
            try:
                if self.pago_efectivo:
                    precio = float(art.item.final_efectivo or 0.0)
                else:
                    precio = float(art.item.final or 0.0)
                cantidad = float(art.cantidad or 0.0)
                total_acumulado += cantidad * precio
            except AttributeError:
                 logger.warning(f"Artículo {art.id} o su item relacionado no tiene el campo de precio esperado.")
            except (ValueError, TypeError):
                 logger.warning(f"Error al convertir precio o cantidad para artículo {art.id}")


        # Sum for ArticuloSinRegistro (using prefetched data)
        for art_sr in self.articulos_sin_registro:
             try:
                precio = float(art_sr.precio or 0.0)
                cantidad = float(art_sr.cantidad or 0.0)
                total_acumulado += cantidad * precio
             except (ValueError, TypeError):
                 logger.warning(f"Error al convertir precio o cantidad para artículo sin registro {art_sr.id}")

        logger.debug(f"Total calculado para el carrito: {total_acumulado}")
        return total_acumulado


    def _add_comando(self, comando_str, orden):
        """Adds a command to the Boleta's sequence."""
        if not isinstance(comando_str, str) or not comando_str:
            logger.warning(f"Intento de agregar comando inválido (orden {orden}): {comando_str}")
            return
        try:
            # Use update_or_create for Comando if they are truly static strings
            comando, created = Comando.objects.get_or_create(comando=comando_str)
            if created:
                 logger.debug(f"Comando '{comando_str}' creado en la BD.")
            OrdenComando.objects.create(boleta=self.boleta, comando=comando, orden=orden)
            # Log the command being added at debug level
            # logger.debug(f"Orden {orden}: Añadido comando: {comando_str.encode('unicode_escape').decode()}") # Show special chars
        except Exception as e:
             logger.error(f"Error al agregar comando '{comando_str}' (orden {orden}) a la Boleta {self.boleta.id}.", exc_info=True)


    # --- Private Methods for Specific Commands ---
    # (Removed detailed implementation logs for brevity, add if needed)

    def _str_history_capacity(self, orden): self._add_comando(self.CMD_HISTORY_CAPACITY, orden)
    def _informe_z(self, orden): self._add_comando(self.CMD_INFORME_Z, orden)
    def _cierre_fiscal_z(self, orden): self._add_comando(self.CMD_CIERRE_FISCAL_Z, orden)
    # ... (other specific command methods like _daily_close_by_date, etc.) ...
    def _get_working_memory(self, orden): self._add_comando(self.CMD_GET_WORKING_MEMORY, orden)
    def _send_first_IVA(self, orden): self._add_comando(self.CMD_SENT_FIRST_IVA, orden)
    def _next_IVA_transmission(self, orden): self._add_comando(self.CMD_NEXT_IVA_TRANSMISSION, orden)
    def _open_fiscal_receipt(self, orden): self._add_comando(self.CMD_OPEN_FISCAL_RECEIPT, orden)
    def _print_fiscal_text(self, texto, orden): self._add_comando(f"A\x1c{texto}\x1c0", orden)
    def _print_line_item(self, descripcion, cantidad, precio, orden):
        # Ensure values are formatted correctly for the command string
        desc_trunc = descripcion[:20] if len(descripcion) > 20 else descripcion # Printer char limit
        qty_str = f"{float(cantidad):.4f}" # Adjust precision as needed by printer
        price_str = f"{float(precio):.4f}" # Adjust precision as needed by printer
        iva_str = "21.0" # Make configurable if needed

        line_item_cmd = f"B\x1c{desc_trunc}\x1c{qty_str}\x1c{price_str}\x1c{iva_str}\x1cM\x1c0\x1c0\x1cT"
        logger.debug(f"Comando Line Item (orden {orden}): {line_item_cmd}")
        self._add_comando(line_item_cmd, orden)
    def _last_item_discount(self, texto, cantidad, orden): self._add_comando(f"U\x1c{texto}\x1c{cantidad:.2f}\x1cm\x1c0\x1cT", orden)
    def _last_item_recargo(self, texto, cantidad, orden): self._add_comando(f"U\x1c{texto}\x1c{cantidad:.2f}\x1cM\x1c0\x1cT", orden)
    def _general_discount(self, texto, cantidad, orden): self._add_comando(f"T\x1c{texto}\x1c{cantidad:.2f}\x1cm\x1c0\x1cT", orden)
    # ... (other commands) ...
    def _sub_total(self, orden): self._add_comando(self.CMD_SUB_TOTAL, orden)
    def _total_tender(self, orden):
        # Use the calculated sub_total if not efectivo, or the provided monto_abonado if efectivo
        monto_pago = self.monto_abonado if self.pago_efectivo else self.sub_total_calculado_para_ticket
        monto_pago_str = f"{float(monto_pago):.2f}"
        logger.debug(f"ComandoFiscal._total_tender - Monto para comando D: {monto_pago_str} (Subtotal Ticket: {self.sub_total_calculado_para_ticket}, Pago Efectivo: {self.pago_efectivo}, Monto Abonado Original: {self.monto_abonado})")
        # Ensure tipo_pago doesn't exceed printer limits
        tipo_pago_trunc = self.tipo_pago[:20] if len(self.tipo_pago) > 20 else self.tipo_pago
        total_pago_cmd = f"D\x1c{tipo_pago_trunc}\x1c{monto_pago_str}\x1cT\x1c0" # Check 'T' and '0' flags meaning
        self._add_comando(total_pago_cmd, orden)
    def _close_fiscal_receipt(self, orden): self._add_comando(self.CMD_CLOSE_FISCAL_RECEIPT, orden)
    def _set_customer_data(self, orden):
        if self.cliente:
            # Clean and format client data for the command
            razon_social = (self.cliente.razon_social or '')[:40] # Check printer limits
            cuit_dni = (self.cliente.cuit_dni or '').replace('-', '')[:20]
            resp_iva = self.cliente.responsabilidad_iva or 'C' # Default to Consumidor Final IVA type?
            tipo_doc = self.cliente.tipo_documento or '2' # Default to DNI type?
            domicilio = (self.cliente.domicilio or '')[:40]
            cmd_cliente = f"b\x1c{razon_social}\x1c{cuit_dni}\x1c{resp_iva}\x1c{tipo_doc}\x1c{domicilio}"
        else:
            # Default command for Consumidor Final
            cmd_cliente = f"b\x1cConsumidor Final\x1c0\x1cC\x1c2\x1c"
        logger.debug(f"Comando Set Customer Data (orden {orden}): {cmd_cliente}")
        self._add_comando(cmd_cliente, orden)
    def _set_fantasy_name(self, texto, orden): self._add_comando(f"{self.CMD_SET_FANTASY_NAME_BASE}{texto}", orden)
    def _set_fantasy_name_barra(self, i, orden): self._set_fantasy_name(f"{i+1}/{self.cantidad_tickets}", orden)
    def _get_status(self, orden): self._add_comando(self.CMD_GET_STATUS, orden)


    # --- Public Methods to Build Command Sequences ---

    def get_status(self):
        """Adds a GET_STATUS command."""
        logger.info("Añadiendo comando GET_STATUS.")
        self._get_status(self.orden)
        self.orden += 1

    def set_encabezado(self, ticket_index):
        """Sets header commands for a specific ticket index."""
        logger.info(f"Configurando encabezado para ticket {ticket_index + 1}/{self.cantidad_tickets}.")
        self._get_status(self.orden); self.orden += 1 # Start with status check
        # Set Fantasy Name (e.g., Store Name) - Do this only once? Or per ticket? Depends on printer.
        self._set_fantasy_name(self.DEFAULT_FANTASY_NAME, self.orden); self.orden += 1
        # Add ticket sequence if splitting
        if self.cantidad_tickets > 1:
            self._set_fantasy_name_barra(ticket_index, self.orden); self.orden += 1


    def set_tipo_cliente(self):
        """Sets customer data and opens the fiscal receipt."""
        logger.info("Configurando datos del cliente y abriendo recibo fiscal.")
        self._set_customer_data(self.orden); self.orden += 1
        self._open_fiscal_receipt(self.orden); self.orden += 1


    def set_articulos(self):
        """Adds line item commands for all articles (no splitting)."""
        # This method seems unused if set_articulos_desborde handles all cases?
        logger.info("Añadiendo artículos (sin desborde).")
        self.sub_total_calculado_para_ticket = 0.0 # Reset for this ticket
        for articulo in self.articulos + self.articulos_sin_registro:
            logger.debug(f"ComandoFiscal.set_articulos - Procesando: {articulo}")
            if isinstance(articulo, Articulo):
                descripcion = articulo.item.descripcion
                precio = float(articulo.item.final_efectivo if self.pago_efectivo else articulo.item.final)
            else:  # ArticuloSinRegistro
                descripcion = articulo.descripcion
                precio = float(articulo.precio)

            cantidad = float(articulo.cantidad)
            self._print_line_item(descripcion, cantidad, precio, self.orden); self.orden += 1
            self.sub_total_calculado_para_ticket += precio * cantidad
        logger.debug(f"Subtotal calculado para set_articulos: {self.sub_total_calculado_para_ticket}")


    def set_articulos_desborde(self):
        """Adds line item commands, applying division factor if splitting tickets."""
        logger.info("Añadiendo artículos (con posible desborde).")
        self.sub_total_calculado_para_ticket = 0.0 # Reset subtotal for the current ticket being generated
        for articulo in self.articulos + self.articulos_sin_registro:
            logger.debug(f"ComandoFiscal.set_articulos_desborde - Procesando: {articulo}")
            precio = 0.0
            cantidad = 0.0
            descripcion = "N/A"

            try:
                if isinstance(articulo, Articulo):
                    descripcion = articulo.item.descripcion
                    precio = float(articulo.item.final_efectivo if self.pago_efectivo else articulo.item.final)
                    logger.debug(f"  -> Artículo reg: desc='{descripcion}', precio={precio}")
                else:  # ArticuloSinRegistro
                    descripcion = articulo.descripcion
                    precio = float(articulo.precio)
                    logger.debug(f"  -> Artículo s/reg: desc='{descripcion}', precio={precio}")

                cantidad = float(articulo.cantidad)
                logger.debug(f"  -> Cantidad original: {cantidad}, Factor: {self.factor}")

                cantidad_aplicar = round(cantidad * self.factor, 10) # Apply factor
                precio_aplicar = round(precio, 4) # Use original price, quantity is adjusted

                # Add command using adjusted quantity and original price
                self._print_line_item(descripcion, cantidad_aplicar, precio_aplicar, self.orden); self.orden += 1
                self.sub_total_calculado_para_ticket += precio_aplicar * cantidad_aplicar

            except AttributeError as ae:
                 logger.warning(f"Error de atributo procesando item {articulo.id}: {ae}")
            except (ValueError, TypeError) as ve:
                 logger.warning(f"Error de valor/tipo procesando item {articulo.id}: {ve}")
            except Exception as e:
                 logger.error(f"Error inesperado procesando item {articulo.id} en set_articulos_desborde", exc_info=True)

        # Round the final subtotal for the ticket
        self.sub_total_calculado_para_ticket = round(self.sub_total_calculado_para_ticket, 2)
        logger.debug(f"Subtotal calculado para este ticket (desborde): {self.sub_total_calculado_para_ticket}")


    def set_cierre(self):
        """Adds subtotal, total tender, and close receipt commands."""
        logger.info("Añadiendo comandos de cierre de ticket.")
        self._sub_total(self.orden); self.orden += 1
        self._total_tender(self.orden); self.orden += 1
        self._close_fiscal_receipt(self.orden); self.orden += 1
        # Mark boleta as ready (though not yet sent/printed)
        # self.boleta.impreso = False # Or a 'pendiente' status?
        # self.boleta.save() # Save status changes if needed


    # --- Standalone Commands ---

    def cierre_z(self):
        """Adds the Z Close command."""
        logger.info("Añadiendo comando CIERRE_FISCAL_Z.")
        self.orden = 1 # Reset order for standalone command
        self._cierre_fiscal_z(self.orden)
        # Maybe create a different Boleta type for administrative commands?

    def informe_z(self):
        """Adds the Z Report command."""
        logger.info("Añadiendo comando INFORME_Z.")
        self.orden = 1 # Reset order
        self._informe_z(self.orden)