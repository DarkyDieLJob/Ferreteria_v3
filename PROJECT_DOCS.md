# Documentación del Proyecto: Ferretería V3

**Fecha de generación:** 2025-07-14 10:50:22

## Resumen

- **Aplicaciones:** 25
- **Modelos:** 70
- **Vistas:** 3
- **Formularios:** 0

### Allauth (`allauth`)

### Cuentas (`account`)

#### Modelos

- **EmailAddress**
  > EmailAddress(id, user, email, verified, primary)
  - **Campos:**
    - `id` (AutoField)
    - `user` (ForeignKey) → `User`
    - `email` (CharField)
    - `verified` (BooleanField)
    - `primary` (BooleanField)

- **EmailConfirmation**
  > EmailConfirmation(id, email_address, created, sent, key)
  - **Campos:**
    - `id` (AutoField)
    - `email_address` (ForeignKey) → `EmailAddress`
    - `created` (DateTimeField)
    - `sent` (DateTimeField)
    - `key` (CharField)

### Cuentas de redes sociales (`socialaccount`)

#### Modelos

- **SocialApp**
  > SocialApp(id, provider, provider_id, name, client_id, secret, key, settings)
  - **Campos:**
    - `id` (AutoField)
    - `provider` (CharField)
    - `provider_id` (CharField)
    - `name` (CharField)
    - `client_id` (CharField) - Identificador de App, o clave de consumidor
    - `secret` (CharField) - frase secreta de API, frase secreta cliente o frase secreta de consumidor
    - `key` (CharField) - Clave
    - `settings` (JSONField)
    - `sites` (ManyToManyField) → `Site`

- **SocialAccount**
  > SocialAccount(id, user, provider, uid, last_login, date_joined, extra_data)
  - **Campos:**
    - `id` (AutoField)
    - `user` (ForeignKey) → `User`
    - `provider` (CharField)
    - `uid` (CharField)
    - `last_login` (DateTimeField)
    - `date_joined` (DateTimeField)
    - `extra_data` (JSONField)

- **SocialToken**
  > SocialToken(id, app, account, token, token_secret, expires_at)
  - **Campos:**
    - `id` (AutoField)
    - `app` (ForeignKey) → `SocialApp`
    - `account` (ForeignKey) → `SocialAccount`
    - `token` (TextField) - "oauth_token" (OAuth1) o token de acceso (OAuth2)
    - `token_secret` (TextField) - "oauth_token_secret" (OAuth1) o token de refresco (OAuth2)
    - `expires_at` (DateTimeField)

### Google (`google`)

#### Vistas

- **LoginByTokenView**
  - **Métodos:**
    - `dispatch(request)`
    - `get(request)`
    - `post(request)`
    - `check_csrf(request)`

### Visualizador UML (`uml_visualizer`)

### Django Extensions (`django_extensions`)

### Core_Docs (`core_docs`)

### Core_Andamios (`core_andamios`)

#### Modelos

- **Contenedor**
  > Contenedor(id, nombre, text_display, html)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `text_display` (CharField)
    - `html` (CharField)

- **Script**
  > Script(id, nombre, text_display, html)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `text_display` (CharField)
    - `html` (CharField)

- **Pie**
  > Pie(id, nombre, text_display, html)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `text_display` (CharField)
    - `html` (CharField)

- **Url**
  > Url(id, nombre, text_display, ruta, contenedor, script, pie)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `text_display` (CharField)
    - `ruta` (CharField)
    - `contenedor` (ForeignKey) → `Contenedor`
    - `script` (ForeignKey) → `Script`
    - `pie` (ForeignKey) → `Pie`

- **Nav_Bar**
  > Nav_Bar(id, nombre, text_display, url)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `text_display` (CharField)
    - `url` (OneToOneField) → `Url`

- **Contexto**
  > Contexto(id, json)
  - **Campos:**
    - `id` (BigAutoField)
    - `json` (JSONField)

### Core_Index (`core_index`)

### Core_Elementos (`core_elementos`)

#### Modelos

- **Modelo_Tablas**
  > Modelo_Tablas(id, nombre, elemento_html, lista_de_titulos, lista_articulos)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `elemento_html` (CharField)
    - `lista_de_titulos` (TextField)
    - `lista_articulos` (TextField)

- **Modelo_Formularios**
  > Modelo_Formularios(id, nombre, elemento_html, lista_de_campos)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `elemento_html` (CharField)
    - `lista_de_campos` (TextField)

- **Modelo_Tarjetas**
  > Modelo_Tarjetas(id, nombre, elemento_html, titulo, descripcion)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `elemento_html` (CharField)
    - `titulo` (CharField)
    - `descripcion` (CharField)

- **Modelo_Listas**
  > Modelo_Listas(id, nombre, elemento_html)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `elemento_html` (CharField)

- **Paginas**
  > Paginas(id, tiene_tabla, tiene_formulario, tiene_tarjeta, tiene_lista)
  - **Campos:**
    - `id` (BigAutoField)
    - `tiene_tabla` (BooleanField)
    - `tiene_formulario` (BooleanField)
    - `tiene_tarjeta` (BooleanField)
    - `tiene_lista` (BooleanField)
    - `modelo_tablas` (ManyToManyField) → `Modelo_Tablas`
    - `modelo_formularios` (ManyToManyField) → `Modelo_Formularios`
    - `modelo_tarjetas` (ManyToManyField) → `Modelo_Tarjetas`
    - `modelo_lista` (ManyToManyField) → `Modelo_Listas`

### X_Widgets (`x_widgets`)

### X_Articulos (`x_articulos`)

#### Modelos

- **Articulo**
  > Articulo(id, codigo, descripcion, precio_base, ultimo_cambio, actualizado, precio_efectivo)
  - **Campos:**
    - `id` (BigAutoField)
    - `codigo` (CharField)
    - `descripcion` (CharField)
    - `precio_base` (FloatField)
    - `ultimo_cambio` (DateField)
    - `actualizado` (BooleanField)
    - `precio_efectivo` (FloatField)

### X_Cartel (`x_cartel`)

#### Modelos

- **Cartelitos**
  > Cartelitos(id, item, proveedor, revisar, habilitado, descripcion)
  - **Campos:**
    - `id` (BigAutoField)
    - `item` (OneToOneField) → `Item`
    - `proveedor` (ForeignKey) → `Proveedor`
    - `revisar` (BooleanField)
    - `habilitado` (BooleanField)
    - `descripcion` (TextField)

- **Carteles**
  > Carteles(id, item, proveedor, revisar, descripcion, tamano_descripcion, texto_final, tamano_texto_final, final, tamano_final, texto_final_efectivo, tamano_texto_final_efectivo, final_efectivo, tamano_final_efectivo)
  - **Campos:**
    - `id` (BigAutoField)
    - `item` (ForeignKey) → `Item`
    - `proveedor` (ForeignKey) → `Proveedor`
    - `revisar` (BooleanField)
    - `descripcion` (TextField)
    - `tamano_descripcion` (IntegerField)
    - `texto_final` (TextField)
    - `tamano_texto_final` (IntegerField)
    - `final` (TextField)
    - `tamano_final` (IntegerField)
    - `texto_final_efectivo` (TextField)
    - `tamano_texto_final_efectivo` (IntegerField)
    - `final_efectivo` (TextField)
    - `tamano_final_efectivo` (IntegerField)

- **CartelesCajon**
  > CartelesCajon(id, item, proveedor, revisar, descripcion, tamano_descripcion, texto_final, tamano_texto_final, final, tamano_final, texto_final_efectivo, tamano_texto_final_efectivo, final_efectivo, tamano_final_efectivo)
  - **Campos:**
    - `id` (BigAutoField)
    - `item` (ForeignKey) → `Item`
    - `proveedor` (ForeignKey) → `Proveedor`
    - `revisar` (BooleanField)
    - `descripcion` (TextField)
    - `tamano_descripcion` (IntegerField)
    - `texto_final` (TextField)
    - `tamano_texto_final` (IntegerField)
    - `final` (TextField)
    - `tamano_final` (IntegerField)
    - `texto_final_efectivo` (TextField)
    - `tamano_texto_final_efectivo` (IntegerField)
    - `final_efectivo` (TextField)
    - `tamano_final_efectivo` (IntegerField)

#### Vistas

- **CrearCartelitoView**
  - **Métodos:**
    - `get(request)`
    - `post(request)`

### Bdd (`bdd`)

#### Modelos

- **ListaProveedores**
  > ListaProveedores(id, nombre, abreviatura, hay_csv_pendiente)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `abreviatura` (CharField)
    - `hay_csv_pendiente` (BooleanField)

- **Proveedor**
  > Proveedor(id, identificador, text_display, cuit, direccion, email, telefono, corredor, corredor_telefono)
  - **Campos:**
    - `id` (BigAutoField)
    - `identificador` (ForeignKey) → `ListaProveedores`
    - `text_display` (CharField)
    - `cuit` (CharField)
    - `direccion` (CharField)
    - `email` (CharField)
    - `telefono` (CharField)
    - `corredor` (CharField)
    - `corredor_telefono` (CharField)

- **Condiciones**
  > Condiciones(id, proveedor, fila_inicial, codigo, nombre, precio_base, porcentaje, porcentaje_21, porcentaje_10_5, dolar)
  - **Campos:**
    - `id` (BigAutoField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `fila_inicial` (IntegerField)
    - `codigo` (CharField)
    - `nombre` (CharField)
    - `precio_base` (CharField)
    - `porcentaje` (FloatField)
    - `porcentaje_21` (FloatField)
    - `porcentaje_10_5` (FloatField)
    - `dolar` (CharField)

- **Sub_Carpeta**
  > Sub_Carpeta(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Sub_Titulo**
  > Sub_Titulo(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Tipo_Cartel**
  > Tipo_Cartel(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Archivo**
  > Archivo(id, proveedor, condiciones, agregado, editado, archivo)
  - **Campos:**
    - `id` (BigAutoField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `condiciones` (ForeignKey) → `Condiciones`
    - `agregado` (DateField)
    - `editado` (DateField)
    - `archivo` (FileField)

- **Sector**
  > Sector(id, codigo)
  - **Campos:**
    - `id` (BigAutoField)
    - `codigo` (CharField)

- **Cajonera**
  > Cajonera(id, codigo, sector)
  - **Campos:**
    - `id` (BigAutoField)
    - `codigo` (CharField)
    - `sector` (ForeignKey) → `Sector`

- **Cajon**
  > Cajon(id, codigo, cajonera)
  - **Campos:**
    - `id` (BigAutoField)
    - `codigo` (CharField)
    - `cajonera` (ForeignKey) → `Cajonera`

- **Marca**
  > Marca(id, codigo)
  - **Campos:**
    - `id` (BigAutoField)
    - `codigo` (CharField)

- **Item**
  > Item(id, cajon, marca, codigo, barras, descripcion, precio_base, porcentaje, porcentaje_efectivo, porcentaje_oferta, porcentaje_oferta_efectivo, oferta, precio_rollo_caja, venta_rollo_caja, porcentaje_metro, pack_cantidad, cantidad_rollo_caja, descuento_rollo_caja, descuento_rollo_caja_efectivo, final_rollo, final_rollo_efectivo, final, final_efectivo, trabajado, sub_carpeta, sub_titulo, actualizado, fecha, stock, proveedor, tiene_cartel, tipo_cartel, p_c_efectivo, p_c_debito, p_c_credito)
  - **Campos:**
    - `id` (BigAutoField)
    - `cajon` (ForeignKey) → `Cajon`
    - `marca` (ForeignKey) → `Marca`
    - `codigo` (CharField)
    - `barras` (IntegerField)
    - `descripcion` (CharField)
    - `precio_base` (FloatField)
    - `porcentaje` (FloatField)
    - `porcentaje_efectivo` (FloatField)
    - `porcentaje_oferta` (FloatField)
    - `porcentaje_oferta_efectivo` (FloatField)
    - `oferta` (BooleanField)
    - `precio_rollo_caja` (BooleanField)
    - `venta_rollo_caja` (BooleanField)
    - `porcentaje_metro` (FloatField)
    - `pack_cantidad` (FloatField)
    - `cantidad_rollo_caja` (FloatField)
    - `descuento_rollo_caja` (FloatField)
    - `descuento_rollo_caja_efectivo` (FloatField)
    - `final_rollo` (FloatField)
    - `final_rollo_efectivo` (FloatField)
    - `final` (FloatField)
    - `final_efectivo` (FloatField)
    - `trabajado` (BooleanField)
    - `sub_carpeta` (ForeignKey) → `Sub_Carpeta`
    - `sub_titulo` (ForeignKey) → `Sub_Titulo`
    - `actualizado` (BooleanField)
    - `fecha` (DateField)
    - `stock` (FloatField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `tiene_cartel` (BooleanField)
    - `tipo_cartel` (ForeignKey) → `Tipo_Cartel`
    - `p_c_efectivo` (FloatField)
    - `p_c_debito` (FloatField)
    - `p_c_credito` (FloatField)

- **Cod_Barras**
  > Cod_Barras(id, barras, articulo)
  - **Campos:**
    - `id` (BigAutoField)
    - `barras` (IntegerField)
    - `articulo` (ForeignKey) → `Item`

- **Lista_Pedidos**
  > Lista_Pedidos(id, proveedor, item, cantidad, pedido)
  - **Campos:**
    - `id` (BigAutoField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `item` (ForeignKey) → `Item`
    - `cantidad` (FloatField)
    - `pedido` (BooleanField)

- **NavBar**
  > NavBar(id, url_inicial, text_display)
  - **Campos:**
    - `id` (BigAutoField)
    - `url_inicial` (CharField)
    - `text_display` (CharField)

- **Muro**
  > Muro(id, muro_html)
  - **Campos:**
    - `id` (BigAutoField)
    - `muro_html` (CharField)

- **Plantilla**
  > Plantilla(id, plantilla_html)
  - **Campos:**
    - `id` (BigAutoField)
    - `plantilla_html` (CharField)

- **Contenedor**
  > Contenedor(id, nombre, url, a, b, c)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `url` (CharField)
    - `a` (ForeignKey) → `Plantilla`
    - `b` (ForeignKey) → `Plantilla`
    - `c` (ForeignKey) → `Plantilla`

- **Modelo_Campos**
  > Modelo_Campos(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Formulario_Campos**
  > Formulario_Campos(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Formulario_Campos_Contiene**
  > Formulario_Campos_Contiene(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Formulario_Campos_Empieza_Con**
  > Formulario_Campos_Empieza_Con(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Armador**
  > Armador(id, nav_bar, vista, url, url_nombre, muro, contenedor, modelo, busqueda, formulario, formulario_boton)
  - **Campos:**
    - `id` (BigAutoField)
    - `nav_bar` (ForeignKey) → `NavBar`
    - `vista` (CharField)
    - `url` (CharField)
    - `url_nombre` (CharField)
    - `muro` (ForeignKey) → `Muro`
    - `contenedor` (ForeignKey) → `Contenedor`
    - `modelo` (CharField)
    - `busqueda` (BooleanField)
    - `formulario` (CharField)
    - `formulario_boton` (CharField)
    - `modelo_campos` (ManyToManyField) → `Modelo_Campos`
    - `formulario_campos` (ManyToManyField) → `Formulario_Campos`
    - `formulario_campos_contiene` (ManyToManyField) → `Formulario_Campos_Contiene`
    - `formulario_campos_empieza_con` (ManyToManyField) → `Formulario_Campos_Empieza_Con`

- **Tipo_Registro**
  > Tipo_Registro(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Registros**
  > Registros(id, fecha, tipo, nombre, link, link_descargar, automatioco)
  - **Campos:**
    - `id` (BigAutoField)
    - `fecha` (DateField)
    - `tipo` (ForeignKey) → `Tipo_Registro`
    - `nombre` (CharField)
    - `link` (CharField)
    - `link_descargar` (CharField)
    - `automatioco` (BooleanField)

- **Compras**
  > Compras(id, proveedor, fecha, numero_remito, importe, saldo, observaciones)
  - **Campos:**
    - `id` (BigAutoField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `fecha` (DateField)
    - `numero_remito` (IntegerField)
    - `importe` (FloatField)
    - `saldo` (FloatField)
    - `observaciones` (TextField)

- **Listado_Planillas**
  > Listado_Planillas(id, proveedor, fecha, descripcion, identificador, hoja, listo, descargar, link_descarga, link_descarga_ods, id_sp, hojas)
  - **Campos:**
    - `id` (BigAutoField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `fecha` (DateField)
    - `descripcion` (CharField)
    - `identificador` (CharField)
    - `hoja` (CharField)
    - `listo` (BooleanField)
    - `descargar` (BooleanField)
    - `link_descarga` (CharField)
    - `link_descarga_ods` (CharField)
    - `id_sp` (CharField)
    - `hojas` (TextField)

- **Carrito**
  > Carrito(id, usuario)
  - **Campos:**
    - `id` (BigAutoField)
    - `usuario` (ForeignKey) → `User`

- **Articulo**
  > Articulo(id, item, carrito, cantidad, precio, precio_efectivo)
  - **Campos:**
    - `id` (BigAutoField)
    - `item` (ForeignKey) → `Item`
    - `carrito` (ForeignKey) → `Carrito`
    - `cantidad` (FloatField)
    - `precio` (DecimalField)
    - `precio_efectivo` (DecimalField)

- **ArticuloSinRegistro**
  > ArticuloSinRegistro(id, descripcion, carrito, cantidad, precio)
  - **Campos:**
    - `id` (BigAutoField)
    - `descripcion` (CharField)
    - `carrito` (ForeignKey) → `Carrito`
    - `cantidad` (FloatField)
    - `precio` (DecimalField)

### Crispy_Forms (`crispy_forms`)

### Bootstrap4 (`bootstrap4`)

### Crispy_Bootstrap4 (`crispy_bootstrap4`)

### Boletas (`boletas`)

#### Modelos

- **Comando**
  > Comando(id, comando)
  - **Campos:**
    - `id` (BigAutoField)
    - `comando` (CharField)

- **Boleta**
  > Boleta(id, tipo, impreso)
  - **Campos:**
    - `id` (BigAutoField)
    - `tipo` (CharField)
    - `impreso` (BooleanField)
    - `comandos` (ManyToManyField) → `Comando`

- **OrdenComando**
  > OrdenComando(id, boleta, comando, orden)
  - **Campos:**
    - `id` (BigAutoField)
    - `boleta` (ForeignKey) → `Boleta`
    - `comando` (ForeignKey) → `Comando`
    - `orden` (PositiveIntegerField)

#### Vistas

- **BoletasView**
  - **Métodos:**
    - `get(request)`
    - `post(request)`

### Carga_Archivo (`carga_archivo`)

#### Modelos

- **Document**
  > Document(id, uploaded_file)
  - **Campos:**
    - `id` (BigAutoField)
    - `uploaded_file` (FileField)

### Facturacion (`facturacion`)

#### Modelos

- **Cliente**
  > Cliente(id, razon_social, cuit_dni, responsabilidad_iva, tipo_documento, domicilio, telefono)
  - **Campos:**
    - `id` (BigAutoField)
    - `razon_social` (CharField)
    - `cuit_dni` (CharField)
    - `responsabilidad_iva` (CharField)
    - `tipo_documento` (CharField)
    - `domicilio` (CharField)
    - `telefono` (CharField)

- **ArticuloVendido**
  > ArticuloVendido(id, item, sin_registrar, cantidad)
  - **Campos:**
    - `id` (BigAutoField)
    - `item` (ForeignKey) → `Item`
    - `sin_registrar` (ForeignKey) → `ArticuloSinRegistro`
    - `cantidad` (FloatField)

- **MetodoPago**
  > MetodoPago(id, display, ticket)
  - **Campos:**
    - `id` (BigAutoField)
    - `display` (CharField)
    - `ticket` (BooleanField)

- **Transaccion**
  > Transaccion(id, cliente, usuario, metodo_de_pago, fecha, total, tipo_cbte, numero_cbte)
  - **Campos:**
    - `id` (BigAutoField)
    - `cliente` (ForeignKey) → `Cliente`
    - `usuario` (ForeignKey) → `User`
    - `metodo_de_pago` (ForeignKey) → `MetodoPago`
    - `fecha` (DateTimeField)
    - `total` (FloatField)
    - `tipo_cbte` (CharField)
    - `numero_cbte` (IntegerField)
    - `articulos_vendidos` (ManyToManyField) → `ArticuloVendido`

- **CierreZ**
  > CierreZ(id, fecha, RESERVADO_SIEMPRE_CERO, cant_doc_fiscales, cant_doc_fiscales_a_emitidos, cant_doc_fiscales_bc_emitidos, cant_doc_fiscales_cancelados, cant_doc_nofiscales, cant_doc_nofiscales_homologados, cant_nc_a_fiscales_a_emitidos, cant_nc_bc_emitidos, cant_nc_canceladas, monto_credito_nc, monto_imp_internos, monto_imp_internos_nc, monto_iva_doc_fiscal, monto_iva_nc, monto_iva_no_inscripto, monto_iva_no_inscripto_nc, monto_percepciones, monto_percepciones_nc, monto_ventas_doc_fiscal, status_fiscal, status_impresora, ultima_nc_a, ultima_nc_b, ultimo_doc_a, ultimo_doc_b, ultimo_remito, zeta_numero)
  - **Campos:**
    - `id` (BigAutoField)
    - `fecha` (DateField)
    - `RESERVADO_SIEMPRE_CERO` (IntegerField)
    - `cant_doc_fiscales` (IntegerField)
    - `cant_doc_fiscales_a_emitidos` (IntegerField)
    - `cant_doc_fiscales_bc_emitidos` (IntegerField)
    - `cant_doc_fiscales_cancelados` (IntegerField)
    - `cant_doc_nofiscales` (IntegerField)
    - `cant_doc_nofiscales_homologados` (IntegerField)
    - `cant_nc_a_fiscales_a_emitidos` (IntegerField)
    - `cant_nc_bc_emitidos` (IntegerField)
    - `cant_nc_canceladas` (IntegerField)
    - `monto_credito_nc` (FloatField)
    - `monto_imp_internos` (FloatField)
    - `monto_imp_internos_nc` (FloatField)
    - `monto_iva_doc_fiscal` (FloatField)
    - `monto_iva_nc` (FloatField)
    - `monto_iva_no_inscripto` (FloatField)
    - `monto_iva_no_inscripto_nc` (FloatField)
    - `monto_percepciones` (FloatField)
    - `monto_percepciones_nc` (FloatField)
    - `monto_ventas_doc_fiscal` (FloatField)
    - `status_fiscal` (CharField)
    - `status_impresora` (CharField)
    - `ultima_nc_a` (IntegerField)
    - `ultima_nc_b` (IntegerField)
    - `ultimo_doc_a` (IntegerField)
    - `ultimo_doc_b` (IntegerField)
    - `ultimo_remito` (IntegerField)
    - `zeta_numero` (IntegerField)

### Cajas (`cajas`)

### Pedido (`pedido`)

#### Modelos

- **Vendido**
  > Vendido(id, proveedor, item, cantidad, umbral, pedido)
  - **Campos:**
    - `id` (BigAutoField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `item` (ForeignKey) → `Item`
    - `cantidad` (FloatField)
    - `umbral` (FloatField)
    - `pedido` (BooleanField)

- **ArticuloPedido**
  > ArticuloPedido(id, fecha, proveedor, item, cantidad, llego)
  - **Campos:**
    - `id` (BigAutoField)
    - `fecha` (DateField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `item` (ForeignKey) → `Item`
    - `cantidad` (FloatField)
    - `llego` (BooleanField)

- **Pedido**
  > Pedido(id, fecha, proveedor, total, fecha_entrega, estado)
  - **Campos:**
    - `id` (BigAutoField)
    - `fecha` (DateField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `total` (FloatField)
    - `fecha_entrega` (DateField)
    - `estado` (CharField)
    - `articulo_pedido` (ManyToManyField) → `ArticuloPedido`

- **ArticuloDevolucion**
  > ArticuloDevolucion(id, fecha, proveedor, item, cantidad)
  - **Campos:**
    - `id` (BigAutoField)
    - `fecha` (DateField)
    - `proveedor` (ForeignKey) → `Proveedor`
    - `item` (ForeignKey) → `Item`
    - `cantidad` (FloatField)

### Articulos (`articulos`)

#### Modelos

- **Marca**
  > Marca(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Categoria**
  > Categoria(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Cartel**
  > Cartel(id, nombre)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)

- **Proveedor**
  > Proveedor(id, nombre, constante, abreviatura)
  - **Campos:**
    - `id` (BigAutoField)
    - `nombre` (CharField)
    - `constante` (FloatField)
    - `abreviatura` (CharField)

- **Articulo**
  > Articulo(id, display, marca, categoria, trabajado)
  - **Campos:**
    - `id` (BigAutoField)
    - `display` (CharField)
    - `marca` (ForeignKey) → `Marca`
    - `categoria` (ForeignKey) → `Categoria`
    - `trabajado` (BooleanField)

- **CodigoBarras**
  > CodigoBarras(id, articulo, codigo_barras)
  - **Campos:**
    - `id` (BigAutoField)
    - `articulo` (ForeignKey) → `Articulo`
    - `codigo_barras` (CharField)

- **ArticuloProveedor**
  > ArticuloProveedor(id, articulo, proveedor, codigo_base, descripcion, precio_base, actualizado, fecha, codigo_final, precio_final, precio_contado, precio_cantidad, precio_cantidad_contado, cartel)
  - **Campos:**
    - `id` (BigAutoField)
    - `articulo` (ForeignKey) → `Articulo`
    - `proveedor` (ForeignKey) → `Proveedor`
    - `codigo_base` (CharField)
    - `descripcion` (CharField)
    - `precio_base` (FloatField)
    - `actualizado` (BooleanField)
    - `fecha` (DateField)
    - `codigo_final` (CharField)
    - `precio_final` (FloatField)
    - `precio_contado` (FloatField)
    - `precio_cantidad` (FloatField)
    - `precio_cantidad_contado` (FloatField)
    - `cartel` (ForeignKey) → `Cartel`

### Actualizador (`actualizador`)

### Utils (`utils`)
