from django.db.models import FloatField, ExpressionWrapper
from boletas.models import Boleta, OrdenComando, Comando
from django.db.models import F, Sum
import math
from bdd.models import Carrito, Articulo, ArticuloSinRegistro
from facturacion.models import Cliente, Transaccion

class FormasPago():
    ds = "Cuenta Corriente",
    importe = 4924.39
    def __init__(self, transaccion):
        self.tr = transaccion
        self.ds = self.tr.metodo_de_pago.display
        self.importe = self.tr.total
    
    def get_importe(self):
        if isinstance(self.importe, str):
            return round(float(self.importe), 2)
        elif isinstance(self.importe, int):
            return round(float(self.importe), 2)
        elif isinstance(self.importe, float):
            return round(self.importe, 2)
        
    def get_formas_pago_json(self, cant):
        json = {
            "formasPago": [
            {
                "ds": self.ds,
                "importe": float(round(self.get_importe() / cant)),
            },
        ]}
        return json
    
    def get_efectivo(self):
        if self.ds == "Efectivo S/Ticket" or self.ds == "Efectivo con Ticket":
            efectivo=True
        else:
            efectivo=False
        return efectivo


class TicketCabecera():
    cliente = Cliente()
    tipo_cbte = "FB"
    nro_doc = '0'
    domicilio_cliente = ' '
    tipo_doc = 'DNI'
    nombre_cliente = 'M'
    tipo_responsable = 'CONSUMIDOR_FINAL'
    cabezera_json = {}
    def __init__(self, cliente_id=None):
        print("Cliente id desde ticket: ", cliente_id)
        if cliente_id != None and isinstance(int(cliente_id), int):
            self.cliente = Cliente.objects.get(id=cliente_id)
            print(self.cliente)
            if cliente_id != 1:
                if self.cliente.get_responsabilidad() == 'EXENTO':
                    self.tipo_cbte = "FB"
                else:
                    self.tipo_cbte = "FA"
                self.nro_doc = self.cliente.cuit_dni.replace("-","")
                self.domicilio_cliente = self.cliente.domicilio
                self.tipo_doc = self.cliente.get_tipo_documento()
                self.nombre_cliente = self.cliente.razon_social
                self.tipo_responsable = self.cliente.get_responsabilidad()
       
    def get_boleta_a(self):
        if self.tipo_cbte == "FA":
            boleta_a = True
        else:
            boleta_a = False
        return boleta_a
            
    def get_cabezera_json(self):
        if self.cliente.id != 1:
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
        else:
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

        return self.cabezera_json

class TicketItem():
    alic_iva = 21,
    importe = 128.57,
    ds = "FERNET",
    qty = 24,
    tasaAjusteInternos = 0
    efectivo = False
    def __init__(self, data):
        dic_item = data
        
        self.alic_iva = 21
        
        self.importe = dic_item['importe']
        self.importe_efectivo = dic_item['importe_efectivo']
        
        self.ds = dic_item['ds']
        self.qty = dic_item['qty']
        
        self.tasaAjusteInternos = 0
    
    def set_div_cant(self, cantidad):
        self.qty = round(self.qty / cantidad, 8)
    
    def get_item_json(self, efectivo=False, boleta_a=False):
        if efectivo:
            importe = self.importe_efectivo
        else:
            importe = self.importe
        
        if boleta_a:
            importe = float(importe) * 0.82644
            #importe = self.importe
        
        importe = round(importe, 2)
        
        json = {
            'alic_iva' : self.alic_iva,
            'ds' : self.ds,
            'importe' : float(importe),
            'qty' : float(self.qty),
            'tasaAjusteInternos' : float(self.tasaAjusteInternos)
        }
        return json

class TicketFactura():
    cantidad = 1
    PRINTNAME = "IMPRESORA_FISCAL"

    def __init__(self, transaccion):
        self.transaccion = transaccion
        
        self.formas_pago = FormasPago(self.transaccion)
        print("get_cliente_id: ", self.transaccion.get_cliente_id())
        self.cabecera = TicketCabecera(self.transaccion.get_cliente_id())
        
        self.cantidad = math.ceil(self.formas_pago.get_importe() / 999999999.00)
        
        self.items = []
        for articulo_vendido in self.transaccion.articulos_vendidos.all():
            data = articulo_vendido.get_item()
            ticket_item = TicketItem(data)
            self.items.append(ticket_item)
            
    def setear_items(self):    
        for item in self.items:
            item.set_div_cant(self.cantidad)
            
    def get_items_json(self, efectivo, boleta_a):
        items_json = {
            'items' : []
            }
        for ticket_item in self.items:
            items_json['items'].append(ticket_item.get_item_json(efectivo=efectivo , boleta_a=boleta_a))
        return items_json
        
    def get_ticket_json(self):
        json = []
        ticket_json = {"printTicket":{}}
        self.setear_items()
        for i in range(self.cantidad):
            ticket_json["printTicket"].update(self.cabecera.get_cabezera_json())
            ticket_json["printTicket"].update(self.get_items_json(self.formas_pago.get_efectivo(), self.cabecera.get_boleta_a()))
            ticket_json["printTicket"].update(self.formas_pago.get_formas_pago_json(self.cantidad))
            ticket_json.update({"printerName": self.PRINTNAME})
            json.append(ticket_json)
        print("Desde ticket:")    
        print(json)
        print("")
        return json



class ComandoFiscal():
    texto = '???'
    GET_STATUS = "*"
    HISTORY_CAPACITY = '7'
    INFORME_Z = '9\x1cX'
    CIERRE_FISCAL = '9\x1cZ'
    GET_WORKING_MEMORY = 'g'
    SENT_FIRST_IVA ='p\x1cD'
    NEXT_IVA_TRANSMISSION = 'q'
    FISCAL_TEXT = f"A\x1c{texto}\x1c0"
    SUB_TOTAL = "C\x1cP\x1cSubtotal\x1c0"
    CLOSE_FISCAL_RECEIPT = "E"
    FANTASY_NAME = "_\x1c1\x1cPinturería y Ferretería Paoli"
    
    
    def __init__(self, carrito_id=int, id_cliente=int, tipo_pago=str, monto_abonado=str):
        self.carrito = Carrito.objects.get(id=carrito_id)
        self.articulos = Articulo.objects.filter(carrito=self.carrito)
        self.articulos_sin_registro = ArticuloSinRegistro.objects.filter(carrito=self.carrito)
        
        if id_cliente != 0 and id_cliente != None and id_cliente != '':
            self.cliente = Cliente.objects.get(id=id_cliente)
            if self.cliente.responsabilidad_iva == 'I':
                self.tipo_boleta = 'A'
            else:
                self.tipo_boleta = 'B'
        else:
            self.cliente = None
            self.tipo_boleta = 'B'
            
        self.orden = 1
        self.tipo_pago = tipo_pago
        print("ComandoFiscal.tipo_pago", self.tipo_pago)
        if self.tipo_pago == 'Efectivo con Ticket':
            self.pago_efectivo = True
        else:
            self.pago_efectivo = False
            
        
        
        self.boleta = Boleta.objects.create(tipo=self.tipo_boleta)
        self.sub_total = 0
        self.monto_abonado = monto_abonado
        
        self.monto_limite = 25000
        
        if self.pago_efectivo:
            # Calculate the total for Articulo
            suma_dic = self.articulos.annotate(
                total=ExpressionWrapper(F('cantidad') * F('item__final_efectivo'), output_field=FloatField())
            ).aggregate(Sum('total'))
            total_articulo = suma_dic['total__sum'] if suma_dic['total__sum'] is not None else 0

            # Calculate the total for ArticuloSinRegistro
            suma_dic_sin_registro = self.articulos_sin_registro.annotate(
                total=ExpressionWrapper(F('cantidad') * F('precio'), output_field=FloatField())
            ).aggregate(Sum('total'))
            total_articulo_sin_registro = suma_dic_sin_registro['total__sum'] if suma_dic_sin_registro['total__sum'] is not None else 0

            # Calculate the total
            total = total_articulo + total_articulo_sin_registro
            
            if total > self.monto_limite:
                self.cantidad_tickets = math.ceil(total / self.monto_limite)
                self.factor = 1 / self.cantidad_tickets
            else:    
                self.cantidad_tickets = 1
                self.factor = 1
        else:
            suma_dic = self.articulos.annotate(
                total=ExpressionWrapper(F('cantidad') * F('item__final'), output_field=FloatField())
            ).aggregate(Sum('total'))
            total_articulo = suma_dic['total__sum'] if suma_dic['total__sum'] is not None else 0

            # Calculate the total for ArticuloSinRegistro
            suma_dic_sin_registro = self.articulos_sin_registro.annotate(
                total=ExpressionWrapper(F('cantidad') * F('precio'), output_field=FloatField())
            ).aggregate(Sum('total'))
            total_articulo_sin_registro = suma_dic_sin_registro['total__sum'] if suma_dic_sin_registro['total__sum'] is not None else 0

            # Calculate the total
            total = total_articulo + total_articulo_sin_registro
            
            if total > self.monto_limite:
                self.cantidad_tickets = math.ceil(total / self.monto_limite)
                self.factor = 1 / self.cantidad_tickets
            else:    
                self.cantidad_tickets = 1
                self.factor = 1
        
        self.open_fiscal_receipt = f"@\x1c{self.tipo_boleta}\x1cS"
        
    def _add_comando(self, str=str, orden=int):
        comando, _ = Comando.objects.get_or_create(comando=str)
        OrdenComando.objects.create(boleta=self.boleta, comando=comando, orden=orden)
    
    def _str_history_capacity(self, orden=int):
        self._add_comando(self.HISTORY_CAPACITY,orden)
    
    def _informe_z(self, orden=int):
        self._add_comando(self.INFORME_Z, orden)
    
    def _cierre_fiscal(self, orden=int):
        self._add_comando(self.CIERRE_FISCAL, orden)
        
    def _daily_close_by_date(self, fecha_inicio=str, fecha_final=str, orden=int):
        ''' La fecha debe tener un formato 070827 
        T: datos globales; otro caracter: datos por Z'''
        str_daily_close_by_date = f':\x1c{fecha_inicio}\x1c{fecha_final}\x1cT'
        self._add_comando(str_daily_close_by_date, orden)
    
    def _daily_close_by_date(self, inicio=str, final=str, orden=int):
        ''' formato ;∟1∟3800∟T 
        T: datos globales; otro caracter: datos por Z'''
        str_daily_close_by_number = f';\x1c{inicio}\x1c{final}\x1cT'
        self._add_comando(str_daily_close_by_number, orden)
    
    def _get_daily_report(self, fecha=str, orden=int):
        str_daily_report = f'<\x1c{fecha}\x1cZ'
        self._add_comando(str_daily_report, orden)
    
    def _get_working_memory(self, orden=int):
        self._add_comando(self.GET_WORKING_MEMORY, orden)
    
    def _send_first_IVA(self, orden=int):
        self._add_comando(self.SENT_FIRST_IVA, orden)
        
    def _next_IVA_transmission(self, orden=int):
        self._add_comando(self.NEXT_IVA_TRANSMISSION, orden)
        
    def _open_fiscal_receipt(self, orden=int):
        self._add_comando(self.open_fiscal_receipt, orden)
        
    def _print_fiscal_text(self, orden=int):
        self._add_comando(self.FISCAL_TEXT, orden)
    
    def _print_line_item(self, descripcion=str, cantidad=str, precio=str, orden=int):
        line_item = f"B\x1c{descripcion}\x1c{cantidad}\x1c{precio}\x1c21.0\x1cM\x1c0\x1c0\x1cT"
        print(line_item)
        self._add_comando(line_item, orden)
    
    def _last_item_discount(self, texto_descuento=str, cant_descuento=str, orden=int):
        descuento = f"U\x1c{texto_descuento}\x1c{cant_descuento}\x1cm\x1c0\x1cT"
        self._add_comando(descuento, orden)
        
    def _last_item_recargo(self, texto_recargo=str, cant_recargo=str, orden=int):
        recargo = f"U\x1c{texto_recargo}\x1c{cant_recargo}\x1cM\x1c0\x1cT"
        self._add_comando(recargo, orden)
        
    def _general_discount(self, texto_descuento_general=str, cant_descuento_general=str, orden=int):
        descuento_general = f"T\x1c{texto_descuento_general}\x1c{cant_descuento_general}\x1cm\x1c0\x1cT"
        self._add_comando(descuento_general, orden)
        
    def _return_recharge(self, orden=int):
        retornable = "m\x1cFinanciero\x1c5.00\x1c21.00\x1cM\x1c0.0\x1c0\x1cT\x1cB"
        self._add_comando(retornable, orden)
        
    def _perceptions(self, orden=int):
        persepcion = f"\`\x1c21.0\x1cPercep. IVA21\x1c12.00"
        self._add_comando(persepcion, orden)
        
    def _sub_total(self, orden=int):
        self._add_comando(self.SUB_TOTAL, orden)
    
    def _total_tender(self, orden=int):
        if self.pago_efectivo:
            monto_abonado = self.monto_abonado
        else:
            monto_abonado = self.sub_total
        print("MONTO_ABONADO: ",monto_abonado)
        total_pago = f"D\x1c{self.tipo_pago}\x1c{round(float(monto_abonado), 2)}\x1cT\x1c0"
        self._add_comando(total_pago, orden)
    
    def _close_fiscal_receipt(self, orden=int):
        self._add_comando(self.CLOSE_FISCAL_RECEIPT, orden)
        self.sub_total = 0
        
    def _set_customer_data(self, orden=int):
        '''Segun el tipo de voleta y el tipo de cliente etc...'''
        if self.cliente != None:
            self.cliente.cuit_dni = self.cliente.cuit_dni.replace('-', '')
            cmd_cliente = f"b\x1c{self.cliente.razon_social}\x1c{self.cliente.cuit_dni}\x1c{self.cliente.responsabilidad_iva}\x1c{self.cliente.tipo_documento}\x1c{self.cliente.domicilio}"
        else:
            cmd_cliente = f"b\x1cM\x1c0\x1cC\x1c2\x1c" 
        self._add_comando(cmd_cliente, orden)
    
    def _set_fantasy_name(self, orden=int):
        self._add_comando(self.FANTASY_NAME, orden)
    
    def _set_fantasy_name_barra(self, i=int, orden=int):
        barra = f"{i+1}/{self.cantidad_tickets}"
        fantasy_name_barra = f"_\x1c1\x1c{barra}"
        self._add_comando(fantasy_name_barra, orden)
    
    def _get_status(self, orden=int):
        self._add_comando(self.GET_STATUS, orden)
        
    ### ------------ PUBLICOS --------------------- ###
    
    
    def get_status(self):
        self._get_status(self.orden)
        
    def set_encabezado(self, i):
        self._get_status(self.orden)
        self.orden += 1
    
    def set_tipo_cliente(self):
        self._set_customer_data(self.orden)
        self.orden += 1
        self._open_fiscal_receipt(self.orden)
        self.orden += 1
        
    
    def set_articulos(self):
        for articulo in list(self.articulos) + list(self.articulos_sin_registro):
            print(articulo, 'set_articulos')
            if isinstance(articulo, Articulo):
                descripcion = articulo.item.descripcion
                if self.pago_efectivo:
                    precio = float(articulo.item.final_efectivo)
                else:
                    precio = float(articulo.item.final)
            else:  # ArticuloSinRegistro
                descripcion = articulo.descripcion
                precio = float(articulo.precio)

            if len(descripcion) > 20:
                descripcion = descripcion[:20]
            
            cantidad = articulo.cantidad
                
            self._print_line_item(descripcion, cantidad, precio, self.orden)
            self.orden += 1
            self.sub_total += precio * cantidad

    def set_articulos_desborde(self):
        for articulo in list(self.articulos) + list(self.articulos_sin_registro):
            print('set_articulos_desborde: ', articulo )
            if isinstance(articulo, Articulo):
                descripcion = articulo.item.descripcion
                if self.pago_efectivo:
                    precio = float(articulo.item.final_efectivo)
                else:
                    precio = float(articulo.item.final)
                print("articulo: ")
                print("descripcion: ", descripcion)
                print("precio: ", precio)
            else:  # ArticuloSinRegistro
                descripcion = articulo.descripcion
                precio = float(articulo.precio)
                print("articulo sin registrar: ")
                print("descripcion: ", descripcion)
                print("precio: ", precio)

            if len(descripcion) > 20:
                descripcion = descripcion[:20]
            
            cantidad = float(articulo.cantidad)
            print("cantidad: ", cantidad)
            print("factor: ", self.factor)
            self._print_line_item(descripcion, round(cantidad * self.factor,10), round(precio,4), self.orden)
            self.orden += 1
            self.sub_total += precio * round(cantidad * self.factor,10)


            
    def set_cierre(self):
        self._sub_total(self.orden)
        self.orden += 1
        self._total_tender(self.orden)
        self.orden += 1
        self._close_fiscal_receipt(self.orden)
        self.orden += 1
        self.boleta.impreso = False
        self.boleta.save()
    
    def cierre_z(self):
        self._cierre_fiscal(self.orden)
    
    def informe(self):
        self._informe_z(self.orden)