from django.db import models

# Create your models here.

class GenericaLista(models.Model):
    abreviatura = models.CharField(max_length=3)
    nombre = models.CharField(max_length=25)

    class Meta:
        abstract = True

    def __str__(self):
        text = "{}".format(self.nombre,)
        return text
'''
class MetodoPago(GenericaLista):
    pass

class Ticket(GenericaLista):
    abreviatura = models.CharField(max_length=1)

class Tipo(GenericaLista):
    abreviatura = models.CharField(max_length=2)'''

class ListaProveedores(GenericaLista):
    abreviatura = models.CharField(max_length=5)
    hay_csv_pendiente = models.BooleanField(default=False)


###########################################################################################


class Generica(models.Model):
    nombre = models.CharField(max_length=25)

    class Meta:
        abstract = True

    def __str__(self):
        text = "{}".format(self.nombre,)
        return text

class Proveedor(models.Model):
    identificador = models.ForeignKey(ListaProveedores, blank=True, null=True, on_delete=models.CASCADE)
    text_display = models.CharField(max_length=30, blank=True, null=True)
    cuit = models.CharField(max_length=13)
    direccion = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    telefono = models.CharField(max_length=50)

    corredor = models.CharField(max_length=50)
    corredor_telefono = models.CharField(max_length=50)

    def __str__(self):
        text = "{}".format(self.text_display,)
        return text

class Condiciones(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    fila_inicial = models.IntegerField(default=1)

    codigo = models.CharField(max_length=1)
    nombre = models.CharField(max_length=1)
    precio_base = models.CharField(max_length=1)

    porcentaje = models.FloatField(default=1.0)
    porcentaje_21 = models.FloatField(default=1.0)
    porcentaje_10_5 = models.FloatField(default=1.0)

    dolar = models.CharField(max_length=1)

    def detectar_columna(self, n):
       if n == self.codigo:
           columna = 'Codigo'
       elif n == self.descripcion:
           columna = 'Nombre'
       elif n == self.precio_base:
           columna = 'Precio'
       return columna

    def ordenar_columnas(self):
       columnas = []
       col = [
       self.codigo,
       self.descripcion,
       self.precio_base,
       ]
       c_ordenado = sorted(col)

       for c in c_ordenado:
           print(c)
           print('columnas: ',columnas)
           item = self.detectar_columna(c)
           print('items: ',item)
           columnas.append(item)

       return columnas

class Sub_Carpeta(Generica):
    pass

class Sub_Titulo(Generica):
    pass

class Tipo_Cartel(Generica):
    pass

class Archivo(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    condiciones = models.ForeignKey(Condiciones, on_delete=models.CASCADE)

    agregado = models.DateField(auto_now_add=True, blank=True)
    editado = models.DateField(auto_now=True, blank=True)

    archivo = models.FileField(upload_to="inbox", unique=True, null=True, blank=True)

    def __str__(self):
        return self.proveedor.id.nombre

    def descargar(self):
        basename = os.path.basename(str(self.descarga))
        base = os.getcwd()
        destino = os.path.join(base,'mysite', 'media','destino',basename)
        return destino

    def basename(self):
        basename = os.path.basename(str(self.descarga))
        return basename

class Sector(models.Model):
    codigo = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.codigo

class Cajonera(models.Model):
    codigo = models.CharField(max_length=20, blank=True, null=True)
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.codigo

class Cajon(models.Model):
    codigo = models.CharField(max_length=20, blank=True, null=True)
    cajonera = models.ForeignKey(Cajonera, on_delete=models.CASCADE, blank=True, null=True)
    
    def __str__(self):
        return self.codigo

class Marca(models.Model):
    codigo = models.CharField(max_length=20, blank=True, null=True)

class Item(models.Model):
    cajon = models.ForeignKey(Cajon, on_delete=models.CASCADE, blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.CASCADE, blank=True, null=True)

    #Codigo mas /
    codigo = models.CharField(max_length=20, blank=True, null=True)

    #Barras
    barras = models.IntegerField(blank=True, null=True)

    #Item
    descripcion = models.CharField(max_length=200, blank=True, null=True)

    #Precio de planilla
    precio_base = models.FloatField(default=0.0, blank=True)

    #Porcentaje al publico
    porcentaje = models.FloatField(default=1.0, blank=True)

    #Porcentaje en efectivo
    porcentaje_efectivo = models.FloatField(default=1.0, blank=True)

    #Porcentaje si hay descuento
    porcentaje_oferta = models.FloatField(default=1.0, blank=True)

    #Porcentaje si hay descuento y en efectivo
    porcentaje_oferta_efectivo = models.FloatField(default=1.0, blank=True, null=True)

    #Precio final de oferta
    oferta = models.BooleanField(default=False)

    #El precio base esta por rollo o caja?
    precio_rollo_caja = models.BooleanField(default=False)

    #Se vende este item por rollo o caja?
    venta_rollo_caja = models.BooleanField(default=False)

    #Si se vende por metro.. Porcentaje distinto?
    porcentaje_metro = models.FloatField(default=1.0, blank=True)

    #Cantidad por la que se divide o multiplica el precio base
    pack_cantidad = models.FloatField(default=1.0, blank=True)

    #Cantidad que trae el rollo o la caja
    cantidad_rollo_caja = models.FloatField(default=1.0, blank=True)

    #Descuento venta por rollo o caja
    descuento_rollo_caja = models.FloatField(default=1.0, blank=True)

    #Descuento venta por rollo o caja en efectivo
    descuento_rollo_caja_efectivo = models.FloatField(default=1.0, blank=True)

    #Precio final por rollo
    final_rollo = models.FloatField(default=0.0, blank=True)

    #Precio final por rollo en efectivo
    final_rollo_efectivo = models.FloatField(default=0.0, blank=True)

    #Precio final
    final = models.FloatField(default=0.0, blank=True)

    #Precio final en efectivo
    final_efectivo = models.FloatField(default=0.0, blank=True)

    #Lo trabajamos?
    trabajado = models.BooleanField(default=False)

    #Hoja de destino
    sub_carpeta = models.ForeignKey(Sub_Carpeta, null=True, on_delete=models.SET_NULL, blank=True)

    #Subtitulo
    sub_titulo = models.ForeignKey(Sub_Titulo, null=True, on_delete=models.SET_NULL, blank=True)

    #Esta actualizado
    actualizado = models.BooleanField(default=False)

    #Fecha
    fecha = models.DateField(auto_now_add=True, blank=True, null=True)

    #Cantidad en stock
    stock = models.FloatField(default=0.0, blank=True)

    #Proveedor
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, blank=True, null=True)

    #Tiene cartel?
    tiene_cartel = models.BooleanField(default=False)

    #Tipo de cartel
    tipo_cartel = models.ForeignKey(Tipo_Cartel, null=True, on_delete=models.SET_NULL, blank=True)

    #% cartel efectivo
    p_c_efectivo = models.FloatField(default=0.0, blank=True)

    #% cartel debito
    p_c_debito = models.FloatField(default=0.0, blank=True)

    #% cartel credito
    p_c_credito = models.FloatField(default=0.0, blank=True)

    def __str__(self):
        text = "{}-{}".format(self.codigo, self.descripcion,)
        return text

    def calcular_precio_final(self):
        if self.precio_rollo_caja:
            self.final = (self.precio_base/self.pack_cantidad) * self.porcentaje * self.constante
        else:
            self.final = self.precio_base * self.porcentaje * self.constante

        if self.venta_metro:
            self.final = self.final * self.porcentaje_metro

        if self.oferta:
            self.final = self.final * self.porcentaje_oferta

    def calcular_precio_efectivo_final(self):
        if self.precio_rollo_caja:
            self.final_efectivo = (self.precio_base/self.pack_cantidad) * self.porcentaje_efectivo * self.constante
        else:
            self.final_efectivo = self.precio_base * self.porcentaje_efectivo * self.constante

        if self.venta_metro:
            self.final_efectivo = self.final_efectivo * self.porcentaje_metro

        if self.oferta:
            self.final_efectivo = self.final_efectivo * self.porcentaje_oferta_efectivo

    def calcular_precio_rollo_final(self):
        if self.venta_rollo_caja:
            self.final_rollo = self.final * self.cantidad_rollo_caja * 0.9

    def calcular_precio_rollo_efectivo_final(self):
        if self.venta_rollo_caja:
            self.final_rollo_efectivo = self.final * self.cantidad_rollo_caja * 0.85

    def marcar_actualizado(self):
        self.actualizado = True

    def marcar_desactualizado(self):
        self.actualizado = False


class Cod_Barras(models.Model):
    barras = models.IntegerField(blank=True, null=True)
    articulo = models.ForeignKey(Item, on_delete=models.CASCADE, blank=True, null=True)

class Lista_Pedidos(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)

    item = models.ForeignKey(Item, on_delete=models.CASCADE)

    cantidad = models.FloatField(default=0.0)
    
    pedido = models.BooleanField(default=False)


######################################################################################################


class NavBar(models.Model):
    url_inicial = models.CharField(max_length=20)
    text_display = models.CharField(max_length=30)

    def __str__(self):
        text = "{}".format(self.text_display,)
        return text

class Muro(models.Model):
    muro_html = models.CharField(max_length=30)

    def __str__(self):
        text = "{}".format(self.muro_html,)
        return text

'''
class Estructura(models.Model):
    tipo_de_estructura = models.CharField(max_length=30, default='')

    def __str__(self):
        text = "{}".format(self.tipo_de_estructura,)
        return text'''

class Plantilla(models.Model):
    plantilla_html = models.CharField(max_length=30)
    #tipo = models.CharField(max_length=30)

    def __str__(self):
        text = "{}".format(self.plantilla_html,)
        return text

class Contenedor(models.Model):
    nombre = models.CharField(max_length=30, default='simple')
    #estructura = models.ForeignKey(Estructura, on_delete=models.CASCADE)
    url = models.CharField(max_length=30)

    a = models.ForeignKey(Plantilla, on_delete=models.CASCADE, related_name='plantilla_a', default=1)
    b = models.ForeignKey(Plantilla, on_delete=models.CASCADE, related_name='plantilla_b', default=1, blank=True, null=True)
    c = models.ForeignKey(Plantilla, on_delete=models.CASCADE, related_name='plantilla_c', default=1, blank=True, null=True)


    def __str__(self):
        text = "{}".format(self.nombre,)
        return text

class Modelo_Campos(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        text = "{}".format(self.nombre,)
        return text

class Formulario_Campos(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        text = "{}".format(self.nombre,)
        return text

class Formulario_Campos_Contiene(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        text = "{}".format(self.nombre,)
        return text

class Formulario_Campos_Empieza_Con(models.Model):
    nombre = models.CharField(max_length=30)

    def __str__(self):
        text = "{}".format(self.nombre,)
        return text

class Armador(models.Model):
    nav_bar = models.ForeignKey(NavBar, on_delete=models.CASCADE)
    vista = models.CharField(max_length=30, blank=True, default='Inicio')
    url = models.CharField(max_length=30, blank=True, default='')
    url_nombre = models.CharField(max_length=30, default='')
    muro = models.ForeignKey(Muro, on_delete=models.CASCADE)
    contenedor = models.ForeignKey(Contenedor,on_delete=models.CASCADE,default=1)
    modelo = models.CharField(max_length=30)
    modelo_campos = models.ManyToManyField(Modelo_Campos)
    busqueda = models.BooleanField(default=False)
    formulario = models.CharField(max_length=30)
    formulario_boton = models.CharField(max_length=30, default='')
    formulario_campos = models.ManyToManyField(Formulario_Campos, blank=True, null=True)
    formulario_campos_contiene = models.ManyToManyField(Formulario_Campos_Contiene, blank=True, null=True)
    formulario_campos_empieza_con = models.ManyToManyField(Formulario_Campos_Empieza_Con, blank=True, null=True)

    def __str__(self):
        text = "{}".format(self.nav_bar,)
        return text

class Tipo_Registro(models.Model):
    nombre = models.CharField(max_length=30, default='')

    def __str__(self):
        text = "{}".format(self.nombre,)
        return text


class Registros(models.Model):
    fecha = models.DateField(blank=True, null=True)
    tipo = models.ForeignKey(Tipo_Registro, null=True, on_delete=models.SET_NULL, blank=True)
    nombre = models.CharField(max_length=30, default='')
    link = models.CharField(max_length=200, default='')
    link_descargar = models.CharField(max_length=200, default='')
    automatioco = models.BooleanField(default=False)

class Compras(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE)
    fecha = models.DateField()
    numero_remito = models.IntegerField()
    importe = models.FloatField(default=0.0)
    saldo = models.FloatField(default=0.0)
    observaciones = models.TextField()

    def __str__(self):
        text = "{} - {}".format(self.proveedor, self.fecha)
        return text

class Listado_Planillas(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, blank=True, null=True)
    fecha = models.DateField(auto_now_add=True, blank=True, null=True)
    descripcion = models.CharField(max_length=50, default='', unique=False)
    identificador = models.CharField(max_length=50, default='', unique=True)
    hoja = models.CharField(max_length=50, default='', null=True, blank=True)
    listo = models.BooleanField(default=False)
    descargar = models.BooleanField(default=False)
    link_descarga = models.CharField(max_length=50, default='', null=True, blank=True)
    link_descarga_ods = models.CharField(max_length=50, default='', null=True, blank=True)
    id_sp = models.CharField(max_length=50, default='', null=True, blank=True)
    hojas = models.TextField(max_length=300, default='', null=True, blank=True)


    def __str__(self):
        text = "{} - {}".format(self.proveedor, self.fecha)
        return text

#########################################################################


from django.conf import settings
        

class Carrito(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    def __str__(self):
        text = "{}".format(self.usuario)
        return text
    
class Articulo(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='articulos')
    cantidad = models.FloatField(default=1.0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    precio_efectivo = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    def __str__(self):
        text = "{}".format(self.item)
        return text

class ArticuloSinRegistro(models.Model):
    descripcion = models.CharField(max_length=300, unique=False)
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='articulos_sin_registro')
    cantidad = models.FloatField(default=1.0)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    def __str__(self):
        text = "{}".format(self.descripcion)
        return text