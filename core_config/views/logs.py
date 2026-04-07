import logging
import os
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

from django import forms
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, Http404
from django.shortcuts import render
from django.utils import timezone as tz

logger = logging.getLogger(__name__)


class LogDownloadForm(forms.Form):
    apps = forms.MultipleChoiceField(choices=[], widget=forms.CheckboxSelectMultiple)
    from_date = forms.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )
    to_date = forms.DateTimeField(
        required=True,
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M"],
        widget=forms.DateTimeInput(format="%Y-%m-%dT%H:%M", attrs={"type": "datetime-local"}),
    )
    include_rotated = forms.BooleanField(required=False, initial=True)
    include_info = forms.BooleanField(required=False, initial=True)
    include_error = forms.BooleanField(required=False, initial=True)
    max_size_mb = forms.IntegerField(min_value=1, max_value=500, initial=100)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apps = getattr(settings, "APPS_TO_LOG", [])
        # Mostramos todas las apps configuradas, aunque aún no exista la carpeta; más tarde se valida por existencia
        self.fields["apps"].choices = [(a, a) for a in sorted(apps)]


@staff_member_required
def download_logs(request):
    # Feature flag opcional: por defecto deshabilitado si no está definido en settings
    if not getattr(settings, "ENABLE_LOG_DOWNLOAD", False):
        raise Http404()

    if request.method == "GET":
        # Prepopular últimos 24h (timezone-aware)
        now = tz.localtime(tz.now()).replace(second=0, microsecond=0)
        defaults = {
            "from_date": now - timedelta(days=1),
            "to_date": now,
        }
        form = LogDownloadForm(initial=defaults)
        return render(request, "core_config/logs_download.html", {"form": form})

    form = LogDownloadForm(request.POST)
    if not form.is_valid():
        return render(request, "core_config/logs_download.html", {"form": form})

    apps = form.cleaned_data["apps"]
    from_dt = form.cleaned_data["from_date"]
    to_dt = form.cleaned_data["to_date"]
    # Asegurar timezone-aware para comparaciones
    cur_tz = tz.get_current_timezone()
    if tz.is_naive(from_dt):
        from_dt = tz.make_aware(from_dt, cur_tz)
    if tz.is_naive(to_dt):
        to_dt = tz.make_aware(to_dt, cur_tz)
    include_rotated = form.cleaned_data["include_rotated"]
    include_info = form.cleaned_data["include_info"]
    include_error = form.cleaned_data["include_error"]
    max_size = form.cleaned_data["max_size_mb"] * 1024 * 1024

    # Fallback: si el usuario desmarca ambas por error, por defecto tomamos INFO
    if not include_info and not include_error:
        include_info = True

    if not apps:
        return render(
            request,
            "core_config/logs_download.html",
            {"form": form, "message": "Seleccioná al menos una app."},
        )

    logs_root = Path(settings.BASE_DIR) / "logs"

    # Construir patrones
    patterns = []
    if include_info:
        patterns += ["info.log"]
        if include_rotated:
            patterns += ["info.log.*"]
    if include_error:
        patterns += ["error.log"]
        if include_rotated:
            patterns += ["error.log.*"]

    # Candidatos y filtrado por mtime
    candidates = []
    for app in apps:
        app_dir = (logs_root / app).resolve()
        # Validación de path para evitar traversal
        if logs_root.resolve() not in app_dir.parents and logs_root.resolve() != app_dir:
            continue
        for pat in patterns:
            for p in app_dir.glob(pat):
                candidates.append((app, p))

    files = []
    for app, p in candidates:
        try:
            mtime = datetime.fromtimestamp(p.stat().st_mtime, tz=cur_tz)
            if from_dt <= mtime <= to_dt and p.is_file():
                files.append((app, p))
        except Exception:
            logger.warning(f"No se pudo leer metadata del archivo: {p}")

    if not files:
        logger.debug(
            f"[logs_download] sin archivos: apps={apps} patterns={patterns} rango=({from_dt}..{to_dt}) include_rotated={include_rotated} candidates={len(candidates)}"
        )
        return render(
            request,
            "core_config/logs_download.html",
            {"form": form, "message": "No hay archivos para el rango dado."},
        )

    # Crear ZIP temporal con límite de tamaño agregado
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=f"-logs.zip")
    tmp.close()
    total_written = 0
    skipped = []

    try:
        with zipfile.ZipFile(tmp.name, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for app, f in sorted(files, key=lambda t: (t[0], t[1].name)):
                try:
                    size = f.stat().st_size
                    if total_written + size > max_size:
                        skipped.append(f"{app}/{f.name}")
                        continue
                    zf.write(f, arcname=f"{app}/{f.name}")
                    total_written += size
                except Exception as e:
                    logger.warning(f"No se pudo agregar {f} al ZIP: {e}")

            if skipped:
                zf.writestr("_SKIPPED.txt", "Omitidos por límite de tamaño:\n" + "\n".join(skipped))

        logger.info(
            f"[logs_download] user={request.user} apps={apps} files={len(files)} written={total_written} skipped={len(skipped)}"
        )
        filename = f"logs-{len(apps)}apps-{from_dt:%Y%m%d%H%M}-{to_dt:%Y%m%d%H%M}.zip"
        resp = FileResponse(
            open(tmp.name, "rb"),
            as_attachment=True,
            filename=filename,
            content_type="application/zip",
        )

        # Limpieza del temporal al cerrar la respuesta
        def _cleanup(orig_close, file_path):
            def _inner():
                try:
                    orig_close()
                finally:
                    try:
                        os.remove(file_path)
                    except Exception:
                        logger.warning(f"No se pudo borrar temporal: {file_path}")
            return _inner

        resp.close = _cleanup(resp.close, tmp.name)
        return resp
    except Exception as e:
        logger.error(f"Error generando ZIP de logs: {e}", exc_info=True)
        try:
            os.remove(tmp.name)
        except Exception:
            pass
        return render(
            request,
            "core_config/logs_download.html",
            {"form": form, "message": "Error generando el ZIP. Reintente más tarde."},
        )
