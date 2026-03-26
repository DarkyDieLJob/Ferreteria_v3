from datetime import date, datetime
from typing import Any
from django.http import JsonResponse, HttpResponse
from django.views import View
from django.utils.dateparse import parse_date
import csv

from .usecases_db import (
    get_last_completed_week,
    get_annual_monthly_summary,
    get_month_daily_summary,
    get_weekly_provider_item_breakdown,
    build_weekly_csv_rows,
)


class AnnualSummaryAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            year = int(request.GET.get("year") or date.today().year)
        except ValueError:
            year = date.today().year
        data = get_annual_monthly_summary(year)
        return JsonResponse({"year": year, "months": data})


class MonthlySummaryAPI(View):
    def get(self, request, *args, **kwargs):
        try:
            year = int(request.GET.get("year") or date.today().year)
            month = int(request.GET.get("month") or date.today().month)
        except ValueError:
            today = date.today()
            year, month = today.year, today.month
        data = get_month_daily_summary(year, month)
        return JsonResponse({"year": year, "month": month, "days": data})


class WeeklySnapshotAPI(View):
    def get(self, request, *args, **kwargs):
        # Params: week_start (YYYY-MM-DD) optional; if missing, last completed week
        ws_param = request.GET.get("week_start")
        if ws_param:
            ws = parse_date(ws_param)
            if not ws:
                return JsonResponse({"error": "Invalid week_start"}, status=400)
            # compute saturday from provided date's week
            from .usecases_db import get_week_bounds_for
            week_start, week_end = get_week_bounds_for(ws)
        else:
            week_start, week_end = get_last_completed_week(date.today())
        data = get_weekly_provider_item_breakdown(week_start, week_end)
        return JsonResponse({
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "rows": data,
        })


class WeeklySnapshotCSV(View):
    def get(self, request, *args, **kwargs):
        ws_param = request.GET.get("week_start")
        if ws_param:
            ws = parse_date(ws_param)
            if not ws:
                return JsonResponse({"error": "Invalid week_start"}, status=400)
            from .usecases_db import get_week_bounds_for
            week_start, week_end = get_week_bounds_for(ws)
        else:
            week_start, week_end = get_last_completed_week(date.today())

        rows = build_weekly_csv_rows(week_start, week_end)

        resp = HttpResponse(content_type='text/csv')
        resp['Content-Disposition'] = f'attachment; filename="ventas_semana_{week_start}_a_{week_end}.csv"'
        writer = csv.writer(resp)
        for row in rows:
            writer.writerow(row)
        return resp
