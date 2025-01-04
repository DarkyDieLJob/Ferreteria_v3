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

