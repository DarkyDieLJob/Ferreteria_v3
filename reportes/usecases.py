from dataclasses import dataclass
from typing import Dict, List, Optional
import pandas as pd
import numpy as np

from .ports import DrivePort, StoragePort, ExcelIO
from .conf import REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID, REPORTES_OUTPUT_ROOT_NAME


@dataclass
class ReportRequest:
    file_bytes: Optional[bytes] = None
    drive_file_id: Optional[str] = None
    output_formats: List[str] = None  # e.g., ['xlsx'] or ['xlsx','ods']
    output_file_name: str = 'informe_diario.xlsx'
    # Drive organization
    output_parent_folder_id: Optional[str] = None
    output_subfolder_name: Optional[str] = None  # e.g., '2025'


@dataclass
class ReportResponse:
    media_urls: Dict[str, str]
    drive_file_ids: Dict[str, str]


class RunDailyReport:
    def __init__(self, drive: DrivePort, storage: StoragePort, excel: ExcelIO):
        self.drive = drive
        self.storage = storage
        self.excel = excel

    def execute(self, req: ReportRequest) -> ReportResponse:
        # 1) obtener stream de entrada
        if req.file_bytes:
            stream = bytes_to_stream(req.file_bytes)
        elif req.drive_file_id:
            stream = self.drive.download_file(req.drive_file_id)
        else:
            raise ValueError('Se requiere archivo subido o drive_file_id')

        # 2) leer todas las hojas (dict nombre->DataFrame)
        all_sheets = self.excel.read_all_sheets(stream)

        # 3) Emular notebook: procesar todas las hojas para extraer etiquetas/valores
        resultados_por_hoja: Dict[str, Dict[str, object]] = {}

        # Etiquetas a buscar (incluye variantes) y configuración de desplazamientos (#2 o #3 según tabla del usuario)
        encabezados_ods = [
            # Base de caja y totales
            'Z', 'N', 'DIFERENCIA', 'VENTA FINAL', 'VENTA BRUTA', 'GASTOS', 'TOTAL GRAL',
            'CAJA INICIAL', 'CAJA FINAL', 'CTA CTE', 'PAGO PROV', 'RETIROS', 'ANULACIONES', 'TARJETAS',
            # Medios de pago actuales
            'DEBITO', 'CREDITO', 'MAESTRO', 'MP', 'DNI', 'NETO TARJETA', 'NETO QR', 'APP EXTERNO',
            # Variantes anteriores usadas por el notebook previo
            'TOTAL TARJ. CRED', 'TOTAL VISA DEB', 'TOTAL MASTRO D', 'TOTAL MERCADO', 'TOTAL DNI',
        ]
        # Desplazamientos: por defecto #2; algunos son #3
        config_parametrizada = [
            {'nombres': ['NETO TARJETA', 'NETO QR'], 'offset': 3, 'nan_a_cero': True},
        ]
        config_default = {'offset': 2, 'nan_a_cero': False}

        for hoja, df in all_sheets.items():
            # 3.a) modificar primer 'GASTOS' a 'TABLA GASTOS' en primeras ~40 filas
            df_mod = _modificar_primer_gasto_df(df)
            # 3.b) renombrar valores específicos
            df_mod = _renombrar_valores_especificos_df(df_mod)
            # 3.c) extraer valores por encabezado con offsets
            resultados_por_hoja[hoja] = _buscar_valores_parametrizado(
                df_mod, encabezados_ods, config_parametrizada, config_default
            )

        # 4) Construir DataFrame final tal como notebook
        resultados_df = pd.DataFrame(resultados_por_hoja).T

        # GASTOS: None -> 0
        if 'GASTOS' in resultados_df.columns:
            resultados_df['GASTOS'] = resultados_df['GASTOS'].fillna(0)

        # Calcular columna 'Días' a partir del nombre de la hoja (día del mes), evitando conteo incremental
        resultados_df.index = resultados_df.index.astype(str)
        dias_series = resultados_df.index.map(_get_day_from_sheet_name)
        # Conservar solo filas donde pudimos extraer un día válido
        mask_valid_day = dias_series.notna()
        resultados_df = resultados_df[mask_valid_day].copy()
        resultados_df.insert(0, 'Días', dias_series[mask_valid_day].astype(int))

        # Convertir todo lo posible a numérico; luego fillna(0)
        resultados_df = resultados_df.apply(pd.to_numeric, errors='ignore')
        resultados_df = resultados_df.fillna(0)

        # Columnas derivadas / mapeos
        # 'B' = 'Z'
        if 'Z' in resultados_df.columns:
            resultados_df['B'] = resultados_df['Z']
        else:
            resultados_df['B'] = 0
        # 'D' = 'DIFERENCIA'
        if 'DIFERENCIA' in resultados_df.columns:
            resultados_df['D'] = resultados_df['DIFERENCIA']
        else:
            resultados_df['D'] = 0
        # 'TOTAL DIARIO' = 'VENTA BRUTA' (preferido), fallback 'VENTA FINAL'
        if 'VENTA BRUTA' in resultados_df.columns:
            resultados_df['TOTAL DIARIO'] = resultados_df['VENTA BRUTA']
        elif 'VENTA FINAL' in resultados_df.columns:
            resultados_df['TOTAL DIARIO'] = resultados_df['VENTA FINAL']
        else:
            resultados_df['TOTAL DIARIO'] = 0
        # '' columna vacía (separador)
        resultados_df[''] = ''
        # 'Tarjeta D' = solo DEBITO (Maestro queda como columna independiente). Fallback legacy: TOTAL VISA DEB
        tarjeta_d_actual = resultados_df.get('DEBITO', 0)
        tarjeta_d_legacy = resultados_df.get('TOTAL VISA DEB', 0)
        resultados_df['Tarjeta D'] = tarjeta_d_actual.where(tarjeta_d_actual != 0, tarjeta_d_legacy)
        # 'Tarjeta C' = CREDITO o fallback TOTAL TARJ. CRED
        resultados_df['Tarjeta C'] = resultados_df.get('CREDITO', resultados_df.get('TOTAL TARJ. CRED', 0))
        # 'Total MP' = MP o fallback TOTAL MERCADO
        resultados_df['Total MP'] = resultados_df.get('MP', resultados_df.get('TOTAL MERCADO', 0))
        # 'Total DNI' = DNI o fallback TOTAL DNI
        resultados_df['Total DNI'] = resultados_df.get('DNI', resultados_df.get('TOTAL DNI', 0))

        # Incluir MAESTRO como columna dedicada
        resultados_df['Maestro'] = resultados_df.get('MAESTRO', 0)

        # Porcentajes (evitar división por cero)
        denom = resultados_df['TOTAL DIARIO'].replace(0, np.nan)
        resultados_df['% Tarjeta D'] = (resultados_df['Tarjeta D'] / denom) * 100
        resultados_df['% Tarjeta C'] = (resultados_df['Tarjeta C'] / denom) * 100
        resultados_df['% MP'] = (resultados_df['Total MP'] / denom) * 100
        resultados_df['% DNI'] = (resultados_df['Total DNI'] / denom) * 100
        resultados_df['% Maestro'] = (resultados_df['Maestro'] / denom) * 100
        resultados_df[['% Tarjeta D', '% Tarjeta C', '% MP', '% DNI']] = (
            resultados_df[['% Tarjeta D', '% Tarjeta C', '% MP', '% DNI']].fillna(0)
        )
        resultados_df['% Maestro'] = resultados_df['% Maestro'].fillna(0)

        # Ajustar GASTOS para contemplar pago a proveedores
        if 'PAGO PROV' in resultados_df.columns:
            resultados_df['GASTOS'] = resultados_df.get('GASTOS', 0) + resultados_df.get('PAGO PROV', 0)

        # Ordenar por día
        resultados_df = resultados_df.sort_values(by='Días')

        # Agregar contador de días trabajados (1..n) junto a 'Días'
        resultados_df.insert(1, 'Días trabajados', range(1, len(resultados_df) + 1))

        # Agregar columna de App Externa (valor)
        resultados_df['Ap Ex'] = resultados_df.get('APP EXTERNO', 0)

        # Reordenar columnas exactamente como el notebook, con nuevas columnas solicitadas
        columnas_finales = [
            'Días', 'Días trabajados', 'B', 'N', 'D', '', 'TOTAL DIARIO', 'Tarjeta D', 'Tarjeta C',
            'Total MP', 'Total DNI', 'Maestro', '% Tarjeta D', '% Tarjeta C', '% MP', '% DNI', '% Maestro', 'GASTOS', 'Ap Ex'
        ]
        # Asegurar existencia
        for c in columnas_finales:
            if c not in resultados_df.columns:
                resultados_df[c] = 0 if c not in {'',} else ''
        resultados_df = resultados_df[columnas_finales]

        # Calcular fila final 'TOTALES'
        dias_trabajados = resultados_df['Días trabajados'].iloc[-1] if not resultados_df.empty else 0
        suma_columnas = resultados_df.select_dtypes(include=np.number).drop(columns=['Días'], errors='ignore').sum()
        ultima_fila = pd.Series({col: suma_columnas.get(col, 0) for col in suma_columnas.index})
        ultima_fila.name = 'TOTALES'
        # 'Días' mantiene el último día del mes, 'Días trabajados' muestra el conteo final
        ultima_fila['Días trabajados'] = dias_trabajados
        # Mantener columna separadora vacía
        ultima_fila[''] = ''
        resultados_df = pd.concat([resultados_df, pd.DataFrame(ultima_fila).T], ignore_index=False)

        # Redondear porcentajes a 2 decimales (incluye la fila de totales)
        percent_cols = ['% Tarjeta D', '% Tarjeta C', '% MP', '% DNI', '% Maestro']
        for col in percent_cols:
            if col in resultados_df.columns:
                resultados_df[col] = pd.to_numeric(resultados_df[col], errors='coerce').round(2).fillna(0)

        # 5) Preparar salida: solo una hoja con el informe final
        report_sheets = {'InformeGastosMensual': resultados_df}

        media_urls = {}
        drive_ids = {}
        base = req.output_file_name.rsplit('.', 1)[0]
        if not req.output_formats:
            req.output_formats = ['xlsx']

        # Determinar carpeta destino en Drive
        # Estructura deseada: Informes Ferreteria / Informes Finales / <Año opcional>
        target_parent = req.output_parent_folder_id or REPORTES_DEFAULT_OUTPUT_DRIVE_FOLDER_ID
        output_root_name = REPORTES_OUTPUT_ROOT_NAME or 'Informes Finales'
        output_root_folder = self.drive.ensure_child_folder(target_parent, output_root_name)
        target_folder = output_root_folder
        if req.output_subfolder_name:
            target_folder = self.drive.ensure_child_folder(output_root_folder, req.output_subfolder_name)

        for fmt in req.output_formats:
            if fmt == 'xlsx':
                out = self.excel.write_xlsx(report_sheets)
                file_name = f"{base}.xlsx"
                drive_ids['xlsx'] = self.drive.upload_or_update(
                    file_name=file_name,
                    folder_id=target_folder,
                    data=out.getvalue(),
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                )
                media_urls['xlsx'] = f"https://drive.google.com/file/d/{drive_ids['xlsx']}/view"
            elif fmt == 'ods':
                out = self.excel.write_ods(report_sheets)
                file_name = f"{base}.ods"
                drive_ids['ods'] = self.drive.upload_or_update(
                    file_name=file_name,
                    folder_id=target_folder,
                    data=out.getvalue(),
                    mime='application/vnd.oasis.opendocument.spreadsheet',
                )
                media_urls['ods'] = f"https://drive.google.com/file/d/{drive_ids['ods']}/view"
            else:
                continue

        return ReportResponse(media_urls=media_urls, drive_file_ids=drive_ids)


def bytes_to_stream(b: bytes):
    import io
    s = io.BytesIO(b)
    s.seek(0)
    return s


def _modificar_primer_gasto_df(df: pd.DataFrame) -> pd.DataFrame:
    # Copia para no mutar original
    d = df.copy()
    max_filas = min(40, len(d))
    try:
        for fila in range(max_filas):
            for columna in range(len(d.columns)):
                if d.iloc[fila, columna] == 'GASTOS':
                    d.iloc[fila, columna] = 'TABLA GASTOS'
                    return d
    except Exception:
        pass
    return d


def _renombrar_valores_especificos_df(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    reemplazos = {
        'TOTAL TARJ. CREDITO': 'TOTAL TARJ. CRED',
        'total dni': 'TOTAL DNI',
        'TOTAL DURACRIL': 'TOTAL DNI',
        'TOTAL MASTRO DEBITO': 'TOTAL MASTRO D',
    }
    try:
        # Recorremos el array para localizar y reemplazar
        arr = d.values
        for buscar, reemplazar in reemplazos.items():
            filas, columnas = np.where(arr == buscar)
            for f, c in zip(filas, columnas):
                if d.iloc[f, c] == buscar:
                    d.iloc[f, c] = reemplazar
    except Exception:
        pass
    return d


def _buscar_valores_parametrizado(
    df: pd.DataFrame,
    encabezados_a_buscar: List[str],
    config_desplazamientos: List[Dict[str, object]],
    default_config: Dict[str, object],
) -> Dict[str, object]:
    resultados: Dict[str, object] = {}
    try:
        arr = df.to_numpy()
    except Exception:
        arr = df.values
    # También una vista normalizada para matching más robusto (mayúsculas, sin acentos, trim)
    norm_df = df.applymap(_normalize_str_cell)
    try:
        norm_arr = norm_df.to_numpy()
    except Exception:
        norm_arr = norm_df.values

    for encabezado in encabezados_a_buscar:
        valor_encontrado = None
        try:
            filas, columnas = np.where(arr == encabezado)
            # Si no hay match exacto, intentar por normalización
            if len(filas) == 0:
                target = _normalize_str(encabezado)
                filas, columnas = np.where(norm_arr == target)
            if len(filas) > 0:
                fila = filas[0]
                columna = columnas[0]
                # Determinar config específica o default
                offset_actual = default_config.get('offset', 1)
                convertir_nan = default_config.get('nan_a_cero', False)
                for grupo in config_desplazamientos:
                    if encabezado in grupo.get('nombres', []):
                        offset_actual = grupo.get('offset', offset_actual)
                        convertir_nan = grupo.get('nan_a_cero', convertir_nan)
                        break
                col_valor = columna + offset_actual
                if col_valor < df.shape[1]:
                    valor_celda = df.iloc[fila, col_valor]
                    if convertir_nan and pd.isna(valor_celda):
                        valor_encontrado = 0
                    else:
                        # Intentar parseos similares al notebook para montos
                        valor_encontrado = _try_parse_number(valor_celda)
                else:
                    valor_encontrado = None
            else:
                valor_encontrado = None
        except Exception:
            valor_encontrado = None
        resultados[encabezado] = valor_encontrado
    return resultados


def _try_parse_number(v):
    # Igualar limpieza del notebook: quitar $, miles '.', decimales ','
    try:
        if v is None:
            return None
        s = str(v).strip()
        if s == '':
            return None
        # Normalizar espacios (incluye NBSP)
        s = s.replace('\xa0', ' ').replace(' ', '')
        s = s.replace('$', '')
        if ',' in s:
            # Formato español: '.' miles, ',' decimales
            s = s.replace('.', '')
            s = s.replace(',', '.')
        else:
            # Sin coma: asumir '.' ya es decimal, no tocar
            pass
        return float(s)
    except Exception:
        try:
            return float(v)
        except Exception:
            return v


def _normalize_str_cell(v):
    try:
        if pd.isna(v):
            return v
        return _normalize_str(str(v))
    except Exception:
        return v


def _normalize_str(s: str) -> str:
    try:
        import unicodedata, re
        s2 = unicodedata.normalize('NFKD', s)
        s2 = ''.join(c for c in s2 if not unicodedata.combining(c))
        s2 = s2.strip().upper()
        s2 = re.sub(r"\s+", " ", s2)
        return s2
    except Exception:
        return s.strip().upper() if isinstance(s, str) else s


def _get_day_from_sheet_name(name: str):
    """Extrae el día del mes a partir del nombre de la hoja.
    Acepta formatos comunes como '2-1', '02-01', '2/1', '2-01', '02/1'.
    Retorna int día (1-31) o None si no se puede parsear.
    """
    try:
        s = (name or '').strip()
        if not s:
            return None
        # Normalizar separadores
        s = s.replace('\u2011', '-').replace('\u2013', '-').replace('\u2014', '-').replace('_', '-')
        if '/' in s:
            parts = s.split('/')
        elif '-' in s:
            parts = s.split('-')
        else:
            return None
        # Tomar primer componente como día
        day_str = parts[0].strip()
        if not day_str:
            return None
        day = int(day_str)
        if 1 <= day <= 31:
            return day
        return None
    except Exception:
        return None
