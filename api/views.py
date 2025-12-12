from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.throttling import UserRateThrottle
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from sgea_app.models import Evento
from .serializers import EventoSerializer, InscricaoSerializer


# Controle do número de requisições
class EventoThrottle(UserRateThrottle):
    scope = 'eventos'

class InscricaoThrottle(UserRateThrottle):
    scope = 'inscricoes'



# Endpoint de consulta à Lista de Eventos
class ListaEventosAPIView(generics.ListAPIView):
    queryset = Evento.objects.all()
    serializer_class = EventoSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [EventoThrottle]



# Endpoint de inscrição em eventos
class InscricaoAPIView(generics.CreateAPIView):
    serializer_class = InscricaoSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [InscricaoThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'mensagem': 'Inscrição realizada com sucesso!'}, status=status.HTTP_201_CREATED)



# Endpoint para login com token authentication
class LoginAPIView(ObtainAuthToken):
   
     def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'usuario_id': user.id,
            'usuario_nome': getattr(user, 'nome', str(user)),
            'mensagem': 'Login realizado com sucesso!'
        })