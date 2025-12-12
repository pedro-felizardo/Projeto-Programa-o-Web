from django.urls import path
from .views import ListaEventosAPIView, InscricaoAPIView, LoginAPIView

urlpatterns = [
    path('eventos/', ListaEventosAPIView.as_view(), name='api_eventos'), # URL para o endpoint que consulta a lista de eventos
    path('inscricoes/', InscricaoAPIView.as_view(), name='api_inscricoes'), # URL para o endpoint que realiza a inscrição em eventos
    path('login/', LoginAPIView.as_view(), name='api_login'), # URL para o endpoint de autenticação via login
]


