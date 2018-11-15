from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
import pg_logger
import json

# Create your views here.
class GenerateTrace(APIView):
    """
    Vista para generar la traza de ejecución.

    * Requires token authentication.
    """
    #authentication_classes = (authentication.TokenAuthentication,)

    def post(self, request, format = None):
        """
        Ejecuta el código y retorna la traza de ejecución.
        """
        data = request.data
        user_script = data['script']
        raw_input_json = data['raw_input_json'] if 'raw_input_json' in data else None
        trace = pg_logger.exec_script_str_local(user_script, raw_input_json, False, False)
        return Response(trace)
