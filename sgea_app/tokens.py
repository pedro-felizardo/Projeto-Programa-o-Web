from django.contrib.auth.tokens import PasswordResetTokenGenerator

class UsuarioTokenGenerator(PasswordResetTokenGenerator):
    pass

token_ativacao = UsuarioTokenGenerator()