from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Estufa

class EstufaCreateView(APIView):
    def post(self, request):
        nome = request.data.get("nome")
        observacoes = request.data.get("observacoes")

        if not nome:
            return Response({"error": "Nome é obrigatório"}, status=400)

        estufa = Estufa.objects.create(
            nome=nome,
            observacoes=observacoes,
            usuario=request.user  # depois vamos garantir login
        )

        return Response({"message": "Estufa criada com sucesso"})