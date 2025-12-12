from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UsuarioManager 
from django.utils import timezone

class Usuario(AbstractBaseUser, PermissionsMixin):
    """
    Modelo customizado para o usuário, herdando de AbstractBaseUser para gerenciar
    a autenticação e PermissionsMixin para permissões (is_staff, is_superuser).
    """
    PERFIL_CHOICES = [
        ('Aluno', 'Aluno'),
        ('Professor', 'Professor'),
        ('Organizador', 'Organizador'),
    ]

    # Campos do seu projeto (PK e campos obrigatórios)
    nome = models.CharField(max_length=50, verbose_name="Nome Completo")
    telefone = models.CharField(max_length=50, verbose_name="Telefone")
    instituicao_ensino = models.CharField(max_length=50, verbose_name="Instituição de Ensino")
    
    # Campos para o envio do e-mail
    email = models.EmailField(max_length=255, unique=True, verbose_name="E-mail")

    # Campo usado para login. O Django cuidará do hashing da senha (campo 'password' ou 'senha' se renomeado)
    login = models.CharField(max_length=50, unique=True, verbose_name="Login (E-mail)") 
    perfil = models.CharField(max_length=50, choices=PERFIL_CHOICES, default='Aluno', verbose_name="Perfil")
    
    # Campos de estado do Django
    is_active = models.BooleanField(default=False, verbose_name="Ativo") # Novo usuário só pode acessar após confirmação (link ou código) [cite: 97]
    is_staff = models.BooleanField(default=False) # Permissão para acessar o /admin
    
    # Configurações obrigatórias para AbstractBaseUser
    objects = UsuarioManager()
    
    USERNAME_FIELD = 'login' # Campo usado como identificador de login
    REQUIRED_FIELDS = ['nome', 'telefone', 'instituicao_ensino', 'email'] # Campos obrigatórios para criar superusuário na linha de comando
    
    class Meta:
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"

    def __str__(self):
        return self.nome
        
        
class Evento(models.Model):
    """
    Modelo para armazenar informações sobre eventos acadêmicos.
    """
    TIPO_EVENTO_CHOICES = [
        ('Palestra', 'Palestra'),
        ('Seminário', 'Seminário'),
        ('Minicurso', 'Minicurso'),
        ('Semana Acadêmica', 'Semana Acadêmica'),
        # ... outros tipos
    ]
    
    # Chaves Estrangeiras (FKs):
    # organizador_id é o usuário que criou o evento (Organizador)
    organizador = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='eventos_organizados', verbose_name="Organizador Responsável")
    
    # [cite_start]professor_responsavel_id (adicionado pela Regra de Negócio: Todo evento deverá ter um professor responsável vinculado [cite: 44])
    professor_responsavel = models.ForeignKey(Usuario, on_delete=models.PROTECT, related_name='eventos_professor', verbose_name="Professor Responsável")

    # Campos de dados do Evento:
    tipo_evento = models.CharField(max_length=50, choices=TIPO_EVENTO_CHOICES, verbose_name="Tipo de Evento")
    data_inicial = models.DateField(verbose_name="Data de Início") # Regra de Negócio: Não será permitido o cadastro com data de início anterior à data atual[cite: 43].
    data_final = models.DateField(verbose_name="Data de Fim")
    horario = models.CharField(max_length=50, verbose_name="Horário")
    local = models.CharField(max_length=50, verbose_name="Local")
    
    # [cite_start]Requisito de Banner[cite: 34]:
    # Usamos ImageField para lidar com o upload e validação de imagem.
    banner = models.ImageField(upload_to='eventos/banners/', null=True, blank=True, verbose_name="Banner do Evento")
    
    # [cite_start]Quantidade de Participantes é o limite de vagas[cite: 92].
    quantidade_participantes = models.IntegerField(verbose_name="Limite de Participantes")

    # Requisito 'nome' do Evento não está no diagrama, mas é crucial.
    nome = models.CharField(max_length=100, verbose_name="Nome do Evento", default='Novo Evento') 

    class Meta:
        verbose_name = "Evento"
        verbose_name_plural = "Eventos"

    def esta_encerrado(self):
        """ Verifica se a data final do evento já passou. """
        return self.data_final < timezone.now().date()
        
    def status_certificado(self):
        """ Determina o status dos certificados baseado na data final. """
        if not self.esta_encerrado():
            return 'Pendente (Evento Ativo)'
        
        # O certificado é gerado após a data de término.
        # Se o evento está encerrado, o status é "Pronto para Emissão".
        # Uma lógica mais robusta checaria se a automação já rodou.
        return 'Pronto para Emissão'

    def __str__(self):
        return self.nome

class Inscricao(models.Model):
    """
    Modelo de ligação entre Usuário e Evento.
    Representa a inscrição de um Usuário em um Evento.
    """
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='inscricoes')
    evento = models.ForeignKey(Evento, on_delete=models.CASCADE, related_name='inscricoes')
    
    # [cite_start]Campo adicionado para a Regra de Emissão de Certificados[cite: 58]:
    # A emissão de certificados ocorre após a presença ser confirmada.
    presenca_confirmada = models.BooleanField(default=False, verbose_name="Presença Confirmada")

    class Meta:
        # [cite_start]Garante que um usuário só pode se inscrever uma vez no mesmo evento[cite: 46].
        unique_together = ('usuario', 'evento')
        verbose_name = "Inscrição"
        verbose_name_plural = "Inscrições"

    def __str__(self):
        return f"{self.usuario.nome} inscrito em {self.evento.nome}"

class Certificado(models.Model):
    """
    Modelo para armazenar os certificados emitidos.
    """
    STATUS_CHOICES = [
        ('Pendente', 'Pendente'),
        ('Emitido', 'Emitido'),
    ]
    
    # inscricao_id (FK1 no diagrama) é única, então usamos OneToOneField.
    # Um certificado pertence a exatamente uma inscrição.
    inscricao = models.OneToOneField(Inscricao, on_delete=models.CASCADE, verbose_name="Inscrição Referente")
    
    data_emissao = models.DateField(auto_now_add=True, verbose_name="Data de Emissão")
    texto_certificado = models.CharField(max_length=255, verbose_name="Texto do Certificado")
    status_emissao = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pendente', verbose_name="Status de Emissão")
    
    # Campo opcional: O caminho ou URL para o arquivo do certificado gerado.
    arquivo_certificado = models.FileField(upload_to='certificados/', null=True, blank=True)

    class Meta:
        verbose_name = "Certificado"
        verbose_name_plural = "Certificados"

    def __str__(self):
        return f"Certificado para {self.inscricao.usuario.nome} - Status: {self.status_emissao}"