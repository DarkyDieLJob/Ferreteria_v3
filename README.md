# Ferretería Paoli v3

Sistema de gestión integral para ferretería con control de inventario, ventas, compras y más.

## Características Principales

- 🛒 **Gestión de Inventario** - Control completo de productos, marcas y ubicaciones
- 📦 **Sistema de Compras** - Gestión de proveedores y órdenes de compra
- 💰 **Ventas y Facturación** - Punto de venta integrado con facturación electrónica
- 🧪 **Sistema de Pruebas** - Framework de pruebas integrado con seguimiento de cobertura
  - 📊 Dashboard interactivo de pruebas
  - 📈 Tendencias de cobertura de código
  - 🔍 Búsqueda y filtrado de ejecuciones de pruebas
  - 📝 Documentación integrada con el flujo de desarrollo
- 🔍 **Búsqueda Avanzada** - Búsqueda rápida de productos por múltiples criterios
- 📱 **Interfaz Responsiva** - Funciona en dispositivos de escritorio y móviles

## Flujo de Trabajo de Pruebas

### Desarrollo de Pruebas

1. **Rama de Desarrollo**
   - Todo el desarrollo de pruebas se realiza en la rama `develop`
   - Cada cambio debe incluir pruebas unitarias y de integración
   - Se debe mantener la cobertura de código por encima del 80%

2. **Ejecución de Pruebas**
   ```bash
   # Ejecutar todas las pruebas con cobertura
   python manage.py run_tests --coverage
   
   # Ejecutar pruebas específicas
   python manage.py test core_testing.tests.test_basic
   
   # Verificar cobertura de código
   coverage report -m
   ```

3. **Integración con Documentación**
   - Los cambios en las pruebas deben documentarse en `TESTING_PLAN.md`
   - Se debe actualizar `PLAN_PRUEBAS.md` con cualquier cambio en la estrategia de pruebas
   - Los PRs de `develop` a `documentation` deben incluir actualizaciones de documentación

4. **Flujo de Integración**
   ```mermaid
   graph LR
     A[develop] -->|PR| B[documentation]
     B -->|PR| C[pre-release]
     C -->|PR| D[main]
   ```

## Instalación

### 1. Requisitos del Sistema

## Características Principales

- 🖥️ **Visualización UML** - Herramienta para generar y visualizar diagramas de clases y relaciones del sistema (solo administradores)
  - Generación automática de diagramas de clases
  - Visualización de relaciones entre modelos
  - Análisis de estructura del proyecto.

    - Antes de mergear de *pre-release* a *main*, debe ejecutarse el comando
    ''' npx standard-version ''', para generar el CHANGELOG.md correspondiente.

#### Producción
- Nginx
- Gunicorn o uWSGI
- PostgreSQL 13+
- Redis
- Supervisor o systemd

#### Herramientas de Desarrollo Recomendadas
- Visual Studio Code con extensiones:
  - Python
  - Django
  - Docker
  - Conventional Commits

### 2. Instalación en Raspbian

1. **Actualizar el sistema**:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Instalar dependencias**:
   ```bash
   sudo apt install ca-certificates curl gnupg lsb-release -y
   ```

3. **Configurar repositorio de Docker**:
   ```bash
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   sudo chmod a+r /etc/apt/keyrings/docker.gpg
   ```

4. **Añadir repositorio de Docker**:
   ```bash
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   ```

5. **Actualizar e instalar Docker**:
   ```bash
   sudo apt update
   sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
   ```

6. **Configurar usuario para Docker**:
   ```bash
   sudo usermod -aG docker tu_usuario  # Reemplazar 'tu_usuario' con el nombre real del usuario
   ```

   **Importante**: Después de este paso, reinicia la sesión para que los cambios de grupo surtan efecto.

7. **Verificar instalación**:
   ```bash
   docker run hello-world
   ```

8. **Crear contenedor Django**:
   ```bash
   docker run --name django_server -d -p 8000:8000 python:3.12.9
   ```

   **Nota**: El contenedor está configurado para mapear el puerto 8000 del host al puerto 8000 del contenedor.

### 3. Instalación de VSCode

1. **Instalar VSCode**:
   - Descargar e instalar desde: https://code.visualstudio.com/

2. **Instalar la extensión de Conventional Commits**:
   - Abrir VSCode
   - Presionar `Ctrl+Shift+X` para abrir la vista de extensiones
   - Buscar "Conventional Commits"
   - Instalar la extensión oficial de conventional commits

### 4. Clonación del Repositorio

1. **Entrar al contenedor**:
   ```bash
   docker exec -it django_server /bin/bash
   ```

2. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/DarkyDieLJob/Ferreteria_v3.git
   cd Ferreteria_v3
   ```

3. **Configurar entorno virtual**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

4. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

### 2. Configuración

1. **Configurar settings.py**
   Crea un archivo `settings.py` en el directorio `core_config/` con las siguientes configuraciones mínimas:
   ```python
   SECRET_KEY = 'tu_clave_secreta_aqui'  # Genera una clave segura

   # Configuración de la base de datos (SQLite por defecto)
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db.sqlite3',
       }
   }

   # Configuración de medios
   MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
   MEDIA_URL = '/media/'
   STATIC_ROOT = os.path.join(BASE_DIR, 'static')
   STATIC_URL = '/static/'

   # Configuración de seguridad
   ALLOWED_HOSTS = ['*']

   # Configuración de WebSocket para impresora fiscal
   IP_BEW_SOCKET = 'ws://localhost:8080'  # URL del servidor WebSocket de la impresora

   # Configuración de aplicaciones
   INSTALLED_APPS = [
       'core_docs',
       'core_andamios',
       'core_index',
       'core_elementos',
       'x_widgets',
       'x_articulos',
       'x_cartel',
       'bdd',
       'crispy_forms',
       'bootstrap4',
       'crispy_bootstrap4',
       'boletas',
       'carga_archivo',
       'facturacion',
       'cajas',
       'pedido',
       'articulos',
       'actualizador',
       'utils',
   ]
   ```

2. **Configurar Servidor WebSocket de Impresora Fiscal**
   Para que el sistema pueda comunicarse con la impresora fiscal, necesitas tener un servidor WebSocket corriendo que actúe como puente entre el sistema y la impresora. Las opciones son:

   1. Servidor Real:
      - Configurar el servidor WebSocket de la impresora fiscal según la documentación del fabricante
      - El servidor debe estar accesible en la URL configurada en `IP_BEW_SOCKET`

   2. Servidor de Pruebas (Para desarrollo):
      - El proyecto incluye un servidor WebSocket falso para pruebas (`servidor_fake_ws.py`)
      - Para usarlo, ejecuta:
      ```bash
      python facturacion/servidor_fake_ws.py
      ```
      - Este servidor responde con respuestas fijas para pruebas y desarrollo

### 3. Instalación

1. **Crear Entorno Virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   # o
   venv\Scripts\activate    # En Windows
   ```

2. **Instalar Dependencias**
   ```bash
   # Instalar dependencias del sistema
   sudo apt-get install python3-dev libpq-dev
   
   # Crear y activar entorno virtual
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   
   # Instalar dependencias de Python
   pip install -r requirements.txt
   ```

## Ejecución de Pruebas

El sistema incluye un conjunto completo de pruebas automatizadas que deben ejecutarse usando el comando `run_tests` para garantizar el registro adecuado de resultados en el dashboard:

```bash
# Ejecutar todas las pruebas y generar reporte de cobertura
python manage.py run_tests --coverage

# Ejecutar pruebas de un módulo específico
python manage.py run_tests core_testing.tests

# Ejecutar pruebas en paralelo (más rápido)
python manage.py run_tests --parallel=4

# Ver todas las opciones disponibles
python manage.py run_tests --help

# Usar el dashboard de pruebas (requiere servidor en ejecución)
python manage.py runserver
# Luego acceder a: http://localhost:8000/testing/dashboard/
```

> **Importante**: No uses `pytest` directamente, ya que no registrará los resultados en el dashboard. Siempre usa `python manage.py run_tests` para ejecutar las pruebas.

## Estructura del Proyecto

```
ferreteria_v3/
├── core/                     # Configuración principal de Django
├── core_testing/            # Módulo de pruebas automatizadas
│   ├── management/commands/  # Comandos personalizados
│   ├── static/               # Archivos estáticos (CSS, JS)
│   ├── templates/            # Plantillas del dashboard de pruebas
│   └── tests/                # Pruebas unitarias
├── facturacion/             # Módulo de facturación
├── templates/               # Plantillas base
└── utils/                   # Utilidades compartidas
```

## Documentación

- [Guía de Desarrollo](docs/desarrollo.md)
- [Sistema de Pruebas](docs/SISTEMA_DE_PRUEBAS.md)
- [Estructura de la Documentación](docs/ESTRUCTURA_DOCUMENTACION.md)
- [Flujo de Trabajo](docs/FLUJO_TRABAJO.md)

## Contribución

1. Crear un fork del repositorio
2. Crear una rama para tu característica (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer commit de tus cambios (`git commit -am 'feat: agregar nueva funcionalidad'`)
4. Hacer push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crear un Pull Request

## Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## Pruebas

El proyecto incluye un sistema completo de pruebas automatizadas. Para más información, consulta la [documentación detallada de pruebas](./docs/SISTEMA_DE_PRUEBAS.md).

### Ejecutar pruebas

```bash
# Todas las pruebas
python manage.py test

# Pruebas específicas del módulo core_testing
python manage.py test core_testing

# Con mayor verbosidad
python manage.py test --verbosity=2
```

## Documentación

La documentación detallada del proyecto se encuentra en el directorio `docs/`:

- [Sistema de Pruebas](./docs/SISTEMA_DE_PRUEBAS.md): Guía completa sobre el sistema de pruebas automatizadas.
- [Estructura de Documentación](./docs/ESTRUCTURA_DOCUMENTACION.md): Explicación de la estructura de documentación del proyecto.
- [Flujo de Trabajo](./docs/FLUJO_TRABAJO.md): Guía sobre el flujo de desarrollo y contribución.

Para generar documentación adicional, puedes usar:

```bash
# Instalar dependencias de documentación
pip install -r docs/requirements.txt

# Generar documentación
cd docs && make html
```

3. **Inicialización de la Base de Datos**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

4. **Iniciar el Servidor**
   ```bash
   python manage.py runserver
   ```
   El sistema estará disponible en `http://localhost:8000`

## Documentación del Proyecto

El proyecto sigue una estructura de documentación estandarizada para mantener el código bien documentado y fácil de mantener.

### 1. Estructura de Documentación

Cada aplicación del proyecto sigue esta estructura:

```
cada_aplicacion/
├── docs/                 # Documentación detallada
│   ├── ARQUITECTURA.md   # Diseño de la aplicación
│   └── FLUJOS.md        # Flujos de trabajo principales
├── README.md            # Documentación básica
└── OBJETIVOS.md         # Objetivos y roadmap
```

### 2. Generar Documentación

Para generar la estructura de documentación en todas las aplicaciones:

```bash
# Instalar dependencias si es necesario
pip install -r requirements.txt

# Generar documentación
python scripts/crear_documentacion.py
```

### 3. Documentación Detallada

Para más información sobre la documentación, consulta:
- [Guía de Documentación](docs/GUIA_DOCUMENTACION.md)
- [Estructura de Documentación](docs/ESTRUCTURA_DOCUMENTACION.md)

## Flujo de Trabajo de Desarrollo

### 1. Estructura de Ramas

- `main`: Rama principal con código estable
- `develop`: Rama de desarrollo para nuevas características
- `feature/*`: Ramas de características específicas
- `hotfix/*`: Ramas para correcciones urgentes

### 2. Documentación de Cambios

Al hacer cambios en el código, asegúrate de:

1. Actualizar la documentación afectada
2. Usar commits semánticos
3. Documentar cambios importantes en CHANGELOG.md

### 3. Proceso de Desarrollo

1. **Crear una nueva característica**:
   ```bash
   git checkout develop
   git checkout -b feature/nombre-de-la-caracteristica
   ```

2. **Ejecutar pruebas**:
   ```bash
   pytest
   ```
   Las pruebas se ejecutan automáticamente en cualquier archivo que coincida con los patrones:
   - `tests.py`
   - `test_*.py`
   - `*_test.py`

3. **Crear commit**:
   ```bash
   git add .
   ```
   
   Luego, en VSCode:
   1. Presiona `Ctrl+P`
   2. Escribe `:commit` para abrir el asistente de commits
   3. En la interfaz gráfica:
      - Selecciona el tipo de commit (feat, fix, docs, etc.)
      - Selecciona o escribe el scope (ej: `bdd`, `facturacion`, `articulos`, etc.)
      - Selecciona un icono para el commit
      - Escribe una descripción breve en el cuadro de diálogo
      - Escribe una descripción más detallada en el cuadro de diálogo correspondiente
      - Si aplica, completa el cuadro de diálogo de "breaking changes o issues cerrados"
   
   Ejemplo de commit:
   ```
   feat(bdd): agregar nueva funcionalidad de búsqueda

   Agregada nueva funcionalidad de búsqueda avanzada en la aplicación principal
   que permite buscar por múltiples campos y filtros.

   BREAKING CHANGE: Se modificó la estructura de la URL de búsqueda
   ```

4. **Integrar cambios**:
   ```bash
   git checkout develop
   git merge feature/nombre-de-la-caracteristica
   git branch -d feature/nombre-de-la-caracteristica
   ```

5. **Crear un hotfix**:
   ```bash
   git checkout main
   git checkout -b hotfix/nombre-del-hotfix
   # ... hacer cambios ...
   git checkout main
   git merge hotfix/nombre-del-hotfix
   git branch -d hotfix/nombre-del-hotfix
   git push origin main
   ```

