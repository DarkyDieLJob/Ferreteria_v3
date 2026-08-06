import csv
import logging
import os

from django.conf import settings as const
from bdd.classes import Patoba
from bdd.models import Listado_Planillas, ListaProveedores
from actualizador.actualizador_main import _load_django_deps, retry_with_backoff
from actualizador.actualizador_csv import buscar_modificar_registros_lotes

logger = logging.getLogger(__name__)

RECREAR_IDS = [1532, 1538]  # Fischer, Poxipol
RELOAD_CSV_IDS = [1538]     # Solo Poxipol necesita recargar CSV

_load_django_deps()
patoba = Patoba(None)

for sp_id in RECREAR_IDS:
    sp = Listado_Planillas.objects.get(id=sp_id)
    nombre = sp.proveedor.identificador.nombre if sp.proveedor and hasattr(sp.proveedor, 'identificador') and sp.proveedor.identificador else sp.descripcion
    print(f"--- Recreando descargables para '{nombre}' (ID {sp.id}) ---")

    id_plantilla = sp.id_sp
    if not id_plantilla:
        print(f"  ERROR: sin id_sp (template ID). Saltando.")
        continue

    # Si necesita recargar CSV, descargar BDD y procesar
    if sp_id in RELOAD_CSV_IDS:
        print(f"  Recargando CSV desde BDD de plantilla...")
        try:
            def descargar_bdd():
                req = patoba.sheet_service.spreadsheets().values().get(
                    spreadsheetId=id_plantilla, range="BDD"
                )
                req.http.timeout = 600
                return req.execute()

            result_bdd = retry_with_backoff(descargar_bdd, max_retries=5, initial_delay=5, backoff_factor=2)
            values_bdd = result_bdd.get("values", [])
            if values_bdd:
                csv_path = f"{nombre}.csv"
                with open(csv_path, "w", encoding="utf-8", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(values_bdd)
                print(f"  BDD descargado: {len(values_bdd)} filas")

                abrev = sp.proveedor.identificador.abreviatura
                if abrev:
                    print(f"  Procesando CSV con filtro '{abrev}'...")
                    buscar_modificar_registros_lotes(csv_path, abrev, proveedor_obj=sp.proveedor)
                    print(f"  CSV procesado OK")
                else:
                    print(f"  WARNING: sin abreviatura, no se proceso CSV")
            else:
                print(f"  WARNING: BDD vacia")
        except Exception as e:
            print(f"  ERROR recargando CSV: {e}")
            import traceback
            traceback.print_exc()

    # Regenerar archivos descargables
    print(f"  Generando archivos descargables...")
    try:
        spreadsheet = patoba.obtener_g_sheet_por_id(id_plantilla)
        patoba.actualizar_plantilla(spreadsheet, sp)
        print(f"  Descargables generados: {sp.link_descarga} | {sp.link_descarga_ods}")
    except Exception as e:
        print(f"  ERROR generando descargables: {e}")
        import traceback
        traceback.print_exc()

print("--- FIN ---")
