# Exploration: Impresor fiscal — estado as-is (qué camino está vivo, qué quedó colgado)

**Tipo:** exploración standalone — estado real de la capa de impresión fiscal.
**Fecha:** 2026-09-24 · **Rama:** `produccion`
**Contexto previo:** `openspec/changes/explore-arquitectura-monolito/exploration.md`, `openspec/changes/explore-bdd-acoplamiento/exploration.md`, `facturacion/readme.md` (protocolo fiscalberry), `negocio_apps/DOCUMENTATION.md` §facturacion/§boletas, `docs/informe_arquitectura.md` §6.5/§10.4. Todo verificado contra código y `git log`.

---

## Veredicto (resumen ejecutivo)

**Camino vivo:** `TicketFactura` + WebSocket JSON (`procesar_transaccion` → `conectar_a_websocket` → daemon fiscalberry/printFiscal externo en la LAN → Hasar FPH441). Es el ÚNICO camino ejecutado en ventas y cierres Z.

**Camino colgado:** `ComandoFiscal` + app `boletas` (cola HTTP de comandos serie crudos). No solo está muerto — está **roto**: usa `articulo_set`/`articulosinregistro_set` pero `bdd` define `related_name="articulos"`/`"articulos_sin_registro"` (`bdd/models.py:635,649`), así que `ComandoFiscal(...)` explota en el `prefetch_related` de su `__init__` (`facturacion/classes.py:430-437`). Nadie puede instanciarlo aunque quiera. El commit `ca924e4` (ago-2024, literalmente titulado *"a medio camino"*) borró las líneas ya-comentadas `fiscal = ComandoFiscal(...)` / `ciclo_desborde(fiscal)` del flujo de venta — la desconexión es anterior a ese commit y la limpieza nunca se completó.

## Current State

### 1. Camino vivo — venta → ticket fiscal

```
static/templates/tabla_lateral_carritos.html:920   JS POST /procesar_transaccion/ (form serializado)
  → facturacion/views.py:69  procesar_transaccion  (@csrf_exempt + @require_POST, SIN auth)
    → funtions.py:88   request_on_procesar_transaccion_to_dict
    → funtions.py:109  registrar_articulos_vendidos  (@transaction.atomic)
        · crea Transaccion + ArticuloVendido (por Articulo y ArticuloSinRegistro del carrito)
        · si metodo_de_pago.id != 1  AND  cliente_id presente:
            classes.py:274 TicketFactura(transaccion).get_ticket_json()
            → lista de {"printTicket": {cabecera, items, formasPago}, "printerName": "IMPRESORA_FISCAL"}
    → views.py:85  for boleta in boletas_json:
        asyncio.run(conectar_a_websocket(boleta))     # cliente.py:14 → IP_BEW_SOCKET
        rta["rta"][0]["rta"] → numero_cbte; boleta["printTicket"]["cabecera"]["tipo_cbte"] → tipo_cbte
    → views.py:136-143  borra Articulo/ArticuloSinRegistro del carrito
    → views.py:146-156  guarda tipo_cbte/numero_cbte en la Transaccion
    → HTTP 200 → JS limpia UI del carrito (solo handler `success`; no hay handler `error`)
```

- `IP_BEW_SOCKET`: `core_config/settings.py:25` (`os.environ.setdefault`) y `:35` (`os.getenv`, default `ws://192.168.1.119:12000/ws`) — definido dos veces. El daemon es el componente **externo** `printFiscal` (fork propio de fiscalberry, `facturacion/readme.md`) que corre en un host de la LAN (la Pi) y maneja la Hasar por serie. No está en el repo ni en docker-compose.
- `TicketFactura` (classes.py:274-390): cabecera según `Cliente` (id=1 = Consumidor Final hardcodeado), items desde `ArticuloVendido.get_item()` (models.py:117 — lee `item.final`/`final_efectivo` **en vivo**, no el `Articulo.precio` capturado al cargar el carrito), forma de pago desde `MetodoPago.display` + `transaccion.total`. Boleta A (`FA`) netea IVA con `/1.21` hardcodeado (classes.py:246). `MONTO_LIMITE_TICKET = 999999999` → el split multi-ticket está deshabilitado de facto. `PRINTNAME` hardcodeado.
- Condición de "no emitir ticket": `metodo_de_pago.id != 1` (funtions.py:297-301) — ID mágico; el campo `MetodoPago.ticket` (BooleanField, models.py:138) existe para eso pero **nunca se consulta**.

### 2. Camino vivo — cierre Z

`POST /vista_cierre_z/` → `CierreZVieW.post` (views.py:655) envía `{"dailyClose": "Z", "printerName": "IMPRESORA_FISCAL"}` por WS → parsea `rta` (dict con ~20 campos del cierre Hasar) → `CierreZ.objects...save()` (views.py:705-751) → `agregar_tareas_en_cola()` (views.py:760 → `actualizador/task.py:299` encola `principal`+`principal_csv`+`buckup` en `ColaTareasWorker`, ejecución diferida a las 21:00) → redirect. GET lista los `CierreZ` históricos.

### 3. Camino colgado — ComandoFiscal + boletas

- `ComandoFiscal` (classes.py:398-847): construye en DB una `Boleta` con `Comando`/`OrdenComando` ordenados que contienen **comandos serie Hasar crudos** (`@\x1cB\x1cS` abrir comprobante, `B\x1c…\x1cT` ítem, `D\x1c` pago, `E` cierre, `9\x1cZ` cierre Z, `b\x1c` datos cliente, `_\x1c1\x1c` nombre de fantasía "Pinturería y Ferretería Paoli"). Tiene su propio split por `MONTO_LIMITE_TICKET_CMD = 25000` y su propio cálculo de totales.
- `ciclo`/`ciclo_desborde` (funtions.py:24,40): orquestan `set_encabezado → set_tipo_cliente → set_articulos[_desborde] → set_cierre`. El propio archivo lo admite: *"These cycle functions seem designed for the older ComandoFiscal"* (funtions.py:22). **Cero llamadores.**
- `boletas/` app (INSTALLED_APPS settings.py:252; mount `core_config/urls.py:30`):
  - `Boleta` (tipo A/B/C, `impreso` BooleanField **default=True**), `Comando` (string), `OrdenComando` (boleta+comando+orden) — models.py completo son 33 líneas.
  - `BoletasView` en `/boletas_pendientes/` (boletas/views.py:10): GET devuelve boletas `impreso=False` con sus comandos ordenados; POST con `status="2"` marca `impreso=True`. `@csrf_exempt`, sin auth. Era el transporte **HTTP-polling** del daemon pre-fiscalberry: el demonio consultaba pendientes, ejecutaba los comandos serie y confirmaba. Hoy: productor muerto → endpoint vivo sirviendo una cola eternamente vacía.
  - `boletas/classes.py` y `boletas/funtions.py` existen con **0 líneas**; `admin.py` registra los 3 modelos.
- `mostrara_boletas(bool_value)` (`actualizador/actualizador_csv.py:933-944`, duplicado en `actualizador_csv.py:298` raíz): hace `Boleta.objects.all().update(impreso=bool_value)` — era el release manual del lote (como `impreso` nace `True`, había que flippear para que la cola los "mostrara"). **Cero llamadores** en el repo; también el flag pendiente quedó sin cablear: `set_cierre` tiene comentado `# self.boleta.impreso = False` (classes.py:831-832).
- `script.py:85-92` (raíz): `get_status_fiscal()` instancia `ComandoFiscal(carrito_id=2, …)` — script manual de mantenimiento; hoy crashearía por el related_name.
- `facturacion/views.py:15` `from boletas.models import Boleta` — import muerto (la variable `boleta` del loop en :85 es un dict JSON, no el modelo).
- `facturacion/notebook/procesador_de_informes.py` (1646 líneas): **no es fiscal** — es un notebook Colab volcado a .py que procesa informes/Excel de Drive con pandas+gspread ("Planillas diarias" → "Informes Finales"). Tooling huérfano, nada lo importa.
- `facturacion/servidor_fake_ws.py`: server WS fake que responde un `dailyClose` fijo — utilidad manual de prueba sin impresora. No lo invoca nada.

### 4. Qué significa "colgado" acá, concretamente

No es una migración a medias funcional: es **código muerto que además está roto**, más una **superficie HTTP viva sin propósito**:

| Pieza | Estado | Evidencia |
|---|---|---|
| `ComandoFiscal` | Muerto **y roto** (imposible instanciar) | related_name incorrecto classes.py:430-437 vs bdd/models.py:635,649; único caller es script manual |
| `ciclo`/`ciclo_desborde` | Muerto | sin callers; solo type-check de ComandoFiscal |
| `/boletas_pendientes/` (GET/POST) | **Vivo pero sin productor** — endpoint abierto a una cola vacía | mount core_config/urls.py:30 |
| `mostrara_boletas` | Muerto (utilidad de shell) | sin callers; duplicado en raíz |
| `impreso` flag | Semántica contradictoria: nace `True`, la cola filtra `False`, y el seteo a `False` quedó comentado | models.py:17, classes.py:831 |
| `MetodoPago.ticket` | Campo colgado: la condición real usa `id != 1` | funtions.py:297 vs models.py:138 |
| `consulta_impresora_fiscal_generica` | **Vivo pero siempre 500**: `conectar_a_websocket` ya devuelve dict y la vista hace `json.loads(dict)` → `TypeError` escapa del `except JSONDecodeError` → 500 genérico | views.py:912-955 (bug ya documentado en negocio_docs §368) |
| `from bdd.views_old import Inicio` / `from boletas.models import Boleta` | imports muertos | views.py:5,15 |

### 5. Auth y manejo de errores

- **Auth: ninguna.** Todos los endpoints fiscales (`procesar_transaccion`, `vista_cierre_z`, `consulta_impresora_generica`, `boletas_pendientes`, y todo el CRUD del carrito) son `@csrf_exempt` + sin `login_required`/`staff_required`. Cualquiera en la LAN puede disparar un **cierre fiscal Z** con un POST.
- **Impresora offline en venta (caso grave):** `conectar_a_websocket` nunca propaga errores de conexión — devuelve `{"error": …}` (cliente.py:96-121). En `procesar_transaccion` eso cae en `rta.get("rta") → None` → warning "Formato de respuesta inesperado" (views.py:106) → **el flujo sigue**: se commitea la `Transaccion` (numero_cbte=0, tipo_cbte=""), se vacía el carrito y se devuelve **HTTP 200**. Resultado: venta registrada **sin ticket fiscal** y el cajero ve éxito (el JS ni siquiera tiene handler `error`; encima en un 500 real los inputs quedan `disabled` para siempre). Incumplimiento fiscal silencioso.
- **Impresora offline en cierre Z:** error dict → `context["error_procesamiento"]` → re-render sin guardar `CierreZ` ni encolar tareas. Comportamiento seguro.
- Dentro de `registrar_articulos_vendidos` (@atomic): carrito vacío, cantidad ≤ 0 o precio ≤ 0 → `ValueError` → rollback completo de la transacción (bien). Pero el WS corre **fuera** del atomic — nada vincula la emisión fiscal con el commit de la venta.

## Affected Areas

- `facturacion/classes.py` — `TicketFactura`+helpers (vivo, 1-390) y `ComandoFiscal` (muerto/roto, 393-847). Borrable: ~455 líneas.
- `facturacion/funtions.py` — `ciclo`/`ciclo_desborde` muertos (22-68); import `ComandoFiscal` solo para isinstance (línea 2).
- `facturacion/views.py` — imports muertos líneas 5 y 15; `procesar_transaccion` (69) y `CierreZVieW` (636) = los dos entry-points vivos; `consulta_impresora_fiscal_generica` (887) rota.
- `facturacion/cliente.py` — cliente WS vivo; errores se tragan a dicts `{"error"}`.
- `facturacion/models.py` — `CierreZ` (réplica del cierre Hasar), `Transaccion.numero_cbte` default 0 = centinela de "no se imprimió", `MetodoPago.ticket` sin uso.
- `boletas/` — app entera retirable: models, `BoletasView`, urls, admin, migraciones; `classes.py`/`funtions.py` ya vacíos.
- `actualizador/actualizador_csv.py:933` + `actualizador_csv.py:298` (raíz) — `mostrara_boletas` muerto.
- `core_config/urls.py:30`, `core_config/settings.py:252` — mount e INSTALLED_APPS de `boletas`.
- `script.py:85-92` — `get_status_fiscal` manual.
- `facturacion/notebook/procesador_de_informes.py` — no fiscal (Drive/informes); `facturacion/servidor_fake_ws.py` — mock manual.
- `facturacion/readme.md` — doc del printFiscal externo (protocolo WS); candidata a `docs/protocolo_fiscalberry.md` (informe §10.4).
- Colisión de nombres: `boletas.Boleta` (cola fiscal) vs `administracion_financiera.Boleta` (factura de proveedor) — informe §6.5.

## Approaches (para retirar el camino legacy)

1. **Retiro directo en un solo change** — borrar `ComandoFiscal`+`ciclo*`, sacar `boletas` de INSTALLED_APPS/urls/admin, borrar `mostrara_boletas`, imports muertos y `get_status_fiscal` en script.py.
   - Pros: elimina ~600 líneas + una app + un endpoint sin auth. Cons: hay que decidir qué hacer con las tablas `boletas_*` en prod (datos históricos → migración de borrado o `managed=False`); verificar en el host Pi que **ningún** daemon viejo siga polleando `/boletas_pendientes/`. Effort: Low-Medium.

2. **Retiro + tapar los agujeros del camino vivo (recomendado)** — lo anterior, más: (a) que `procesar_transaccion` distinga el dict `{"error"}` y devuelva 502/504 con handler `error` en el JS (o reintento/cola de tickets); (b) auth mínima en endpoints fiscales; (c) usar `MetodoPago.ticket` en vez del ID mágico; (d) mover el protocolo a `docs/`.
   - Pros: el retiro no deja el flanco de "venta sin ticket silencioso" tal cual. Cons: más alcance. Effort: Medium.

3. **Solo documentar y congelar** — marcar el código legacy como deprecated, no tocar nada.
   - Pros: cero riesgo. Cons: el endpoint `/boletas_pendientes/` sin auth sigue expuesto y el dead code sigue confundiendo. Effort: Low.

## Recommendation

**Approach 2**, ejecutado en dos slices: primero el retiro puro (approach 1, todo verificado como sin-callers) y después el hardening del camino vivo. Antes de borrar el endpoint, confirmar en el host Pi (`printFiscal`) que el daemon actual es el WS y que nada consulta `/boletas_pendientes/` — el readme documenta solo el protocolo WS, así que lo esperable es que el poller HTTP ya no exista. Las tablas `boletas_*` tienen historia en prod: decidir drop vs. conservar.

## Risks

- Verificación externa pendiente: el daemon `printFiscal` vive fuera del repo (host 192.168.1.119/Pi) — no se puede confirmar desde el código que el poller HTTP esté retirado del lado del daemon.
- `boletas_*` en prod DB: borrar la app sin migración deja tablas huérfanas; con migración se pierde historia.
- `procesar_transaccion` hoy commitea ventas sin ticket cuando la impresora está caída — cualquier refactor que endurezca esto cambia comportamiento observable en el mostrador (decisión de negocio: ¿bloquear la venta o registrar pendiente de impresión?).
- IDs mágicos: `Cliente` id=1 (Consumidor Final) y `MetodoPago` id=1 (sin comprobante) están hardcodeados en funtions.py/classes.py — un reseed de esas tablas rompe el flujo silenciosamente.
- Cero tests sobre el camino fiscal (`tests/facturacion/` tiene 1 test trivial de Cliente); `IP_BEW_SOCKET` default apunta a la impresora real de la LAN → riesgo si un test futuro lo alcanza (ya flagged en explore-entorno-test).

## Ready for Proposal

**Sí** — si el usuario quiere convertir esto en change, el alcance natural es: "retirar el camino fiscal legacy (`ComandoFiscal`+`boletas`) y endurecer el manejo de errores del camino vivo". La evidencia de muerte es concluyente (sin callers + related_name roto + commit 'a medio camino'); el único pendiente externo es verificar el daemon en la Pi.
