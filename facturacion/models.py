from django.db import models
from bdd.models import Item, ArticuloSinRegistro
from django.conf import settings
# Create your models here.
class Cliente(models.Model):
    razon_social = models.CharField(max_length=45)
    cuit_dni = models.CharField(max_length=11)
    
    RESPONSABILIDAD_IVA_OPCIONES = [
        ('I', 'Responsable inscripto'),
        ('E', 'Exento'),
        ('A', 'No responsable'),
        ('C', 'Consumidor final'),
        ('B', 'Responsable no inscripto, venta de bienes de uso'),
        ('M', 'Resp. monotributo'),
        ('S', 'Monotributista social'),
        ('V', 'Pequeño contribuyente eventual'),
        ('W', 'Pequeño contribuyente eventual social'),
        ('T', 'No categorizado')
    ]
    
    '''
    tipo_cbte
        "TA", 	#Tiquets A
        "TB",  	#Tiquets B
        "FA", 	#Factura A
        "FB", 	#Factura B
        "NDA", 	#Nota Debito A
        "NCA", 	#Nota Credito A
        "NDB", 	#Nota Debito B
        "NCB", 	#Nota Credito B
        "FC", 	#Factura C
        "NDC", 	#Nota Debito C
        "NDC", 	#Nota Credito C
        "R" 		#Remito
    '''

    responsabilidad_iva = models.CharField(
        max_length=1,
        choices=RESPONSABILIDAD_IVA_OPCIONES,
        default='C',
    )

    TIPO_DOCUMENTO_OPCIONES = [
        ('C', 'CUIT'),
        ('0', 'Libreta de enrolamiento'),
        ('1', 'Libreta cívica'),
        ('2', 'Documento Nacional de Identidad'),
        ('3', 'Pasaporte'),
        ('4', 'Cédula de identidad'),
        (' ', 'Sin calificador'),
    ]

    tipo_documento = models.CharField(
        max_length=1,
        choices=TIPO_DOCUMENTO_OPCIONES,
        default=' ',
    )
    domicilio = models.CharField(max_length=45, null=True, blank=True)
    telefono = models.CharField(max_length=45, null=True, blank=True)
    def __str__(self):
        text = "{}".format(self.razon_social,)
        return text
    
    # Creamos un diccionario para mapear los códigos a los nombres descriptivos
    RESPONSABILIDAD_A_NOMBRE = {
        'I': 'RESPONSABLE_INSCRIPTO',
        'E': 'EXENTO',
        'A': 'NO_RESPONSABLE',
        'C': 'CONSUMIDOR_FINAL',
        'B': 'RESPONSABLE_NO_INSCRIPTO',
        'M': 'RESPONSABLE_MONOTRIBUTO',
        'S': 'MONOTRIBUTISTA_SOCIAL',
        'V': 'PEQUENIO_CONTRIBUYENTE_EVENTUAL',
        'W': 'PEQUENIO_CONTRIBUYENTE_EVENTUAL_SOCIAL',
        'T': 'NO_CATEGORIZADO'
    }
    
    TIPO_DOCUMENTO_A_NOMBRE = {
        'C': 'CUIT',
        '0': 'Libreta de enrolamiento',
        '1': 'Libreta cívica',
        '2': 'Documento Nacional de Identidad',
        '3': 'Pasaporte',
        '4': 'Cédula de identidad',
        ' ': 'Sin calificador',
    }

    def get_responsabilidad(self):
        return self.RESPONSABILIDAD_A_NOMBRE.get(self.responsabilidad_iva, "No encontrado")
    
    def get_tipo_documento(self):
        return self.TIPO_DOCUMENTO_A_NOMBRE.get(self.tipo_documento, "No encontrado")

class ArticuloVendido(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE, null=True, blank=True)
    sin_registrar = models.ForeignKey(ArticuloSinRegistro, on_delete=models.CASCADE, null=True, blank=True)
    cantidad = models.FloatField()
    def __str__(self):
        text = "{}".format(self.item if self.item else self.sin_registrar)
        return text
    
    def get_item(self):
        if isinstance(self.item, Item):
            print(self.item)
            ds = self.item.descripcion
            importe = self.item.final
            importe_efectivo = self.item.final_efectivo
        else:
            ds = self.sin_registrar.descripcion
            importe = self.sin_registrar.precio
            importe_efectivo = self.sin_registrar.precio
        data = {
            'ds' : ds,
            'importe' : round(importe, 2),
            'importe_efectivo': round(importe_efectivo, 2),
            'qty' : round(self.cantidad, 2)
        }
        return data


class MetodoPago(models.Model):
    display = models.CharField(max_length=250)
    ticket = models.BooleanField(default=False)
    def __str__(self):
        text = "{}".format(self.display,)
        return text


class Transaccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, default=1)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    articulos_vendidos = models.ManyToManyField(ArticuloVendido)
    metodo_de_pago = models.ForeignKey(MetodoPago, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.FloatField(default=0.0)
    
    def __str__(self):
        text = "{}-{}-{}".format(self.fecha, self.metodo_de_pago, self.total,)
        return text
    
    def get_cliente_id(self):
        return self.cliente.id
    


class CierreZ(models.Model):
    fecha = models.DateField(auto_now_add=True)
    RESERVADO_SIEMPRE_CERO = models.IntegerField(default=0)
    cant_doc_fiscales = models.IntegerField(default=0)
    cant_doc_fiscales_a_emitidos = models.IntegerField(default=0)
    cant_doc_fiscales_bc_emitidos = models.IntegerField(default=0)
    cant_doc_fiscales_cancelados = models.IntegerField(default=0)
    cant_doc_nofiscales = models.IntegerField(default=1)
    cant_doc_nofiscales_homologados = models.IntegerField(default=0)
    cant_nc_a_fiscales_a_emitidos = models.IntegerField(default=0)
    cant_nc_bc_emitidos = models.IntegerField(default=0)
    cant_nc_canceladas = models.IntegerField(default=0)
    monto_credito_nc = models.FloatField(default=0.00)
    monto_imp_internos = models.FloatField(default=0.00)
    monto_imp_internos_nc = models.FloatField(default=0.00)
    monto_iva_doc_fiscal = models.FloatField(default=0.00)
    monto_iva_nc = models.FloatField(default=0.00)
    monto_iva_no_inscripto = models.FloatField(default=0.00)
    monto_iva_no_inscripto_nc = models.FloatField(default=0.00)
    monto_percepciones = models.FloatField(default=0.00)
    monto_percepciones_nc = models.FloatField(default=0.00)
    monto_ventas_doc_fiscal = models.FloatField(default=0.00)
    status_fiscal = models.CharField(max_length=4, default="0600")
    status_impresora = models.CharField(max_length=4, default="C080")
    ultima_nc_a = models.IntegerField(default=30)
    ultima_nc_b = models.IntegerField(default=327)
    ultimo_doc_a = models.IntegerField(default=2262)
    ultimo_doc_b = models.IntegerField(default=66733)
    ultimo_remito = models.IntegerField(default=0)
    zeta_numero = models.IntegerField(default=1)

    def __str__(self):
        return f"FiscalZ {self.fecha}"
