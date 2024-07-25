
## que es lo que se pretende que gestione la app_andamios?

En esta app_andamios se gestiona la estructura basica de todas las paginas, junto con su contexto general. 
En el html principal se define en su etiqueta **head** el idioma, el **titulo** y algunos **links** a hojas de estilo.
En su body se definen 3 **blocks contents**:
- block nav_bar
- block contenedor
- block pie

El contexto se define en el archivo **views.py** bajo la clase **ContextoAndamio**.
Contexto:
- titulo = **str**
- core_navbar = objeto **Nav_Bar**
- core_contenedor = objeto **Contenedor**
- core_script = objeto **Script**
- core_pie = objeto **Pie**

