from rest_framework import serializers
from sgea_app.models import Evento, Usuario, Inscricao

class EventoSerializer(serializers.ModelSerializer):
    organizador_nome = serializers.CharField(source='organizador.nome', read_only=True)

    class Meta:
        model = Evento
        fields = [
            'id',
            'nome',
            'local',
            'data_inicial',
            'organizador_nome'
        ]


class InscricaoSerializer(serializers.Serializer):
    usuario_nome = serializers.CharField()
    evento_nome = serializers.CharField()

    def validate(self, data):
        usuario_nome = data.get('usuario_nome')
        evento_nome = data.get('evento_nome')

        # Verificar se o usuário e o evento existem
        try:
            usuario = Usuario.objects.get(nome__iexact=usuario_nome)
        except Usuario.DoesNotExist:
            raise serializers.ValidationError({'usuario_nome': 'Usuário não encontrado.'})

        try:
            evento = Evento.objects.get(nome__iexact=evento_nome)
        except Evento.DoesNotExist:
            raise serializers.ValidationError({'evento_nome': 'Evento não encontrado.'})

        # Verificar duplicidade de inscrição
        if Inscricao.objects.filter(usuario=usuario, evento=evento).exists():
            raise serializers.ValidationError({'detalhe': 'Usuário já inscrito neste evento.'})

        # Adiciona instâncias para uso no create()
        data['usuario'] = usuario
        data['evento'] = evento
        return data

    def create(self, validated_data):
        return Inscricao.objects.create(
            usuario=validated_data['usuario'],
            evento=validated_data['evento']
        )