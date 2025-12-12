from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone
import re # Usado para validação de formato (Regex)
from .models import *

# Obtém o modelo de usuário customizado (sgea_app.Usuario)
Usuario = get_user_model()

class CadastroUsuarioForm(forms.ModelForm):
    """
    Formulário para o cadastro de novos usuários, aplicando as regras de negócio
    para senha e telefone.
    """
    
    # Campo de confirmação de senha (não faz parte do modelo, mas é exigido no formulário) 
    senha_confirmacao = forms.CharField(
        widget=forms.PasswordInput, 
        label="Confirmação de Senha",
        help_text="Repita a senha para confirmação."
    )
    
    email = forms.EmailField(
        label="E-mail de Contato",
        help_text="Informe um e-mail válido para receber o link de confirmação."
    )

    class Meta:
        model = Usuario
        fields = ['nome', 'telefone', 'instituicao_ensino','email' ,'login', 'perfil', 'password']
        # Mapeamos 'password' no formulário para 'senha' no modelo customizado.
        # No seu modelo, o campo se chama 'login', mas o Django usa o campo
        # definido como USERNAME_FIELD para o nome do login.
        widgets = {
            'password': forms.PasswordInput,
        }
        labels = {
            'login': 'E-mail (Login)',
            'password': 'Senha',
            'instituicao_ensino': 'Instituição de Ensino',
        }

    def clean_telefone(self):
        """
        Validação do campo Telefone. 
        Requisito: Formato (XX) XXXXX-XXXX.
        """
        telefone = self.cleaned_data.get('telefone')
        # Regex para validar o formato (XX) XXXXX-XXXX
        # Nota: O front-end usará máscara, mas o backend deve validar.
        padrao_telefone = r'^\(\d{2}\) \d{4,5}-\d{4}$'
        
        if not re.match(padrao_telefone, telefone):
            raise ValidationError(
                "O telefone deve estar no formato (XX) XXXX-XXXX ou (XX) XXXXX-XXXX."
            )
        return telefone

    def clean_password(self):
        """
        Validação do campo Senha.
        Requisito: Mínimo 8 caracteres, contendo letras, números e caracteres especiais.
        """
        senha = self.cleaned_data.get('password')

        if len(senha) < 8:
            raise ValidationError("A senha deve ter no mínimo 8 caracteres.")
        if not re.search(r'[a-zA-Z]', senha):
            raise ValidationError("A senha deve conter letras.")
        if not re.search(r'\d', senha):
            raise ValidationError("A senha deve conter números.")
        if not re.search(r'[^a-zA-Z0-9]', senha):
            raise ValidationError("A senha deve conter caracteres especiais.")
        
        return senha

    def clean(self):
        """
        Validação de consistência entre senha e confirmação de senha.
        """
        cleaned_data = super().clean()
        senha = cleaned_data.get("password")
        senha_confirmacao = cleaned_data.get("senha_confirmacao")

        # Verifica se ambas as senhas foram preenchidas e se são diferentes
        if senha and senha_confirmacao and senha != senha_confirmacao:
            raise ValidationError(
                "As senhas informadas não coincidem."
            )

        # Regra de Negócio: Instituição de Ensino obrigatória para Aluno/Professor
        perfil = cleaned_data.get('perfil')
        instituicao = cleaned_data.get('instituicao_ensino')
        
        if perfil in ['Aluno', 'Professor'] and not instituicao:
            raise ValidationError(
                "A Instituição de Ensino é obrigatória para perfis Aluno e Professor."
            )
            
        return cleaned_data
        
    def save(self, commit=True):
        """
        Sobrescreve o método save para usar o create_user do Manager
        e garantir que a senha seja hasheada.
        """
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
        
        # Configura a senha corretamente, hasheando-a
        user.set_password(password) 
        
        # Salvando o e-mail
        user.email = self.cleaned_data["email"]

        # O campo 'login' do seu modelo é o USERNAME_FIELD
        user.login = self.cleaned_data["login"]
        
        user.is_active = True

        if commit:
            # Salva o usuário customizado
            user.save() 
        return user


class FormularioEvento(forms.ModelForm):
    """
    Formulário para a criação de novos eventos.
    Aplica validações de data e professor responsável.
    """
    class Meta:
        model = Evento
        # 'banner' e 'nome' não estavam no diagrama, mas foram adicionados no modelo.
        # Organizador e Professor Responsável serão definidos pela lógica da view/validação.
        fields = [
            'nome', 'tipo_evento', 'data_inicial', 'data_final', 'horario', 
            'local', 'quantidade_participantes', 'professor_responsavel', 'banner'
        ]
        
        # Requisito de validação avançada: usar seletor de data e hora (datepicker/timepicker)[cite: 8].
        # Aqui, usamos widgets para aprimorar a UX, mas o front-end precisará de JS/jQuery.
        widgets = {
            'data_inicial': forms.DateInput(attrs={'type': 'date'}),
            'data_final': forms.DateInput(attrs={'type': 'date'}),
            'horario': forms.TextInput(attrs={'placeholder': 'Ex: 14:00'}),
            # Professor Responsável será um dropdown filtrado
            'professor_responsavel': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'professor_responsavel': 'Professor Responsável',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtra o campo 'professor_responsavel' para mostrar apenas usuários com perfil 'Professor'.
        professores = Usuario.objects.filter(perfil='Professor')
        self.fields['professor_responsavel'].queryset = professores

    def clean_data_inicial(self):
        """
        Regra de Negócio: Não será permitido o cadastro de eventos com data de início 
        anterior à data atual.
        """
        data_inicial = self.cleaned_data.get('data_inicial')
        
        # Compara a data inicial com a data de hoje (apenas a data)
        if data_inicial and data_inicial < timezone.now().date():
            raise ValidationError(
                "A data de início do evento não pode ser anterior à data atual."
            )
        return data_inicial
        
    def clean(self):
        """
        Validação de consistência entre datas.
        """
        cleaned_data = super().clean()
        data_inicial = cleaned_data.get("data_inicial")
        data_final = cleaned_data.get("data_final")

        if data_inicial and data_final and data_final < data_inicial:
            raise ValidationError(
                "A data final do evento não pode ser anterior à data inicial."
            )
            
        return cleaned_data