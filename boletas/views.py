from django.http import JsonResponse
from .models import Boleta
from django.views.decorators.csrf import csrf_exempt
import json
from django.views import View
from django.utils.decorators import method_decorator

@method_decorator(csrf_exempt, name='dispatch')
class BoletasView(View):

    def get(self, request, *args, **kwargs):
        boletas = Boleta.objects.filter(impreso=False)
        data = {"boletas": []}
        for boleta in boletas:
            comandos = boleta.comandos.through.objects.filter(boleta=boleta).order_by('orden')
            comandos_list = list(comandos.values('comando__comando'))
            comandos_str = [comando['comando__comando'] for comando in comandos_list]
            data["boletas"].append({
                "id_boleta": boleta.id,
                "tipo": boleta.tipo,
                "comandos": comandos_str
            })
        return JsonResponse(data)

    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        status = data.get('status')
        id_boleta = int(data.get('id_boleta'))
        boleta = Boleta.objects.get(id=id_boleta)
        if status == '2':
            # Actualiza el estado de la boleta para deshabilitarla
            # ...
            boleta.impreso = True
            boleta.save()
            pass

        return JsonResponse({})