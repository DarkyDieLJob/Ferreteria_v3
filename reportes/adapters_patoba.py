import io
from typing import Dict
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from bdd.classes import Patoba
from .ports import DrivePort


class PatobaDriveAdapter(DrivePort):
    def __init__(self, request=None) -> None:
        self._patoba = Patoba(request)
        self._drive = self._patoba.drive_service

    def download_file(self, file_id: str) -> io.BytesIO:
        request = self._drive.files().get_media(fileId=file_id)
        buf = io.BytesIO()
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        buf.seek(0)
        return buf

    def upload_or_update(self, file_name: str, folder_id: str, data: bytes, mime: str) -> str:
        # Check existing
        query = f"name='{file_name}' and '{folder_id}' in parents and trashed=false"
        results = self._drive.files().list(q=query, fields='files(id)').execute()
        files = results.get('files', [])

        media = MediaIoBaseUpload(io.BytesIO(data), mimetype=mime, resumable=True)
        if files:
            file_id = files[0]['id']
            file = self._drive.files().update(fileId=file_id, media_body=media).execute()
            return file.get('id')
        else:
            file_metadata = {'name': file_name, 'parents': [folder_id]}
            file = self._drive.files().create(body=file_metadata, media_body=media).execute()
            return file.get('id')

    def ensure_child_folder(self, parent_folder_id: str, child_name: str) -> str:
        query = (
            f"name='{child_name}' and '{parent_folder_id}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and trashed=false"
        )
        results = self._drive.files().list(q=query, fields='files(id,name)').execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
        metadata = {
            'name': child_name,
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [parent_folder_id],
        }
        folder = self._drive.files().create(body=metadata, fields='id').execute()
        return folder.get('id')

    def list_folder(self, folder_id: str, page_size: int = 100) -> list:
        query = f"'{folder_id}' in parents and trashed=false"
        res = self._drive.files().list(
            q=query,
            pageSize=page_size,
            orderBy='modifiedTime desc',
            fields='files(id,name,mimeType,modifiedTime)'
        ).execute()
        return res.get('files', [])

    def read_sheet_values(self, spreadsheet_id: str, tab_name: str) -> list:
        rng = f"{tab_name}!A:Z"
        vals = self._patoba.sheet_service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=rng
        ).execute()
        return vals.get('values', [])

    def find_child_folder_by_name(self, parent_folder_id: str, child_name: str) -> str | None:
        query = (
            f"name='{child_name}' and '{parent_folder_id}' in parents and "
            "mimeType='application/vnd.google-apps.folder' and trashed=false"
        )
        results = self._drive.files().list(q=query, fields='files(id,name)').execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None

    def find_folder_by_name(self, name: str) -> str | None:
        query = (
            f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        )
        results = self._drive.files().list(q=query, fields='files(id,name)').execute()
        files = results.get('files', [])
        return files[0]['id'] if files else None
