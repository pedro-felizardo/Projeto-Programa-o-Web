from django.contrib.auth.models import BaseUserManager

class UsuarioManager(BaseUserManager):
    """Gerenciador de modelos para o modelo Usuario."""
    
    def create_user(self, login, senha=None, **extra_fields):
        if not login:
            raise ValueError('O login (e-mail) deve ser fornecido')
        
        # O Django utiliza a classe de autenticação para gerenciar o login
        user = self.model(
            login=self.normalize_email(login),
            **extra_fields
        )
        
        # Define e hasheia a senha
        user.set_password(senha) 
        user.save(using=self._db)
        return user

    def create_superuser(self, login, senha=None, **extra_fields):
        # A criação de superusuário usa o mesmo login/senha, 
        # mas define flags de permissão como True.
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('perfil', 'Organizador') # Superusuário é sempre Organizador/Admin

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(login, senha, **extra_fields)