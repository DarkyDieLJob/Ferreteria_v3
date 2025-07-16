import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from django.contrib.auth import get_user_model

from facturacion.models import Cliente, Transaccion, MetodoPago, ArticuloVendido
from facturacion.classes import FormasPago, TicketCabecera, TicketItem, TicketFactura, ComandoFiscal
from bdd.models import Carrito, Articulo, Item, Marca, Cajon, Cajonera, Sector, ArticuloSinRegistro, Proveedor, ListaProveedores
from boletas.models import Boleta

User = get_user_model()

# Fixture para crear datos de prueba comunes
@pytest.fixture
def setup_test_data():
    # Crear usuario
    user = User.objects.create_user(username='testuser', password='testpass')
    
    # Crear cliente
    cliente = Cliente.objects.create(
        razon_social="Cliente de Prueba S.A.",
        cuit_dni="20123456789",
        domicilio="Calle Falsa 123",
        responsabilidad_iva="I",  # Responsable Inscripto
        tipo_documento='2'  # DNI según el modelo
    )
    
    # Crear método de pago
    metodo_pago = MetodoPago.objects.create(
        display="TARJETA CREDITO",
        ticket=True
    )
    
    # Crear transacción
    transaccion = Transaccion.objects.create(
        cliente=cliente,
        usuario=user,
        total=1000.50,
        metodo_de_pago=metodo_pago
    )
    
    # Crear lista de proveedores necesaria para el Proveedor
    lista_proveedores = ListaProveedores.objects.create(
        abreviatura='TEST',
        nombre='Proveedores Test',
        hay_csv_pendiente=False
    )
    
    # Crear datos para pruebas de factura
    proveedor = Proveedor.objects.create(
        identificador=lista_proveedores,
        text_display="Proveedor Test",
        cuit="20345678901",
        direccion="Calle Falsa 123",
        email="proveedor@test.com",
        telefono="12345678",
        corredor="Corredor Test",
        corredor_telefono="98765432"
    )
    
    # Crear marca
    marca = Marca()
    marca.nombre = "Marca Test"
    marca.proveedor = proveedor
    marca.save()
    
    # Crear sector, cajonera y cajón
    sector = Sector.objects.create(codigo="S1")
    cajonera = Cajonera.objects.create(sector=sector, codigo="CJ1")
    cajon = Cajon.objects.create(cajonera=cajonera, codigo="CN1")
    
    # Crear ítem
    item = Item.objects.create(
        codigo="TEST001",
        descripcion="Producto Test 1",
        final=100.0,  # Usando 'final' en lugar de 'precio_venta'
        final_efectivo=90.0,  # Precio en efectivo con descuento
        marca=marca,
        cajon=cajon,
        stock=10  # Añadir stock para evitar problemas de validación
    )
    
    # Crear artículo vendido
    articulo_vendido = ArticuloVendido.objects.create(
        item=item,
        cantidad=2
    )
    
    return {
        'user': user,
        'cliente': cliente,
        'metodo_pago': metodo_pago,
        'transaccion': transaccion,
        'item': item,
        'articulo_vendido': articulo_vendido,
        'marca': marca,
        'sector': sector,
        'cajonera': cajonera,
        'cajon': cajon,
        'proveedor': proveedor
    }

# Tests for FormasPago
@pytest.mark.django_db
def test_formas_pago_initialization(setup_test_data):
    # Setup
    test_data = setup_test_data
    
    # Test
    formas_pago = FormasPago(test_data['transaccion'])
    
    # Assertions
    assert formas_pago.ds == "TARJETA CREDITO"
    assert formas_pago.importe == 1000.50
    assert formas_pago.get_importe() == 1000.5  # Test get_importe method

@pytest.mark.django_db
def test_formas_pago_with_invalid_transaccion():
    # Test with None transaction - debería manejar el error
    with patch('facturacion.classes.logger') as mock_logger:
        # La implementación actual no lanza una excepción, solo registra el error
        formas_pago = FormasPago(None)
        
        # Verificar que se establecieron los valores por defecto
        assert formas_pago.ds == "Error"
        assert formas_pago.importe == 0.0
        assert formas_pago.get_importe() == 0.0
        
        # Verificar que se registró el error
        mock_logger.error.assert_called_once()
        error_msg = mock_logger.error.call_args[0][0]
        assert "Error al inicializar FormasPago" in error_msg
        assert mock_logger.error.called
        
        # Verificar que el mensaje de error contiene información relevante
        error_message = mock_logger.error.call_args[0][0]
        assert "Error al inicializar FormasPago" in error_message

# Tests for TicketCabecera
@pytest.mark.django_db
def test_ticket_cabecera_consumidor_final():
    # Test with default consumer (None como parámetro)
    cabecera = TicketCabecera()
    assert cabecera.tipo_cbte == "FB"
    assert cabecera.tipo_doc == 'DNI'
    assert cabecera.tipo_responsable == 'CONSUMIDOR_FINAL'
    assert cabecera.nombre_cliente == 'Consumidor Final'  # Valor por defecto actual

@pytest.mark.django_db
def test_ticket_cabecera_with_cliente(db):
    """
    Prueba que TicketCabecera asigne correctamente el tipo de comprobante
    para diferentes tipos de responsabilidades IVA.
    """
    import logging
    import sys
    
    # Configurar logger para ver la salida en la consola
    logger = logging.getLogger('test_facturacion')
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    logger.info("\n=== INICIO PRUEBA test_ticket_cabecera_with_cliente ===")
    
    from facturacion.models import Cliente
    
    # Imprimir opciones de responsabilidad_iva
    logger.info("\n=== OPCIONES DE RESPONSABILIDAD_IVA ===")
    for codigo, descripcion in Cliente.RESPONSABILIDAD_IVA_OPCIONES:
        logger.info(f"  '{codigo}': '{descripcion}'")
    
    # Crear cliente con responsabilidad 'I' (Responsable Inscripto)
    logger.info("\n=== CREANDO CLIENTE RESPONSABLE INSCRIPTO ===")
    logger.info(f"Valores a guardar: responsabilidad_iva='I', tipo_documento='C'")
    
    # Usar ID 2 para el Responsable Inscripto (ID 1 es Consumidor Final)
    cliente_ri = Cliente.objects.create(
        id=2,  # Forzar ID 2 para el Responsable Inscripto
        razon_social="Cliente de Prueba S.A.",  # Usar el nombre completo que se espera en las aserciones
        cuit_dni="20345678901",
        responsabilidad_iva='I',  # Responsable Inscripto
        tipo_documento='C',  # CUIT
        domicilio="Calle Falsa 123",
        telefono="12345678"
    )
    
    # Refrescar de la base de datos para asegurar que vemos los valores guardados
    cliente_ri_db = Cliente.objects.get(id=cliente_ri.id)
    
    # Imprimir información detallada después de crear el cliente RI
    logger.info("\n=== INFORMACIÓN DEL CLIENTE RESPONSABLE INSCRIPTO ===")
    logger.info(f"Cliente creado con ID: {cliente_ri.id}")
    logger.info(f"Valor en memoria - responsabilidad_iva: {cliente_ri.responsabilidad_iva!r} (tipo: {type(cliente_ri.responsabilidad_iva)})")
    logger.info(f"Valor en BD - responsabilidad_iva: {cliente_ri_db.responsabilidad_iva!r} (tipo: {type(cliente_ri_db.responsabilidad_iva)})")
    logger.info(f"Método get_responsabilidad(): {cliente_ri.get_responsabilidad()!r}")
    
    # Verificar que el valor se guardó correctamente
    if cliente_ri.responsabilidad_iva != 'I':
        logger.error(f"ERROR: responsabilidad_iva debería ser 'I' pero es '{cliente_ri.responsabilidad_iva}'")
    
    # Crear cliente con responsabilidad 'C' (Consumidor Final)
    logger.info("\n=== CREANDO CLIENTE CONSUMIDOR FINAL ===")
    logger.info(f"Valores a guardar: responsabilidad_iva='C', tipo_documento='2'")
    
    cliente_cf = Cliente.objects.create(
        razon_social="Consumidor Final",
        cuit_dni="20123456789",
        responsabilidad_iva='C',  # Consumidor Final
        tipo_documento='2',  # DNI
        domicilio="Calle Falsa 456",
        telefono="87654321"
    )
    
    # Refrescar de la base de datos
    cliente_cf_db = Cliente.objects.get(id=cliente_cf.id)
    
    # Imprimir información detallada después de crear el cliente CF
    logger.info("\n=== INFORMACIÓN DEL CLIENTE CONSUMIDOR FINAL ===")
    logger.info(f"Cliente creado con ID: {cliente_cf.id}")
    logger.info(f"Valor en memoria - responsabilidad_iva: {cliente_cf.responsabilidad_iva!r} (tipo: {type(cliente_cf.responsabilidad_iva)})")
    logger.info(f"Valor en BD - responsabilidad_iva: {cliente_cf_db.responsabilidad_iva!r} (tipo: {type(cliente_cf_db.responsabilidad_iva)})")
    logger.info(f"Método get_responsabilidad(): {cliente_cf.get_responsabilidad()!r}")
    
    # Verificar que el valor se guardó correctamente
    if cliente_cf.responsabilidad_iva != 'C':
        logger.error(f"ERROR: responsabilidad_iva debería ser 'C' pero es '{cliente_cf.responsabilidad_iva}'")
    
    # Forzar el guardado y recargar
    cliente_ri.refresh_from_db()
    cliente_cf.refresh_from_db()
    
    print("\n=== INFORMACIÓN DE LOS CLIENTES CREADOS ===")
    for cliente in [cliente_ri, cliente_cf]:
        print(f"\nCliente: {cliente.razon_social}")
        print(f"  ID: {cliente.id}")
        print(f"  CUIT/DNI: {cliente.cuit_dni}")
        print(f"  responsabilidad_iva: '{cliente.responsabilidad_iva}'")
        print(f"  get_responsabilidad(): '{cliente.get_responsabilidad()}'")
    
    # Verificar que los valores se guardaron correctamente
    assert cliente_ri.responsabilidad_iva == 'I', f"responsabilidad_iva debería ser 'I', pero es '{cliente_ri.responsabilidad_iva}'"
    assert cliente_cf.responsabilidad_iva == 'C', f"responsabilidad_iva debería ser 'C', pero es '{cliente_cf.responsabilidad_iva}'"
    
    # Crear instancias de TicketCabecera para ambos clientes
    from facturacion.classes import TicketCabecera
    
    # Habilitar logs de depuración
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('facturacion.classes')
    logger.setLevel(logging.DEBUG)
    
    print("\n=== PROBANDO CLIENTE RESPONSABLE INSCRIPTO (I) ===")
    cabecera_ri = TicketCabecera(cliente_id=cliente_ri.id)
    print(f"  tipo_cbte: {cabecera_ri.tipo_cbte}")
    print(f"  Se espera 'FA': {cabecera_ri.tipo_cbte == 'FA'}")
    
    print("\n=== PROBANDO CLIENTE CONSUMIDOR FINAL (C) ===")
    cabecera_cf = TicketCabecera(cliente_id=cliente_cf.id)
    print(f"  tipo_cbte: {cabecera_cf.tipo_cbte}")
    print(f"  Se espera 'FB': {cabecera_cf.tipo_cbte == 'FB'}")
    
    # Verificaciones finales
    print("\n=== VERIFICACIONES FINALES ===")
    print(f"Cliente RI - tipo_cbte: {cabecera_ri.tipo_cbte} (esperado: 'FA')")
    print(f"Cliente CF - tipo_cbte: {cabecera_cf.tipo_cbte} (esperado: 'FB')")
    
    # Verificar que el tipo de comprobante se asigne correctamente
    assert cabecera_ri.tipo_cbte == 'FA', f"Para Responsable Inscripto, tipo_cbte debería ser 'FA', pero es {cabecera_ri.tipo_cbte}"
    assert cabecera_cf.tipo_cbte == 'FB', f"Para Consumidor Final, tipo_cbte debería ser 'FB', pero es {cabecera_cf.tipo_cbte}"
    
    # Asignar cabecera para compatibilidad con el resto del código
    cabecera = cabecera_ri
    
    # Imprimir información de depuración
    print("\n=== INFORMACIÓN DE LA CABECERA CREADA ===")
    print(f"tipo_cbte: {cabecera.tipo_cbte} (esperado: 'FA')")
    print(f"nro_doc: {cabecera.nro_doc} (esperado: '20123456789')")
    print(f"nombre_cliente: {cabecera.nombre_cliente} (esperado: 'Cliente de Prueba S.A.')")
    print(f"tipo_responsable: {cabecera.tipo_responsable} (esperado: 'RESPONSABLE_INSCRIPTO')")
    print(f"Cliente en cabecera: {cabecera.cliente.id if cabecera.cliente else 'None'}")
    
    # Verificar los valores esperados
    print("\n=== VERIFICANDO ASERCIONES ===")
    print(f"Verificando tipo_cbte == 'FA'...")
    assert cabecera.tipo_cbte == "FA", f"tipo_cbte es {cabecera.tipo_cbte}, se esperaba 'FA'"
    
    print(f"Verificando nro_doc == '20345678901'...")
    assert cabecera.nro_doc == "20345678901", f"nro_doc es {cabecera.nro_doc}, se esperaba '20345678901'"
    
    print(f"Verificando nombre_cliente == 'Cliente de Prueba S.A.'...")
    assert cabecera.nombre_cliente == "Cliente de Prueba S.A.", f"nombre_cliente es '{cabecera.nombre_cliente}', se esperaba 'Cliente de Prueba S.A.'"
    
    # Verificar que el tipo_responsable sea el valor descriptivo en mayúsculas
    print(f"\nVerificando tipo_responsable == 'RESPONSABLE_INSCRIPTO'...")
    print(f"Valor actual: {cabecera.tipo_responsable}")
    print(f"Tipo de dato: {type(cabecera.tipo_responsable)}")
    assert cabecera.tipo_responsable == 'RESPONSABLE_INSCRIPTO', f"tipo_responsable es '{cabecera.tipo_responsable}', se esperaba 'RESPONSABLE_INSCRIPTO'"
    
    print("\n=== TODAS LAS PRUEBAS PASARON ===")
    
    # Verificar que el cliente se haya asignado correctamente
    assert cabecera.cliente is not None
    assert cabecera.cliente.id == cliente_ri.id  # Usar cliente_ri en lugar de cliente

# Tests for TicketItem
@pytest.mark.django_db
def test_ticket_item_initialization():
    # Test with minimal data
    item_data = {
        'ds': 'Producto de prueba',
        'qty': 2,
        'importe': 100.0,
        'alic_iva': 21.0
    }
    
    item = TicketItem(item_data)
    assert item.ds == "Producto de prueba"
    assert item.qty == 2.0
    assert item.importe == 100.0
    assert item.alic_iva == 21.0
    
    # Test get_item_json method
    item_json = item.get_item_json()
    assert item_json['ds'] == "Producto de prueba"
    assert item_json['qty'] == 2.0
    assert item_json['importe'] == 100.0

# Tests for TicketFactura
@pytest.mark.django_db
def test_ticket_factura_initialization(setup_test_data):
    """Test para verificar la inicialización correcta de TicketFactura con datos de cliente."""
    # Obtener los datos de prueba
    test_data = setup_test_data
    cliente = test_data['cliente']
    transaccion = test_data['transaccion']
    
    # Agregar artículo vendido a la transacción
    transaccion.articulos_vendidos.add(test_data['articulo_vendido'])
    
    # Forzar la recarga de la transacción desde la base de datos para asegurar que los cambios se han guardado
    transaccion.refresh_from_db()
    
    # Verificar que la transacción tiene un cliente asignado
    assert hasattr(transaccion, 'cliente'), "La transacción no tiene el atributo 'cliente'"
    assert transaccion.cliente is not None, "La transacción no tiene un cliente asignado"
    assert transaccion.cliente.id == cliente.id, "El ID del cliente en la transacción no coincide"
    
    # Crear el ticket de factura
    ticket = TicketFactura(transaccion)
    
    # Verificar que el ticket se creó correctamente
    assert ticket is not None, "No se pudo crear el TicketFactura"
    assert hasattr(ticket, 'cabecera'), "El ticket no tiene atributo 'cabecera'"
    
    # Verificar los datos del cliente en la cabecera
    assert ticket.cabecera.nombre_cliente == cliente.razon_social, \
        f"El nombre del cliente no coincide. Esperado: '{cliente.razon_social}', Obtenido: '{ticket.cabecera.nombre_cliente}'"
    
    # Verificar los ítems del ticket
    assert len(ticket.items) == 1, f"Se esperaba 1 ítem, pero se encontraron {len(ticket.items)}"
    
    if ticket.items:
        articulo = test_data['articulo_vendido']
        assert ticket.items[0].ds == articulo.item.descripcion, \
            f"La descripción del ítem no coincide. Esperado: '{articulo.item.descripcion}', Obtenido: '{ticket.items[0].ds}'"
        assert ticket.items[0].qty == articulo.cantidad, \
            f"La cantidad del ítem no coincide. Esperado: {articulo.cantidad}, Obtenido: {ticket.items[0].qty}"
    
    # Verificar el tipo de comprobante según la responsabilidad del cliente
    if cliente.responsabilidad_iva == 'I':  # Responsable Inscripto
        assert ticket.cabecera.tipo_cbte == "FA", "Se esperaba Factura A para Responsable Inscripto"
    else:
        assert ticket.cabecera.tipo_cbte == "FB", "Se esperaba Factura B para otros tipos de responsabilidad"