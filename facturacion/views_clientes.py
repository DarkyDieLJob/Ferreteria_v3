# -*- coding: utf-8 -*-
"""CRUD de Clientes para la app de facturación.

Incluye:
- Listado con filtros y paginación.
- Alta (página dedicada y endpoint JSON para alta rápida desde el buscador).
- Edición (página completa y fragmento para modal AJAX).
- Eliminación con reasignación de transacciones a un cliente destino.
"""
from __future__ import annotations

import json
import logging

from django.core.paginator import Paginator
from django.db import transaction as db_transaction
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import TemplateView

from .forms import ClienteFilterForm, ClienteForm, ClienteQuickForm
from .funtions import cliente_to_dict
from .models import Cliente, Transaccion

logger = logging.getLogger(__name__)

PAGE_SIZE_DEFAULT = 25
CONSUMIDOR_FINAL_ID = 1


def _is_ajax(request) -> bool:
    return request.headers.get("x-requested-with") == "XMLHttpRequest"


# ========================
# Listado
# ========================
class ClientesListView(TemplateView):
    """Listado de clientes con filtros, paginación y acciones."""

    template_name = "facturacion/clientes_list.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        request = self.request
        filter_form = ClienteFilterForm(request.GET or None)
        qs = Cliente.objects.all().order_by("razon_social")

        if filter_form.is_valid():
            q = filter_form.cleaned_data.get("q")
            cuit = filter_form.cleaned_data.get("cuit")
            iva = filter_form.cleaned_data.get("iva")
            tdoc = filter_form.cleaned_data.get("tdoc")
            if q:
                qs = qs.filter(razon_social__icontains=q)
            if cuit:
                qs = qs.filter(cuit_dni__icontains=cuit)
            if iva:
                qs = qs.filter(responsabilidad_iva=iva)
            if tdoc:
                qs = qs.filter(tipo_documento=tdoc)

        try:
            page_size = int(request.GET.get("page_size") or PAGE_SIZE_DEFAULT)
        except (TypeError, ValueError):
            page_size = PAGE_SIZE_DEFAULT
        page_size = max(5, min(page_size, 200))

        paginator = Paginator(qs, page_size)
        page_number = request.GET.get("page") or 1
        page_obj = paginator.get_page(page_number)

        # Mantener querystring sin 'page' para paginación
        qd = request.GET.copy()
        qd.pop("page", None)
        preserved_qs = qd.urlencode()

        ctx.update(
            {
                "filter_form": filter_form,
                "page_obj": page_obj,
                "paginator": paginator,
                "preserved_qs": preserved_qs,
                "page_size": page_size,
                "total_count": paginator.count,
            }
        )
        return ctx


# ========================
# Alta (página)
# ========================
class ClienteNuevoView(TemplateView):
    """Alta de cliente mediante página completa."""

    template_name = "facturacion/cliente_form_page.html"

    def get(self, request, *args, **kwargs):
        form = ClienteForm()
        return render(
            request,
            self.template_name,
            {"form": form, "titulo": "Nuevo cliente", "accion_label": "Crear"},
        )

    def post(self, request, *args, **kwargs):
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            logger.info("Cliente creado id=%s razon=%s", cliente.id, cliente.razon_social)
            return redirect(reverse("clientes-list"))
        return render(
            request,
            self.template_name,
            {"form": form, "titulo": "Nuevo cliente", "accion_label": "Crear"},
        )


# ========================
# Edición (página + modal)
# ========================
class ClienteEditarView(TemplateView):
    """Edita cliente. Si la request es AJAX devuelve el fragmento del form."""

    template_name = "facturacion/cliente_form_page.html"
    partial_template = "facturacion/partials/cliente_form.html"

    def get(self, request, id: int, *args, **kwargs):
        cliente = get_object_or_404(Cliente, pk=id)
        form = ClienteForm(instance=cliente)
        if _is_ajax(request):
            return render(
                request,
                self.partial_template,
                {
                    "form": form,
                    "cliente": cliente,
                    "action_url": reverse("clientes-editar", args=[cliente.id]),
                    "modo": "editar",
                },
            )
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "cliente": cliente,
                "titulo": f"Editar cliente: {cliente.razon_social}",
                "accion_label": "Guardar",
            },
        )

    def post(self, request, id: int, *args, **kwargs):
        cliente = get_object_or_404(Cliente, pk=id)
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save()
            logger.info("Cliente editado id=%s", cliente.id)
            if _is_ajax(request):
                return JsonResponse(
                    {"ok": True, "cliente": cliente_to_dict(cliente)}
                )
            return redirect(reverse("clientes-list"))
        if _is_ajax(request):
            html = render(
                request,
                self.partial_template,
                {
                    "form": form,
                    "cliente": cliente,
                    "action_url": reverse("clientes-editar", args=[cliente.id]),
                    "modo": "editar",
                },
            ).content.decode("utf-8")
            return JsonResponse({"ok": False, "html": html}, status=400)
        return render(
            request,
            self.template_name,
            {
                "form": form,
                "cliente": cliente,
                "titulo": f"Editar cliente: {cliente.razon_social}",
                "accion_label": "Guardar",
            },
        )


# ========================
# Eliminación con reasignación
# ========================
class ClienteEliminarView(TemplateView):
    """Elimina un cliente reasignando sus transacciones a un cliente destino."""

    template_name = "facturacion/partials/cliente_delete.html"

    def get(self, request, id: int, *args, **kwargs):
        cliente = get_object_or_404(Cliente, pk=id)
        transacciones_count = Transaccion.objects.filter(cliente=cliente).count()
        destinos = (
            Cliente.objects.exclude(pk=cliente.pk)
            .order_by("razon_social")
        )
        ctx = {
            "cliente": cliente,
            "transacciones_count": transacciones_count,
            "destinos": destinos,
            "default_destino_id": CONSUMIDOR_FINAL_ID,
            "action_url": reverse("clientes-eliminar", args=[cliente.id]),
        }
        return render(request, self.template_name, ctx)

    def post(self, request, id: int, *args, **kwargs):
        cliente = get_object_or_404(Cliente, pk=id)
        if cliente.pk == CONSUMIDOR_FINAL_ID:
            msg = "No se puede eliminar el cliente Consumidor Final (pk=1)."
            logger.warning(msg)
            if _is_ajax(request):
                return JsonResponse({"ok": False, "error": msg}, status=400)
            return HttpResponse(msg, status=400)

        destino_id = request.POST.get("destino_id") or CONSUMIDOR_FINAL_ID
        try:
            destino_id = int(destino_id)
        except (TypeError, ValueError):
            destino_id = CONSUMIDOR_FINAL_ID

        if destino_id == cliente.pk:
            msg = "El cliente destino no puede ser el mismo que se elimina."
            if _is_ajax(request):
                return JsonResponse({"ok": False, "error": msg}, status=400)
            return HttpResponse(msg, status=400)

        destino = get_object_or_404(Cliente, pk=destino_id)

        try:
            with db_transaction.atomic():
                reasignadas = Transaccion.objects.filter(cliente=cliente).update(
                    cliente=destino
                )
                cliente_repr = f"{cliente.razon_social} (id={cliente.pk})"
                cliente.delete()
                logger.info(
                    "Cliente eliminado %s. Transacciones reasignadas=%s destino=%s (id=%s)",
                    cliente_repr,
                    reasignadas,
                    destino.razon_social,
                    destino.pk,
                )
        except Exception as e:
            logger.error("Error eliminando cliente id=%s", id, exc_info=True)
            if _is_ajax(request):
                return JsonResponse({"ok": False, "error": str(e)}, status=500)
            return HttpResponse(f"Error: {e}", status=500)

        if _is_ajax(request):
            return JsonResponse(
                {
                    "ok": True,
                    "reasignadas": reasignadas,
                    "destino": cliente_to_dict(destino),
                }
            )
        return redirect(reverse("clientes-list"))


# ========================
# API: Alta rápida desde buscador
# ========================
@require_POST
def api_crear_cliente(request):
    """Crea un cliente desde el buscador y devuelve su representación JSON."""
    # Aceptamos tanto application/json como form-data
    if request.content_type and "application/json" in request.content_type:
        try:
            payload = json.loads(request.body or b"{}")
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "JSON inválido"}, status=400)
        form = ClienteQuickForm(payload)
    else:
        form = ClienteQuickForm(request.POST)

    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    cliente = form.save()
    logger.info("Cliente creado (quick) id=%s razon=%s", cliente.id, cliente.razon_social)
    return JsonResponse({"ok": True, "cliente": cliente_to_dict(cliente)}, status=201)
