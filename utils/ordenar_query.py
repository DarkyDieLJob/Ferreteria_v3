from django.db.models import QuerySet

def agrupar_transacciones_por_fecha(queryset: QuerySet) -> dict:

    datos = {}

    for dato in queryset:
        año = dato.fecha.year
        mes = dato.fecha.month
        dia = dato.fecha.day

        if año not in datos:
            datos[año] = {}
        if mes not in datos[año]:
            datos[año][mes] = {}
        if dia not in datos[año][mes]:
            datos[año][mes][dia] = []
        datos[año][mes][dia].append(dato)


    return datos