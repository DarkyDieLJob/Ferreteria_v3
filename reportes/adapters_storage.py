import os
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .ports import StoragePort
from .conf import REPORTES_MEDIA_SUBDIR


class DjangoStorageAdapter(StoragePort):
    def save(self, relative_path: str, data: bytes) -> str:
        rel = os.path.join(REPORTES_MEDIA_SUBDIR, relative_path)
        if default_storage.exists(rel):
            default_storage.delete(rel)
        default_storage.save(rel, ContentFile(data))
        return settings.MEDIA_URL.rstrip('/') + '/' + rel
