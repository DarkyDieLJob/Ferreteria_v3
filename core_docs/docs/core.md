# apps nucleo

> Aplicaciones que son la base del proyecto, al cual se le pueden acoplar mas apps.

---
## .app_docs

 > Gestiona las vistas de la documentacion.


---
## .andamios

 > **Introduccion:**
 > Un **andamio** hace referencia a un **bloque de codigo** que en conjunto con un **template** (el andamio en si) 
 > forma la **estructura basica** o **estructura fija**, que van a tener varias **vistas**, a partir de la informacion
 > almacenada en una tabla ` **app_andamios.andamio** ` en la base de datos.
 >
 > [Aquí está la documentacion aislada](core_andamios_index)

 ### andamio-basico
 
 El andamio basico que se va a usar se compone de tres secciones cuyos elementos y 
 distribucion se rellenaran a partir de la informacion almacenada en un modelo ( tabla ), 
 las secciones son:

 - Nav_bar - Una barra de navegacion.
 - Contenedor - Un contenedor general ( cuerpo del contenido ).
 - Scripts - Una seccion ( oculta ) para agregar scripts.

 ### andamio-vacio

 Otro andamio que estara disponible es uno "vacio". para poder implementar carteles imprimibles 
 a partir del archivo html generado.

 **Composicion:**
 - Contenedor.
 - Scripts.

---
## .elementos

 > Todo lo referente a los distintos elementos que se utilizan para rellenar los contenedores de los andamios.

---
## .widgets

 > Elementos que se pueden incluir o no en las diferentes vistas, que por lo general dependen de APIs externas.