from io import BytesIO
from typing import Dict
import pandas as pd

from .ports import ExcelIO


class PandasExcelIO(ExcelIO):
    def read_all_sheets(self, stream: BytesIO) -> Dict[str, pd.DataFrame]:
        stream.seek(0)
        xls = pd.read_excel(stream, sheet_name=None, engine=None)  # pandas auto-detects
        # Ensure no NaNs
        return {k: v.fillna("") for k, v in xls.items()}

    def write_xlsx(self, sheets: Dict[str, pd.DataFrame]) -> BytesIO:
        out = BytesIO()
        with pd.ExcelWriter(out, engine='openpyxl') as writer:
            for name, df in sheets.items():
                df.to_excel(writer, sheet_name=name[:31] or 'Hoja1', index=False)
        out.seek(0)
        return out

    def write_ods(self, sheets: Dict[str, pd.DataFrame]) -> BytesIO:
        out = BytesIO()
        with pd.ExcelWriter(out, engine='odf') as writer:
            for name, df in sheets.items():
                df.to_excel(writer, sheet_name=name[:31] or 'Hoja1', index=False)
        out.seek(0)
        return out
