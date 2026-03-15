from abc import ABC, abstractmethod
from io import BytesIO
from typing import Dict
import pandas as pd


class DrivePort(ABC):
    @abstractmethod
    def download_file(self, file_id: str) -> BytesIO:
        ...

    @abstractmethod
    def upload_or_update(self, file_name: str, folder_id: str, data: bytes, mime: str) -> str:
        ...

    @abstractmethod
    def ensure_child_folder(self, parent_folder_id: str, child_name: str) -> str:
        """Ensure a subfolder exists under parent; return its ID."""
        ...

    @abstractmethod
    def list_folder(self, folder_id: str, page_size: int = 100) -> list:
        """List files (id, name, mimeType) in a Drive folder."""
        ...

    @abstractmethod
    def read_sheet_values(self, spreadsheet_id: str, tab_name: str) -> list:
        """Read values from a Google Sheet tab; returns list of rows (lists)."""
        ...

    @abstractmethod
    def find_child_folder_by_name(self, parent_folder_id: str, child_name: str) -> str | None:
        """Return folder ID if exists, else None."""
        ...

    @abstractmethod
    def find_folder_by_name(self, name: str) -> str | None:
        """Return first folder ID matching name (global search), else None."""
        ...


class StoragePort(ABC):
    @abstractmethod
    def save(self, relative_path: str, data: bytes) -> str:
        ...


class ExcelIO(ABC):
    @abstractmethod
    def read_all_sheets(self, stream: BytesIO) -> Dict[str, pd.DataFrame]:
        ...

    @abstractmethod
    def write_xlsx(self, sheets: Dict[str, pd.DataFrame]) -> BytesIO:
        ...

    @abstractmethod
    def write_ods(self, sheets: Dict[str, pd.DataFrame]) -> BytesIO:
        ...
