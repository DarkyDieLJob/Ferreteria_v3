# Informe de Arquitectura - Errores y Refactorizaciones

**Proyecto:** Ferreteria v3  
**Fecha:** 2026-07-13  
**Objetivo:** Detectar errores de novato en arquitectura y proponer refactorizaciones sin romper funcionalidad existente.

---

## Índice

1. [Categorización de hallazgos](#1-categorización-de-hallazgos)
2. [CRÍTICO - Seguridad](#2-crítico---seguridad)
3. [ALTO - Configuración y settings](#3-alto---configuración-y-settings)
4. [ALTO - Código legacy y duplicación](#4-alto---código-legacy-y-duplicación)
5. [ALTO - Arquitectura de apps](#5-alto---arquitectura-de-apps)
6. [MEDIO - Modelos y datos](#6-medio---modelos-y-datos)
7. [MEDIO - Vistas y controladores](#7-medio---vistas-y-controladores)
8. [MEDIO - Manejo de errores](#8-medio---manejo-de-errores)
9. [BAJO - Código y estilo](#9-bajo---código-y-estilo)
10. [BAJO - Organización de archivos](#10-bajo---organización-de-archivos)
11. [Resumen de refactorizaciones propuestas](#11-resumen-de-refactorizaciones-propuestas)
12. [Plan de ejecución sin romper](#12-plan-de-ejecución-sin-romper)

---

## 1. Categorización de hallazgos

| Severidad | Cantidad | Categoría |
|-----------|----------|-----------|
| CRÍTICO | 4 | Seguridad |
| ALTO | 8 | Configuración, legacy, arquitectura |
| MEDIO | 12 | Modelos, vistas, errores |
| BAJO | 10 | Código, estilo, organización |
| **Total** | **34** | |

---

## 2. CRÍTICO - Seguridad

### 2.1 `SECRET_KEY` hardcodeada en código

**Archivo:** `core_config/settings.py:225`
```python
SECRET_KEY = 'django-insecure-5258*z#xf)z0f5bthv+xwa1v1n82(kmivxn1rd3l3ox6h8$s06'
```

**Problema:** La secret key está commiteada en el repositorio. Cualquiera con acceso al código puede firmar sesiones, tokens CSRF y cookies.

**Refactorización:**
```python
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-...')
```
Usar `.env` con `python-dotenv` (ya instalado) para desarrollo, y variables de entorno en producción.

---

### 2.2 `DEBUG = True` en producción

**Archivo:** `core_config/settings.py:229`
```python
DEBUG = True
```

**Problema:** Expone tracebacks completos, información sensible del servidor y desactiva protecciones de seguridad.

**Refactorización:**
```python
DEBUG = os.environ.get('DJANGO_DEBUG', 'False').lower() == 'true'
```

---

### 2.3 `ALLOWED_HOSTS = ['*']`

**Archivo:** `core_config/settings.py:231-232`
```python
ALLOWED_HOSTS = ['172.17.0.3','darkydiel.pythonanywhere.com','localhost', ...]
ALLOWED_HOSTS = ['*']  # ← Sobrescribe la lista anterior
```

**Problema:** La segunda línea anula completamente la primera. Permite requests desde cualquier Host header, habilitando ataques de host header injection.

**Refactorización:**
```python
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

---

### 2.4 `@csrf_exempt` masivo en endpoints de venta

**Archivos:** `facturacion/views.py` (7 endpoints), `bdd/views/ajax.py` (1 endpoint), `boletas/views.py` (1 clase)

**Problema:** Todos los endpoints AJAX de carrito, transacciones y facturación están exentos de CSRF. Un atacante puede realizar operaciones de venta, modificar carritos y disparar impresiones fiscales desde otro sitio.

**Refactorización progresiva:**
1. **Fase 1 (no rompe):** Documentar cuáles endpoints son internos vs externos
2. **Fase 2 (no rompe):** Agregar validación de `Origin` header en los endpoints exentos
3. **Fase 3 (puede romper JS legacy):** Reemplazar `@csrf_exempt` por CSRF token en headers AJAX. El JS de `tabla_buscador.html` ya usa `Cookies.get('csrftoken')` en algunos lugares pero no consistentemente.

```python
# Fase 2: Validación de origen sin romper
def require_same_origin(view_func):
    def wrapped(request, *args, **kwargs):
        origin = request.headers.get('Origin', '')
        allowed = request.build_absolute_uri('/').rstrip('/')
        if origin and origin not in (allowed, ''):
            return JsonResponse({'error': 'Origin no permitido'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapped
```

---

## 3. ALTO - Configuración y settings

### 3.1 Import inútil que ejecuta código al cargar

**Archivo:** `core_config/settings.py:20`
```python
from ensurepip import bootstrap  # ← Import inútil, nunca se usa
```

**Problema:** `ensurepip.bootstrap` es una función del módulo ensurepip que se ejecuta para instalar pip en entornos aislados. Importar `bootstrap` desde `ensurepip` tiene side effects (puede intentar bootstrapping de pip) y no se usa en ningún lado.

**Refactorización:** Eliminar la línea.

---

### 3.2 IPs y IDs de Google Drive hardcodeados en settings

**Archivo:** `core_config/settings.py:25,32-36`
```python
os.environ['IP_BEW_SOCKET'] = 'ws://192.168.1.119:12000/ws'
INBOX = '15yv7_Nk_8gbwbhOzsV2t9Qs-ANQEjedG'
PLANTILLAS = '1G-TtSaGhLa5-d_PnIbLqnz59henhngwo'
DESCARGAR = '1Ax9N63ac7XRS9qXrbNUnpAnQcbN1CMho'
IP_BEW_SOCKET = "ws://192.168.1.119:12000/ws"
```

**Problemas:**
- La IP del WebSocket se setea dos veces (línea 25 como `os.environ` y línea 36 como variable)
- IDs de Google Drive hardcodeados (si se comparte el repo, se exponen)
- IP local hardcodeada (cambia entre entornos)

**Refactorización:**
```python
IP_BEW_SOCKET = os.environ.get('IP_BEW_SOCKET', 'ws://localhost:12000/ws')
INBOX = os.environ.get('DRIVE_INBOX_ID', '')
PLANTILLAS = os.environ.get('DRIVE_PLANTILLAS_ID', '')
DESCARGAR = os.environ.get('DRIVE_DESCARGAR_ID', '')
```

---

### 3.3 `STATIC_ROOT` vs `STATIC_ROOT_S` - confusión de nombres

**Archivo:** `core_config/settings.py:210-214`
```python
STATIC_ROOT_S = os.path.join(BASE_DIR, 'static')  # ← Nombre no estándar
STATIC_URL = '/static/'
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)
```

**Problema:** Django usa `STATIC_ROOT` para `collectstatic`. Aquí se llama `STATIC_ROOT_S` (con sufijo `_S`), lo que significa que `collectstatic` fallará en producción. Además `STATIC_ROOT_S` y `STATICFILES_DIRS` apuntan al mismo directorio, lo cual Django no permite (warning en `collectstatic`).

**Refactorización:**
```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directorio separado para collectstatic
```

---

### 3.4 No hay separación de settings por entorno

**Problema:** Un único `settings.py` de 406 líneas que mezcla desarrollo y producción. No hay `settings_dev.py`, `settings_prod.py`, ni variables de entorno (excepto logging).

**Refactorización (sin romper):**
1. Crear `.env` con `python-dotenv` (ya importado en `actualizador_main.py`)
2. Mover valores sensibles a `.env`
3. Mantener `settings.py` como base con defaults
4. Opcional: `settings_prod.py` que hereda y sobrescribe

---

### 3.5 `EMAIL_BACKEND` en modo consola

**Archivo:** `core_config/settings.py:280`
```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

**Problema:** Los emails se imprimen por consola en lugar de enviarse. Si hay recuperación de contraseña, no funcionará.

**Refactorización:** Mover a `.env` con SMTP config.

---

### 3.6 `CELERY_BROKER_URL` definido pero Celery no configurado

**Archivo:** `core_config/settings.py:406`
```python
CELERY_BROKER_URL = 'amqp://guest:guest@172.17.0.4:5672//'
```

**Problema:** Hay un `core_config/celery.py` pero Celery no está en `INSTALLED_APPS` ni hay tareas registradas con `@shared_task`. El `actualizador/task.py` implementa su propia cola con `threading` en lugar de usar Celery. La URL del broker tiene IP hardcodeada.

**Refactorización:** O bien configurar Celery properly o eliminar la configuración muerta.

---

## 4. ALTO - Código legacy y duplicación

### 4.1 `bdd/views_old.py` - 1242 líneas de código duplicado activo

**Problema:** `views_old.py` contiene duplicados de `MiVista`, `MyForm`, `Inicio`, `ItemsView`, `Imprimir`, `ListarCarteles`, y todas las funciones AJAX. Pero **aún está en uso**:

- `bdd/urls.py:5-8` importa `Imprimir`, `ItemsView` desde `views_old`
- `bdd/urls.py:23` importa `ListarCarteles` desde `views_old`
- `facturacion/views.py:5` importa `Inicio` desde `views_old` (sobrescrito en línea 6)

**Refactorización (sin romper):**
1. **Fase 1:** Mover `Imprimir`, `ItemsView`, `ListarCarteles` de `views_old.py` a `views/main.py`
2. **Fase 2:** Actualizar imports en `bdd/urls.py` y `facturacion/views.py`
3. **Fase 3:** Eliminar `views_old.py` (1242 líneas menos)

---

### 4.2 Scripts sueltos en la raíz del proyecto

**Archivos en raíz:**
```
actualizador_csv.py    (13869 bytes)  ← Duplicado de actualizador/actualizador_csv.py
actualizador_main.py   (12647 bytes)  ← Duplicado de actualizador/actualizador_main.py
actualizador_csv.py    (5605 bytes)
cargar_datos_csv.py    (1911 bytes)
script.py              (5605 bytes)
reset_pass.py          (351 bytes)
agregar_csv_ignore.py  (839 bytes)
script_seteado_false_lista_faltantes.py (364 bytes)
ejecutar_utils.py      (87 bytes)
```

**Problema:** Hay duplicados de `actualizador_csv.py` y `actualizador_main.py` en la raíz y dentro de `actualizador/`. Scripts sueltos sin gestión ni documentación.

**Refactorización:** Mover a `scripts/` o eliminar si ya están dentro de la app.

---

### 4.3 Dos sistemas fiscales paralelos

**Problema:** `facturacion/classes.py` tiene dos sistemas completos:
- `ComandoFiscal` (legacy): genera `Boleta` + `Comando` en DB, usa `boletas` app para polling
- `TicketFactura` (actual): genera JSON en memoria, envía via WebSocket directo

El sistema legacy sigue en el código pero `procesar_transaccion` usa `TicketFactura`.

**Refactorización (sin romper):**
1. **Fase 1:** Verificar que `ComandoFiscal` no se llama desde ningún lado (grep)
2. **Fase 2:** Si no se usa, mover a `facturacion/legacy.py` o eliminar
3. **Fase 3:** Evaluar si `boletas` app se puede eliminar (solo sirve al legacy)

---

### 4.4 Doble import de `Inicio` en `facturacion/views.py`

**Archivo:** `facturacion/views.py:5-6`
```python
from bdd.views_old import Inicio  # ← Import inútil (sobrescrito)
from bdd.views.main import Inicio  # ← Este es el que queda
```

**Refactorización:** Eliminar línea 5.

---

## 5. ALTO - Arquitectura de apps

### 5.1 `bdd` es un Dios-módulo (God object)

**Problema:** `bdd` centraliza:
- Modelos de inventario (Item, Articulo, Cajon, Sub_Carpeta, Sub_Titulo)
- Modelos de proveedores (Proveedor, ListaProveedores)
- Modelos de pedidos (Lista_Pedidos, Carrito, Articulo)
- Modelos de UI (NavBar, Armador, Contenedor, Pie, Head)
- Modelos de registros (Registro, Registro_Stock)
- Clase de integración Google (Patoba - 832 líneas)
- Vistas dinámicas (Armador)
- AJAX endpoints de carrito
- Funciones helper (funtions.py)

**12 apps importan desde `bdd`**: facturacion, boletas, actualizador, administracion_financiera, reportes, x_cartel, x_articulos, pedido, y scripts.

**Refactorización (sin romper, gradual):**
1. **Fase 1:** Extraer `Patoba` a un servicio independiente (`core_google/` o `integrations/`)
2. **Fase 2:** Extraer modelos de UI (NavBar, Armador, etc.) a `core_andamios/models.py`
3. **Fase 3:** Extraer modelos de inventario a `inventario/` o `articulos/` (que ya existe pero está vacía)
4. **Fase 4:** `bdd` queda solo como orquestador de vistas dinámicas

**Nota:** Cada fase mantiene los imports viejos funcionando via re-exports.

---

### 5.2 URLs dinámicas con `except: pass` silencioso

**Archivo:** `bdd/urls.py:53`
```python
try:
    armador = Armador.objects.get(nav_bar=nav_bar)
    vista = import_string(f"bdd.views.{armador.vista}")
    armador_paths.append(path(...))
except:
    pass  # ← Silencioso: si falla, la URL no existe y no hay log
```

**Problema:** Un `except:` bare silencia cualquier error (ImportError, AttributeError, DoesNotExist, SyntaxError...). Si una vista configurada en DB tiene un typo, la URL simplemente no existe sin ninguna pista.

**Refactorización:**
```python
except Armador.DoesNotExist:
    logger.warning("No hay Armador para NavBar id=%s", nav_bar.id)
except ImportError as e:
    logger.error("Vista '%s' no encontrada para NavBar '%s': %s", 
                 armador.vista, nav_bar.text_display, e)
except Exception as e:
    logger.error("Error configurando URL dinámica para '%s': %s", 
                 nav_bar.text_display, e, exc_info=True)
```

---

### 5.3 URLs sin prefijo de namespace

**Archivo:** `core_config/urls.py:28-38`
```python
path("", include("carga_archivo.urls")),
path("", include("facturacion.urls")),
path("", include("boletas.urls")),
path("", include("bdd.urls")),
path("", include("x_cartel.urls")),
path("", include("x_articulos.urls")),
path("", include("actualizador.urls")),
```

**Problema:** 8 apps montadas en `""` (raíz) sin namespace. Solo `administracion_financiera`, `pedido` y `reportes` usan prefijo. Esto causa riesgo de colisión de nombres de URL y hace `reverse()` ambiguo.

**Refactorización (sin romper):**
1. **Fase 1:** Agregar `app_name` en cada `urls.py` que no lo tenga
2. **Fase 2:** Usar `reverse('app:name')` en templates y vistas
3. **Fase 3:** Opcionalmente agregar prefijos de path (`facturacion/`, `bdd/`)

**Nota:** Esto puede romper templates existentes que usan `{% url 'name' %}` sin namespace. Hacer gradual.

---

### 5.4 `x_articulos` con filtro hardcodeado

**Archivo:** `x_articulos/views.py:34`
```python
datos = Item.objects.filter(codigo__contains="metdh")
```

**Problema:** El filtro `metdh` está hardcodeado. Esta app no sirve para nada fuera de ese filtro específico.

**Refactorización:** Parameterizar via URL o eliminar si es experimental.

---

## 6. MEDIO - Modelos y datos

### 6.1 `FloatField` para dinero

**Archivos:** `bdd/models.py` (30+ campos), `facturacion/models.py` (15+ campos)

**Problema:** Todos los precios, montos y totales usan `FloatField`. Los floats tienen problemas de precisión: `0.1 + 0.2 != 0.3`. Para dinero, `DecimalField` es obligatorio.

**Inconsistencia:** `ArticuloSinRegistro` usa `DecimalField` para `precio` y `precio_efectivo`, pero `Item` usa `FloatField` para los mismos conceptos.

**Refactorización (sin romper, gradual):**
1. **Fase 1:** Nuevos modelos usan `DecimalField`
2. **Fase 2:** Migrar campos existentes con `RunPython` que convierta floats a Decimal
3. **Fase 3:** Actualizar vistas que hacen aritmética con `round()` manual

**Nota:** SQLite no tiene tipo Decimal nativo, pero Django lo maneja correctamente.

---

### 6.2 `Patoba(None)` - instanciación sin request

**Archivos:** `actualizador/sincronizador.py:31,42`, `actualizador/actualizador_main.py` (lazy)

**Problema:** `Patoba` requiere un `request` para obtener credenciales OAuth del usuario. Cuando se pasa `None`, usa el usuario ID 1 (hardcodeado en `Patoba.__init__`). Esto significa que las tareas en background usan las credenciales del usuario 1, no del usuario que disparó la tarea.

**Refactorización:**
- Guardar el `user_id` en la cola de tareas al encolar
- Pasar el `user_id` a `Patoba` en lugar de `request`
- `Patoba` debe poder obtener credenciales por `user_id`

---

### 6.3 Consultas a DB en `urls.py` al cargar

**Archivo:** `bdd/urls.py:38`
```python
dos = NavBar.objects.all()  # ← Query en import time
```

**Problema:** Las URLs se generan dinámicamente consultando la DB al cargar el módulo. Si la DB no está lista (migraciones iniciales, tests), falla. El `except Exception` lo captura pero las URLs dinámicas no se registran.

**Refactorización:** Usar un middleware que resuelva URLs dinámicas en runtime, o cargar lazy en el primer request.

---

### 6.4 `CONSUMIDOR_FINAL_ID = 1` hardcodeado

**Archivo:** `facturacion/views_clientes.py:31`
```python
CONSUMIDOR_FINAL_ID = 1
```

**Problema:** Asume que el cliente con ID 1 es Consumidor Final. Si se borra o se recrea la DB, esto falla silenciosamente.

**Refactorización:** Usar `get_or_create` en una señal post_migrate o un data migration.

---

### 6.5 `administracion_financiera.Boleta` vs `boletas.Boleta` - colisión de nombres

**Problema:** Dos modelos llamados `Boleta` en apps distintas con significados completamente diferentes:
- `boletas.Boleta`: Cola de comandos para impresora fiscal
- `administracion_financiera.Boleta`: Boleta de proveedor (factura de compra)

**Refactorización:** Renombrar `boletas.Boleta` a `ComandoBoleta` o `boletas.BoletaFiscal`.

---

## 7. MEDIO - Vistas y controladores

### 7.1 `asyncio.run()` en views sincrónicas

**Archivos:** `facturacion/views.py:87,666,912`

**Problema:** `asyncio.run()` crea un nuevo event loop en cada llamada. Si Django usa un loop async (ASGI), esto puede causar conflictos. Además, bloquea el hilo de la vista mientras espera la respuesta del WebSocket.

**Refactorización:**
- **Corto plazo:** Usar `sync_to_async` o `nest_asyncio` si hay problemas
- **Largo plazo:** Mover a Celery task o canal de Django Channels

---

### 7.2 Falta de autenticación en endpoints AJAX

**Archivos:** `bdd/views/ajax.py` (todos los endpoints), `facturacion/views.py` (todos los endpoints)

**Problema:** Ningún endpoint AJAX verifica autenticación. `carrito`, `editar_item`, `agregar_articulo_a_carrito`, `procesar_transaccion` son accesibles sin login.

**Refactorización (sin romper):**
```python
from django.contrib.auth.decorators import login_required

@login_required
def carrito(request):
    ...
```

**Nota:** Puede romper si hay JS que funciona sin sesión. Verificar primero.

---

### 7.3 `print()` en lugar de `logger` en código de producción

**Archivos:** `x_cartel/views.py` (3 prints), `bdd/views_old.py` (múltiples), `core_config/settings.py:218`, `bdd/urls.py:37,44,50`

**Problema:** `print()` no se captura en logs, no tiene nivel, no tiene contexto de request.

**Refactorización:** Reemplazar todos los `print()` con `logger.debug()` o `logger.info()`.

---

### 7.4 `HiloManager.agregar_proceso()` es bloqueante

**Archivo:** `actualizador/task.py:155-170`
```python
def agregar_proceso(self, name, nuevo_name, proceso_nuevo, ...):
    self.hilos[name].join()  # ← Bloquea hasta que termine
```

**Problema:** Si se llama desde una vista, bloquea el request hasta que el hilo anterior termine.

**Refactorización:** Ya existe `ColaTareasWorker` que es no bloqueante. Eliminar `HiloManager` o marcar como deprecated.

---

## 8. MEDIO - Manejo de errores

### 8.1 `except:` bare (sin especificar excepción)

**18 ocurrencias** en:
- `bdd/urls.py:53`
- `bdd/views_old.py:114,118,188,197,201,311,315,358,362,441,445`
- `bdd/classes.py:413,630`
- `facturacion/views.py:232`
- `actualizador_csv.py:65,130`
- `actualizador_main.py:192`
- `script.py:68`

**Problema:** `except:` captura TODO incluyendo `KeyboardInterrupt`, `SystemExit` y `GeneratorExit`. Oculta bugs reales.

**Refactorización:** Reemplazar cada `except:` con `except Exception:` como mínimo, idealmente con la excepción específica esperada.

---

### 8.2 `subprocess.call(comando, shell=True)` - inyección de comandos

**Archivo:** `actualizador/task.py:85`
```python
subprocess.call(comando, shell=True)
```

**Problema:** `shell=True` permite inyección de comandos si `comando` contiene input del usuario.

**Refactorización:** Usar `subprocess.run(comando.split(), shell=False)` o `shlex.split()`.

---

### 8.3 `ast.literal_eval` sobre input del POST

**Archivos:** `actualizador/views.py:387`, `facturacion/views.py:930`

**Problema:** `ast.literal_eval` es más seguro que `eval()`, pero sigue siendo innecesario si el cliente envía JSON. Usar `json.loads()`.

**Refactorización:** Cambiar el formato del POST a JSON y usar `json.loads()`.

---

### 8.4 `os.system()` con `shell=True` implícito

**Archivos:** `agregar_csv_ignore.py:21`, `script.py:147,150`

**Problema:** `os.system(f"git rm --cached {linea.strip()}")` permite inyección si `linea` contiene caracteres especiales.

**Refactorización:** Usar `subprocess.run(['git', 'rm', '--cached', linea.strip()])`.

---

## 9. BAJO - Código y estilo

### 9.1 Typos en nombres de variables y funciones

| Archivo | Typo | Correcto |
|---------|------|----------|
| `facturacion/funtions.py` | `funtions` | `functions` |
| `bdd/funtions.py` | `funtions` | `functions` |
| `boletas/funtions.py` | `funtions` | `functions` |
| `core_config/settings.py:36` | `IP_BEW_SOCKET` | `IP_WEB_SOCKET` |
| `core_config/urls.py:40` | `bienbenida` | `bienvenida` |
| `facturacion/views.py` | `CierreZVieW` | `CierreZView` |
| `actualizador/sincronizador.py` | `buckup` | `backup` |
| `actualizador/task.py` | `buckup` | `backup` |

**Refactorización:** Renombrar archivos y variables. Usar imports relativos para que no rompa.

---

### 9.2 `from ensurepip import bootstrap` - import fantasma

Ya mencionado en 3.1. Eliminar.

---

### 9.3 Comentarios de debug en código de producción

**Archivos:** `bdd/urls.py:37,44,50,55,118-124` (comentados `# print(...)`)

**Refactorización:** Eliminar comentarios de debug.

---

### 9.4 `x_cartel/views.py:13` - `print(cartelitos)` en producción

```python
context["cartelitos"] = cartelitos
print(cartelitos)  # ← Debug print
```

**Refactorización:** Eliminar.

---

### 9.5 `x_cartel/views.py:20` - `get_context_data` con firma incorrecta

```python
def get_context_data(self, request, *args, **kwargs):  # ← `request` no va aquí
```

**Problema:** `get_context_data` no recibe `request` como parámetro. Django lo llama con `**kwargs` solo. El `request` se accede via `self.request`. Esto funciona porque se llama manualmente en `get()` y `post()`, pero rompería si se usa con mixins estándar.

**Refactorización:**
```python
def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # usar self.request
```

---

### 9.6 Imports duplicados en `utils/queryset_to_xlsx.py`

```python
import openpyxl  # línea 5
import openpyxl  # línea 8 (duplicado)
```

Y `import os` duplicado en `actualizador/sincronizador.py:1,4`.

**Refactorización:** Eliminar duplicados.

---

### 9.7 `utils/queryset_to_xlsx.py` ejecuta `arrancar_django_config()` al importar

**Archivo:** `utils/queryset_to_xlsx.py:3`
```python
arrancar_django_config()  # ← Se ejecuta al importar
```

**Problema:** Si se importa desde Django, `django.setup()` ya fue llamado. Llamarlo de nuevo puede causar `populate() isn't reentrant`.

**Refactorización:** Envolver en `if __name__ == '__main__':` o usar guard `if not django.apps.apps.ready:`.

---

## 10. BAJO - Organización de archivos

### 10.1 Apps abandonadas en `INSTALLED_APPS`

**Archivo:** `core_config/settings.py:242-261`

Apps en `INSTALLED_APPS` que no tienen funcionalidad:
- `x_widgets` - sin modelos, sin vistas, sin URLs
- `cajas` - sin modelos, sin vistas, sin URLs
- `articulos` - tiene modelos pero sin vistas ni URLs (duplica `bdd`)
- `core_testing` - vacía

**Refactorización:** Remover de `INSTALLED_APPS` y eliminar directorios.

---

### 10.2 `__init__.py` en raíz del proyecto

**Archivo:** `/home/fedora/Documentos/GitHub/Ferreteria_v3/__init__.py` (vacío)

**Problema:** Hace que el directorio raíz sea un paquete Python, lo cual no es necesario para un proyecto Django.

**Refactorización:** Eliminar (verificar que no rompa imports primero).

---

### 10.3 Templates dispersos

**Problema:** Los templates están en dos lugares:
- `static/templates/` (templates globales: `generic_template.html`, `tabla_buscador.html`, etc.)
- `<app>/templates/<app>/` (templates por app)

Django busca en `STATIC_ROOT_S/templates` (configurado en TEMPLATES DIRS) y en cada app con `APP_DIRS: True`.

**Refactorización:** Mover templates globales a `core_templates/templates/` o mantener pero documentar.

---

### 10.4 `facturacion/readme.md` documenta el protocolo fiscalberry, no la app

**Problema:** El readme de 466 líneas documenta el protocolo de impresión fiscal Hasar/Epson, no la app Django.

**Refactorización:** Mover a `docs/protocolo_fiscalberry.md` y crear readme real de la app.

---

## 11. Resumen de refactorizaciones propuestas

### Prioridad 1: Seguridad (CRÍTICO)

| # | Refactorización | Esfuerzo | Riesgo |
|---|----------------|----------|--------|
| 1 | `SECRET_KEY` a env var | 5 min | Ninguno |
| 2 | `DEBUG` a env var | 5 min | Ninguno |
| 3 | `ALLOWED_HOSTS` a env var | 5 min | Ninguno |
| 4 | CSRF en endpoints AJAX | 2-4h | Medio (JS) |

### Prioridad 2: Limpieza de legacy (ALTO)

| # | Refactorización | Esfuerzo | Riesgo |
|---|----------------|----------|--------|
| 5 | Eliminar `views_old.py` | 2h | Bajo (mover 3 vistas) |
| 6 | Eliminar import fantasma `bootstrap` | 1 min | Ninguno |
| 7 | Eliminar scripts sueltos en raíz | 30 min | Bajo |
| 8 | Eliminar `ComandoFiscal` legacy | 1h | Bajo (verificar uso) |
| 9 | Eliminar import duplicado `Inicio` | 1 min | Ninguno |

### Prioridad 3: Arquitectura (ALTO)

| # | Refactorización | Esfuerzo | Riesgo |
|---|----------------|----------|--------|
| 10 | Settings por entorno (.env) | 2h | Bajo |
| 11 | `STATIC_ROOT` correcto | 10 min | Bajo |
| 12 | Fix `except:` bare (18 casos) | 1h | Bajo |
| 13 | `app_name` en URLs | 2h | Medio (templates) |
| 14 | Autenticación en endpoints AJAX | 1h | Medio |
| 15 | Fix URLs dinámicas (except: pass) | 30 min | Bajo |

### Prioridad 4: Modelos y datos (MEDIO)

| # | Refactorización | Esfuerzo | Riesgo |
|---|----------------|----------|--------|
| 16 | `FloatField` → `DecimalField` | 4-8h | Alto (migración) |
| 17 | `Patoba(None)` → `Patoba(user_id)` | 2h | Medio |
| 18 | `CONSUMIDOR_FINAL_ID` dinámico | 30 min | Bajo |
| 19 | Renombrar `Boleta` duplicada | 1h | Medio |

### Prioridad 5: Código y estilo (BAJO)

| # | Refactorización | Esfuerzo | Riesgo |
|---|----------------|----------|--------|
| 20 | Typos en nombres (`funtions`, `BEW`, `bienbenida`) | 1h | Bajo |
| 21 | `print()` → `logger` | 30 min | Ninguno |
| 22 | Eliminar apps abandonadas | 30 min | Bajo |
| 23 | Fix imports duplicados | 5 min | Ninguno |
| 24 | Fix `get_context_data` en x_cartel | 10 min | Bajo |
| 25 | `subprocess.call` → `subprocess.run` sin shell | 10 min | Bajo |

---

## 12. Plan de ejecución sin romper

### Principio: Cada cambio debe ser independiente y reversible.

### Sprint 1: Quick wins (1 día)

1. `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` → env vars
2. Eliminar `from ensurepip import bootstrap`
3. Eliminar import duplicado `Inicio` en `facturacion/views.py`
4. Eliminar `print()` en `x_cartel/views.py`
5. Fix `STATIC_ROOT` → `STATIC_ROOT`
6. Eliminar imports duplicados
7. Fix `except:` bare → `except Exception:`
8. `subprocess.call(shell=True)` → `subprocess.run(shell=False)`

**Criterio de éxito:** `python manage.py check` pasa, tests existentes pasan.

### Sprint 2: Legacy cleanup (1-2 días)

1. Mover `Imprimir`, `ItemsView`, `ListarCarteles` de `views_old.py` a `views/main.py`
2. Actualizar imports en `bdd/urls.py` y `facturacion/views.py`
3. Eliminar `views_old.py`
4. Mover scripts sueltos a `scripts/`
5. Verificar que `ComandoFiscal` no se usa, eliminar si es seguro
6. Eliminar apps abandonadas de `INSTALLED_APPS`

**Criterio de éxito:** Todas las URLs responden, no hay ImportError.

### Sprint 3: Settings y seguridad (1-2 días)

1. Crear `.env` con `python-dotenv`
2. Mover IPs, IDs de Drive, y config sensible a `.env`
3. Agregar `app_name` en `urls.py` de cada app
4. Agregar `@login_required` en endpoints AJAX
5. Fix URLs dinámicas (except: pass → except Exception con log)

**Criterio de éxito:** Login funciona, endpoints AJAX requieren auth, URLs dinámicas loguean errores.

### Sprint 4: Arquitectura (1-2 semanas)

1. Extraer `Patoba` a módulo independiente
2. Extraer modelos de UI a `core_andamios`
3. `FloatField` → `DecimalField` con migración de datos
4. Renombrar typos (`funtions` → `functions`, etc.)

**Criterio de éxito:** Tests pasan, imports viejos funcionan via re-exports, migraciones aplican sin pérdida de datos.

---

## Apéndice A: Mapa de dependencias (acoplamiento)

```
bdd ← (12 apps dependen de ella)
  ├── facturacion (models, views, classes, funtions)
  ├── boletas (models)
  ├── actualizador (models, classes, views, funtions)
  ├── administracion_financiera (models, views)
  ├── reportes (classes via adapter)
  ├── x_cartel (models, views)
  ├── x_articulos (models, forms, views)
  ├── pedido (models, views)
  └── scripts sueltos
```

**Nivel de acoplamiento:** CRÍTICO. `bdd` es un single point of failure. Cualquier cambio en `bdd/models.py` afecta a 12 apps.

## Apéndice B: Métricas del codebase

| Métrica | Valor |
|---------|-------|
| Apps Django | 17 |
| Apps activas | 11 |
| Apps abandonadas | 6 |
| Líneas totales (py) | ~15000 |
| Archivo más grande | `bdd/views_old.py` (1242 líneas) |
| `@csrf_exempt` | 10 endpoints |
| `except:` bare | 18 ocurrencias |
| `print()` en producción | 10+ archivos |
| `FloatField` para dinero | 45+ campos |
| Scripts sueltos en raíz | 9 |
| Imports desde `bdd` | 12 apps |
| Modelos duplicados | 2 (`Boleta`, `Articulo`) |
