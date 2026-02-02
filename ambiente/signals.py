from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Ambiente, Role


@receiver(post_save, sender=Ambiente)
def criar_roles_padrao(sender, instance, created, **kwargs):
    """
    Cria as 3 roles padrão quando um novo ambiente é criado:
    - Leitor: apenas visualizar
    - Editor: visualizar, criar e editar
    - Administrador: todas as permissões
    """
    if created:
        # Role Leitor - Apenas visualizar
        Role.objects.create(
            nome=Role.LEITOR,
            ambiente=instance,
            pode_visualizar_atividades=True,
            pode_criar_atividades=False,
            pode_editar_atividades=False,
            pode_deletar_atividades=False
        )
        
        # Role Editor - Visualizar, criar e editar
        Role.objects.create(
            nome=Role.EDITOR,
            ambiente=instance,
            pode_visualizar_atividades=True,
            pode_criar_atividades=True,
            pode_editar_atividades=True,
            pode_deletar_atividades=False
        )
        
        # Role Administrador - Todas as permissões
        Role.objects.create(
            nome=Role.ADMINISTRADOR,
            ambiente=instance,
            pode_visualizar_atividades=True,
            pode_criar_atividades=True,
            pode_editar_atividades=True,
            pode_deletar_atividades=True
        )
