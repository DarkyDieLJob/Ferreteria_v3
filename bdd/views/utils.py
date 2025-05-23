# tu_app/views/utils.py
from decimal import Decimal, InvalidOperation # Para manejar precios de forma segura
# Importa los modelos necesarios si las funciones dependen de ellos directamente
# (en este caso, parece que operan sobre diccionarios ya extraídos)
from ..models import Articulo, ArticuloSinRegistro # Necesario para isinstance


import logging

logger = logging.getLogger(__name__)


def articulo_to_dict(articulo):
    """Convierte una instancia de Articulo o ArticuloSinRegistro a un diccionario."""
    logger.debug(f"Convirtiendo a dict: {type(articulo)} - ID: {getattr(articulo, 'id', 'N/A')}")
    if isinstance(articulo, Articulo):
        # Asume que 'item' es una FK a Item y queremos su representación string
        item_repr = str(articulo.item) if articulo.item else 'Item no asociado'
        return {
            'id': str(articulo.id), # Convertir UUID/ID a string
            'item': item_repr, # O podrías devolver item.id, item.codigo, etc.
            'descripcion': getattr(articulo.item, 'descripcion', 'N/A') if articulo.item else 'N/A', # Añadir descripción
            'cantidad': articulo.cantidad,
            'precio': str(articulo.precio), # Convertir Decimal a string para JSON
            'precio_efectivo': str(articulo.precio_efectivo), # Convertir Decimal a string
        }
    elif isinstance(articulo, ArticuloSinRegistro):
        return {
            'id': str(articulo.id),
            'descripcion': articulo.descripcion,
            'cantidad': articulo.cantidad,
            'precio': str(articulo.precio), # Convertir Decimal a string
            # ArticuloSinRegistro no tiene precio_efectivo separado? Usar precio normal.
            'precio_efectivo': str(articulo.precio),
        }
    else:
        logger.warning(f"articulo_to_dict recibió un tipo no esperado: {type(articulo)}")
        return {}


def calcular_total(datos):
    """Calcula los totales para una estructura de datos de carritos."""
    logger.info(f"Calculando totales para {len(datos)} carritos.")
    if not isinstance(datos, dict):
         logger.error(f"calcular_total esperaba un dict, pero recibió {type(datos)}")
         return datos # Devolver sin modificar o lanzar error

    for nombre_carrito, carrito_data in datos.items():
        if not isinstance(carrito_data, dict):
            logger.warning(f"Elemento para '{nombre_carrito}' no es un diccionario, saltando cálculo de total.")
            continue

        total = Decimal('0.00') # Usar Decimal para precisión monetaria
        total_efectivo = Decimal('0.00')

        # Procesar Articulos (con registro)
        articulos = carrito_data.get('articulos', [])
        if not isinstance(articulos, list):
             logger.warning(f"'articulos' para '{nombre_carrito}' no es una lista, saltando.")
             articulos = []

        for articulo in articulos:
            try:
                # Los precios vienen como string desde articulo_to_dict
                precio = Decimal(articulo.get('precio', '0'))
                precio_efectivo = Decimal(articulo.get('precio_efectivo', '0'))
                cantidad = int(articulo.get('cantidad', 0))

                if cantidad < 0:
                     logger.warning(f"Cantidad negativa encontrada en {nombre_carrito} - Articulo ID {articulo.get('id')}. Ignorando para total.")
                     continue

                total += precio * cantidad
                total_efectivo += precio_efectivo * cantidad
            except (InvalidOperation, TypeError, ValueError) as e:
                 logger.error(f"Error al procesar artículo {articulo.get('id')} en carrito '{nombre_carrito}': {e}. Artículo: {articulo}")
            except Exception as e:
                  logger.error(f"Error inesperado procesando artículo {articulo.get('id')} en carrito '{nombre_carrito}': {e}", exc_info=True)


        # Procesar ArticulosSinRegistro
        articulos_sr = carrito_data.get('articulos_sin_registro', [])
        if not isinstance(articulos_sr, list):
            logger.warning(f"'articulos_sin_registro' para '{nombre_carrito}' no es una lista, saltando.")
            articulos_sr = []

        for articulo_sr in articulos_sr:
             try:
                # Precio viene como string, usarlo para ambos totales
                precio = Decimal(articulo_sr.get('precio', '0'))
                cantidad = int(articulo_sr.get('cantidad', 0))

                if cantidad < 0:
                     logger.warning(f"Cantidad negativa encontrada en {nombre_carrito} - ArticuloSinRegistro ID {articulo_sr.get('id')}. Ignorando.")
                     continue

                total += precio * cantidad
                total_efectivo += precio * cantidad # Usa precio normal para efectivo
             except (InvalidOperation, TypeError, ValueError) as e:
                 logger.error(f"Error al procesar art sin registro {articulo_sr.get('id')} en carrito '{nombre_carrito}': {e}. Artículo: {articulo_sr}")
             except Exception as e:
                  logger.error(f"Error inesperado procesando art sin registro {articulo_sr.get('id')} en carrito '{nombre_carrito}': {e}", exc_info=True)


        # Guardar totales como string para consistencia JSON
        carrito_data['total'] = str(total)
        carrito_data['total_efectivo'] = str(total_efectivo)
        logger.debug(f"Totales para '{nombre_carrito}': Normal={total}, Efectivo={total_efectivo}")

    return datos


def carrito_to_dict(carrito):
    """Convierte una instancia de Carrito a un diccionario simple."""
    if not carrito:
        logger.warning("carrito_to_dict recibió None.")
        return {}
    logger.debug(f"Convirtiendo Carrito ID {carrito.id} a dict.")
    return {
        'id': carrito.id,
        'usuario': carrito.usuario.username if carrito.usuario else 'Usuario no asignado',
        # Añadir otros campos relevantes si existen en el modelo Carrito
        # 'fecha_creacion': carrito.fecha_creacion.isoformat() if carrito.fecha_creacion else None,
    }