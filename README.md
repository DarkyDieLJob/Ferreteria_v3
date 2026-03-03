# Ferreteria_v3.

## Flujo de trabajo GIT.
    - Release: npx standard-version

### Descripcion de ramas.

    - En *main* se pushean solo las releases.
    - En *pre-release* se pushean todos los cambios hasta el release.

    - En *test* o *test_models* se pushean todos los cambios a testear.
    - En *fix* se pushean las correcciones no graves.
    - En *hot_fix* se pushea las correcciones directo a main.

    - Se genera una rama por cada app.

    - En *dev* se pushean pruebas de distintas nuevas fixtures.

### Descripcion del flujo de trabajo.

    - Los cambios en *dev* se quedan en *dev*.
    sin repercutir en el resto de ramas.
    
    - Los cambios en las distintas apps deven mergearse a *test*.

    - Los cambios en *test* deben mergearse a *pre-release*.

    - La correccion de errores debe tomarse como cambios en una app.
    es decir, los cambios se mergenan primero a *test* y luego a *pre-release*.

    - La correccion de cambios graves debe saltarse el *test* es decir:
    aqui se deven gestionar la marcha atras, buckups o las correcciones puntuales.

    - Antes de mergear de *pre-release* a *main*, debe ejecutarse el comando
    ''' npx standard-version ''', para generar el CHANGELOG.md correspondiente.

### Tratamiento de migraciones.

    - Las migraciones inpactan directamente en la bdd de prueba.

    - Se recomienda solo editar los modelos para agregar campos. Se desaconseja
    editar campos que puedan repercutir directa o indirectamente en otros modelos o en el funcionamiento de otras apps.

    - En caso de tener que refactorizar modelos se recomienda, para no perder la compatibilidad entre versiones, que se creen nuevos modelos y se recarguen los datos. Aunque el modelo anterior quede sin efecto puede ser necesario en alguna otra version y/o hacer mas facil una "vuelta atras".


## Configuración de Actualizadores (CSV)

- ACT_CSV_BATCH_SIZE
  - Tamaño de lote para el procesamiento por lotes del CSV en `actualizador/actualizador_csv.py`.
  - Tipo: entero.
  - Valor por defecto: 1000.
  - Cómo configurarlo:
    - En settings.py: `ACT_CSV_BATCH_SIZE = 1000` (u otro valor)
    - Por variable de entorno: `export ACT_CSV_BATCH_SIZE=1000`

- ACT_CSV_EFECTIVO_DESCUENTO_PCT
  - Porcentaje de descuento a aplicar sobre la columna `final_efectivo` leída del CSV, antes del redondeo y de actualizar la BDD.
  - Tipo: float/porcentaje (por ejemplo, 15 para 15%).
  - Valor por defecto: 0.
  - Cómo configurarlo:
    - En settings.py: `ACT_CSV_EFECTIVO_DESCUENTO_PCT = 0.0` (u otro valor)
    - Por variable de entorno: `export ACT_CSV_EFECTIVO_DESCUENTO_PCT=15`

Notas:
- Si no se definen estas claves en settings.py, se intentan leer desde variables de entorno. Si tampoco existen, se usan los valores por defecto indicados.
- El descuento aplica únicamente sobre `final_efectivo` proveniente del CSV y luego se realiza el redondeo configurado.


## Redondeo unificado de precios

- Simular impacto (no guarda):

  ```bash
  python manage.py apply_rounding --dry-run --batch-size 1000
  ```

- Aplicar cambios en BD:

  ```bash
  python manage.py apply_rounding --batch-size 1000
  ```

- Nota: Los precios se redondean y persisten en la base de datos. Las vistas deben mostrar directamente los valores almacenados (por ejemplo, usando `floatformat:0`), sin aplicar filtros adicionales.

