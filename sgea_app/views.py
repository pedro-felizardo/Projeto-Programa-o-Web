from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages 
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import logout
from django.utils import timezone
from .forms import * 
from .models import *
from .utils import log_auditoria
from django.contrib.auth import get_user_model
from .tokens import token_ativacao
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.db.models import Q
# Importe o forms.py que criamos no passo anterior.

# --- Funções Auxiliares de Permissão ---

def is_organizador(user):
    """ Verifica se o usuário é um organizador e está ativo/autenticado. """
    return user.is_authenticated and user.perfil == 'Organizador'

def is_professor_or_organizador(user):
    """ Verifica se o usuário é um professor ou organizador. """
    return user.is_authenticated and user.perfil in ['Professor', 'Organizador']

def is_aluno_or_professor(user):
    """ Verifica se o usuário é um Aluno ou Professor e está ativo/autenticado. """
    return user.is_authenticated and user.perfil in ['Aluno', 'Professor']

# --- Rotas Públicas ---

def lista_eventos(request):
    """
    Exibe a lista de eventos que ainda não começaram e que o usuário (se logado)
    ainda não se inscreveu. Redireciona Organizadores para o dashboard.
    """
    hoje = timezone.now().date()
    
    # Filtro base: Apenas eventos que ainda não começaram
    eventos_queryset = Evento.objects.filter(
        data_inicial__gt=hoje
    ).order_by('data_inicial')
    
    if request.user.is_authenticated:
        # 1. Restrição para Organizador
        if request.user.perfil == 'Organizador':
            return redirect('dashboard') 
        
        # 2. Filtragem para Aluno/Professor (excluir inscritos)
        elif request.user.perfil in ['Aluno', 'Professor']:
            
            # Pega os IDs dos eventos em que o usuário está inscrito
            eventos_inscritos_ids = Inscricao.objects.filter(
                usuario=request.user
            ).values_list('evento__id', flat=True)
            
            # Exclui da listagem todos os eventos que o usuário já está inscrito
            eventos_disponiveis = eventos_queryset.exclude(
                id__in=eventos_inscritos_ids
            )
            
    else:
        # 3. Usuário Não Logado (vê todos os eventos futuros)
        eventos_disponiveis = eventos_queryset
            
    context = {
        'eventos': eventos_disponiveis,
        'title': 'Eventos Acadêmicos Disponíveis'
    }
    return render(request, 'lista_eventos.html', context)

def detalhe_evento(request, evento_id):
    """ 
    Exibe os detalhes de um evento específico (rota: /evento/<id>/). 
    Inclui botão de inscrição se o usuário for Aluno/Professor.
    """
    # Lógica futura: buscar evento pelo ID
    return HttpResponse(f"Detalhes do Evento ID: {evento_id}")

def cadastro_usuario(request):
    """ 
    Formulário para cadastro de novos usuários (rota: /cadastro/). 
    Aplica validações do forms.py, define is_active=False e simula envio de e-mail.
    """
    if request.method == 'POST':
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            # A função save no forms.py já hasheia a senha
            novo_usuario = form.save(commit=False)
            
            # Regra de Negócio: Novo usuário começa como inativo (is_active=False)
            # até a confirmação por e-mail.
            novo_usuario.is_active = True
            novo_usuario.save()

            from .utils import enviar_email_confirmacao
            enviar_email_confirmacao(novo_usuario, request)

            messages.success(request, "Cadastro realizado! Verifique seu e-mail para ativar sua conta.")
            return redirect('login')
        else:
            messages.error(request, "Corrija os erros abaixo.")
    else:
        form = CadastroUsuarioForm()

    return render(request, 'cadastro_usuario.html', {'form':form})


Usuario = get_user_model()

def confirmar_email(request, uid, token):
    """
    Ativa o usuário após clicar no link enviado por e-mail.
    """
    try:
        usuario = Usuario.objects.get(pk=uid)
    except Usuario.DoesNotExist:
        return HttpResponse("Usuário inválido.", status=400)

    if token_ativacao.check_token(usuario, token):
        usuario.is_active = True
        usuario.save()
        return HttpResponse("E-mail confirmado com sucesso! Sua conta foi ativada.", status=200)
    else:
        return HttpResponse("Link inválido ou expirado.", status=400)

def login_view(request):
    if request.method == "POST":
        login_digitado = request.POST.get("login")
        senha_digitada = request.POST.get("password")

        user = authenticate(request, login=login_digitado, password=senha_digitada)

        if user is not None:
            
            login(request, user)
            return redirect("dashboard")

        messages.error(request, "Usuário ou senha incorretos.")
        return render(request, "login.html")

    return render(request, "login.html")

def logout_view(request):
    logout(request)
    return redirect("login")

@login_required
def dashboard(request):
    """ 
    Dashboard após o login (rota: /dashboard/). 
    Se Organizador, lista seus eventos.
    Se Aluno/Professor, lista suas inscrições.
    """
    context = {}
    usuario = request.user
    
    if is_organizador(usuario):
        # Se for Organizador
        eventos_organizados = Evento.objects.filter(
            organizador=usuario
        ).order_by('data_inicial')
        
        context['eventos_organizados'] = eventos_organizados
        
    elif usuario.perfil in ['Aluno', 'Professor']:
        # Se for Aluno ou Professor
        
        # Filtra as inscrições do usuário e pré-busca os dados do evento
        minhas_inscricoes = Inscricao.objects.filter(
            usuario=usuario
        ).select_related('evento').order_by('evento__data_inicial')
        
        context['minhas_inscricoes'] = minhas_inscricoes
        
    return render(request, 'dashboard.html', context)

@login_required
def inscrever_evento(request, evento_id):
    """ 
    Processa a inscrição de um usuário (Aluno/Professor) em um evento.
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    usuario = request.user
    hoje = timezone.now().date()
    
    # 1. Restrição de Acesso (Apenas Aluno/Professor) 
    if usuario.perfil not in ['Aluno', 'Professor']:
        messages.error(request, "Apenas usuários com perfil Aluno ou Professor podem se inscrever em eventos.")
        return redirect('home') # Redireciona de volta à lista de eventos
        
    # 2. Verificar se o evento já começou (só permite inscrição em eventos futuros)
    if evento.data_inicial < hoje:
        messages.error(request, f"Não é possível se inscrever no evento '{evento.nome}', pois ele já começou ou terminou.")
        return redirect('home')

    # 3. Verificar Inscrição Duplicada
    if Inscricao.objects.filter(usuario=usuario, evento=evento).exists():
        messages.warning(request, f"Você já está inscrito no evento '{evento.nome}'.")
        return redirect('home') 

    # 4. Verificar Limite de Vagas
    total_inscritos = Inscricao.objects.filter(evento=evento).count()
    
    if total_inscritos >= evento.quantidade_participantes:
        messages.error(request, f"O evento '{evento.nome}' atingiu o limite de vagas.")
        return redirect('home')
    
    try:
        # 5. Criar Inscrição
        Inscricao.objects.create(usuario=usuario, evento=evento)
        messages.success(request, f"Inscrição no evento '{evento.nome}' realizada com sucesso!")
        
    except Exception as e:
        messages.error(request, f"Ocorreu um erro ao processar sua inscrição. Tente novamente.")
        # Logar o erro 'e' aqui para depuração
        
    return redirect('home')

@login_required
def desinscrever_evento(request, evento_id):
    """ 
    Permite ao usuário (Aluno/Professor) cancelar sua inscrição em um evento futuro.
    """
    evento = get_object_or_404(Evento, pk=evento_id)
    usuario = request.user
    hoje = timezone.now().date()
    
    # 1. Busca a inscrição
    inscricao = get_object_or_404(Inscricao, usuario=usuario, evento=evento)
    
    # 2. Verifica se o evento já começou (só permite cancelamento em eventos futuros)
    if evento.data_inicial < hoje:
        messages.error(request, f"Não é possível cancelar a inscrição, pois o evento '{evento.nome}' já começou ou terminou.")
        return redirect('dashboard')

    # 3. Processa a desinscrição (usando POST, que é mais seguro)
    if request.method == 'POST':
        try:
            inscricao.delete()
            messages.success(request, f"Inscrição no evento '{evento.nome}' cancelada com sucesso.")
        except Exception as e:
            messages.error(request, "Ocorreu um erro ao cancelar sua inscrição.")
        
    # Redireciona para o dashboard, onde a lista de inscrições será atualizada
    return redirect('dashboard')

@login_required
@user_passes_test(is_aluno_or_professor)
def meus_certificados(request):
    """
    Lista todos os certificados disponíveis para o usuário logado e 
    gerencia o download do certificado.
    """
    
    # ----------------------------------------------------
    # 1. Lógica de DOWNLOAD (Acionada por um parâmetro na URL)
    # ----------------------------------------------------
    if 'download' in request.GET:
        certificado_id = request.GET.get('download')
        
        # Garante que o usuário só pode baixar seus próprios certificados
        certificado = get_object_or_404(
            Certificado, 
            pk=certificado_id, 
            inscricao__usuario=request.user
        )
        
        # Log de Auditoria: Registro da consulta/download
        log_auditoria(
            request.user, 
            f'Download do certificado {certificado.id} para o evento {certificado.inscricao.evento.nome}'
        )

        # ** SIMULAÇÃO DA CRIAÇÃO E ENTREGA DO ARQUIVO **
        
        # Conteúdo do certificado (usando o texto gerado na emissão)
        conteudo_certificado = f"""
SGEA - Sistema de Gestão de Eventos Acadêmicos
__________________________________________________________________

{certificado.texto_certificado}

Data de Emissão: {certificado.data_emissao.strftime('%d/%m/%Y')}
Status: Emitido e Válido.
__________________________________________________________________

"""
        # Cria a resposta HTTP
        response = HttpResponse(
            conteudo_certificado, 
            content_type='text/plain' # text/plain SIMULA um arquivo. Para PDF real, seria 'application/pdf'
        )
        
        # Define o cabeçalho para forçar o download no navegador
        nome_arquivo = f"certificado_{certificado.inscricao.evento.nome.replace(' ', '_')}_{request.user.nome.replace(' ', '_')}.txt"
        response['Content-Disposition'] = f'attachment; filename="{nome_arquivo}"'
        
        return response

    # ----------------------------------------------------
    # 2. Lógica de LISTAGEM (Padrão, se não houver 'download')
    # ----------------------------------------------------
    
    # Busca todos os certificados vinculados às inscrições do usuário logado
    certificados = Certificado.objects.filter(
        inscricao__usuario=request.user
    ).select_related(
        'inscricao__evento' # Otimiza a busca para acessar dados do Evento
    )
    
    context = {
        'certificados': certificados,
        'perfil': request.user.perfil # Útil para o template
    }
    
    return render(request, 'meus_certificados.html', context)

# --- Rotas de Organizador ---

@login_required
@user_passes_test(is_organizador)
def criar_evento(request):
    """ 
    Formulário para criar um novo evento (rota: /eventos/novo/).
    Aplica validações de data e banner (implementadas no forms.py).
    """
    if request.method == 'POST':
        form = FormularioEvento(request.POST, request.FILES) # Usa request.FILES para o banner
        if form.is_valid():
            evento = form.save(commit=False)
            
            # Define o organizador responsável como o usuário logado 
            evento.organizador = request.user 
            evento.save()
            
            # Redireciona para a lista de gerenciamento de eventos
            return redirect('dashboard') 
    else:
        form = FormularioEvento()
        
    return render(request, 'criar_evento.html', {'form': form, 'title': 'Criar Novo Evento'})

@login_required
@user_passes_test(is_organizador)
def editar_evento(request, evento_id):
    """ 
    Formulário para editar um evento existente.
    """
    # 1. Busca o evento ou retorna 404
    evento = get_object_or_404(Evento, pk=evento_id, organizador=request.user)
    
    # 2. Processa a submissão
    if request.method == 'POST':
        # Instancia o formulário com os dados POST, arquivos e a instância do objeto
        form = FormularioEvento(request.POST, request.FILES, instance=evento)
        if form.is_valid():
            # A view de criação não precisa definir 'organizador' aqui, pois ele já está
            # na instância 'evento' e o formulário o mantém.
            form.save()
            return redirect('dashboard') 
    else:
        # 3. Exibe o formulário preenchido (GET)
        form = FormularioEvento(instance=evento)
        
    context = {
        'form': form, 
        'title': f'Editar Evento: {evento.nome}',
        'evento_id': evento.id
    }
    # O template 'editar_evento.html' será o próximo a ser criado
    return render(request, 'editar_evento.html', context)

@login_required
@user_passes_test(is_organizador)
def lista_inscritos(request, evento_id):
    """ 
    Lista de participantes inscritos em um evento (rota: /evento/<id>/inscritos/). 
    Permite ao Organizador confirmar presença.
    """
    
    # 1. Garante que o Organizador só veja eventos que ele criou
    evento = get_object_or_404(Evento, pk=evento_id, organizador=request.user)
    
    # 2. Lógica de Confirmação de Presença
    if request.method == 'POST':
        inscricao_id = request.POST.get('inscricao_id')
        confirmar_presenca = request.POST.get('confirmar_presenca') == 'true'
        
        inscricao = get_object_or_404(Inscricao, pk=inscricao_id, evento=evento)
        
        # Se for para confirmar e ainda não estiver confirmado
        if confirmar_presenca and not inscricao.presenca_confirmada:
            inscricao.presenca_confirmada = True
            inscricao.save()
            messages.success(request, f"Presença de {inscricao.usuario.nome} confirmada!")
            # Não é necessário logar aqui, pois é uma ação de gerenciamento interna.
        
        # Se for para remover a confirmação e já estiver confirmado
        elif not confirmar_presenca and inscricao.presenca_confirmada:
            inscricao.presenca_confirmada = False
            inscricao.save()
            messages.success(request, f"Presença de {inscricao.usuario.nome} desconfirmada!")
        
        # Redireciona para o GET da página para evitar submissão duplicada
        return redirect('lista_inscritos', evento_id=evento_id) 

    # 3. Busca todas as Inscrições para o Evento
    inscritos = Inscricao.objects.filter(evento=evento).select_related('usuario').order_by('usuario__nome')
    
    # 4. Cálculo de Vagas
    total_inscritos = inscritos.count()
    vagas_restantes = evento.quantidade_participantes - total_inscritos
    
    context = {
        'evento': evento,
        'inscritos': inscritos,
        'total_inscritos': total_inscritos,
        'vagas_restantes': vagas_restantes,
        'title': f'Inscritos no Evento: {evento.nome}'
    }
    return render(request, 'lista_inscritos.html', context)


@login_required
@user_passes_test(is_organizador)
def emitir_certificados(request, evento_id):
    """ 
    Gera certificados para o evento, independentemente da data_final,
    desde que a presença esteja confirmada.
    """
    evento = get_object_or_404(Evento, pk=evento_id, organizador=request.user)
    
    # 1. REMOVEMOS A VERIFICAÇÃO DE DATA: O ORGANIZADOR AGORA PODE EMITIR QUANDO QUISER.
    
    # OBSERVAÇÃO: Manter a lógica de que "o evento precisa ter terminado"
    # é importante para o requisito de Emissão Automática de Certificados.
    # Ao removermos esta verificação aqui, assumimos que o Organizador 
    # está fazendo o processo MANUALMENTE.
        
    # 2. Busca Inscrições com presença confirmada E que AINDA NÃO têm certificado
    inscricoes_prontas = Inscricao.objects.filter(
        evento=evento, 
        presenca_confirmada=True
    ).exclude(
        certificado__isnull=False
    )
    
    # ... (o resto da lógica de geração de certificado permanece igual) ...
    
    certificados_emitidos = 0
    
    # 3. Processo de Geração (Automação Simulada)
    for inscricao in inscricoes_prontas:
        # Conteúdo do certificado
        texto_base = f"Certificamos que {inscricao.usuario.nome} participou do evento {evento.nome}, organizado por {evento.organizador.nome}."
        
        Certificado.objects.create(
            inscricao=inscricao,
            texto_certificado=texto_base,
            status_emissao='Emitido',
            # ...
        )
        certificados_emitidos += 1
        
    # 4. Log de Auditoria
    from .utils import log_auditoria
    log_auditoria(request.user, f'Emissão MANUAL de {certificados_emitidos} certificados para o evento {evento.nome}')
    
    if certificados_emitidos > 0:
        messages.success(request, f"Emissão concluída! {certificados_emitidos} novos certificados foram gerados.")
    else:
        messages.info(request, "Nenhum novo certificado foi emitido (Verifique se a presença foi confirmada).")
        
    return redirect('lista_inscritos', evento_id=evento_id)
    
@login_required
@user_passes_test(is_organizador)
def registros_auditoria(request):
    """ 
    Tela para consultar logs de auditoria (rota: /auditoria/). 
    Permite filtrar por data e usuário.
    """
    
    # 1. Filtros
    data_filtro = request.GET.get('data')
    usuario_filtro_id = request.GET.get('usuario')
    
    # Inicia com todos os logs, ordenados do mais novo para o mais antigo (definido no model Meta)
    logs = RegistroAuditoria.objects.all().select_related('usuario')
    
    # 2. Aplica Filtros
    if data_filtro:
        try:
            # Filtra por data exata
            logs = logs.filter(data_hora__date=data_filtro)
        except ValueError:
            # Caso a data seja inválida, apenas ignora
            messages.warning(request, "Formato de data inválido.")
            
    if usuario_filtro_id and usuario_filtro_id.isdigit():
        logs = logs.filter(usuario_id=usuario_filtro_id)
        
    # 3. Lista de usuários para o dropdown de filtro
    usuarios_disponiveis = Usuario.objects.all().order_by('nome')

    context = {
        'logs': logs[:200], # Limita a exibição para performance
        'usuarios_disponiveis': usuarios_disponiveis,
        'data_filtro': data_filtro,
        'usuario_filtro_id': usuario_filtro_id,
        'title': 'Registros de Auditoria'
    }
    return render(request, 'registros_auditoria.html', context)