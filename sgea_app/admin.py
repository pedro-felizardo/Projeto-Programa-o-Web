# sgea_app/admin.py
from django.contrib import admin
from .models import Usuario, Evento # Importe todos os seus modelos

# Registre o modelo de usuário customizado
admin.site.register(Usuario) 

# Registre os demais modelos
admin.site.register(Evento)
# admin.site.register(Inscricao)
# admin.site.register(Certificado)