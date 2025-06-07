# Instalación del Sistema

```{important}
Este documento describe el proceso de instalación para el sistema de Ferretería Paoli.
```

## Requisitos Previos

### Sistema Operativo
- Linux (recomendado) o Windows
- Python 3.12.9

### Dependencias del Sistema
- SQLite (incluido en Django)
- Servicios adicionales para Raspbian:
  - Unicorn (para producción)
  - Nginx (para producción)
  - Docker
- Visual Studio Code (VSCode)
  - Extension: Conventional Commits

### Instalación en Raspbian

1. **Actualizar el sistema**:
   ```bash
   sudo apt update
   sudo apt upgrade -y
   ```

2. **Instalar Docker y crear contenedor**:
   Ejecuta el script de instalación automática:
   ```bash
   python instalacion_raspbian/crear_contenedor_python.py ferreteria
   ```
   
   Este script realizará automáticamente:
   - Instalación de Docker si no está presente
   - Creación de un volumen y contenedor para Django
   - Configuración del entorno virtual dentro del contenedor
   
   **Nota**: Si prefieres instalar manualmente, puedes seguir los pasos individuales:
   ```bash
   # Instalar dependencias
   sudo apt install ca-certificates curl gnupg lsb-release -y
   
   # Configurar repositorio de Docker
   sudo install -m 0755 -d /etc/apt/keyrings
   curl -fsSL https://download.docker.com/linux/debian/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
   sudo chmod a+r /etc/apt/keyrings/docker.gpg
   
   # Añadir repositorio de Docker
   echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
   
   # Instalar Docker
   sudo apt update
   sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
   
   # Configurar usuario para Docker
   sudo usermod -aG docker tu_usuario  # Reemplazar 'tu_usuario' con el nombre real del usuario
   ```

   **Importante**: Después de configurar el usuario para Docker, reinicia la sesión para que los cambios de grupo surtan efecto.

### Instalación de VSCode

1. **Instalar VSCode**:
   - Descargar e instalar desde: https://code.visualstudio.com/

2. **Instalar la extensión de Conventional Commits**:
   - Abrir VSCode
   - Presionar `Ctrl+Shift+X` para abrir la vista de extensiones
   - Buscar "Conventional Commits"
   - Instalar la extensión oficial de conventional commits

## Instalación del Entorno

### 1. Clonar el Repositorio
```bash
git clone https://github.com/DarkyDieLJob/Ferreteria_v3.git
cd Ferreteria_v3
```

### 2. Crear y Activar Entorno Virtual
```bash
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate    # En Windows
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```



## Configuración Inicial

### 1. Configurar settings.py
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

### 2. Configurar Servidor WebSocket de Impresora Fiscal
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

### 2. Inicialización de la Base de Datos

1. **Aplicar Migraciones**
```bash
python manage.py migrate
```

2. **Crear Usuario Administrador**
```bash
python manage.py createsuperuser
```

## Iniciar el Servidor

```bash
python manage.py runserver
```

El sistema estará disponible en `http://localhost:8000`

## Flujo de Trabajo de Desarrollo

### 1. Estructura de Ramas
El proyecto utiliza las siguientes ramas principales:

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

## Comandos Útiles

### Reconstruir Documentación
```bash
python manage.py rebuild_docs
```

### Ejecutar Tests
```bash
python manage.py test
```

### Limpiar Cache
```bash
python manage.py clear_cache
```

## Problemas Comunes y Soluciones

### 1. Error de Migraciones
Si encuentras errores de migraciones, intenta:
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

### 2. Error de Dependencias
Si hay problemas con las dependencias de Python:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 3. Error de Base de Datos
Si no puedes conectar a PostgreSQL:
1. Verifica que el servicio está corriendo
2. Revisa las credenciales en el archivo .env
3. Ejecuta `createdb ferreteria` si la base de datos no existe
