# Auditoría de Documentación vs Implementación

**Fecha:** 2026-07-13
**Versión auditada:** v3.10.0 (rama `produccion`)
**Auditor:** Cascade

---

## 1. Inventario de Apps Django (17 apps + 1 módulo utils)

| App | Modelos | Vistas | URLs | Templates | Líneas código | Doc existente |
|-----|---------|--------|------|-----------|---------------|---------------|
| **bdd** | 22 modelos | 11 vistas (base+main+ajax) | 18 rutas | 37 (static/templates) | ~6500 | Solo memory interna |
| **facturacion** | 5 modelos | 2 archivos views (~960 líneas) | Verificar | 9 templates | ~1200 | `facturacion/readme.md` (protocolo fiscalberry, NO la app) |
| **pedido** | 4 modelos | 7 archivos views | 10+ rutas | 17 templates | ~800 | `pedido/README.md` (buen estado) |
| **boletas** | 3 modelos | 1 view (39 líneas) | 1 ruta | 0 | ~80 | Sin doc |
| **cajas** | 0 modelos | 0 views (vacío) | 0 rutas | 2 templates | ~10 | Sin doc |
| **actualizador** | 0 modelos | 4 views (617 líneas) | 4 rutas | 2 templates | ~2600 | Solo config en README |
| **administracion_financiera** | 12 modelos | 24 views (341 líneas) | 24 rutas | 20 templates | ~750 | Sin doc |
| **articulos** | 6 modelos | 0 views útiles | 0 rutas | 0 | ~80 | Sin doc |
| **carga_archivo** | 1 modelo | 1 view | 1 ruta | 2 templates | ~50 | Sin doc |
| **reportes** | 1 modelo | 2 archivos views (~370 líneas) | Verificar | 2 templates | ~900 | Sin doc |
| **core_config** | 0 modelos | 1 view (logs, 188 líneas) | 1 ruta + includes | 1 template | ~500 | Solo config en README |
| **core_andamios** | 7 modelos | 1 view (ContextoAndamio) | 0 rutas propias | 5 templates | ~100 | `core_andamios/docs/` (desactualizado) |
| **core_docs** | 0 modelos | 2 views (serve_docs, changeLog) | 2 rutas | 1 template | ~100 | `core_docs/docs/` (stubs vacíos) |
| **core_elementos** | 6 modelos | 1 view (Crud) | 0 rutas propias | 7 templates | ~180 | Mencionado en `core.md` (mal) |
| **core_index** | 0 modelos | 1 view (Vista_Index) | 1 ruta | 1 template | ~20 | Mencionado en `core.md` (mal) |
| **core_testing** | 0 modelos | 0 views | 0 rutas | 0 | 0 | Sin doc (app vacía) |
| **x_articulos** | 1 modelo | 1 view (112 líneas) | Verificar | 1 template | ~200 | Sin doc |
| **x_cartel** | 3 modelos | 5 views (227 líneas) | 7 rutas | 3 templates | ~350 | Sin doc |
| **x_widgets** | 0 modelos | 0 views | 0 rutas | 0 | ~10 | Mencionado en `core.md` (mal) |
| **utils** (módulo) | N/A | N/A | N/A | N/A | ~260 | Sin doc |

---

## 2. Documentación Existente - Estado y Problemas

### 2.1 `README.md` (raíz) - 158 líneas

**Vigente:**
- Configuración de actualizadores CSV (ACT_CSV_BATCH_SIZE, ACT_CSV_EFECTIVO_DESCUENTO_PCT)
- Redondeo unificado de precios
- Configuración de logging
- Generación de PDF de pedidos
- Carritos en buscador: roles, visibilidad y colores

**Desactualizado:**
- **Sección "Flujo de trabajo GIT"** describe ramas que NO existen:
  - Dice: `main`, `pre-release`, `test`, `test_models`, `fix`, `hot_fix`, `dev`
  - Real: `produccion`, `Pre-Release`, `develop`, `main`, `feature/*`, `documentation`
  - Dice "Se genera una rama por cada app" → falso, se usa `feature/*`
  - Dice `npx standard-version` → ahora es `./scripts/release.sh`
- **No menciona** el script `scripts/release.sh` ni el workflow de release
- **No menciona** el sistema de versionado (package.json → navbar)

### 2.2 `pedido/README.md` - 92 líneas

**Estado: BUENO** - mapea correctamente modelos, vistas, templates, JS y flujo.

**Gaps menores:**
- No menciona `pedido/views/externo.py` (agregar_al_pedido, usado desde bdd)
- No documenta `pedido/views/faltantes.py`
- Sección "Guía de Estilo" dice `static/css/pedido.css` (a crear) → verificar si ya existe

### 2.3 `facturacion/readme.md` - 466 líneas

**Estado: EQUIVOCADO** - este archivo es la documentación del proyecto fiscalberry/printFiscal (protocolo de impresora fiscal Hasar/Epson), NO documenta la app Django `facturacion`.

**Falta documentar de la app real:**
- Modelos: `Cliente`, `ArticuloVendido`, `MetodoPago`, `Transaccion`, `CierreZ`
- Views: `views.py` (962 líneas), `views_clientes.py` (CRUD clientes)
- Forms: `ClienteForm`
- Functions: `funtions.py`, `cliente.py` (websocket), `classes.py`, `servidor_fake_ws.py`
- Templates: 9 templates en `facturacion/templates/facturacion/`
- Integración con boletas (impresión fiscal)

### 2.4 `core_docs/docs/` (Sphinx/MyST) - 7 archivos .md + conf.py

| Archivo | Líneas | Problema |
|---------|--------|----------|
| `index.md` | 28 | Stub - dice "en desarrollo", toctree con nombres informales |
| `instalacion.md` | 5 | **Vacío** - solo dice "ver requirements.txt" |
| `sintaxis.md` | 35 | Solo ejemplos de sintaxis MyST/RST, no documenta el proyecto |
| `documentacion_codigo_fuente.md` | 18 | Solo índice, sin contenido real |
| `core.md` | 48 | **DESACTUALIZADO** - nombres de apps incorrectos |
| `apps.md` | 8 | **Vacío** - solo dice "La vista de bienbenida" |
| `core_andamios_index.md` | 7 | Include de `core_andamios/docs/` |
| `conf.py` | 53 | **STALE** - `release = "v2.0"` (actual: v3.10.0) |

**Errores específicos en `core.md`:**
- Dice `.app_index` → real: `core_index`
- Dice `.app_docs` → real: `core_docs`
- Dice `.andamios` → real: `core_andamios`
- Dice `.elementos` → real: `core_elementos`
- Dice `.widgets` → real: `x_widgets`
- No menciona: `core_config`, `core_testing`, `bdd`, `facturacion`, `pedido`, `boletas`, `cajas`, `actualizador`, `administracion_financiera`, `articulos`, `carga_archivo`, `reportes`, `x_articulos`, `x_cartel`

### 2.5 `core_andamios/docs/core_andamios/index.md` - 19 líneas

**DESACTUALIZADO** - describe context vars que NO coinciden con el código:

| Documentación dice | Código real (`context_processors.py`) |
|--------------------|---------------------------------------|
| `core_navbar` | `core_navbar_html` |
| `core_contenedor` | `core_contenedor_html` |
| `core_script` | (no existe, es `core_head_html`) |
| `core_pie` | `core_pie_html` |

Además dice "El contexto se define en views.py bajo la clase ContextoAndamio" pero:
- `ContextoAndamio` está en `core_andamios/views.py` (correcto)
- El contexto real del navbar viene de `core_andamios/context_processors.py` (no mencionado)
- La vista base real es `bdd/views/base.py:MiVista` (no mencionada)

---

## 3. Gaps Críticos por App

### 3.1 `bdd` (app central) - SIN DOCUMENTACIÓN

**Modelos (22):**
- Inventario: `Item` (40+ campos), `Marca`, `Cod_Barras`, `Sector`, `Cajonera`, `Cajon`
- Proveedores: `Proveedor`, `ListaProveedores`, `Condiciones`, `Compras`
- Pedidos: `Lista_Pedidos`
- Planillas: `Listado_Planillas`, `Archivo`
- UI/Andamios: `NavBar`, `Muro`, `Plantilla`, `Contenedor`, `Armador`, `Modelo_Campos`, `Formulario_Campos`, `Formulario_Campos_Contiene`, `Formulario_Campos_Empieza_Con`
- Carrito: `Carrito`, `Articulo`, `ArticuloSinRegistro`
- Registros: `Tipo_Registro`, `Registros`
- Organización: `Sub_Carpeta`, `Sub_Titulo`, `Tipo_Cartel`

**Vistas:**
- `base.py` (529 líneas): `MiVista` - vista base con construcción dinámica via Armador, contexto de versión, MercadoPago, planillas
- `main.py` (632 líneas): `Inicio`, `Prueba`, `BusquedaView`, `ItemsView`, `Imprimir`, `ListadoPedidos`, `ListarCarteles`
- `ajax.py` (827 líneas): 11 endpoints AJAX (carrito, pedidos, editar_item, reportes)
- `forms.py`: `MyForm` (dinámico), `BusquedaForm`
- `utils.py`: helpers `articulo_to_dict`, `calcular_total`, `carrito_to_dict`

**`views_old.py` (1230 líneas) - CÓDIGO LEGACY:**
- Contiene duplicados de TODAS las vistas que ya están en `views/`
- Aún importado en `bdd/urls.py` (líneas 5, 23) para `Imprimir`, `ItemsView`, `ListarCarteles`
- Importado en `facturacion/views.py:5` (pero sobrescrito en línea 6 por `views.main`)
- **Riesgo:** confusión sobre qué versión de la vista se ejecuta

**Bugs detectados en modelos:**
- `Item.calcular_precio_final()` referencia `self.constante` (no existe como campo)
- `Item.calcular_precio_efectivo_final()` referencia `self.constante` (no existe)
- `Item.calcular_precio_rollo_final()` referencia `self.venta_metro` (no existe como campo, quizás es `venta_rollo_caja`)
- `Condiciones.detectar_columna()` referencia `self.descripcion` (no existe como campo)
- `Condiciones.ordenar_columnas()` referencia `self.descripcion` (no existe)
- `Archivo.descargar()` referencia `self.descarga` (no existe como campo)
- `Archivo.basename()` referencia `self.descarga` (no existe)
- `Paginas.__str__` referencia `self.html` (no existe como campo)

### 3.2 `facturacion` - DOCUMENTACIÓN EQUIVOCADA

- `readme.md` es del fiscalberry, no de la app
- 5 modelos sin documentar (`Cliente`, `ArticuloVendido`, `MetodoPago`, `Transaccion`, `CierreZ`)
- 2 archivos de views sin documentar (`views.py` 962 líneas, `views_clientes.py`)
- `cliente.py` (websocket a impresora fiscal) sin documentar
- `servidor_fake_ws.py` sin documentar
- `classes.py` sin documentar

### 3.3 `administracion_financiera` - SIN DOCUMENTACIÓN

- 12 modelos complejos (pago polimórfico, cuentas, tarjetas, cheques, débitos automáticos)
- 24 URLs (CRUD completo de servicios, impuestos, cuentas, tarjetas, boletas, cheques)
- 20 templates con Tailwind
- `services.py` (184 líneas) con lógica de negocio
- `templatetags/form_tags.py`

### 3.4 `actualizador` - SIN DOCUMENTACIÓN (solo config en README)

- `actualizador_csv.py` (1155 líneas) - procesamiento CSV de planillas de proveedores
- `actualizador_main.py` (807 líneas) - orquestador principal
- `views.py` (617 líneas) - 4 vistas (Actualizar, Reckup, ActualizarAhora, MarcarDescargado)
- `task.py` (397 líneas) - tareas en hilos
- `sincronizador.py` (47 líneas)

### 3.5 `reportes` - SIN DOCUMENTACIÓN

- Arquitectura hexagonal (ports.py, adapters_patoba.py, adapters_storage.py, usecases.py)
- Integración con Google Drive
- `views.py` (222 líneas) + `views_batch.py` (147 líneas)
- `excel_io.py`, `forms.py`, `conf.py`

### 3.6 `x_cartel` - SIN DOCUMENTACIÓN

- 3 modelos (`Cartelitos`, `Carteles`, `CartelesCajon`) con campos de tamaño de fuente
- 5 views (227 líneas) para impresión de carteles
- 7 URLs
- Integración con `bdd.models.Item`

### 3.7 Apps vacías/abandonadas

- **`cajas`**: 0 modelos, 0 views, 0 URLs, pero tiene 2 templates (caja_formulario.html, caja_tabla_resultado.html)
- **`core_testing`**: completamente vacía (solo migrations)
- **`x_widgets`**: 0 modelos, 0 views, 0 URLs
- **`articulos`**: 6 modelos definidos pero 0 views, 0 URLs (¿abandonada?)

---

## 4. Templates - Estructura

### Templates globales (`static/templates/`) - 37 archivos
- `generic_template.html` - template base principal (navbar, versión, estructura)
- `base_*.html` - 8 bases alternativas (buscador, carrito, inicio, registros, etc.)
- `tabla_*.html` - 8 tablas específicas
- `muro_*.html` - 3 muros (simple, doble, imprimir)
- `plantilla_*.html` - 4 plantillas
- `imprimir_*.html` - 2 templates de impresión
- `account/login.html`, `registration/*` - autenticación

### Templates por app - 65+ archivos
- `administracion_financiera/`: 20 templates (Tailwind)
- `pedido/`: 17 templates (Bootstrap)
- `facturacion/`: 9 templates
- `core_andamios/`: 5 templates (navbar, contenedor, pie, head)
- `core_elementos/`: 7 templates (tabla, formulario, modal, tarjeta, lista, parrafo)
- Resto: 1-3 templates por app

---

## 5. Arquitectura Real vs Documentada

### Flujo de request real:
1. `core_config/urls.py` incluye todas las apps
2. `bdd/urls.py` genera rutas dinámicamente desde modelo `Armador` (DB-driven)
3. `bdd/views/base.py:MiVista` es la vista base de casi todo
4. `MiVista.get_context_data()` lee `package.json` (versión), `NavBar`, `Armador`, `Listado_Planillas`, MercadoPago
5. `core_andamios/context_processors.py` agrega navbar global
6. `static/templates/generic_template.html` renderiza con blocks: navbar, contenedor, pie

### Lo que la documentación dice:
- `core_andamios/docs/` describe `ContextoAndamio` (que es una vista mínima para `core_index`)
- `core.md` menciona apps con nombres incorrectos
- No existe documentación del flujo `Armador` → `MiVista` → `generic_template.html`
- No existe documentación del sistema de carrito, AJAX, ni roles de usuario

---

## 6. Resumen de Gaps

| Categoría | Total | Documentados | Faltan |
|-----------|-------|-------------|--------|
| Apps Django | 17 | 1 (pedido, parcial) | 16 |
| Modelos | ~65 | 4 (pedido) | ~61 |
| Vistas | ~50 | 7 (pedido) | ~43 |
| Endpoints AJAX | 11 | 0 | 11 |
| Templates | ~100 | 17 (pedido) | ~83 |
| Módulos utils | 6 | 0 | 6 |

### Prioridad de documentación sugerida:

1. **CRÍTICA** - `bdd` (app central, sin doc, 6500 líneas, bugs en modelos)
2. **CRÍTICA** - `facturacion` (doc equivocada, app de negocio principal)
3. **ALTA** - `actualizador` (2600 líneas, sin doc, core del negocio)
4. **ALTA** - `administracion_financiera` (750 líneas, 12 modelos, sin doc)
5. **ALTA** - `reportes` (900 líneas, arquitectura hexagonal, sin doc)
6. **MEDIA** - `x_cartel` (350 líneas, sin doc)
7. **MEDIA** - Fix `README.md` git workflow
8. **MEDIA** - Fix `core_docs/docs/` (Sphinx stubs vacíos)
9. **MEDIA** - Fix `core_andamios/docs/` (context vars mal)
10. **BAJA** - `x_articulos`, `carga_archivo`, `boletas`, `cajas` (apps pequeñas)
11. **BAJA** - `core_testing`, `x_widgets`, `articulos` (apps vacías/abandonadas)
12. **BAJA** - `views_old.py` (debería eliminarse, no documentarse)

---

## 7. Bugs Detectados (no documentación)

1. **`bdd/models.py:Item`** - métodos `calcular_precio_*` referencian `self.constante` (campo inexistente)
2. **`bdd/models.py:Item`** - `calcular_precio_rollo_final` referencia `self.venta_metro` (campo inexistente)
3. **`bdd/models.py:Condiciones`** - `detectar_columna` y `ordenar_columnas` referencian `self.descripcion` (campo inexistente)
4. **`bdd/models.py:Archivo`** - `descargar()` y `basename()` referencian `self.descarga` (campo inexistente)
5. **`bdd/models.py:Paginas`** - `__str__` referencia `self.html` (campo inexistente)
6. **`facturacion/views.py:5-6`** - import duplicado de `Inicio` (views_old + views.main)
7. **`bdd/urls.py:5,23`** - importa `Imprimir`, `ItemsView`, `ListarCarteles` de `views_old` en lugar de `views/`
8. **`views_old.py`** (1230 líneas) - código duplicado que debería eliminarse
