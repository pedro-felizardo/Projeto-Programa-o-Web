# 🎓 SGEA: Sistema de Gestão de Eventos Acadêmicos

## 📖 1. Visão Geral do Projeto

O **Sistema de Gestão de Eventos Acadêmicos (SGEA)** é uma aplicação web desenvolvida em **Django (Python)**, com foco no gerenciamento completo de eventos como seminários, palestras, minicursos e semanas acadêmicas.

O projeto visa robustecer a interação do usuário e as regras de negócio , introduzindo automação e uma arquitetura expandida com uma **API REST** utilizando `djangorestframework`.

### 1.1. 🔑 Funcionalidades Chave (Fase 1 & 2)

| Categoria | Funcionalidade | Requisitos Específicos |
| :--- | :--- | :--- |
| **Acesso & Segurança** | Autenticação e Cadastro de Usuários | Perfis Aluno, Professor e Organizador. Senha segura (min. 8 caracteres, letras, números, especial)  e confirmação de e-mail. |
| **Gerenciamento de Eventos** | Criação, Edição e Exclusão de Eventos | Validação da data de início (não pode ser anterior à data atual). Inclusão de banner para eventos. Todo evento deve ter um Professor Responsável. |
| **Inscrição** | Inscrição e Cancelamento de Participantes  | Regras de Negócio: Limite de vagas  e proibição de inscrição duplicada. Organizadores não se inscrevem em eventos. |
| **Automação** | Notificação por E-mail  e Certificados | Envio de e-mail de confirmação ao novo usuário. Emissão de certificados automatizada após o término e confirmação de presença. |
| **API REST** | Exposição de Endpoints | Consulta de Eventos e Inscrição de Participantes. Requer autenticação por token e possui limitação de requisições (20/dia para consulta, 50/dia para inscrição). |
| **Rastreabilidade** | Registros de Auditoria (Logs)  | Logs para criação de usuário, gerenciamento de eventos, consultas à API, geração e consulta de certificados, e inscrições. |

***

## 👥 2. Membros do Projeto

O projeto foi desenvolvido pelos seguintes membros do grupo:

| Nome do Estudante | Matrícula |
| :--- | :--- |
| Davi Klein Levy | 22505003 | 
| Pedro Felizardo Barbosa | 22405245 |
| Gabriel Valentim Moreira Cardoso | 22451256 |
| Caio Lyra Silgueiro Peixoto | 22309559 | 

***

## 🚀 3. Guia de Instalação e Execução

Este guia fornece as instruções passo a passo para configurar o ambiente de desenvolvimento e executar a aplicação SGEA[cite: 38].

### 3.1. Pré-requisitos

* Python 3.8+ instalado.
* `pip` (gerenciador de pacotes Python).
* Configurações de E-mail SMTP (necessário para o requisito de notificação [cite: 50]).

### 3.2. Configuração do Ambiente Virtual (`venv`)

1.  **Crie o Ambiente Virtual:**
    ```bash
    python -m venv venv
    ```

2.  **Ative o Ambiente Virtual:**
    * **Windows (PowerShell):**
        ```bash
        .\venv\Scripts\Activate
        ```
    * **Linux/macOS:**
        ```bash
        source venv/bin/activate
        ```
    *(Você deve ver `(venv)` no prompt do terminal.)*

### 3.3. Instalação de Dependências

Instale todos os pacotes necessários, incluindo Django, Django REST Framework, e `python-decouple`, a partir do arquivo de requisitos:

```bash
pip install -r requirements.txt
```

### 3.4. Automação de envio de email de confirmação de login via terminal

Optamos por fazer o cadastro de usuário via terminal para envitar com que o usuário tenha que ficar colocando dados sensíveis para fazer o envio de emails. 
Por isso simulamos o envio dos emails via terminal com o link de confirmação também sendo liberado no próprio terminal do código.

### 3.5. Configuração e Comandos Django

1 - Crie a estrutura do Banco de Dados: Aplique as migrações iniciais para criar as tabelas (incluindo o modelo Usuario customizado e RegistroAuditoria).

```bash
python manage.py makemigrations
python manage.py migrate
```
2 - Inicie o Servidor Local:

```bash
python manage.py runserver
```
O sistema estará acessível em: http://127.0.0.1:8000/

## 🧪 4. Guia de Testes

Para testar o fluxo de usuários e as regras de negócio, utilize o arquivo:

**Guia de teste - dados para povoar o banco de dados e testar o código** 

Este guia contém:

* Instruções para popular o banco de dados com os dados iniciais (seeding).
* Dados de login prontos para teste de perfis: Organizador, Aluno e Professor.
    * Organizador: organizador@sgea.com / Admin@123 
    * Aluno: aluno@sgea.com / Aluno@123
    * Professor: professor@sgea.com / Professor@123 
* Roteiro de testes funcionais para validar a inscrição, a emissão de certificados e o acesso à API.

## 🖼️ 5. Diagrama de Arquitetura

O sistema segue o padrão Model-View-Controller (MVC) (conhecido no Django como MVT - Model-View-Template) e é expandido com uma camada de API REST para comunicação externa

