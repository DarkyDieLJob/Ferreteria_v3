# Ferretería Paoli v3

## Instalación

### 1. Requisitos del Sistema

- Python 3.12.9
- Servicios adicionales para Raspbian:
  - Unicorn (para producción)
  - Nginx (para producción)
  - Docker (para desarrollo)
- Visual Studio Code (VSCode)
  - Extension: Conventional Commits

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
   pip install -r requirements.txt
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

## Flujo de Trabajo de Desarrollo

### 1. Estructura de Ramas

- `main`: Rama principal con código estable
- `develop`: Rama de desarrollo para nuevas características
- `feature/*`: Ramas de características específicas
- `hotfix/*`: Ramas para correcciones urgentes

### 2. Proceso de Desarrollo

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

