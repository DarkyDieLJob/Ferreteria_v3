# Exploration: Mapa de arquitectura y dominio del monolito Ferreteria_v3

**Tipo:** exploración standalone (sin change asociado) — contexto fundacional para futuros cambios SDD.
**Fecha:** 2026-09-23 · **Rama:** `produccion` (v3.10.x)
**Fuentes:** síntesis verificada de `docs/informe_arquitectura.md` (34 hallazgos), `docs/auditoria_documentacion.md`, `bdd/DOCUMENTATION.md`, `core_apps/DOCUMENTATION.md`, `negocio_apps/DOCUMENTATION.md`, `auxiliares_apps/DOCUMENTATION.md`, `pedido/README.md`, `openspec/config.yaml` + verificación directa del código (2026-09-23).

---

## Current State

### Stack y despliegue

- Python 3.10, Django 4.0.6, monolito MTV. SQLite por defecto (`db.sqlite3`, ~40MB); PostgreSQL 16 cuando `DB_HOST` está seteado (`core_config/settings.py:362`). gunicorn + Docker (`python:3.10-slim`) + `docker-compose.yml`.
- `core_config/settings.py` está **gitignored** (env-based), pero estuvo trackeado en historia (`git log --follow core_config/settings.py` muestra commits) → los secretos históricos siguen en el historial de git.
- Auth: `django-allauth` con provider Google — el `SocialToken` del usuario 1 es la credencial OAuth para TODA la integración Google.
- Locale `es-ar`, TZ `America/Argentina/Buenos_Aires`. UI: Bootstrap 4 + crispy-forms (administracion_financiera usa Tailwind). Releases con `scripts/release.sh` + conventional commits → `CHANGELOG.md`.

### Mapa de apps (17 locales en `INSTALLED_APPS` + `core_config` + `utils`)

| Capa | App | Responsabilidad | Estado |
|------|-----|-----------------|--------|
| **Dominio** | `bdd` | God-app: inventario (`Item` 40+ campos), proveedores, carritos, andamio dinámico (NavBar/Armador), clase `Patoba` (Google Drive/Gmail/Sheets, 832 líneas), vistas base y 11 endpoints AJAX | Activa, central |
| | `facturacion` | Ventas: `procesar_transaccion` (carrito → Transaccion → JSON fiscal), `TicketFactura` → WebSocket a impresora fiscal (fiscalberry), cierres Z, CRUD clientes | Activa |
| | `pedido` | Ciclo de pedidos a proveedores (creación, control de recepción, faltantes, devoluciones). Única app bien documentada | Activa |
| | `boletas` | Cola de comandos fiscales legacy (Boleta/Comando/OrdenComando) — solo sirve al `ComandoFiscal` legacy | Semi-abandonada |
| | `actualizador` | Pipeline de precios: descarga planillas de Gmail/Drive, parsea CSV/Sheets según `Condiciones`, actualiza `Item.*_base`, cola de tareas en hilos (`ColaTareasWorker`) | Activa, core |
| | `administracion_financiera` | Finanzas: boletas de proveedor, servicios, impuestos, cheques, cuentas, ctacte; `Pago` polimórfico (GenericFK); todas las vistas `@staff_required` | Activa |
| | `reportes` | Reportes de ventas con arquitectura hexagonal real (ports/adapters/usecases) — la app mejor diseñada | Activa |
| | `articulos` | 6 modelos que duplican conceptos de `bdd`, sin vistas ni URLs | Abandonada |
| | `carga_archivo` | Upload simple de archivos (1 modelo `Document`) | Activa, mínima |
| | `cajas` | Solo 2 templates copiados, sin código | Abandonada |
| **Plataforma** | `core_config` | Settings (gitignored), URLs raíz, logging dinámico por app (`log_config.py`), middlewares request_id/exception, descarga de logs staff | Activa |
| | `core_andamios` | Sistema de andamio ORIGINAL (Nav_Bar/Url/Contenedor) — reemplazado en la práctica por el Armador de `bdd`; su context processor corre en todas las vistas pero `MiVista` lo sobrescribe | Semi-abandonada |
| | `core_elementos` | Biblioteca de componentes HTML (tabla, modal, formulario); la mayoría placeholders | Parcial |
| | `core_index` | Página de bienvenida `/bienbenida/` (sic) — única consumidora de core_andamios | Activa |
| | `core_docs` | Sirve docs Sphinx (stubs vacíos, `release="v2.0"`) y renderiza `CHANGELOG.md` | Parcial |
| | `core_testing` | Vacía. NOTA: ya NO está en `INSTALLED_APPS` (el informe decía que sí) | Abandonada |
| **UI** | `x_cartel` | Carteles de precios imprimibles (tamaños de fuente configurables) | Activa |
| | `x_articulos` | CRUD experimental con filtro `codigo__contains="metdh"` hardcodeado | Experimental |
| | `x_widgets` | Vacía (aún en `INSTALLED_APPS`) | Abandonada |
| **Módulo** | `utils/` | `rounding.round_price` (regla unificada de precios), `ordenar_query`, `outsider.arrancar_django_config`, `queryset_to_xlsx` | Activa, transversal |

### Flujos de datos clave

**1. Request dinámico (patrón Armador — el corazón del sistema):**
`bdd/urls.py` consulta `NavBar`/`Armador` en la DB al cargar el módulo y genera rutas con `import_string("bdd.views.{armador.vista}")` envuelto en `except: pass` silencioso. `MiVista.get_context_data()` (`bdd/views/base.py`) construye todo el contexto: versión (lee `package.json`), navbar, muro/contenedor/plantillas del Armador, `MyForm` dinámico, badges de planillas, MercadoPago. Renderiza `static/templates/generic_template.html`.

**2. Venta (buscador → ticket fiscal):**
Búsqueda en tabla → `agregar_articulo_a_carrito` (AJAX) → carrito por usuario con roles (`cajeros` vs `caja_general` que ve todos los carritos; polling JS cada 3s en `tabla_lateral_carritos.html`, ~1000 líneas) → `procesar_transaccion` (facturacion/views.py) → `registrar_articulos_vendidos` (@transaction.atomic) crea `Transaccion`+`ArticuloVendido` → `TicketFactura` genera JSON fiscal → `asyncio.run(conectar_a_websocket(...))` a `IP_BEW_SOCKET` → impresora fiscal responde nro. de comprobante → carrito limpio. Sistema legacy paralelo: `ComandoFiscal` + `boletas` (polling) sigue en el código sin uso.

**3. Pipeline del actualizador (precios de proveedores):**
Tarea `principal` (`actualizador_main.py`): Gmail (adjuntos de proveedores) → Drive INBOX → `Listado_Planillas` → copia a Google Sheets plantilla → el usuario etiqueta hojas en `/actualizar/` → tarea `principal_csv` (`actualizador_csv.py`, 1156 líneas): descarga planillas `listo=True`, parsea con pandas según `Condiciones` (columnas por letra), escribe `Item.final_base` etc., `recompute_finales()` aplica `factor_division` + `round_price`, marca `actualizado`/`trabajado`.

**4. Cierre Z → tareas nocturnas (verificado):**
POST `/vista_cierre_z/` → `dailyClose:"Z"` por WebSocket → guarda `CierreZ` → `agregar_tareas_en_cola()` (`facturacion/views.py:760` → `actualizador/task.py:299`) encola `principal` + `principal_csv` + `buckup` en `ColaTareasWorker` (hilo daemon singleton) que **espera hasta las 21:00** (default; `ActualizarAhora` usa ahora+1min). `buckup` = `sincronizador.buckup()` sube `db.sqlite3` a Drive. Todo con `Patoba(None)` → credenciales del `user id=1` hardcodeadas.

**5. Reportes (hexagonal):** `DailyReportView` → `RunDailyReport` → ports (`DrivePort`, `StoragePort`, `ExcelIO`) → adapters (`PatobaDriveAdapter` envuelve `bdd.classes.Patoba`).

### Testing

- Suite real: `tests/` — **45 tests colectados** (verificado con `pytest --collect-only` 2026-09-23): `tests/test_rounding.py` (~33 parametrizados de `round_price`), `tests/articulos/test_articulo.py` (8, con factories/fakers), `tests/facturacion/test_facturacion.py` (1). Los dirs `tests/app_*` y `tests/facturacion/{test_models,utils}` solo contienen `__pycache__` (residuos).
- Per-app `tests.py`: stubs de 3 líneas (excepto `core_andamios/tests.py`, 27 líneas).
- **Corrección a config.yaml:** el known_issue "pytest at root exits 2 por `__init__.py` stray" ya está RESUELTO (commit `9745bd5` eliminó el archivo); `pytest` en raíz colecta los 45 tests limpiamente.
- Sin coverage, sin linter, sin type checker. `black` en venv pero no pinneado.

### Verificación de docs vs código (qué cambió desde jul-2026)

- `settings.py` ahora es env-based y gitignored: `SECRET_KEY`/`DEBUG`/`ALLOWED_HOSTS`/IDs de Drive leen env vars — PERO conservan los mismos defaults inseguros (`DEBUG` default `True`, `ALLOWED_HOSTS` default `'*'`, key `django-insecure-*` de fallback). Los secretos ya están en historia de git de todos modos.
- Persisten: `from ensurepip import bootstrap` (línea 20), `IP_BEW_SOCKET` duplicado (líneas 25 y 35), `CELERY_BROKER_URL` muerto (línea 418).
- `bdd/views_old.py` (1230 líneas) sigue activo: `bdd/urls.py:5,23` importan `Imprimir`, `ItemsView`, `ListarCarteles` desde ahí (verificado).
- `except:` bare en `bdd/urls.py` sigue presente (verificado línea ~52).

### Hotspots de acoplamiento (deuda priorizada)

1. **`bdd` es single point of failure** — 12 apps importan de ella (modelos + Patoba + MiVista). Cualquier cambio en `bdd/models.py` es blast-radius total.
2. **Dos sistemas paralelos en dos ejes:** scaffold (`core_andamios` vs `Armador` de bdd) y fiscal (`ComandoFiscal`+`boletas` vs `TicketFactura`+WebSocket).
3. **`Patoba(request=None)` → user id=1**: toda la automatización corre con credenciales hardcodeadas; Drive folder IDs son strings mágicos.
4. **`FloatField` para dinero**: 45+ campos en `bdd`/`facturacion`; inconsistente con `Articulo*` que usa `DecimalField`.
5. **Seguridad residual**: ~10 `@csrf_exempt` en endpoints de venta, endpoints AJAX sin `@login_required`, `subprocess.call(shell=True)` en `actualizador/task.py:85`, `ast.literal_eval` sobre POST.
6. **Bugs latentes documentados**: métodos `calcular_precio_*` de `Item` referencian campos inexistentes (código muerto); `Registros.automatioco` (typo en DB).
7. **Raíz contaminada**: 9 scripts sueltos + duplicados de `actualizador_*.py` en raíz y en la app.

## Affected Areas

- `bdd/` — god-app: `models.py` (22 modelos), `classes.py` (Patoba), `views/{base,main,ajax}.py`, `urls.py` (rutas dinámicas), `views_old.py` (legacy activo)
- `actualizador/` — `actualizador_main.py`, `actualizador_csv.py`, `task.py` (cola 21:00), `sincronizador.py` (backup Drive)
- `facturacion/` — `views.py` (procesar_transaccion, CierreZVieW), `classes.py` (TicketFactura + ComandoFiscal legacy), `cliente.py` (WS)
- `core_config/` — `settings.py` (env-based, gitignored), `urls.py` (8 apps montadas en `/` sin namespace), `log_config.py`
- `core_andamios/` + `bdd` (Armador) — dos sistemas de scaffold coexistiendo
- `administracion_financiera/` — app más aislada/sana (solo depende de `bdd.Proveedor`)
- `reportes/` — referencia de buena arquitectura interna (ports/adapters)
- `tests/` — suite real; `*/tests.py` stubs
- `docs/`, `*/DOCUMENTATION.md` — corpus de ~130KB ya existente (ver sección fuentes)

## Approaches

Esta exploración es un mapa, no un change; los "approaches" aplican a cómo atacar la deuda en futuros cambios SDD:

1. **Quick wins primero (recomendado como primeros changes)** — typos (`funtions`, `bienbenida`, `buckup`), `print()`→logger, `except:`→`except Exception`, eliminar `views_old.py` (mover 3 vistas), remover apps abandonadas de `INSTALLED_APPS`, scripts de raíz → `scripts/`.
   - Pros: bajo riesgo, reversible, enseña el codebase al owner. Cons: no toca lo estructural. Effort: Low.

2. **Desacoplar `bdd` por fases** — extraer `Patoba` a módulo de integración propio, luego modelos UI → `core_andamios`, luego inventario → `articulos`/`inventario`, con re-exports para no romper los 12 consumidores.
   - Pros: reduce el blast-radius real. Cons: migraciones + coordinación de imports; riesgo medio-alto. Effort: High.

3. **Hardening de seguridad/datos** — env vars sin defaults inseguros, `@login_required` + CSRF en AJAX (fases: origin-check primero), `FloatField`→`DecimalField` con `RunPython`, `Patoba(user_id)`.
   - Pros: cierra riesgos reales de producción. Cons: puede romper JS legacy y requiere migración de datos. Effort: Medium-High.

## Recommendation

Usar este mapa como contexto base para todo change futuro. Si se arranca trabajo de deuda: empezar por **Approach 1** (quick wins) como primer change SDD — el informe ya trae el plan de sprints (`docs/informe_arquitectura.md` §12). Antes de cualquier change que toque `bdd` o precios, leer `bdd/DOCUMENTATION.md` §3 y §15 (bugs conocidos). Tratar `reportes/` como referencia de estilo para código nuevo.

## Risks

- `bdd/urls.py` consulta la DB en import-time → un typo en un registro `Armador` elimina la URL silenciosamente; cualquier refactor de urls es delicado.
- La cola de tareas vive en un hilo in-process: si el proceso cae entre el cierre Z y las 21:00, el pipeline no corre (sin reintento persistente).
- `Patoba` depende del `SocialToken` del user 1: si ese usuario se desvincula de Google, se cae actualizador + backup + reportes.
- `db.sqlite3` (40MB) está en el repo local y se sube entera a Drive cada noche — datos de prod en el working dir.
- Los docs de jul-2026 están ~90% vigentes; las discrepancias encontradas se listan arriba (pytest ya no falla, settings ya es env-based, `core_testing` no está instalada).
- 6 apps abandonadas siguen inflando `INSTALLED_APPS` y confunden el mapa.

## Ready for Proposal

**No — exploración standalone fundacional.** No hay change que proponer. El orquestador debería decirle al usuario: el mapa de arquitectura ya existe persistido; cuando quiera atacar un problema concreto (ej. quick wins de deuda, extraer Patoba, CSRF en AJAX), lanzar `sdd-propose` con ese alcance y esta exploración como contexto.
