from django.conf import settings

# Defaults with ability to override from project settings
DEFAULT_FOLDER_ID = '1IaqfSk0z3Oy8huw7XpxmFsLaGXE7jouO'

REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID = getattr(
    settings,
    'REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID',
    DEFAULT_FOLDER_ID,
)
REPORTES_INPUT_DRIVE_ROOT_NAME = getattr(settings, 'REPORTES_INPUT_DRIVE_ROOT_NAME', '')
REPORTES_OUTPUT_ROOT_NAME = getattr(settings, 'REPORTES_OUTPUT_ROOT_NAME', '')
REPORTES_ALLOWED_MIME_TYPES = getattr(
    settings,
    'REPORTES_ALLOWED_MIME_TYPES',
    [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'application/vnd.oasis.opendocument.spreadsheet',
    ],
)
REPORTES_DEFAULT_OUTPUT_FORMATS = getattr(settings, 'REPORTES_DEFAULT_OUTPUT_FORMATS', ['xlsx'])
REPORTES_MEDIA_SUBDIR = getattr(settings, 'REPORTES_MEDIA_SUBDIR', 'reportes')
REPORTES_REQUIRE_STAFF = getattr(settings, 'REPORTES_REQUIRE_STAFF', True)

# Control-book flow
REPORTES_INPUT_FOLDER_ID = getattr(settings, 'REPORTES_INPUT_FOLDER_ID', '')  # carpeta de entrada (Drive)
REPORTES_CONTROL_SHEET_ID = getattr(settings, 'REPORTES_CONTROL_SHEET_ID', '')  # ID del libro de control (Google Sheets)
REPORTES_CONTROL_TAB = getattr(settings, 'REPORTES_CONTROL_TAB', 'Control')  # nombre de la hoja dentro del libro de control
REPORTES_INPUT_FOLDER_NAME = getattr(settings, 'REPORTES_INPUT_FOLDER_NAME', 'Planillas diarias')  # nombre de carpeta de entrada (si no se provee ID)

# Año mínimo a considerar al explorar subcarpetas dentro de la carpeta de entrada
REPORTES_MIN_YEAR = getattr(settings, 'REPORTES_MIN_YEAR', 2026)
