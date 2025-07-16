"""
Fábricas para crear instancias de prueba de los modelos de facturación.

Estas fábricas utilizan django-dynamic-fixture para crear instancias de prueba
con datos aleatorios pero válidos.
"""
from ddf import G
from facturacion import models
from bdd.models import Item, ArticuloSinRegistro
from django.contrib.auth import get_user_model

# Obtener el modelo de usuario
auth_user_model = get_user_model()

def cliente_factory(**kwargs):
    """
    Crea una instancia de Cliente con datos de prueba.
    
    Args:
        **kwargs: Valores personalizados para sobrescribir los valores por defecto
        
    Returns:
        Cliente: Instancia de Cliente con datos de prueba
    """
    defaults = {
        'razon_social': 'Cliente de Prueba S.A.',
        'cuit_dni': '20345678901',
        'responsabilidad_iva': 'C',  # Consumidor Final
    }
    defaults.update(kwargs)
    return G(models.Cliente, **defaults)

def articulo_vendido_factory(**kwargs):
    """
    Crea una instancia de ArticuloVendido con datos de prueba.
    
    Args:
        **kwargs: Valores personalizados para sobrescribir los valores por defecto
        
    Returns:
        ArticuloVendido: Instancia con datos de prueba
    """
    # Si no se proporciona un item o sin_registrar, creamos un ArticuloSinRegistro
    if 'item' not in kwargs and 'sin_registrar' not in kwargs:
        kwargs['sin_registrar'] = G(ArticuloSinRegistro, descripcion='Artículo sin registrar')
    
    defaults = {
        'cantidad': 1.0,
    }
    defaults.update(kwargs)
    return G(models.ArticuloVendido, **defaults)

def metodo_pago_factory(**kwargs):
    """
    Crea una instancia de MetodoPago con datos de prueba.
    
    Args:
        **kwargs: Valores personalizados para sobrescribir los valores por defecto
        
    Returns:
        MetodoPago: Instancia con datos de prueba
    """
    defaults = {
        'display': 'Efectivo',
        'ticket': True,
    }
    defaults.update(kwargs)
    return G(models.MetodoPago, **defaults)

def transaccion_factory(**kwargs):
    """
    Crea una instancia de Transaccion con datos de prueba.
    
    Args:
        **kwargs: Valores personalizados para sobrescribir los valores por defecto
        
    Returns:
        Transaccion: Instancia con datos de prueba
    """
    # Crear datos por defecto si no se proporcionan
    if 'cliente' not in kwargs:
        kwargs['cliente'] = cliente_factory()
    
    if 'usuario' not in kwargs:
        kwargs['usuario'] = G(auth_user_model, username='usuario_prueba')
    
    if 'metodo_de_pago' not in kwargs:
        kwargs['metodo_de_pago'] = metodo_pago_factory()
    
    defaults = {
        'total': 1000.00,
        'tipo_cbte': 'FB',  # Factura B
        'numero_cbte': 1,
    }
    
    defaults.update(kwargs)
    
    # Crear la transacción
    transaccion = G(models.Transaccion, **defaults)
    
    # Si no se proporcionan artículos, crear uno por defecto
    if 'articulos_vendidos' not in kwargs:
        articulo = articulo_vendido_factory()
        transaccion.articulos_vendidos.add(articulo)
    
    return transaccion

def cierre_z_factory(**kwargs):
    """
    Crea una instancia de CierreZ con datos de prueba.
    
    Args:
        **kwargs: Valores personalizados para sobrescribir los valores por defecto
        
    Returns:
        CierreZ: Instancia con datos de prueba
    """
    defaults = {
        'cant_doc_fiscales': 10,
        'monto_ventas_doc_fiscal': 10000.00,
        'zeta_numero': 1,
    }
    defaults.update(kwargs)
    return G(models.CierreZ, **defaults)
