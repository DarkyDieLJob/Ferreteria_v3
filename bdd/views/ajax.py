# tu_app/views/ajax.py
import json
import os
import logging
from django.conf import settings
from django.http import FileResponse, JsonResponse, HttpResponse
from django.shortcuts import render
from django.db import connection
from django.db.models import F
from django.contrib.auth.models import User, Group
import hashlib
from django.forms.models import model_to_dict
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt

# Importa modelos y utils
from ..models import (
    Lista_Pedidos,
    Item,
    ListaProveedores,
    Proveedor,
    Carrito,
    Articulo,
    Cajon,
    ArticuloSinRegistro,
    Sub_Titulo,
)
from .utils import articulo_to_dict, calcular_total, carrito_to_dict

logger = logging.getLogger(__name__)

_ITEM_BASE_PRICE_COLUMNS_CACHE = None


def _is_caja_general(user: User) -> bool:
    try:
        if not user.is_authenticated:
            return False
        if user.is_superuser:
            return True
        if user.username == "Caja":
            return True
        return user.groups.filter(name="caja_general").exists()
    except Exception:
        return False


def _item_base_price_columns_exist():
    global _ITEM_BASE_PRICE_COLUMNS_CACHE
    if _ITEM_BASE_PRICE_COLUMNS_CACHE is not None:
        return _ITEM_BASE_PRICE_COLUMNS_CACHE

    expected = {
        "final_base",
        "final_efectivo_base",
        "final_rollo_base",
        "final_rollo_efectivo_base",
    }
    try:
        with connection.cursor() as cursor:
            table = Item._meta.db_table
            columns = {
                column.name
                for column in connection.introspection.get_table_description(cursor, table)
            }
        _ITEM_BASE_PRICE_COLUMNS_CACHE = expected.issubset(columns)
    except Exception as e:
        logger.warning(f"No se pudo inspeccionar columnas base de Item: {e}")
        _ITEM_BASE_PRICE_COLUMNS_CACHE = False
    return _ITEM_BASE_PRICE_COLUMNS_CACHE


def _item_queryset_runtime_safe():
    qs = Item.objects.all()
    if not _item_base_price_columns_exist():
        qs = qs.defer(
            "final_base",
            "final_efectivo_base",
            "final_rollo_base",
            "final_rollo_efectivo_base",
        )
    return qs


def _get_cajeros_queryset():
    try:
        grupo = Group.objects.filter(name="cajeros").first()
        if not grupo:
            return User.objects.none()
        return grupo.user_set.exclude(username="Caja")
    except Exception:
        return User.objects.none()


_USER_COLOR_MAP = {
    "Mati": "#FFD54F",   # amber 300
    "Carlos": "#4FC3F7", # light blue 300
}

_PALETTE = [
    "#F44336",  # Red 500
    "#2196F3",  # Blue 500
    "#4CAF50",  # Green 500
    "#FF9800",  # Orange 500
    "#9C27B0",  # Purple 500
    "#009688",  # Teal 500
    "#795548",  # Brown 500
]


def _user_color(username: str) -> str:
    if not username:
        return "#FFFFFF"
    if username in _USER_COLOR_MAP:
        return _USER_COLOR_MAP[username]
    idx = int(hashlib.md5(username.encode("utf-8")).hexdigest(), 16) % len(_PALETTE)
    return _PALETTE[idx]


def _hsl_to_hex(h, s, l) -> str:
    # Retenido por compatibilidad si se necesitara en el futuro
    s /= 100.0
    l /= 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = l - c / 2
    if 0 <= h < 60:
        r, g, b = c, x, 0
    elif 60 <= h < 120:
        r, g, b = x, c, 0
    elif 120 <= h < 180:
        r, g, b = 0, c, x
    elif 180 <= h < 240:
        r, g, b = 0, x, c
    elif 240 <= h < 300:
        r, g, b = x, 0, c
    else:
        r, g, b = c, 0, x
    r = int((r + m) * 255)
    g = int((g + m) * 255)
    b = int((b + m) * 255)
    return f"#{r:02X}{g:02X}{b:02X}"


def crear_modificar_lista_pedidos(request, proveedor_id=None):
    if request.method == "GET":
        logger.debug(f"GET request para lista de pedidos, proveedor_id={proveedor_id}")

        try:
            proveedor_filter = {}
            if proveedor_id is not None:
                proveedor_id = int(proveedor_id)
                proveedor_filter["proveedor_id"] = proveedor_id

            items = Lista_Pedidos.objects.filter(**proveedor_filter).select_related(
                "proveedor", "item"
            )
            logger.debug(
                f"Encontrados {items.count()} pedidos para el filtro {proveedor_filter}."
            )

            data = [
                {
                    "id": item.id,
                    "proveedor": {
                        "id": item.proveedor.id,
                        "text_display": getattr(
                            item.proveedor, "text_display", str(item.proveedor)
                        ),
                    },
                    "item": {
                        "id": item.item.id,
                        "codigo": item.item.codigo,
                        "descripcion": item.item.descripcion,
                    },
                    "cantidad": item.cantidad,
                    "pedido": item.pedido,
                }
                for item in items
            ]

            return JsonResponse(data, safe=False)

        except ValueError:
            logger.warning(f"Proveedor ID inválido recibido en GET: {proveedor_id}")
            return JsonResponse({"error": "ID de proveedor inválido"}, status=400)
        except Exception as e:
            logger.error(
                f"Error obteniendo lista de pedidos (GET, proveedor_id={proveedor_id}): {e}",
                exc_info=True,
            )
            return JsonResponse({"error": "Error interno"}, status=500)

    elif request.method == "POST":
        logger.debug("POST request para crear/modificar lista de pedidos.")
        try:
            data = json.loads(request.body)
            codigo = data.get("codigo")

            if not codigo:
                logger.warning("Solicitud POST sin 'codigo' en el body.")
                return JsonResponse(
                    {"error": "Código del item es requerido"}, status=400
                )

            logger.debug(f"Código recibido: {codigo}")
            item = _item_queryset_runtime_safe().get(codigo=codigo)

            try:
                abreviatura = "/" + codigo.split("/")[-1]
                lista_proveedores = ListaProveedores.objects.get(
                    abreviatura=abreviatura
                )
                proveedor = Proveedor.objects.get(identificador=lista_proveedores)
                logger.debug(
                    f"Proveedor determinado por abreviatura '{abreviatura}': {proveedor.nombre}"
                )
            except (
                ListaProveedores.DoesNotExist,
                Proveedor.DoesNotExist,
                IndexError,
            ) as e:
                logger.error(
                    f"No se pudo determinar el proveedor para el código '{codigo}': {e}"
                )
                if item.proveedor:
                    proveedor = item.proveedor
                    logger.warning(
                        f"Usando proveedor asignado al Item como fallback: {proveedor.nombre}"
                    )
                else:
                    return JsonResponse(
                        {"error": "No se pudo determinar el proveedor para este item"},
                        status=400,
                    )

            lista_pedido, created = Lista_Pedidos.objects.get_or_create(
                item=item,
                proveedor=proveedor,
                defaults={"cantidad": 1, "pedido": False},
            )

            if created:
                logger.debug(
                    f"Creado nuevo registro en Lista_Pedidos para Item ID {item.id}."
                )
            else:
                lista_pedido.cantidad = F("cantidad") + 1
                lista_pedido.save()
                logger.debug(
                    f"Incrementada cantidad en Lista_Pedidos para ID {lista_pedido.id}."
                )

            if not item.trabajado or item.proveedor != proveedor:
                item.trabajado = True
                item.proveedor = proveedor
                item.save(update_fields=["trabajado", "proveedor"])
                logger.debug(f"Item ID {item.id} actualizado.")

            return JsonResponse(
                {
                    "success": True,
                    "lista_pedido_id": lista_pedido.id,
                    "created": created,
                }
            )

        except Item.DoesNotExist:
            logger.warning(f"Item inexistente: {codigo}")
            return JsonResponse({"error": "Item no encontrado"}, status=404)
        except Exception as e:
            logger.error(
                f"Error en POST crear_modificar_lista_pedidos: {e}", exc_info=True
            )
            return JsonResponse({"error": "Error interno"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


def seleccionar_proveedor(request):
    logger.debug("Accediendo a seleccionar_proveedor.")
    if request.accepts("application/json"):
        try:
            proveedores = Proveedor.objects.all().values("id", "nombre")
            return JsonResponse(list(proveedores), safe=False)
        except Exception as e:
            logger.error(f"Error proveedores JSON: {e}", exc_info=True)
            return JsonResponse({"error": "Error interno"}, status=500)
    else:
        try:
            proveedores = Proveedor.objects.all()
            return render(
                request, "seleccionar_proveedor.html", {"proveedores": proveedores}
            )
        except Exception as e:
            logger.error(f"Error renderizando template: {e}", exc_info=True)
            return HttpResponse("Error al cargar la página", status=500)


def cambiar_cantidad_pedido(request, id_articulo, cantidad):
    if request.method == "POST":
        logger.debug(f"POST cambiar cantidad: id={id_articulo}, cant={cantidad}")
        try:
            nueva_cantidad = int(cantidad)
            if nueva_cantidad < 0:
                return JsonResponse(
                    {"error": "Cantidad no puede ser negativa"}, status=400
                )

            pedido = Lista_Pedidos.objects.get(id=id_articulo)

            if nueva_cantidad == 0:
                pedido_id = pedido.id
                pedido.delete()
                return JsonResponse({"status": "deleted", "id": pedido_id})
            else:
                pedido.cantidad = nueva_cantidad
                pedido.save(update_fields=["cantidad"])
                return JsonResponse({"status": "ok", "nueva_cantidad": pedido.cantidad})

        except (Lista_Pedidos.DoesNotExist, ValueError):
            return JsonResponse(
                {"error": "Datos inválidos o no encontrados"}, status=404
            )
        except Exception as e:
            logger.error(f"Error cambiando cantidad: {e}", exc_info=True)
            return JsonResponse({"error": "Error interno"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


def editar_item(request, id_articulo):
    try:
        articulo = _item_queryset_runtime_safe().select_related(
            "cajon", "proveedor", "sub_titulo"
        ).get(
            id=id_articulo
        )
    except Item.DoesNotExist:
        return JsonResponse({"error": "Artículo no encontrado"}, status=404)

    if request.method == "GET":
        try:
            cajon_dict = model_to_dict(articulo.cajon) if articulo.cajon else None
            cajon_vacio_obj = Cajon(id=None, codigo="------")
            cajones_qs = [cajon_vacio_obj] + list(Cajon.objects.all())
            cajones_serialized = serializers.serialize("json", cajones_qs)

            proveedores = list(
                Proveedor.objects.all().values("id", "text_display")
            )
            proveedores_payload = [
                {"id": p["id"], "nombre": p["text_display"] or f"Proveedor {p['id']}"}
                for p in proveedores
            ]

            subtitulos_payload = list(
                Sub_Titulo.objects.all().values("id", "nombre")
            )

            return JsonResponse(
                {
                    "status": "ok",
                    "modal_stock": articulo.stock,
                    "modal_barras": articulo.barras,
                    "modal_tiene_cartel": articulo.tiene_cartel,
                    "modal_cajon": cajon_dict,
                    "cajones": cajones_serialized,
                    "modal_factor_division": articulo.factor_division,
                    "modal_proveedor_id": (
                        articulo.proveedor.id if articulo.proveedor else None
                    ),
                    "modal_sub_titulo_id": (
                        articulo.sub_titulo.id if articulo.sub_titulo else None
                    ),
                    "proveedores": proveedores_payload,
                    "subtitulos": subtitulos_payload,
                }
            )
        except Exception as e:
            logger.error(f"Error GET editar_item: {e}", exc_info=True)
            return JsonResponse({"error": "Error al obtener datos"}, status=500)

    elif request.method == "POST":
        try:
            data = json.loads(request.body)
            articulo.stock = int(data.get("stock", articulo.stock))
            articulo.barras = data.get("barras", articulo.barras) or "0"

            tiene_cartel_recibido = data.get("tiene_cartel")
            if tiene_cartel_recibido is not None:
                if isinstance(tiene_cartel_recibido, bool):
                    articulo.tiene_cartel = tiene_cartel_recibido
                elif isinstance(tiene_cartel_recibido, (int, float)):
                    articulo.tiene_cartel = bool(int(tiene_cartel_recibido))
                elif isinstance(tiene_cartel_recibido, str):
                    articulo.tiene_cartel = tiene_cartel_recibido.strip().lower() in (
                        "1", "true", "t", "yes", "y", "si", "sí"
                    )
                else:
                    articulo.tiene_cartel = bool(tiene_cartel_recibido)

            cajon_id = data.get("cajon")
            if cajon_id in ["null", None]:
                articulo.cajon = None
            elif cajon_id:
                articulo.cajon = Cajon.objects.get(id=int(cajon_id))

            update_fields = ["stock", "barras", "tiene_cartel", "cajon"]

            # Proveedor
            if "proveedor_id" in data:
                prov_id = data.get("proveedor_id")
                if prov_id in ["", None, "null"]:
                    articulo.proveedor = None
                else:
                    try:
                        articulo.proveedor = Proveedor.objects.get(id=int(prov_id))
                    except Proveedor.DoesNotExist:
                        return JsonResponse(
                            {"error": "Proveedor no encontrado"}, status=400
                        )
                update_fields.append("proveedor")

            # Sub_Titulo
            if "sub_titulo_id" in data:
                st_id = data.get("sub_titulo_id")
                if st_id in ["", None, "null"]:
                    articulo.sub_titulo = None
                else:
                    try:
                        articulo.sub_titulo = Sub_Titulo.objects.get(id=int(st_id))
                    except Sub_Titulo.DoesNotExist:
                        return JsonResponse(
                            {"error": "Sub_Titulo no encontrado"}, status=400
                        )
                update_fields.append("sub_titulo")

            # Factor de división
            if "factor_division" in data:
                fd_raw = data.get("factor_division")
                if fd_raw in ["", None, "null"]:
                    articulo.factor_division = None
                else:
                    try:
                        fd_val = float(str(fd_raw).replace(",", "."))
                        articulo.factor_division = fd_val if fd_val > 1 else None
                    except (TypeError, ValueError):
                        articulo.factor_division = None
                update_fields.append("factor_division")

            # Rederivar final/final_efectivo/final_rollo/final_rollo_efectivo
            # desde sus *_base aplicando factor_division (si > 1) y redondeo.
            # Solo si las columnas base existen en la DB (hotfix compatibility).
            if _item_base_price_columns_exist():
                articulo.recompute_finales()
                update_fields += [
                    "final",
                    "final_efectivo",
                    "final_rollo",
                    "final_rollo_efectivo",
                ]
            articulo.save(update_fields=update_fields)

            response_payload = {
                "status": "ok",
                "message": "Artículo actualizado",
            }
            if _item_base_price_columns_exist():
                response_payload.update({
                    "final": articulo.final,
                    "final_efectivo": articulo.final_efectivo,
                    "final_rollo": articulo.final_rollo,
                    "final_rollo_efectivo": articulo.final_rollo_efectivo,
                })
            return JsonResponse(response_payload)

        except Exception as e:
            logger.error(f"Error POST editar_item: {e}", exc_info=True)
            return JsonResponse({"error": "Error al actualizar"}, status=500)


def agregar_articulo_a_carrito(request, id_articulo):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Usuario no autenticado"}, status=401)

    try:
        data = json.loads(request.body)
        # Permitir cantidades decimales (soportar coma como separador)
        raw_qty = data.get("cantidad", 0)
        if isinstance(raw_qty, str):
            raw_qty = raw_qty.replace(",", ".")
        try:
            cantidad_a_agregar = float(raw_qty)
        except (TypeError, ValueError):
            cantidad_a_agregar = 0.0
        usuario_caja_id = data.get("usuario_caja")

        if cantidad_a_agregar <= 0:
            return JsonResponse({"error": "Cantidad debe ser positiva"}, status=400)

        item = _item_queryset_runtime_safe().get(id=id_articulo)

        if usuario_caja_id and _is_caja_general(request.user):
            usuario_objetivo = User.objects.get(id=usuario_caja_id)
        else:
            usuario_objetivo = request.user

        carrito, _ = Carrito.objects.get_or_create(usuario=usuario_objetivo)
        articulo_en_carrito, created = Articulo.objects.get_or_create(
            item=item,
            carrito=carrito,
            defaults={
                "cantidad": cantidad_a_agregar,
                "precio": item.final,
                "precio_efectivo": item.final_efectivo,
            },
        )

        if not created:
            articulo_en_carrito.cantidad = F("cantidad") + cantidad_a_agregar
            articulo_en_carrito.save(update_fields=["cantidad"])

        # Actualizar Lista_Pedidos
        if item.proveedor:
            pedido, p_created = Lista_Pedidos.objects.get_or_create(
                proveedor=item.proveedor,
                item=item,
                defaults={"cantidad": cantidad_a_agregar},
            )
            if not p_created:
                pedido.cantidad = F("cantidad") + cantidad_a_agregar
                pedido.save(update_fields=["cantidad"])

        return JsonResponse({"status": "ok", "message": "Agregado al carrito"})

    except Exception as e:
        logger.error(f"Error agregar_carrito: {e}", exc_info=True)
        return JsonResponse({"error": "Error interno"}, status=500)


def carrito(request):
    """Devuelve info básica del carrito del usuario actual."""
    if request.method == "GET":
        logger.debug("GET request para obtener información del carrito.")
        if not request.user.is_authenticated:
            logger.warning("Intento de ver carrito por usuario no autenticado.")
            return JsonResponse({"error": "Usuario no autenticado"}, status=401)

        try:
            # Obtener carrito (crearlo si no existe para este usuario)
            carrito_obj, created = Carrito.objects.get_or_create(usuario=request.user)
            if created:
                logger.debug(f"Carrito creado para el usuario {request.user.username}")

            # Usar el helper para convertir a dict
            carrito_dict = carrito_to_dict(carrito_obj)
            return JsonResponse({"status": "ok", "carrito": carrito_dict})

        except Exception as e:
            logger.error(
                f"Error obteniendo carrito para {request.user.username}: {e}",
                exc_info=True,
            )
            return JsonResponse({"error": "Error interno"}, status=500)
    else:
        logger.warning(f"Método {request.method} no permitido para carrito.")
        return JsonResponse({"error": "Método no permitido"}, status=405)


def consultar_carrito(request):
    """Devuelve el contenido detallado de uno o más carritos."""
    if request.method == "GET":
        logger.debug("GET request para consultar contenido del carrito.")
        datos = {}

        if not request.user.is_authenticated:
            logger.warning("Intento de consultar carrito por usuario no autenticado.")
            return JsonResponse({"error": "Usuario no autenticado"}, status=401)

        try:
            if _is_caja_general(request.user):
                username_filtro = request.GET.get("usuario")
                if username_filtro:
                    usuarios = User.objects.filter(username=username_filtro)
                else:
                    usuarios = _get_cajeros_queryset()

                for u in usuarios:
                    try:
                        c_obj, _ = Carrito.objects.get_or_create(usuario=u)
                        articulos = Articulo.objects.filter(carrito=c_obj).select_related("item")
                        sin_reg = ArticuloSinRegistro.objects.filter(carrito=c_obj)
                        datos[u.username] = {
                            "articulos": [articulo_to_dict(a) for a in articulos],
                            "articulos_sin_registro": [articulo_to_dict(a) for a in sin_reg],
                            "carrito_id": c_obj.id,
                            "color": _user_color(u.username),
                        }
                    except Exception:
                        datos[u.username] = {
                            "articulos": [],
                            "articulos_sin_registro": [],
                            "carrito_id": None,
                            "error": "No encontrado",
                            "color": _user_color(u.username),
                        }
            else:
                logger.debug(
                    f"Usuario '{request.user.username}' consultando su propio carrito."
                )
                carrito, _ = Carrito.objects.get_or_create(usuario=request.user)
                articulos = Articulo.objects.filter(carrito=carrito).select_related("item")
                sin_reg = ArticuloSinRegistro.objects.filter(carrito=carrito)

                datos[request.user.username] = {
                    "articulos": [articulo_to_dict(a) for a in articulos],
                    "articulos_sin_registro": [articulo_to_dict(a) for a in sin_reg],
                    "carrito_id": carrito.id,
                    "color": _user_color(request.user.username),
                }

            # Calcular totales usando la función utilitaria
            datos_con_totales = calcular_total(datos)
            return JsonResponse(datos_con_totales)

        except Exception as e:
            logger.error(
                f"Error consultando carritos para {request.user.username}: {e}",
                exc_info=True,
            )
            return JsonResponse(
                {"error": "Error interno al consultar carritos"}, status=500
            )

    return JsonResponse({"error": "Método no permitido"}, status=405)


def usuarios_caja(request):
    """Devuelve lista de usuarios que pueden ser seleccionados como 'caja'."""
    if request.method == "GET":
        logger.debug("GET request para obtener usuarios caja.")
        try:
            usuarios = _get_cajeros_queryset().values("id", "username")
            resp = [
                {"id": u["id"], "nombre": u["username"], "color": _user_color(u["username"])}
                for u in usuarios
            ]
            return JsonResponse(resp, safe=False)

        except User.DoesNotExist as e:
            logger.error(f"Error obteniendo ID de usuario caja: {e}")
            return JsonResponse(
                {"error": "Error configurando usuarios caja"}, status=500
            )
        except Exception as e:
            logger.error(
                f"Error inesperado obteniendo usuarios caja: {e}", exc_info=True
            )
            return JsonResponse({"error": "Error interno"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


def eliminar_articulo_pedido(request):
    """Confirma o elimina un item de la Lista_Pedidos."""
    if request.method == "POST":
        pedido_id = request.POST.get("id")
        cantidad = request.POST.get("quantity")
        confirmado = request.POST.get("confirmed", "false").lower() == "true"

        logger.info(
            f"POST eliminar/confirmar pedido ID: {pedido_id}, Cant: {cantidad}, Conf: {confirmado}"
        )

        if not pedido_id:
            return JsonResponse({"error": "ID de pedido requerido"}, status=400)

        try:
            pedido = Lista_Pedidos.objects.get(id=pedido_id)

            if confirmado:
                try:
                    cantidad_validada = int(cantidad)
                    if cantidad_validada <= 0:
                        raise ValueError("Cantidad debe ser positiva.")
                except (ValueError, TypeError):
                    return JsonResponse({"error": "Cantidad inválida"}, status=400)

                pedido.pedido = True
                pedido.cantidad = cantidad_validada
                pedido.save(update_fields=["pedido", "cantidad"])
                return JsonResponse(
                    {
                        "status": "confirmed",
                        "id": pedido.id,
                        "cantidad": pedido.cantidad,
                    }
                )
            else:
                p_id = pedido.id
                pedido.delete()
                return JsonResponse({"status": "deleted", "id": p_id})

        except Lista_Pedidos.DoesNotExist:
            return JsonResponse({"error": "Pedido no encontrado"}, status=404)
        except Exception as e:
            logger.error(f"Error procesando pedido ID {pedido_id}: {e}", exc_info=True)
            return JsonResponse({"error": "Error interno"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


def descargar_archivo(request):
    """Ofrece un archivo específico para descargar."""
    logger.debug("Solicitud GET para descargar archivo.")
    nombre_del_archivo = "script_pyinstaller.py"

    try:
        ruta_al_archivo = os.path.join(settings.MEDIA_ROOT, nombre_del_archivo)
        if not os.path.exists(ruta_al_archivo):
            logger.error(f"Archivo no encontrado: {ruta_al_archivo}")
            return HttpResponse("Archivo no encontrado.", status=404)

        response = FileResponse(
            open(ruta_al_archivo, "rb"), content_type="application/octet-stream"
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{os.path.basename(nombre_del_archivo)}"'
        )
        return response
    except Exception as e:
        logger.error(f"Error al descargar '{nombre_del_archivo}': {e}", exc_info=True)
        return HttpResponse("Error al descargar el archivo.", status=500)


def reportar_item(request, articulo_id):
    """Devuelve datos iniciales para un modal de reporte."""
    if request.method == "GET":
        logger.debug(f"GET reporte item ID: {articulo_id}")
        try:
            estados = getattr(
                settings,
                "ESTADOS_REPORTE_ITEM",
                ["Cantidad mal dividida", "Falta precio en Efectivo", "Otros"],
            )

            data = {
                "status": "ok",
                "estados_posibles": estados,
                "modal_detalles": "",
                "estado_actual": estados[0],
            }
            return JsonResponse(data)
        except Exception as e:
            logger.error(
                f"Error preparando reporte ID {articulo_id}: {e}", exc_info=True
            )
            return JsonResponse({"error": "Error interno"}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


@csrf_exempt
def enviar_reporte(request, articulo_id):
    """Recibe los datos del reporte (POST)."""
    if request.method == "POST":
        logger.debug(f"POST enviar reporte item ID: {articulo_id}")
        try:
            data = json.loads(request.body)
            estado = data.get("estado")
            detalles = data.get("detalles")

            if not estado:
                return JsonResponse({"error": "El estado es requerido"}, status=400)

            try:
                item_reportado = Item.objects.get(id=articulo_id)
                # Lógica de guardado de reporte pendiente (descomentar cuando el modelo exista)
                logger.info(f"Reporte para Item ID {articulo_id} procesado.")
                return HttpResponse("Reporte enviado correctamente", status=200)

            except Item.DoesNotExist:
                return JsonResponse({"error": "Artículo no encontrado"}, status=404)
            except Exception as e:
                logger.error(
                    f"Error al guardar reporte ID {articulo_id}: {e}", exc_info=True
                )
                return JsonResponse(
                    {"error": "Error al guardar el reporte"}, status=500
                )

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON inválido"}, status=400)

    return JsonResponse({"error": "Método no permitido"}, status=405)
