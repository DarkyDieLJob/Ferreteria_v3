# Estructura del Proyecto

  - `agregar_csv_ignore.py`
  - `cargar_datos_csv.py`
    - **Funciones:**
      - `cargar_csv_a_modelo(ruta_csv, nombre_de_tu_app, nombre_modelo)`: Sin documentación
  - `manage.py`
    - **Funciones:**
      - `main()`: Run administrative tasks.
  - `reset_pass.py`
    - **Funciones:**
      - `reset(username, contraseña)`: Sin documentación
  - `script.py`
    - **Funciones:**
      - `agregar_precio()`: Sin documentación
      - `custom_round(price)`: Sin documentación
      - `dibujo()`: Sin documentación
      - `get_status_fiscal()`: Sin documentación
      - `lista()`: Sin documentación
      - `listar_carteles()`: Sin documentación
      - `principal()`: Sin documentación
      - `probando()`: Sin documentación
      - `quitar_guiones_cuit()`: Sin documentación
      - `redondear()`: Sin documentación
      - `update_items()`: Sin documentación
  - `ejecutar_utils.py`
  - `actualizador_main.py`
    - **Funciones:**
      - `buscar_modificar_registros(csv_file, filtro)`: Sin documentación
      - `crear_o_actualizar_registro(row)`: Sin documentación
      - `desactualizar_anteriores(filtro)`: Sin documentación
      - `f()`: Sin documentación
      - `fusionar_hojas(file)`: Sin documentación
      - `marcar_revisar_carteles(id_proveedor)`: Sin documentación
      - `principal()`: Sin documentación
      - `registrar_log(texto)`: Sin documentación
  - `script_seteado_false_lista_faltantes.py`
    - **Funciones:**
      - `setear_false_lista_faltantes()`: Sin documentación
  - `generate_diagram.py`
    - **Funciones:**
      - `generate_diagram()`: Sin documentación
      - `main()`: Sin documentación
  - `generate_project_structure.py`
    - **Funciones:**
      - `analyze_module(module, indent='')`: Analiza un módulo y devuelve sus clases y funciones.
      - `get_project_structure()`: Genera la estructura del proyecto en formato Markdown.
      - `main()`: Función principal.
  - `generate_uml.py`
    - **Funciones:**
      - `configure_django()`: Configura Django para poder usar sus utilidades.
      - `generate_uml(output_file='uml_diagram.png')`: Genera un diagrama UML del proyecto.
  - `generate_uml_direct.py`
    - **Funciones:**
      - `configure_django()`: Configura Django para poder usar sus utilidades.
      - `generate_bdd_uml(output_file=None)`: Genera un diagrama UML para la aplicación 'bdd'.

Args:
    output_file (str, optional): Ruta del archivo de salida. Si es None, 
                               se usará 'media/uml_diagrams/bdd_diagram.png'
      - `get_model_fields(model)`: Obtiene los campos de un modelo en formato para el diagrama.
      - `main()`: Sin documentación
  - `test_graph_models.py`
    - **Funciones:**
      - `test_graph_models()`: Sin documentación
  - `actualizador_csv.py`
    - **Funciones:**
      - `apply_custom_round(batch_size=10000)`: Sin documentación
      - `asociar_proveedores()`: Sin documentación
      - `buscar_modificar_registros(csv_file, filtro)`: Sin documentación
      - `buscar_modificar_registros_lotes(csv_file, filtro)`: Sin documentación
      - `crear_o_actualizar_registro(row)`: Sin documentación
      - `crear_o_actualizar_registros_en_lotes(rows, tamaño_lote=1000)`: Sin documentación
      - `custom_round(price)`: Sin documentación
      - `desactualizar_anteriores(filtro)`: Sin documentación
      - `filtrar_trabajados()`: Sin documentación
      - `limpiar_texto(texto)`: Limpia un texto convirtiendo caracteres no ASCII a su equivalente ASCII.
      - `mostrara_boletas(bool)`: Sin documentación
      - `principal_csv()`: Sin documentación
      - `reset(username, contraseña)`: Sin documentación
      - `validar_digitos_str(cadena)`: Sin documentación
  - `conftest.py`
    - **Funciones:**
      - `pytest_configure()`: Configuración de pytest.
  - **articulos/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `ArticulosConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `models.py`
      - **Clases:**
        - `Articulo`: Articulo(id, display, marca, categoria, trabajado)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `ArticuloProveedor`: ArticuloProveedor(id, articulo, proveedor, codigo_base, descripcion, precio_base, actualizado, fecha, codigo_final, precio_final, precio_contado, precio_cantidad, precio_cantidad_contado, cartel)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Cartel`: Cartel(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Categoria`: Categoria(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `CodigoBarras`: CodigoBarras(id, articulo, codigo_barras)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Marca`: Marca(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Proveedor`: Proveedor(id, nombre, constante, abreviatura)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `tests.py`
    - `views.py`
  - **boletas/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `BoletasConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `classes.py`
    - `funtions.py`
    - `models.py`
      - **Clases:**
        - `Boleta`: Boleta(id, tipo, impreso)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Comando`: Comando(id, comando)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `OrdenComando`: OrdenComando(id, boleta, comando, orden)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `tests.py`
    - `views.py`
      - **Clases:**
        - `BoletasView`: Intentionally simple parent class for all views. Only implements
dispatch-by-method and simple sanity checking.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `http_method_not_allowed()`, `options()`, `post()`, `setup()`
    - `urls.py`
  - **cajas/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `CajasConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `models.py`
    - `tests.py`
    - `views.py`
  - **carga_archivo/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `CargaArchivoConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `forms.py`
      - **Clases:**
        - `UploadFileForm`: The main implementation of all the Form logic. Note that this class is
different than Form. See the comments by the Form class for more info. Any
improvements to the form API should be made to this class, not to the Form
class.
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `validate_unique()`, `visible_fields()`
    - `models.py`
      - **Clases:**
        - `Document`: Document(id, uploaded_file)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `tests.py`
    - `views.py`
      - **Funciones:**
        - `upload_file(request)`: Sin documentación
    - `urls.py`
  - **core_andamios/**
    - `admin.py`
      - **Clases:**
        - `BaseModelAdmin`: Encapsulate all admin options and functionality for a given model.
          - *Métodos:* `__init__()`, `action_checkbox()`, `add_view()`, `change_view()`, `changeform_view()`, `changelist_view()`, `check()`, `construct_change_message()`, `create_display_method()`, `delete_model()`, `delete_queryset()`, `delete_view()`, `formfield_for_choice_field()`, `formfield_for_dbfield()`, `formfield_for_foreignkey()`, `formfield_for_manytomany()`, `get_action()`, `get_action_choices()`, `get_actions()`, `get_autocomplete_fields()`, `get_changeform_initial_data()`, `get_changelist()`, `get_changelist_form()`, `get_changelist_formset()`, `get_changelist_instance()`, `get_deleted_objects()`, `get_empty_value_display()`, `get_exclude()`, `get_field_queryset()`, `get_fields()`, `get_fieldsets()`, `get_form()`, `get_formset_kwargs()`, `get_formsets_with_inlines()`, `get_inline_formsets()`, `get_inline_instances()`, `get_inlines()`, `get_list_display()`, `get_list_display_links()`, `get_list_filter()`, `get_list_select_related()`, `get_model_perms()`, `get_object()`, `get_ordering()`, `get_paginator()`, `get_prepopulated_fields()`, `get_preserved_filters()`, `get_queryset()`, `get_readonly_fields()`, `get_search_fields()`, `get_search_results()`, `get_sortable_by()`, `get_urls()`, `get_view_on_site_url()`, `has_add_permission()`, `has_change_permission()`, `has_delete_permission()`, `has_module_permission()`, `has_view_or_change_permission()`, `has_view_permission()`, `history_view()`, `log_addition()`, `log_change()`, `log_deletion()`, `log_deletions()`, `lookup_allowed()`, `message_user()`, `render_change_form()`, `render_delete_form()`, `response_action()`, `response_add()`, `response_change()`, `response_delete()`, `response_post_save_add()`, `response_post_save_change()`, `save_form()`, `save_formset()`, `save_model()`, `save_related()`, `to_field_allowed()`
    - `apps.py`
      - **Clases:**
        - `AndamiosConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `context_processors.py`
      - **Funciones:**
        - `mi_procesador_de_contexto(request)`: Sin documentación
    - `forms.py`
      - **Clases:**
        - `DateInput`: Widget personalizado para campos de fecha.
Establece el tipo de entrada a 'date'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
        - `DateTimeInput`: Widget personalizado para campos de fecha y hora.
Establece el tipo de entrada a 'datetime-local'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
        - `EmailInput`: Widget personalizado para campos de correo electrónico.
Establece el tipo de entrada a 'email'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
        - `MyForm`: Formulario personalizado que construye dinámicamente un conjunto de campos de formulario
basados en un modelo y una lista de campos especificados.

Parámetros:
    model_name (str): El nombre del modelo en el que se basará el formulario.
    fields_to_show (list): Una lista de nombres de campo para mostrar en el formulario. 
                            Si es ['__all__'], se mostrarán todos los campos del modelo. 
                            Si es ['None'], no se mostrará ningún campo.

Métodos:
    save(self, model_name): Crea una nueva instancia del modelo con los datos del formulario,
                                la valida y luego la guarda en la base de datos.
                                
    Parámetros:
        model_name (str): El nombre del modelo en el que se basará la nueva instancia.
        
    Devuelve:
        None
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `visible_fields()`
        - `TimeInput`: Widget personalizado para campos de tiempo.
Establece el tipo de entrada a 'time'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
    - `views.py`
      - **Clases:**
        - `ContextoAndamio`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
    - `tests.py`
      - **Clases:**
        - `ModeloTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
          - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_modelo_contenedor()`, `test_modelo_nav_bar()`, `test_modelo_pie()`, `test_modelo_script()`, `test_modelo_url()`
    - `models.py`
      - **Clases:**
        - `Contenedor`: Contenedor(id, nombre, text_display, html)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Contexto`: Contexto(id, json)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `ModeloBase`: Make subclasses preserve the alters_data attribute on overridden methods.
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Nav_Bar`: Nav_Bar(id, nombre, text_display, url)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Pie`: Pie(id, nombre, text_display, html)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Script`: Script(id, nombre, text_display, html)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Url`: Url(id, nombre, text_display, ruta, contenedor, script, pie)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - **docs/**
      - **core_andamios/**
  - **core_config/**
    - `wsgi.py`
    - `celery.py`
      - *Error al analizar el módulo: No module named 'celery'*
    - `asgi.py`
    - `log_config.py`
      - **Funciones:**
        - `generate_app_logging_config(apps, base_log_dir, base_formatter='verbose')`: Genera configuraciones de handlers y loggers para cada app especificada.
    - `settings_tests.py`
    - `api_settings.py`
    - `urls.py`
      - **Funciones:**
        - `include_with_namespace(namespace, module_path, app_name=None)`: Incluye URLs con namespace manejando correctamente app_name
    - **tests/**
    - **api/**
      - **v4/**
        - `config.py`
        - `urls.py`
        - **docs/**
        - **permissions/**
        - **serializers/**
        - **views/**
  - **core_docs/**
    - `admin.py`
    - `models.py`
    - `tests.py`
    - `apps.py`
      - **Clases:**
        - `AppDocsConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `signals.py`
      - **Funciones:**
        - `build_docs()`: Construye la documentación usando Sphinx.
        - `setup_signals()`: Configura los signals después de que las apps estén listas.
    - `views.py`
      - **Funciones:**
        - `changeLog(request)`: Sin documentación
        - `serve_docs(request, path)`: Esta función sirve documentos HTML generados por Sphinx.

Parámetros
----------
request : HttpRequest
    Una instancia de HttpRequest.
path : str
    La ruta del documento solicitado.

Devoluciones
------------
HttpResponse
    Un objeto HttpResponse con el documento solicitado.

Notas
-----
Los documentos HTML deben estar ubicados en 'core_docs/docs/_build/html' dentro del directorio BASE_DIR.
Si el archivo solicitado no se encuentra, esta función redirigirá a 'index.html' como página predeterminada.
    - `urls.py`
    - **docs/**
      - `conf.py`
        - **Funciones:**
          - `get_version()`: Sin documentación
      - **_build/**
        - **html/**
          - **_static/**
            - **scripts/**
            - **styles/**
            - **images/**
              - **sistema_pedidos/**
          - **_sources/**
            - **core_andamios/**
          - **core_andamios/**
          - **_images/**
        - **doctrees/**
          - **core_andamios/**
      - **core_andamios/**
      - **_static/**
        - **images/**
          - **sistema_pedidos/**
    - **management/**
      - **commands/**
        - `rebuild_docs.py`
          - **Clases:**
            - `Command`: The base class from which all management commands ultimately
derive.

Use this class if you want access to all of the mechanisms which
parse the command-line arguments and work out what code to call in
response; if you don't need to change any of that behavior,
consider using one of the subclasses defined in this file.

If you are interested in overriding/customizing various aspects of
the command-parsing and -execution behavior, the normal flow works
as follows:

1. ``django-admin`` or ``manage.py`` loads the command class
   and calls its ``run_from_argv()`` method.

2. The ``run_from_argv()`` method calls ``create_parser()`` to get
   an ``ArgumentParser`` for the arguments, parses them, performs
   any environment changes requested by options like
   ``pythonpath``, and then calls the ``execute()`` method,
   passing the parsed arguments.

3. The ``execute()`` method attempts to carry out the command by
   calling the ``handle()`` method with the parsed arguments; any
   output produced by ``handle()`` will be printed to standard
   output and, if the command is intended to produce a block of
   SQL statements, will be wrapped in ``BEGIN`` and ``COMMIT``.

4. If ``handle()`` or ``execute()`` raised any exception (e.g.
   ``CommandError``), ``run_from_argv()`` will  instead print an error
   message to ``stderr``.

Thus, the ``handle()`` method is typically the starting point for
subclasses; many built-in commands and command types either place
all of their logic in ``handle()``, or perform some additional
parsing work in ``handle()`` and then delegate from it to more
specialized methods as needed.

Several attributes affect behavior at various steps along the way:

``help``
    A short description of the command, which will be printed in
    help messages.

``output_transaction``
    A boolean indicating whether the command outputs SQL
    statements; if ``True``, the output will automatically be
    wrapped with ``BEGIN;`` and ``COMMIT;``. Default value is
    ``False``.

``requires_migrations_checks``
    A boolean; if ``True``, the command prints a warning if the set of
    migrations on disk don't match the migrations in the database.

``requires_system_checks``
    A list or tuple of tags, e.g. [Tags.staticfiles, Tags.models]. System
    checks registered in the chosen tags will be checked for errors prior
    to executing the command. The value '__all__' can be used to specify
    that all system checks should be performed. Default value is '__all__'.

    To validate an individual application's models
    rather than all applications' models, call
    ``self.check(app_configs)`` from ``handle()``, where ``app_configs``
    is the list of application's configuration provided by the
    app registry.

``stealth_options``
    A tuple of any options the command uses which aren't defined by the
    argument parser.
              - *Métodos:* `__init__()`, `add_arguments()`, `add_base_argument()`, `check()`, `check_migrations()`, `create_parser()`, `execute()`, `get_check_kwargs()`, `get_version()`, `handle()`, `print_help()`, `run_from_argv()`
  - **core_elementos/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `ElementosConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `models.py`
      - **Clases:**
        - `Modelo_Base`: Make subclasses preserve the alters_data attribute on overridden methods.
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Modelo_Formularios`: Modelo_Formularios(id, nombre, elemento_html, lista_de_campos)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Modelo_Listas`: Modelo_Listas(id, nombre, elemento_html)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Modelo_Tablas`: Modelo_Tablas(id, nombre, elemento_html, lista_de_titulos, lista_articulos)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Modelo_Tarjetas`: Modelo_Tarjetas(id, nombre, elemento_html, titulo, descripcion)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Paginas`: Paginas(id, tiene_tabla, tiene_formulario, tiene_tarjeta, tiene_lista)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `tests.py`
    - `views.py`
      - **Clases:**
        - `Crud`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
    - **templatetags/**
      - `filtro.py`
        - **Funciones:**
          - `get_attr(objeto, nombre_atributo)`: Sin documentación
  - **core_index/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `AppIndexConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `models.py`
    - `tests.py`
    - `views.py`
      - **Clases:**
        - `Vista_Index`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
    - `urls.py`
  - **facturacion/**
    - `admin.py`
      - **Clases:**
        - `TransaccionAdmin`: Encapsulate all admin options and functionality for a given model.
          - *Métodos:* `__init__()`, `action_checkbox()`, `add_view()`, `change_view()`, `changeform_view()`, `changelist_view()`, `check()`, `construct_change_message()`, `delete_model()`, `delete_queryset()`, `delete_view()`, `formfield_for_choice_field()`, `formfield_for_dbfield()`, `formfield_for_foreignkey()`, `formfield_for_manytomany()`, `get_action()`, `get_action_choices()`, `get_actions()`, `get_autocomplete_fields()`, `get_changeform_initial_data()`, `get_changelist()`, `get_changelist_form()`, `get_changelist_formset()`, `get_changelist_instance()`, `get_deleted_objects()`, `get_empty_value_display()`, `get_exclude()`, `get_field_queryset()`, `get_fields()`, `get_fieldsets()`, `get_form()`, `get_formset_kwargs()`, `get_formsets_with_inlines()`, `get_inline_formsets()`, `get_inline_instances()`, `get_inlines()`, `get_list_display()`, `get_list_display_links()`, `get_list_filter()`, `get_list_select_related()`, `get_model_perms()`, `get_object()`, `get_ordering()`, `get_paginator()`, `get_prepopulated_fields()`, `get_preserved_filters()`, `get_queryset()`, `get_readonly_fields()`, `get_search_fields()`, `get_search_results()`, `get_sortable_by()`, `get_urls()`, `get_view_on_site_url()`, `has_add_permission()`, `has_change_permission()`, `has_delete_permission()`, `has_module_permission()`, `has_view_or_change_permission()`, `has_view_permission()`, `history_view()`, `log_addition()`, `log_change()`, `log_deletion()`, `log_deletions()`, `lookup_allowed()`, `message_user()`, `render_change_form()`, `render_delete_form()`, `response_action()`, `response_add()`, `response_change()`, `response_delete()`, `response_post_save_add()`, `response_post_save_change()`, `save_form()`, `save_formset()`, `save_model()`, `save_related()`, `to_field_allowed()`
    - `apps.py`
      - **Clases:**
        - `FacturacionConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `forms.py`
      - **Clases:**
        - `ClienteForm`: The main implementation of all the Form logic. Note that this class is
different than Form. See the comments by the Form class for more info. Any
improvements to the form API should be made to this class, not to the Form
class.
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `validate_unique()`, `visible_fields()`
    - `cliente.py`
      - **Funciones:**
        - `conectar_a_websocket(data)`: Connects to a WebSocket server, sends JSON data, and receives a response.
Logs interaction details and handles potential errors.

Args:
    data (dict): The dictionary to be sent as JSON to the WebSocket server.

Returns:
    dict: The parsed JSON response from the server, or an error dictionary
          if connection, communication, or parsing fails.
    - `funtions.py`
      - **Funciones:**
        - `ciclo(fiscal=None)`: Executes a standard fiscal command cycle (no overflow).
        - `ciclo_desborde(fiscal=None)`: Executes a fiscal command cycle handling potential ticket overflow.
        - `cliente_to_dict(cliente)`: Converts a Cliente object to a dictionary.
        - `registrar_articulos_vendidos(request_dict)`: Creates a Transaccion, associates sold items (ArticuloVendido),
and prepares the JSON for fiscal ticket generation (if applicable).

Args:
    request_dict (dict): Dictionary containing data extracted from the request.

Returns:
    dict: A dictionary containing 'json' (for websocket), 'articulos' (queryset),
          'articulos_sin_registro' (queryset), and 'transaccion' (object).
          Returns None or raises an exception on critical error.
        - `request_on_procesar_transaccion_to_dict(request)`: Extracts relevant data from a POST request for transaction processing.
    - `models.py`
      - **Clases:**
        - `ArticuloVendido`: ArticuloVendido(id, item, sin_registrar, cantidad)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_item()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `CierreZ`: CierreZ(id, fecha, RESERVADO_SIEMPRE_CERO, cant_doc_fiscales, cant_doc_fiscales_a_emitidos, cant_doc_fiscales_bc_emitidos, cant_doc_fiscales_cancelados, cant_doc_nofiscales, cant_doc_nofiscales_homologados, cant_nc_a_fiscales_a_emitidos, cant_nc_bc_emitidos, cant_nc_canceladas, monto_credito_nc, monto_imp_internos, monto_imp_internos_nc, monto_iva_doc_fiscal, monto_iva_nc, monto_iva_no_inscripto, monto_iva_no_inscripto_nc, monto_percepciones, monto_percepciones_nc, monto_ventas_doc_fiscal, status_fiscal, status_impresora, ultima_nc_a, ultima_nc_b, ultimo_doc_a, ultimo_doc_b, ultimo_remito, zeta_numero)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_fecha()`, `get_previous_by_fecha()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Cliente`: Cliente(id, razon_social, cuit_dni, responsabilidad_iva, tipo_documento, domicilio, telefono)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_responsabilidad()`, `get_responsabilidad_iva_display()`, `get_tipo_documento()`, `get_tipo_documento_display()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `MetodoPago`: MetodoPago(id, display, ticket)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Transaccion`: Transaccion(id, cliente, usuario, metodo_de_pago, fecha, total, tipo_cbte, numero_cbte)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_cliente_id()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_fecha()`, `get_previous_by_fecha()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `servidor_fake_ws.py`
      - **Funciones:**
        - `handler(websocket, path)`: Esta función se ejecuta para cada cliente WebSocket que se conecta.
Ahora enviará una respuesta JSON fija después de recibir cualquier mensaje.
        - `main()`: Función principal para iniciar el servidor WebSocket.
    - `views.py`
      - **Clases:**
        - `CierreZVieW`: Handles viewing past Z Closures and initiating a new one.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `Clientes`: Handles adding new clients via a form.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `Facturacion`: Displays daily billing information for a specific date.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
        - `FacturacionMensual`: Displays monthly aggregated billing information.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
      - **Funciones:**
        - `actualizar_cantidad_articulo(request)`: Updates the quantity of a registered item in the cart and related order list.
        - `actualizar_cantidad_articulo_sin_registro(request)`: Updates the quantity of an unregistered item in the cart.
        - `agregar_articulo_sin_registro(request)`: Adds an item not present in the main inventory to the cart.
        - `consulta_impresora_fiscal_generica(request)`: Sends a generic command (GET/SET config) to the fiscal printer via websocket.
        - `eliminar_articulo(request)`: Removes a registered item from the cart and updates related order list.
        - `eliminar_articulo_sin_registro(request)`: Removes an unregistered item from the cart.
        - `obtener_cliente(request)`: Returns a list of all clients.
        - `obtener_metodos_pago(request)`: Returns available payment methods.
        - `procesar_transaccion(request)`: Processes a transaction, registers sold items, generates fiscal documents via websocket.
    - `classes.py`
      - **Clases:**
        - `ComandoFiscal`: Handles creation of command sequences for older fiscal printers.
          - *Métodos:* `__init__()`, `cierre_z()`, `get_status()`, `informe_z()`, `set_articulos()`, `set_articulos_desborde()`, `set_cierre()`, `set_encabezado()`, `set_tipo_cliente()`
        - `FormasPago`: Represents payment information for a transaction.
          - *Métodos:* `__init__()`, `get_efectivo()`, `get_formas_pago_json()`, `get_importe()`
        - `TicketCabecera`: Represents the header information for a fiscal ticket based on client data.
          - *Métodos:* `__init__()`, `get_boleta_a()`, `get_cabezera_json()`
        - `TicketFactura`: Orchestrates the creation of the complete fiscal ticket JSON.
          - *Métodos:* `__init__()`, `get_items_json()`, `get_ticket_json()`, `setear_items()`
        - `TicketItem`: Represents a single item line within a fiscal ticket.
          - *Métodos:* `__init__()`, `get_item_json()`, `set_div_cant()`
    - `tests.py`
    - `urls.py`
  - **pedido/**
    - `apps.py`
      - **Clases:**
        - `PedidosConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `tests.py`
    - `admin.py`
    - `forms.py`
      - **Clases:**
        - `ArticuloPedidoForm`: The main implementation of all the Form logic. Note that this class is
different than Form. See the comments by the Form class for more info. Any
improvements to the form API should be made to this class, not to the Form
class.
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `validate_unique()`, `visible_fields()`
    - `models.py`
      - **Clases:**
        - `ArticuloDevolucion`: ArticuloDevolucion(id, fecha, proveedor, item, cantidad)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `ArticuloPedido`: ArticuloPedido(id, fecha, proveedor, item, cantidad, llego)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_fecha()`, `get_previous_by_fecha()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Pedido`: Pedido(id, fecha, proveedor, total, fecha_entrega, estado)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_estado_display()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Vendido`: Vendido(id, proveedor, item, cantidad, umbral, pedido)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `urls.py`
    - **views/**
      - `base.py`
        - **Clases:**
          - `GeneralPedidoView`: Vista a modo de interfaz para las operaciones generales de pedidos
    
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
          - `ItemAutocomplete`: List options for a Select2 widget.
            - *Métodos:* `__init__()`, `create_object()`, `dispatch()`, `get()`, `get_allow_empty()`, `get_context_data()`, `get_context_object_name()`, `get_create_option()`, `get_ordering()`, `get_paginate_by()`, `get_paginate_orphans()`, `get_paginator()`, `get_queryset()`, `get_result_label()`, `get_result_value()`, `get_results()`, `get_search_fields()`, `get_search_results()`, `get_selected_result_label()`, `has_add_permission()`, `has_more()`, `http_method_not_allowed()`, `lookup_needs_distinct()`, `options()`, `paginate_queryset()`, `post()`, `render_to_response()`, `setup()`, `validate()`
        - **Funciones:**
          - `agregar_al_stock(request)`: Sin documentación
      - `controlar.py`
        - **Clases:**
          - `ControlarPedidoView`: Vista a modo de interfaz para las operaciones generales de pedidos
    
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - **Funciones:**
          - `actualizar_llego(request, articulo_id)`: Sin documentación
          - `agregar_devolucion(request)`: Sin documentación
      - `detalles.py`
        - **Clases:**
          - `DetallePedidoView`: Vista a modo de interfaz para las operaciones generales de pedidos
    
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
      - `devoluciones.py`
        - **Clases:**
          - `ListarDevolucionesView`: Vista a modo de interfaz para las operaciones generales de pedidos
    
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - **Funciones:**
          - `actualizar_cantidad(request, articulo_id)`: Sin documentación
      - `editar.py`
        - **Clases:**
          - `EditarPedidoView`: Vista a modo de interfaz para las operaciones generales de pedidos
    
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - **Funciones:**
          - `actualizar_cantidad(request, articulo_id)`: Sin documentación
          - `agregar_al_pedido(request)`: Sin documentación
          - `cancelar_articulo_pedido(request)`: Sin documentación
          - `enviar_pedido(request)`: Sin documentación
      - `externo.py`
        - **Funciones:**
          - `agregar_al_pedido(request, articulo_id)`: Sin documentación
      - `faltantes.py`
        - **Clases:**
          - `ListarArticulosFaltantesView`: Vista a modo de interfaz para las operaciones generales de pedidos
    
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
      - `home.py`
        - **Clases:**
          - `HomeView`: Vista a modo de interfaz para las operaciones generales de pedidos
    
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
        - **Funciones:**
          - `nuevo_pedido(request, proveedor_id)`: Sin documentación
  - **x_articulos/**
    - `admin.py`
      - **Clases:**
        - `BaseModelAdmin`: Encapsulate all admin options and functionality for a given model.
          - *Métodos:* `__init__()`, `action_checkbox()`, `add_view()`, `change_view()`, `changeform_view()`, `changelist_view()`, `check()`, `construct_change_message()`, `create_display_method()`, `delete_model()`, `delete_queryset()`, `delete_view()`, `formfield_for_choice_field()`, `formfield_for_dbfield()`, `formfield_for_foreignkey()`, `formfield_for_manytomany()`, `get_action()`, `get_action_choices()`, `get_actions()`, `get_autocomplete_fields()`, `get_changeform_initial_data()`, `get_changelist()`, `get_changelist_form()`, `get_changelist_formset()`, `get_changelist_instance()`, `get_deleted_objects()`, `get_empty_value_display()`, `get_exclude()`, `get_field_queryset()`, `get_fields()`, `get_fieldsets()`, `get_form()`, `get_formset_kwargs()`, `get_formsets_with_inlines()`, `get_inline_formsets()`, `get_inline_instances()`, `get_inlines()`, `get_list_display()`, `get_list_display_links()`, `get_list_filter()`, `get_list_select_related()`, `get_model_perms()`, `get_object()`, `get_ordering()`, `get_paginator()`, `get_prepopulated_fields()`, `get_preserved_filters()`, `get_queryset()`, `get_readonly_fields()`, `get_search_fields()`, `get_search_results()`, `get_sortable_by()`, `get_urls()`, `get_view_on_site_url()`, `has_add_permission()`, `has_change_permission()`, `has_delete_permission()`, `has_module_permission()`, `has_view_or_change_permission()`, `has_view_permission()`, `history_view()`, `log_addition()`, `log_change()`, `log_deletion()`, `log_deletions()`, `lookup_allowed()`, `message_user()`, `render_change_form()`, `render_delete_form()`, `response_action()`, `response_add()`, `response_change()`, `response_delete()`, `response_post_save_add()`, `response_post_save_change()`, `save_form()`, `save_formset()`, `save_model()`, `save_related()`, `to_field_allowed()`
    - `apps.py`
      - **Clases:**
        - `CoreArticulosConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `forms.py`
      - **Clases:**
        - `ArticuloForm`: The main implementation of all the Form logic. Note that this class is
different than Form. See the comments by the Form class for more info. Any
improvements to the form API should be made to this class, not to the Form
class.
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `validate_unique()`, `visible_fields()`
        - `Item_Form`: The main implementation of all the Form logic. Note that this class is
different than Form. See the comments by the Form class for more info. Any
improvements to the form API should be made to this class, not to the Form
class.
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `validate_unique()`, `visible_fields()`
    - `models.py`
      - **Clases:**
        - `Articulo`: Articulo(id, codigo, descripcion, precio_base, ultimo_cambio, actualizado, precio_efectivo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `tests.py`
    - `views.py`
      - **Clases:**
        - `Crud`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
    - `urls.py`
  - **x_cartel/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `XCartelConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `models.py`
      - **Clases:**
        - `Carteles`: Carteles(id, item, proveedor, revisar, descripcion, tamano_descripcion, texto_final, tamano_texto_final, final, tamano_final, texto_final_efectivo, tamano_texto_final_efectivo, final_efectivo, tamano_final_efectivo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `set_description()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `CartelesCajon`: CartelesCajon(id, item, proveedor, revisar, descripcion, tamano_descripcion, texto_final, tamano_texto_final, final, tamano_final, texto_final_efectivo, tamano_texto_final_efectivo, final_efectivo, tamano_final_efectivo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `set_description()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Cartelitos`: Cartelitos(id, item, proveedor, revisar, habilitado, descripcion)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `tests.py`
    - `views.py`
      - **Clases:**
        - `Cartel`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `Cartelito`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
        - `CrearCartelitoView`: Intentionally simple parent class for all views. Only implements
dispatch-by-method and simple sanity checking.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `http_method_not_allowed()`, `options()`, `post()`, `setup()`
        - `PruebaEdicion`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
      - **Funciones:**
        - `precios_articulos(request, articulo_id)`: Sin documentación
        - `precios_articulos_cajon(request, cajon_id)`: Sin documentación
    - `urls.py`
  - **x_widgets/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `WidgetsConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `models.py`
    - `tests.py`
    - `views.py`
  - **tests/**
    - **app_articulos/**
    - **app_bdd/**
    - **app_boletas/**
    - **app_facturacion/**
    - **app_pedido/**
    - **app_x_cartel/**
    - **articulos/**
      - `conftest.py`
        - **Clases:**
          - `AppArticulos`: Sin documentación
            - *Métodos:* `__init__()`
      - `custom_faker_proiders.py`
        - **Clases:**
          - `CuitProvider`: Sin documentación
            - *Métodos:* `__init__()`, `bothify()`, `cuit()`, `hexify()`, `language_code()`, `lexify()`, `locale()`, `numerify()`, `random_choices()`, `random_digit()`, `random_digit_above_two()`, `random_digit_not_null()`, `random_digit_not_null_or_empty()`, `random_digit_or_empty()`, `random_element()`, `random_elements()`, `random_int()`, `random_letter()`, `random_letters()`, `random_lowercase_letter()`, `random_number()`, `random_sample()`, `random_uppercase_letter()`, `randomize_nb_elements()`
      - `factories.py`
        - **Clases:**
          - `ArticuloFactory`: Factory base with build and create support.

This class has the ability to support multiple ORMs by using custom creation
functions.
      - `test_articulo.py`
        - **Funciones:**
          - `test_articulo_creation(articulos)`: Sin documentación
          - `test_articulo_proveedor_creation(articulos)`: Sin documentación
          - `test_articulo_proveedor_creation_fail(articulos)`: Sin documentación
          - `test_cartel_creation(articulos)`: Sin documentación
          - `test_categoria_creation(articulos)`: Sin documentación
          - `test_codigo_barras_creation(articulos)`: Sin documentación
          - `test_marca_creation(articulos)`: Sin documentación
          - `test_proveedor_creation(articulos)`: Sin documentación
    - **facturacion/**
      - `conftest.py`
        - **Clases:**
          - `FacturacionTestData`: Clase para agrupar instancias de prueba relacionadas con facturación
            - *Métodos:* `__init__()`
      - `test_classes.py`
        - **Clases:**
          - `FormasPagoTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
            - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_con_transaccion_invalida()`, `test_creacion_con_transaccion_nula()`, `test_creacion_formas_pago()`, `test_get_efectivo()`, `test_get_formas_pago_json()`, `test_get_importe()`
          - `TicketCabeceraTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
            - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_con_cliente_consumidor_final()`, `test_creacion_con_cliente_exento()`, `test_creacion_con_cliente_inexistente()`, `test_creacion_con_cliente_valido()`, `test_creacion_con_id_cliente_invalido()`, `test_creacion_sin_cliente()`, `test_get_boleta_a()`, `test_get_cabezera_json()`, `test_set_consumidor_final_defaults()`
          - `TicketFacturaTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
            - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_ticket_factura()`, `test_get_items_json()`, `test_get_ticket_json()`, `test_setear_items()`
          - `TicketItemTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
            - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_con_datos_minimos()`, `test_creacion_con_todos_los_datos()`, `test_get_item_json()`, `test_set_div_cant()`
      - `test_facturacion.py`
        - **Funciones:**
          - `test_formas_pago_initialization(setup_test_data)`: Sin documentación
          - `test_formas_pago_with_invalid_transaccion()`: Sin documentación
          - `test_ticket_cabecera_consumidor_final()`: Sin documentación
          - `test_ticket_cabecera_with_cliente(db)`: Prueba que TicketCabecera asigne correctamente el tipo de comprobante
para diferentes tipos de responsabilidades IVA.
          - `test_ticket_factura_initialization(setup_test_data)`: Test para verificar la inicialización correcta de TicketFactura con datos de cliente.
          - `test_ticket_item_initialization()`: Sin documentación
      - `test_models.py`
      - **test_models/**
        - `test_articulo_vendido.py`
          - **Clases:**
            - `ArticuloVendidoModelTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
              - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_articulo_vendido_con_item()`, `test_creacion_articulo_vendido_sin_registrar()`, `test_get_item_con_articulo_sin_registrar()`, `test_get_item_con_item_none()`, `test_get_item_con_item_registrado()`, `test_str_representation_con_item()`, `test_str_representation_sin_item_ni_sin_registrar()`, `test_str_representation_sin_registrar()`
        - `test_cierre_z.py`
          - **Clases:**
            - `CierreZModelTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
              - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_cierre_z()`, `test_fecha_auto_ahora()`, `test_incremento_zeta_numero()`, `test_str_representation()`, `test_valores_por_defecto()`
        - `test_cliente.py`
          - **Clases:**
            - `ClienteModelTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
              - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_cliente()`, `test_get_responsabilidad()`, `test_get_tipo_documento()`, `test_responsabilidad_choices()`, `test_str_representation()`, `test_tipo_documento_choices()`
        - `test_metodo_pago.py`
          - **Clases:**
            - `MetodoPagoModelTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
              - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_metodo_pago()`, `test_str_representation()`, `test_str_representation_display_vacio()`, `test_valores_por_defecto()`
        - `test_transaccion.py`
          - **Clases:**
            - `TransaccionModelTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
              - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_creacion_transaccion()`, `test_fecha_auto_ahora()`, `test_get_cliente_id()`, `test_str_representation()`, `test_valores_por_defecto()`
      - **utils/**
        - `factories.py`
          - **Funciones:**
            - `articulo_vendido_factory(**kwargs)`: Crea una instancia de ArticuloVendido con datos de prueba.

Args:
    **kwargs: Valores personalizados para sobrescribir los valores por defecto
    
Returns:
    ArticuloVendido: Instancia con datos de prueba
            - `cierre_z_factory(**kwargs)`: Crea una instancia de CierreZ con datos de prueba.

Args:
    **kwargs: Valores personalizados para sobrescribir los valores por defecto
    
Returns:
    CierreZ: Instancia con datos de prueba
            - `cliente_factory(**kwargs)`: Crea una instancia de Cliente con datos de prueba.

Args:
    **kwargs: Valores personalizados para sobrescribir los valores por defecto
    
Returns:
    Cliente: Instancia de Cliente con datos de prueba
            - `metodo_pago_factory(**kwargs)`: Crea una instancia de MetodoPago con datos de prueba.

Args:
    **kwargs: Valores personalizados para sobrescribir los valores por defecto
    
Returns:
    MetodoPago: Instancia con datos de prueba
            - `transaccion_factory(**kwargs)`: Crea una instancia de Transaccion con datos de prueba.

Args:
    **kwargs: Valores personalizados para sobrescribir los valores por defecto
    
Returns:
    Transaccion: Instancia con datos de prueba
  - **.pytest_cache/**
    - **v/**
      - **cache/**
  - **.vscode/**
  - **actualizador/**
    - `admin.py`
    - `models.py`
    - `tests.py`
    - `sincronizador.py`
      - **Funciones:**
        - `buckup()`: Sin documentación
        - `medir_tiempo(func)`: Sin documentación
        - `reckup()`: Sin documentación
    - `views.py`
      - **Clases:**
        - `Actualizar`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `ActualizarAhora`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
        - `Reckup`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
    - `actualizador_csv.py`
      - **Funciones:**
        - `apply_custom_round(batch_size=10000)`: Aplica redondeo personalizado a varios campos de precio en todos los Items, por lotes.
        - `asociar_proveedores()`: Asocia Items con Proveedores basándose en la abreviatura del código.
        - `buscar_modificar_registros(csv_file, filtro)`: Procesa un archivo CSV para crear o actualizar registros uno por uno.
        - `buscar_modificar_registros_lotes(csv_file, filtro, tamaño_lote=10000)`: Procesa un archivo CSV para crear o actualizar registros en lotes.
        - `crear_o_actualizar_registro(row)`: Sin documentación
        - `crear_o_actualizar_registros_en_lotes(rows, tamaño_lote)`: Sin documentación
        - `custom_round(price)`: Sin documentación
        - `desactualizar_anteriores(filtro)`: Marca como no actualizados los items cuyo código termina con el filtro dado.
        - `filtrar_trabajados()`: Filtra items marcados como 'trabajado' por proveedor y los guarda en archivos CSV.
        - `limpiar_texto(texto)`: Limpia un texto convirtiendo caracteres no ASCII a su equivalente ASCII.
        - `mostrara_boletas(bool)`: Actualiza el estado 'impreso' de todas las boletas.
        - `principal_csv()`: Función principal que procesa archivos CSV pendientes para cada proveedor.
        - `reset(username, contraseña)`: Resetea la contraseña de un usuario.
        - `validar_digitos_str(cadena)`: Sin documentación
    - `actualizador_main.py`
      - **Funciones:**
        - `buscar_modificar_registros(csv_file, filtro)`: Procesa un archivo CSV para crear o actualizar registros uno por uno.
        - `crear_o_actualizar_registro(row)`: Sin documentación
        - `desactualizar_anteriores(filtro)`: Marca como no actualizados los items cuyo código termina con el filtro dado.
        - `fusionar_hojas(file_stream)`: Carga un stream de archivo Excel, fusiona hojas (excepto 'general') en 'cargar datos' y devuelve el Workbook.
        - `marcar_revisar_carteles(id_proveedor)`: Marca los carteles y carteles de cajón asociados a un proveedor para revisión.
        - `principal()`: Función principal del script para procesar planillas de Google Drive/Sheets.
        - `registrar_log(texto)`: Sin documentación
    - `apps.py`
      - **Clases:**
        - `ActualizadorConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `task.py`
      - **Clases:**
        - `ColaTareasWorker`: Gestor Singleton para una cola de tareas simple ejecutada en un hilo
separado en segundo plano. Las tareas se agregan de forma no bloqueante.
          - *Métodos:* `__init__()`, `agregar_tarea()`, `ejecutar_tareas()`, `start_worker()`
        - `HiloManager`: Sin documentación
          - *Métodos:* `__init__()`, `agregar_proceso()`, `iniciar_hilo()`, `nuevo_hilo()`
      - **Funciones:**
        - `actualizador()`: Sin documentación
        - `actualizar()`: Sin documentación
        - `agregar_tareas_en_cola(hora_inicio: Optional[datetime.time] = None)`: Función auxiliar para agregar el conjunto estándar de tareas
(principal, csv, backup) a la cola compartida. Retorna inmediatamente.
        - `etiquetado()`: Sin documentación
        - `fake_apply_custom_round()`: Sin documentación
        - `fake_principal()`: Sin documentación
        - `fake_principal_csv()`: Sin documentación
        - `procesar()`: Sin documentación
        - `recoleccion()`: Sin documentación
        - `recolectar_procesar()`: Se va a cambiar a futuro cuando
 se refactorize el modo en el que se capuran las planillas.
        - `tirar_comando(comando='ls')`: Sin documentación
    - `urls.py`
    - **tests/**
  - **utils/**
    - `constantes_django.py`
    - `ordenar_query.py`
      - **Funciones:**
        - `agrupar_transacciones_por_fecha(queryset: django.db.models.query.QuerySet) -> dict`: Sin documentación
    - `outsider.py`
      - **Funciones:**
        - `arrancar_django_config()`: Este metodo se encarga de arrancar la configuracion de Django.
    - `queryset_to_xlsx.py`
      - **Funciones:**
        - `diccionario_to_xlsx(diccionario, filename)`: Escribir un diccionario en un archivo xlsx 
        - `ejecutar()`: Sin documentación
        - `queryset_to_sheet(queryset, sheet)`: Escribir un queryset en una hoja de un archivo de sheets 
        - `queryset_to_xlsx(queryset, filename)`: Escribir un queryset en un archivo xlsx 
  - **bdd/**
    - `apps.py`
      - **Clases:**
        - `BddConfig`: Class representing a Django application and its configuration.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `forms.py`
      - *Error al analizar el módulo: cannot import name 'Planilla' from 'bdd.models' (/home/fedora/Documentos/GitHub/Ferreteria_v3/bdd/models.py)*
    - `tests.py`
    - `admin.py`
      - **Clases:**
        - `BaseModelAdmin`: Encapsulate all admin options and functionality for a given model.
          - *Métodos:* `__init__()`, `action_checkbox()`, `add_view()`, `change_view()`, `changeform_view()`, `changelist_view()`, `check()`, `construct_change_message()`, `create_display_method()`, `delete_model()`, `delete_queryset()`, `delete_view()`, `formfield_for_choice_field()`, `formfield_for_dbfield()`, `formfield_for_foreignkey()`, `formfield_for_manytomany()`, `get_action()`, `get_action_choices()`, `get_actions()`, `get_autocomplete_fields()`, `get_changeform_initial_data()`, `get_changelist()`, `get_changelist_form()`, `get_changelist_formset()`, `get_changelist_instance()`, `get_deleted_objects()`, `get_empty_value_display()`, `get_exclude()`, `get_field_queryset()`, `get_fields()`, `get_fieldsets()`, `get_form()`, `get_formset_kwargs()`, `get_formsets_with_inlines()`, `get_inline_formsets()`, `get_inline_instances()`, `get_inlines()`, `get_list_display()`, `get_list_display_links()`, `get_list_filter()`, `get_list_select_related()`, `get_model_perms()`, `get_object()`, `get_ordering()`, `get_paginator()`, `get_prepopulated_fields()`, `get_preserved_filters()`, `get_queryset()`, `get_readonly_fields()`, `get_search_fields()`, `get_search_results()`, `get_sortable_by()`, `get_urls()`, `get_view_on_site_url()`, `has_add_permission()`, `has_change_permission()`, `has_delete_permission()`, `has_module_permission()`, `has_view_or_change_permission()`, `has_view_permission()`, `history_view()`, `log_addition()`, `log_change()`, `log_deletion()`, `log_deletions()`, `lookup_allowed()`, `message_user()`, `render_change_form()`, `render_delete_form()`, `response_action()`, `response_add()`, `response_change()`, `response_delete()`, `response_post_save_add()`, `response_post_save_change()`, `save_form()`, `save_formset()`, `save_model()`, `save_related()`, `to_field_allowed()`
    - `funtions.py`
      - **Funciones:**
        - `armar_tabla(id_carpeta_inbox, id_carpeta_plantillas, credentials)`: Sin documentación
        - `get_emails(gmail_service, drive_service)`: Sin documentación
    - `views_old.py`
      - **Clases:**
        - `BusquedaForm`: Formulario de búsqueda que permite al usuario seleccionar una Marca, Cajón, Cajonera y Sector específicos.
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `visible_fields()`
        - `BusquedaView`: Vista de formulario que maneja la lógica de búsqueda y muestra los resultados al usuario.
          - *Métodos:* `__init__()`, `dispatch()`, `form_invalid()`, `form_valid()`, `get()`, `get_context_data()`, `get_form()`, `get_form_class()`, `get_form_kwargs()`, `get_initial()`, `get_prefix()`, `get_success_url()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `put()`, `render_to_response()`, `setup()`
        - `DateInput`: Widget personalizado para campos de fecha.
Establece el tipo de entrada a 'date'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
        - `DateTimeInput`: Widget personalizado para campos de fecha y hora.
Establece el tipo de entrada a 'datetime-local'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
        - `EmailInput`: Widget personalizado para campos de correo electrónico.
Establece el tipo de entrada a 'email'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
        - `Imprimir`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `Inicio`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `ItemsView`: Intentionally simple parent class for all views. Only implements
dispatch-by-method and simple sanity checking.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `http_method_not_allowed()`, `options()`, `setup()`
        - `ListadoPedidos`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `ListarCarteles`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `MiVista`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `MyForm`: Formulario personalizado que construye dinámicamente un conjunto de campos de formulario
basados en un modelo y una lista de campos especificados.

Parámetros:
    model_name (str): El nombre del modelo en el que se basará el formulario.
    fields_to_show (list): Una lista de nombres de campo para mostrar en el formulario. 
                            Si es ['__all__'], se mostrarán todos los campos del modelo. 
                            Si es ['None'], no se mostrará ningún campo.

Métodos:
    save(self, model_name): Crea una nueva instancia del modelo con los datos del formulario,
                                la valida y luego la guarda en la base de datos.
                                
    Parámetros:
        model_name (str): El nombre del modelo en el que se basará la nueva instancia.
        
    Devuelve:
        None
          - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `visible_fields()`
        - `Prueba`: Render a template. Pass keyword arguments from the URLconf to the context.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `TimeInput`: Widget personalizado para campos de tiempo.
Establece el tipo de entrada a 'time'.
          - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
      - **Funciones:**
        - `agregar_articulo_a_carrito(request, id_articulo)`: Sin documentación
        - `articulo_to_dict(articulo)`: Sin documentación
        - `calcular_total(datos)`: Sin documentación
        - `cambiar_cantidad_pedido(request, id_articulo, cantidad)`: Sin documentación
        - `carrito(request)`: Sin documentación
        - `carrito_to_dict(carrito)`: Sin documentación
        - `consultar_carrito(request)`: Sin documentación
        - `crear_modificar_lista_pedidos(request, proveedor_id=1)`: Sin documentación
        - `descargar_archivo(request)`: Sin documentación
        - `editar_item(request, id_articulo)`: Sin documentación
        - `eliminar_articulo_pedido(request)`: Sin documentación
        - `enviar_reporte(request, articulo_id)`: Sin documentación
        - `reportar_item(request, articulo_id)`: Sin documentación
        - `seleccionar_proveedor(request)`: Sin documentación
        - `usuarios_caja(request)`: Sin documentación
    - `classes.py`
      - **Clases:**
        - `Patoba`: Sin documentación
          - *Métodos:* `__init__()`, `actualizar_contenido_copiar()`, `actualizar_plantilla()`, `borrar_por_id()`, `buscar_copia_por_nombre()`, `copiar_hoja()`, `copiar_reemplazable()`, `crear_buscar_copia_descarga()`, `crear_hoja_google_drive()`, `crear_hoja_por_nombre()`, `desaturar()`, `descargar_sqlite3_de_drive()`, `download_and_zip_files()`, `eliminar_hoja()`, `filtrar_trabajados()`, `listar()`, `obtener_g_sheet_por_id()`, `obtener_id_hoja_por_nombre()`, `obtener_id_por_nombre()`, `renombrar_hoja()`, `subir_sqlite3_a_drive()`
    - `models.py`
      - **Clases:**
        - `Archivo`: Archivo(id, proveedor, condiciones, agregado, editado, archivo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `basename()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `descargar()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_agregado()`, `get_next_by_editado()`, `get_previous_by_agregado()`, `get_previous_by_editado()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Armador`: Armador(id, nav_bar, vista, url, url_nombre, muro, contenedor, modelo, busqueda, formulario, formulario_boton)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Articulo`: Articulo(id, item, carrito, cantidad, precio, precio_efectivo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `ArticuloSinRegistro`: ArticuloSinRegistro(id, descripcion, carrito, cantidad, precio)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Cajon`: Cajon(id, codigo, cajonera)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Cajonera`: Cajonera(id, codigo, sector)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Carrito`: Carrito(id, usuario)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Cod_Barras`: Cod_Barras(id, barras, articulo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Compras`: Compras(id, proveedor, fecha, numero_remito, importe, saldo, observaciones)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_fecha()`, `get_previous_by_fecha()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Condiciones`: Condiciones(id, proveedor, fila_inicial, codigo, nombre, precio_base, porcentaje, porcentaje_21, porcentaje_10_5, dolar)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `detectar_columna()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `ordenar_columnas()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Contenedor`: Contenedor(id, nombre, url, a, b, c)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Formulario_Campos`: Formulario_Campos(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Formulario_Campos_Contiene`: Formulario_Campos_Contiene(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Formulario_Campos_Empieza_Con`: Formulario_Campos_Empieza_Con(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Generica`: Make subclasses preserve the alters_data attribute on overridden methods.
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `GenericaLista`: Make subclasses preserve the alters_data attribute on overridden methods.
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Item`: Item(id, cajon, marca, codigo, barras, descripcion, precio_base, porcentaje, porcentaje_efectivo, porcentaje_oferta, porcentaje_oferta_efectivo, oferta, precio_rollo_caja, venta_rollo_caja, porcentaje_metro, pack_cantidad, cantidad_rollo_caja, descuento_rollo_caja, descuento_rollo_caja_efectivo, final_rollo, final_rollo_efectivo, final, final_efectivo, trabajado, sub_carpeta, sub_titulo, actualizado, fecha, stock, proveedor, tiene_cartel, tipo_cartel, p_c_efectivo, p_c_debito, p_c_credito)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `calcular_precio_efectivo_final()`, `calcular_precio_final()`, `calcular_precio_rollo_efectivo_final()`, `calcular_precio_rollo_final()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `marcar_actualizado()`, `marcar_desactualizado()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `ListaProveedores`: ListaProveedores(id, nombre, abreviatura, hay_csv_pendiente)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Lista_Pedidos`: Lista_Pedidos(id, proveedor, item, cantidad, pedido)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Listado_Planillas`: Listado_Planillas(id, proveedor, fecha, descripcion, identificador, hoja, listo, descargar, link_descarga, link_descarga_ods, id_sp, hojas)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Marca`: Marca(id, codigo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Modelo_Campos`: Modelo_Campos(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Muro`: Muro(id, muro_html)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `NavBar`: NavBar(id, url_inicial, text_display)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Plantilla`: Plantilla(id, plantilla_html)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Proveedor`: Proveedor(id, identificador, text_display, cuit, direccion, email, telefono, corredor, corredor_telefono)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Registros`: Registros(id, fecha, tipo, nombre, link, link_descargar, automatioco)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Sector`: Sector(id, codigo)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Sub_Carpeta`: Sub_Carpeta(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Sub_Titulo`: Sub_Titulo(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Tipo_Cartel`: Tipo_Cartel(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `Tipo_Registro`: Tipo_Registro(id, nombre)
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
    - `urls.py`
    - **templatetags/**
      - `custom_filters.py`
        - **Funciones:**
          - `custom_price(price)`: Sin documentación
          - `en_lista(value)`: Sin documentación
          - `to_float(value)`: Sin documentación
          - `zip_lists(a, b)`: Sin documentación
    - **views/**
      - `ajax.py`
        - **Funciones:**
          - `agregar_articulo_a_carrito(request, id_articulo)`: Sin documentación
          - `cambiar_cantidad_pedido(request, id_articulo, cantidad)`: Sin documentación
          - `carrito(request)`: Sin documentación
          - `consultar_carrito(request)`: Sin documentación
          - `crear_modificar_lista_pedidos(request, proveedor_id=None)`: Sin documentación
          - `descargar_archivo(request)`: Sin documentación
          - `editar_item(request, id_articulo)`: Sin documentación
          - `eliminar_articulo_pedido(request)`: Sin documentación
          - `enviar_reporte(request, articulo_id)`: Sin documentación
          - `reportar_item(request, articulo_id)`: Sin documentación
          - `seleccionar_proveedor(request)`: Sin documentación
          - `usuarios_caja(request)`: Sin documentación
      - `base.py`
        - **Clases:**
          - `MiVista`: Render a template. Pass keyword arguments from the URLconf to the context.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
      - `forms.py`
        - **Clases:**
          - `BusquedaForm`: Formulario de búsqueda que permite al usuario seleccionar una Marca, Cajón, Cajonera y Sector específicos.
            - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `visible_fields()`
          - `DateInput`: Widget personalizado para campos de fecha.
Establece el tipo de entrada a 'date'.
            - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
          - `DateTimeInput`: Widget personalizado para campos de fecha y hora.
Establece el tipo de entrada a 'datetime-local'.
            - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
          - `EmailInput`: Widget personalizado para campos de correo electrónico.
Establece el tipo de entrada a 'email'.
            - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
          - `MyForm`: Formulario personalizado que construye dinámicamente un conjunto de campos de formulario
basados en un modelo y una lista de campos especificados.
            - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `save()`, `visible_fields()`
          - `TimeInput`: Widget personalizado para campos de tiempo.
Establece el tipo de entrada a 'time'.
            - *Métodos:* `__init__()`, `build_attrs()`, `format_value()`, `get_context()`, `id_for_label()`, `render()`, `subwidgets()`, `use_required_attribute()`, `value_from_datadict()`, `value_omitted_from_data()`
      - `main.py`
        - **Clases:**
          - `BusquedaView`: Vista de formulario que maneja la lógica de búsqueda y muestra los resultados al usuario.
            - *Métodos:* `__init__()`, `dispatch()`, `form_invalid()`, `form_valid()`, `get()`, `get_context_data()`, `get_form()`, `get_form_class()`, `get_form_kwargs()`, `get_initial()`, `get_prefix()`, `get_success_url()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `put()`, `render_to_response()`, `setup()`
          - `Imprimir`: Render a template. Pass keyword arguments from the URLconf to the context.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
          - `Inicio`: Render a template. Pass keyword arguments from the URLconf to the context.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
          - `ItemsView`: Intentionally simple parent class for all views. Only implements
dispatch-by-method and simple sanity checking.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `http_method_not_allowed()`, `options()`, `setup()`
          - `ListadoPedidos`: Render a template. Pass keyword arguments from the URLconf to the context.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
          - `ListarCarteles`: Render a template. Pass keyword arguments from the URLconf to the context.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
          - `Prueba`: Render a template. Pass keyword arguments from the URLconf to the context.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_template_names()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
      - `utils.py`
        - **Funciones:**
          - `articulo_to_dict(articulo)`: Convierte una instancia de Articulo o ArticuloSinRegistro a un diccionario.
          - `calcular_total(datos)`: Calcula los totales para una estructura de datos de carritos.
          - `carrito_to_dict(carrito)`: Convierte una instancia de Carrito a un diccionario simple.
  - **.github/**
    - **workflows/**
  - **logs/**
    - **facturacion/**
    - **bdd/**
    - **actualizador/**
    - **uml_visualizer/**
  - **core_testing/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `CoreTestingConfig`: Configuration for core_testing application.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `conftest.py`
      - *Error al analizar el módulo: No module named 'model_bakery'*
    - `models.py`
      - **Clases:**
        - `ModuleCoverage`: Almacena información de cobertura de código por módulo.
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_last_updated()`, `get_previous_by_last_updated()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `update_from_coverage_data()`, `validate_constraints()`, `validate_unique()`
        - `TestCase`: Almacena información sobre un caso de prueba individual.
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_created_at()`, `get_previous_by_created_at()`, `get_status_display()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `validate_constraints()`, `validate_unique()`
        - `TestRun`: Almacena información sobre una ejecución de pruebas.
          - *Métodos:* `__init__()`, `adelete()`, `arefresh_from_db()`, `asave()`, `clean()`, `clean_fields()`, `date_error_message()`, `delete()`, `full_clean()`, `get_constraints()`, `get_deferred_fields()`, `get_next_by_created_at()`, `get_next_by_started_at()`, `get_next_by_updated_at()`, `get_previous_by_created_at()`, `get_previous_by_started_at()`, `get_previous_by_updated_at()`, `get_status_display()`, `prepare_database_save()`, `refresh_from_db()`, `save()`, `save_base()`, `serializable_value()`, `unique_error_message()`, `update_from_pytest_json()`, `validate_constraints()`, `validate_unique()`
    - `signals.py`
      - **Funciones:**
        - `module_coverage_post_save(sender, instance, created, **kwargs)`: Señal post-save para el modelo ModuleCoverage.
Actualiza la cobertura en TestRun cuando se guarda un registro de cobertura.
        - `test_case_post_save(sender, instance, created, **kwargs)`: Señal post-save para el modelo TestCase.
Actualiza las estadísticas de TestRun cuando se guarda un caso de prueba.
        - `test_run_post_save(sender, instance, created, **kwargs)`: Señal post-save para el modelo TestRun.
Registra la creación o actualización de una ejecución de pruebas.
        - `test_run_pre_save(sender, instance, **kwargs)`: Señal pre-save para el modelo TestRun.
Genera un nombre por defecto para nuevas ejecuciones de prueba.
    - `storage.py`
      - **Clases:**
        - `TestResultStorage`: Clase para manejar el almacenamiento de resultados de pruebas.
          - *Métodos:* `get_run_filename()`, `get_test_stats()`, `list_test_runs()`, `load_test_run()`, `save_test_run()`
    - `urls.py`
    - `views.py`
    - `views_test.py`
      - **Clases:**
        - `TestInterfaceView`: Vista para probar una interfaz de testing específica.
          - *Métodos:* `__init__()`, `dispatch()`, `get()`, `http_method_not_allowed()`, `options()`, `setup()`
      - **Funciones:**
        - `list_testing_interfaces(request: django.http.request.HttpRequest) -> django.http.response.HttpResponse`: Vista que lista todas las interfaces de testing disponibles.
    - **views/**
      - `views.py`
        - **Clases:**
          - `AppDetailView`: Vista para mostrar detalles de una aplicación específica.

Muestra estadísticas de cobertura y pruebas para una aplicación Django específica,
incluyendo módulos que la componen, tendencias de cobertura y pruebas recientes.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_app_name()`, `get_context_data()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
          - `CoverageReportView`: Vista simple para mostrar el informe de cobertura de pruebas.

Muestra un listado de módulos con su porcentaje de cobertura,
ordenados de mayor a menor cobertura.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
          - `InterfaceTestingView`: Vista para interactuar con una interfaz de testing específica.
Esta vista se encarga de cargar dinámicamente la interfaz solicitada.

Nota: Ya incluye LoginRequiredMixin a través de TestingView.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_interface()`, `get_interface_class()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
          - `ModuleCoverageDetailView`: Vista para mostrar detalles de cobertura de un módulo específico.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_context_object_name()`, `get_login_url()`, `get_object()`, `get_permission_denied_message()`, `get_queryset()`, `get_redirect_field_name()`, `get_slug_field()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
          - `TestHistoryView`: Vista para mostrar el historial de ejecuciones de pruebas.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
          - `TestRunDetailView`: Vista para mostrar los detalles de una ejecución de pruebas.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `setup()`
          - `TestRunListView`: Vista para mostrar una lista de ejecuciones de pruebas.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_allow_empty()`, `get_context_data()`, `get_context_object_name()`, `get_login_url()`, `get_ordering()`, `get_paginate_by()`, `get_paginate_orphans()`, `get_paginator()`, `get_permission_denied_message()`, `get_queryset()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `paginate_queryset()`, `render_to_response()`, `setup()`
          - `TestingDashboardView`: Vista principal del dashboard de testing.
Muestra un resumen de las pruebas y la cobertura de código agrupado por aplicación.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_app_name()`, `get_context_data()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `render_to_response()`, `setup()`
        - **Funciones:**
          - `api_coverage_data(request)`: API para obtener datos de cobertura actualizados.
          - `api_test_status(request)`: API para obtener el estado actual de las pruebas.
          - `discover_testing_interfaces() -> Dict[str, Type[core_testing.testing_interfaces.base.TestingInterface]]`: Descubre automáticamente todas las interfaces de testing disponibles.

Returns:
    Dict[str, Type[TestingInterface]]: Diccionario con las interfaces encontradas
          - `get_test_form(request: django.http.request.HttpRequest, interface_name: str) -> django.http.response.JsonResponse`: Vista que devuelve el formulario HTML para un test específico.

Args:
    request: Objeto HttpRequest
    interface_name: Nombre de la interfaz de testing
    
Returns:
    JsonResponse con el formulario HTML o un mensaje de error
          - `list_testing_interfaces(request: django.http.request.HttpRequest) -> django.http.response.HttpResponse`: Vista que lista todas las interfaces de testing disponibles.

Args:
    request: Objeto HttpRequest
    
Returns:
    HttpResponse con la lista de interfaces renderizada
          - `run_test_api(request: django.http.request.HttpRequest, interface_name: str) -> django.http.response.JsonResponse`: API para ejecutar un test y devolver los resultados en formato JSON.

Args:
    request: Objeto HttpRequest
    interface_name: Nombre de la interfaz de testing
    
Returns:
    JsonResponse con los resultados del test
      - `views_test.py`
        - **Clases:**
          - `TestInterfaceView`: Vista para probar una interfaz de testing específica.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `http_method_not_allowed()`, `options()`, `setup()`
        - **Funciones:**
          - `list_testing_interfaces(request: django.http.request.HttpRequest) -> django.http.response.HttpResponse`: Vista que lista todas las interfaces de testing disponibles.
    - **management/**
      - **commands/**
        - `run_tests.py`
          - **Clases:**
            - `Command`: Comando para ejecutar pruebas y guardar resultados en la base de datos.
              - *Métodos:* `__init__()`, `add_arguments()`, `add_base_argument()`, `check()`, `check_migrations()`, `create_parser()`, `execute()`, `get_check_kwargs()`, `get_version()`, `handle()`, `print_help()`, `run_from_argv()`
          - **Funciones:**
            - `setup_logging()`: Configura el sistema de logging para el comando.
    - **templatetags/**
      - `math_filters.py`
        - **Funciones:**
          - `div(value, arg)`: Sin documentación
          - `mul(value, arg)`: Sin documentación
      - `testing_filters.py`
        - **Funciones:**
          - `basename(filepath)`: Extrae el nombre base de una ruta de archivo.

Args:
    filepath (str): Ruta completa del archivo
    
Returns:
    str: Nombre del archivo con su extensión
          - `coverage_badge_class(coverage_percent)`: Devuelve la clase de color para la insignia de cobertura según el porcentaje.
          - `coverage_color(coverage_percent)`: Devuelve la clase de color para la cobertura según el porcentaje.
          - `coverage_progress(coverage_percent, size='normal')`: Genera una barra de progreso para la cobertura de código.
          - `format_coverage_trend(trend_value)`: Formatea el valor de tendencia de cobertura.
          - `format_duration(seconds)`: Formatea la duración en segundos a un formato legible.
          - `get_status_bg_class(status)`: Devuelve la clase de color de fondo según el estado de la prueba.
          - `get_status_icon(status)`: Devuelve el ícono correspondiente al estado de la prueba.
          - `percentage(value, total)`: Calcula el porcentaje de un valor respecto a un total.

Args:
    value: El valor a calcular
    total: El valor total (100%)
    
Returns:
    float: El porcentaje calculado, o 0 si el total es 0
          - `status_color(status)`: Devuelve la clase de color de Bootstrap para un estado de prueba.

Args:
    status (str): Estado de la prueba (passed, failed, error, skipped, running, pending)
    
Returns:
    str: Clase de color de Bootstrap (success, danger, warning, info, secondary)
          - `test_result_progress(test_run)`: Genera una barra de progreso para los resultados de las pruebas.
          - `test_result_summary(test_run)`: Genera un resumen de los resultados de las pruebas.
          - `test_status_bg_color(status)`: Devuelve la clase de color de fondo para un estado de prueba.
          - `test_status_count(test_runs, status)`: Cuenta el número de ejecuciones con un estado específico.
          - `test_status_percent(test_runs, status)`: Calcula el porcentaje de ejecuciones con un estado específico.
          - `test_trend_icon(trend_value)`: Devuelve un ícono que representa la tendencia del rendimiento de las pruebas.
    - **testing_interfaces/**
      - `base.py`
        - **Clases:**
          - `TestingInterface`: Interfaz base para todos los módulos de testing.
Define los métodos que deben implementar las interfaces de testing específicas.
            - *Métodos:* `get_available_tests()`, `get_test_form()`, `run_test()`
          - `TestingView`: Vista base para las interfaces de testing.
Proporciona funcionalidad común para todas las vistas de testing.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_interface()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
      - `example.py`
        - **Clases:**
          - `ExampleTestingInterface`: Interfaz de ejemplo para testing.
            - *Métodos:* `get_available_tests()`, `get_test_form()`, `run_test()`
      - `example_interface.py`
        - **Clases:**
          - `ExampleTestForm`: Formulario de ejemplo para el test.
            - *Métodos:* `__init__()`, `add_error()`, `add_initial_prefix()`, `add_prefix()`, `as_div()`, `as_p()`, `as_table()`, `as_ul()`, `clean()`, `full_clean()`, `get_context()`, `get_initial_for_field()`, `has_changed()`, `has_error()`, `hidden_fields()`, `is_multipart()`, `is_valid()`, `non_field_errors()`, `order_fields()`, `render()`, `visible_fields()`
          - `ExampleTestingInterface`: Ejemplo de implementación de TestingInterface.
Esta clase muestra cómo implementar una interfaz de testing personalizada.
            - *Métodos:* `get_available_tests()`, `get_test_form()`, `run_test()`
          - `ExampleTestingView`: Vista para la interfaz de ejemplo.
            - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_interface()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
      - `test_interface.py`
        - **Clases:**
          - `TestInterface`: Implementación de prueba de TestingInterface para usar en pruebas unitarias.
            - *Métodos:* `get_available_tests()`, `get_test_form()`, `run_test()`
      - **views/**
        - `example.py`
          - **Clases:**
            - `ExampleInterfaceView`: Vista para la interfaz de ejemplo de testing.
Ya incluye LoginRequiredMixin a través de TestingView.
              - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_interface()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
        - `example_interface.py`
          - **Clases:**
            - `ExampleInterfaceTestingView`: Vista para la interfaz de ejemplo avanzada de testing.
Ya incluye LoginRequiredMixin a través de TestingView.
              - *Métodos:* `__init__()`, `dispatch()`, `get()`, `get_context_data()`, `get_interface()`, `get_login_url()`, `get_permission_denied_message()`, `get_redirect_field_name()`, `get_template_names()`, `handle_no_permission()`, `http_method_not_allowed()`, `options()`, `post()`, `render_to_response()`, `setup()`
    - **tests/**
      - `conftest.py`
        - **Funciones:**
          - `pytest_collection_modifyitems(config, items)`: Modifica la colección de pruebas para excluir clases abstractas.
          - `pytest_configure(config)`: Configura el entorno de pruebas de Django.
      - `test_basic.py`
        - **Clases:**
          - `BasicTest`: Similar to TransactionTestCase, but use `transaction.atomic()` to achieve
test isolation.

In most situations, TestCase should be preferred to TransactionTestCase as
it allows faster execution. However, there are some situations where using
TransactionTestCase might be necessary (e.g. testing some transactional
behavior).

On database backends with no transaction support, TestCase behaves as
TransactionTestCase.
            - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_dashboard_view()`
      - `test_urls.py`
        - **Clases:**
          - `CoreTestingURLTests`: Pruebas para las URLs del módulo core_testing.
            - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_coverage_report_url_accessible()`, `test_coverage_report_url_resolves()`, `test_dashboard_url_accessible()`, `test_dashboard_url_resolves()`, `test_nonexistent_run_detail_returns_404()`, `test_run_detail_url_accessible()`, `test_run_detail_url_resolves()`, `test_testrun_list_url()`, `test_urls_require_authentication()`
    - **utils/**
      - `create_test_data.py`
        - **Funciones:**
          - `create_test_cases(test_run, count=10)`: Crea casos de prueba para una ejecución.
          - `create_test_data()`: Función principal para crear datos de prueba.
          - `create_test_run(user, status='passed', days_ago=0)`: Crea una ejecución de prueba con estado aleatorio.
          - `create_test_user()`: Crea un usuario de prueba si no existe.
      - `migrate_to_file_storage.py`
        - **Funciones:**
          - `migrate_test_runs()`: Migra todos los TestRuns y sus TestCases asociados al almacenamiento en archivos.
    - **.pytest_cache/**
      - **v/**
        - **cache/**
    - **fixtures/**
    - **testing_templates/**
      - **core_testing/**
  - **gestor_articulos/**
  - **htmlcov/**
  - **test_logs/**
  - **core_utils/**
  - **uml_visualizer/**
    - `admin.py`
    - `apps.py`
      - **Clases:**
        - `UmlVisualizerConfig`: Configuración de la aplicación UML Visualizer.
          - *Métodos:* `__init__()`, `get_model()`, `get_models()`, `import_models()`, `ready()`
    - `context_processors.py`
      - **Funciones:**
        - `user_info(request)`: A context processor that provides safe access to user information.
    - `models.py`
    - `project_analyzer.py`
      - **Clases:**
        - `ProjectAnalyzer`: Analiza la estructura del proyecto Django y extrae información sobre
modelos, vistas, formularios y otras clases importantes.
          - *Métodos:* `__init__()`, `generate_project_documentation()`, `get_project_structure()`
    - `tests.py`
    - `urls.py`
    - `views.py`
      - **Funciones:**
        - `_convert_dot_to_png(dot_file, output_file)`: Convierte un archivo DOT a PNG
        - `_generate_forms_diagram(app_label, output_file, all_apps)`: Genera un diagrama de los formularios de la aplicación
        - `_generate_models_diagram(app_label, temp_dot_file, output_file, all_apps)`: Genera el diagrama de modelos usando django-extensions graph_models
        - `_generate_views_diagram(app_label, output_file, all_apps)`: Genera un diagrama de las vistas de la aplicación
        - `app_diagram(request, app_label)`: Vista para mostrar los diagramas de una aplicación específica.
Muestra tres diagramas: modelos, vistas y formularios.
        - `download_diagram(request, app_label)`: Vista para descargar el diagrama de una aplicación o del proyecto completo.

Args:
    request: Objeto HttpRequest
    app_label: Nombre de la aplicación o 'project' para el diagrama completo
        - `download_docs(request)`: Vista para descargar la documentación del proyecto en formato Markdown.
        - `generate_app_diagram(app_label, output_file)`: Genera un diagrama UML para una aplicación específica.

Args:
    app_label (str): Etiqueta de la aplicación
    output_file (str): Ruta completa del archivo de salida
    
Returns:
    bool: True si se generó correctamente, False en caso contrario
    str: Mensaje de error en caso de fallo
        - `generate_diagram(app_label, output_file_base, all_apps=False)`: Genera tres diagramas UML para una aplicación o para todo el proyecto:
1. Diagrama de modelos
2. Diagrama de vistas
3. Diagrama de formularios

Args:
    app_label (str): Nombre de la aplicación o None para todo el proyecto
    output_file_base (str): Ruta base del archivo de salida (sin extensión)
    all_apps (bool): Si es True, genera el diagrama de todo el proyecto
    
Returns:
    tuple: (éxito, mensaje_de_error, diagramas)
        - `is_admin(user)`: Sin documentación
        - `project_diagram(request)`: Vista para mostrar el diagrama completo del proyecto con información detallada.
        - `uml_dashboard(request)`: Vista del panel de control que muestra todas las aplicaciones instaladas.
    - **services/**
    - **management/**
      - **commands/**
        - `cleanup_socialaccounts.py`
          - **Clases:**
            - `Command`: The base class from which all management commands ultimately
derive.

Use this class if you want access to all of the mechanisms which
parse the command-line arguments and work out what code to call in
response; if you don't need to change any of that behavior,
consider using one of the subclasses defined in this file.

If you are interested in overriding/customizing various aspects of
the command-parsing and -execution behavior, the normal flow works
as follows:

1. ``django-admin`` or ``manage.py`` loads the command class
   and calls its ``run_from_argv()`` method.

2. The ``run_from_argv()`` method calls ``create_parser()`` to get
   an ``ArgumentParser`` for the arguments, parses them, performs
   any environment changes requested by options like
   ``pythonpath``, and then calls the ``execute()`` method,
   passing the parsed arguments.

3. The ``execute()`` method attempts to carry out the command by
   calling the ``handle()`` method with the parsed arguments; any
   output produced by ``handle()`` will be printed to standard
   output and, if the command is intended to produce a block of
   SQL statements, will be wrapped in ``BEGIN`` and ``COMMIT``.

4. If ``handle()`` or ``execute()`` raised any exception (e.g.
   ``CommandError``), ``run_from_argv()`` will  instead print an error
   message to ``stderr``.

Thus, the ``handle()`` method is typically the starting point for
subclasses; many built-in commands and command types either place
all of their logic in ``handle()``, or perform some additional
parsing work in ``handle()`` and then delegate from it to more
specialized methods as needed.

Several attributes affect behavior at various steps along the way:

``help``
    A short description of the command, which will be printed in
    help messages.

``output_transaction``
    A boolean indicating whether the command outputs SQL
    statements; if ``True``, the output will automatically be
    wrapped with ``BEGIN;`` and ``COMMIT;``. Default value is
    ``False``.

``requires_migrations_checks``
    A boolean; if ``True``, the command prints a warning if the set of
    migrations on disk don't match the migrations in the database.

``requires_system_checks``
    A list or tuple of tags, e.g. [Tags.staticfiles, Tags.models]. System
    checks registered in the chosen tags will be checked for errors prior
    to executing the command. The value '__all__' can be used to specify
    that all system checks should be performed. Default value is '__all__'.

    To validate an individual application's models
    rather than all applications' models, call
    ``self.check(app_configs)`` from ``handle()``, where ``app_configs``
    is the list of application's configuration provided by the
    app registry.

``stealth_options``
    A tuple of any options the command uses which aren't defined by the
    argument parser.
              - *Métodos:* `__init__()`, `add_arguments()`, `add_base_argument()`, `check()`, `check_migrations()`, `create_parser()`, `execute()`, `get_check_kwargs()`, `get_version()`, `handle()`, `print_help()`, `run_from_argv()`
        - `fix_socialaccounts.py`
          - **Clases:**
            - `Command`: The base class from which all management commands ultimately
derive.

Use this class if you want access to all of the mechanisms which
parse the command-line arguments and work out what code to call in
response; if you don't need to change any of that behavior,
consider using one of the subclasses defined in this file.

If you are interested in overriding/customizing various aspects of
the command-parsing and -execution behavior, the normal flow works
as follows:

1. ``django-admin`` or ``manage.py`` loads the command class
   and calls its ``run_from_argv()`` method.

2. The ``run_from_argv()`` method calls ``create_parser()`` to get
   an ``ArgumentParser`` for the arguments, parses them, performs
   any environment changes requested by options like
   ``pythonpath``, and then calls the ``execute()`` method,
   passing the parsed arguments.

3. The ``execute()`` method attempts to carry out the command by
   calling the ``handle()`` method with the parsed arguments; any
   output produced by ``handle()`` will be printed to standard
   output and, if the command is intended to produce a block of
   SQL statements, will be wrapped in ``BEGIN`` and ``COMMIT``.

4. If ``handle()`` or ``execute()`` raised any exception (e.g.
   ``CommandError``), ``run_from_argv()`` will  instead print an error
   message to ``stderr``.

Thus, the ``handle()`` method is typically the starting point for
subclasses; many built-in commands and command types either place
all of their logic in ``handle()``, or perform some additional
parsing work in ``handle()`` and then delegate from it to more
specialized methods as needed.

Several attributes affect behavior at various steps along the way:

``help``
    A short description of the command, which will be printed in
    help messages.

``output_transaction``
    A boolean indicating whether the command outputs SQL
    statements; if ``True``, the output will automatically be
    wrapped with ``BEGIN;`` and ``COMMIT;``. Default value is
    ``False``.

``requires_migrations_checks``
    A boolean; if ``True``, the command prints a warning if the set of
    migrations on disk don't match the migrations in the database.

``requires_system_checks``
    A list or tuple of tags, e.g. [Tags.staticfiles, Tags.models]. System
    checks registered in the chosen tags will be checked for errors prior
    to executing the command. The value '__all__' can be used to specify
    that all system checks should be performed. Default value is '__all__'.

    To validate an individual application's models
    rather than all applications' models, call
    ``self.check(app_configs)`` from ``handle()``, where ``app_configs``
    is the list of application's configuration provided by the
    app registry.

``stealth_options``
    A tuple of any options the command uses which aren't defined by the
    argument parser.
              - *Métodos:* `__init__()`, `add_arguments()`, `add_base_argument()`, `check()`, `check_migrations()`, `create_parser()`, `execute()`, `get_check_kwargs()`, `get_version()`, `handle()`, `print_help()`, `run_from_argv()`
    - **tests/**
      - `test_views.py`
        - **Clases:**
          - `UMLLoggingMiddleware`: Middleware para registrar información de las peticiones.
            - *Métodos:* `__init__()`
          - `UMLVisualizerViewsTest`: Pruebas para las vistas del visualizador UML.
            - *Métodos:* `__init__()`, `addCleanup()`, `addTypeEqualityFunc()`, `assertAlmostEqual()`, `assertAlmostEquals()`, `assertContains()`, `assertCountEqual()`, `assertDictContainsSubset()`, `assertDictEqual()`, `assertEqual()`, `assertEquals()`, `assertFalse()`, `assertFieldOutput()`, `assertFormError()`, `assertFormSetError()`, `assertGreater()`, `assertGreaterEqual()`, `assertHTMLEqual()`, `assertHTMLNotEqual()`, `assertIn()`, `assertInHTML()`, `assertIs()`, `assertIsInstance()`, `assertIsNone()`, `assertIsNot()`, `assertIsNotNone()`, `assertJSONEqual()`, `assertJSONNotEqual()`, `assertLess()`, `assertLessEqual()`, `assertListEqual()`, `assertLogs()`, `assertMultiLineEqual()`, `assertNoLogs()`, `assertNotAlmostEqual()`, `assertNotAlmostEquals()`, `assertNotContains()`, `assertNotEqual()`, `assertNotEquals()`, `assertNotIn()`, `assertNotInHTML()`, `assertNotIsInstance()`, `assertNotRegex()`, `assertNotRegexpMatches()`, `assertNumQueries()`, `assertQuerySetEqual()`, `assertRaises()`, `assertRaisesMessage()`, `assertRaisesRegex()`, `assertRaisesRegexp()`, `assertRedirects()`, `assertRegex()`, `assertRegexpMatches()`, `assertSequenceEqual()`, `assertSetEqual()`, `assertTemplateNotUsed()`, `assertTemplateUsed()`, `assertTrue()`, `assertTupleEqual()`, `assertURLEqual()`, `assertWarns()`, `assertWarnsMessage()`, `assertWarnsRegex()`, `assertXMLEqual()`, `assertXMLNotEqual()`, `assert_()`, `countTestCases()`, `debug()`, `defaultTestResult()`, `doCleanups()`, `fail()`, `failIf()`, `failIfAlmostEqual()`, `failIfEqual()`, `failUnless()`, `failUnlessAlmostEqual()`, `failUnlessEqual()`, `failUnlessRaises()`, `id()`, `modify_settings()`, `run()`, `setUp()`, `settings()`, `shortDescription()`, `skipTest()`, `subTest()`, `tearDown()`, `test_app_diagram_view()`, `test_download_diagram()`, `test_download_docs()`, `test_generate_diagram()`, `test_project_diagram_view()`, `test_uml_dashboard_view()`, `test_unauthorized_access()`
  - **assets/**
    - **uml_visualizer/**
      - **css/**
  - **docs/**
    - **adr/**
  - **instalacion_raspbian/**
    - `crear_contenedor_python.py`
      - **Funciones:**
        - `crear_contenedor_django(nombre_base)`: Crea un volumen y un contenedor de Python para Django.
        - `ejecutar_comando(comando)`: Ejecuta un comando en la terminal e imprime la salida.
        - `instalar_docker()`: Intenta instalar Docker si no está instalado.
        - `verificar_docker_instalado()`: Verifica si Docker está instalado.
  - **scripts/**
    - `crear_documentacion.py`
      - **Funciones:**
        - `crear_documentacion(app_name, app_path)`: Crea la estructura de documentación para una aplicación.
        - `main()`: Sin documentación
    - `documentation_workflow.py`
      - **Funciones:**
        - `check_git_status() -> bool`: Verifica si hay cambios sin confirmar.
        - `commit_changes()`: Confirma los cambios con un mensaje descriptivo.
        - `create_documentation_branch() -> bool`: Crea la rama de documentación si no existe.
        - `create_feature_branch() -> str`: Crea una rama de feature para los cambios de documentación.
        - `create_pr(base: str, head: str, title: str = None)`: Crea un Pull Request usando el comando gh (GitHub CLI).
        - `get_current_branch() -> str`: Obtiene la rama actual.
        - `main()`: Sin documentación
        - `push_changes(branch: str)`: Hace push de los cambios al repositorio remoto.
        - `run_command(cmd: List[str], cwd: str = None) -> Tuple[bool, str]`: Ejecuta un comando y devuelve (éxito, salida).
  - **test_results/**