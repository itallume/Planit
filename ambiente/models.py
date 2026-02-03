from django.db import models
from django.core.validators import RegexValidator

# Create your models here.


class Ambiente(models.Model):

    nome = models.CharField(max_length=100)
    tema = models.CharField(
        max_length=7, 
        blank=True,
        default='#F26800',
        validators=[
            RegexValidator(
                regex='^#[0-9A-Fa-f]{6}$',
                message='O tema deve ser uma cor no formato #RRGGBB (ex: #FF5733)',
            )
        ],
        help_text='Cor do tema no formato hexadecimal (ex: #FF5733)'
    )
    usuario_administrador = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    usuarios_participantes = models.ManyToManyField('auth.User', related_name='ambientes_participantes', blank=True)

    def __str__(self):
        return self.nome
    
class AmbienteInvitations(models.Model):
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)
    inviter = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='sent_invitations')
    guest = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='invitations')

    def __str__(self):
        return f'Invitation to {self.email} for {self.ambiente.nome}'


class Role(models.Model):
    """
    Define roles com permissões específicas para um ambiente.
    Cada role é vinculada a um ambiente específico.
    """
    LEITOR = 'leitor'
    EDITOR = 'editor'
    ADMINISTRADOR = 'administrador'
    CUSTOM = 'custom'
    
    ROLE_CHOICES = [
        (LEITOR, 'Leitor'),
        (EDITOR, 'Editor'),
        (ADMINISTRADOR, 'Administrador'),
        (CUSTOM, 'Personalizado'),
    ]
    
    nome = models.CharField(max_length=20, choices=ROLE_CHOICES)
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, related_name='roles')
    
    # Permissões CRUD para atividades
    pode_visualizar_atividades = models.BooleanField(default=True)
    pode_criar_atividades = models.BooleanField(default=False)
    pode_editar_atividades = models.BooleanField(default=False)
    pode_deletar_atividades = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['nome', 'ambiente']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return f"{self.get_nome_display()} - {self.ambiente.nome}"


class Participante(models.Model):
    """
    Relaciona um usuário a um ambiente com uma role específica.
    Permite ter permissões diferentes em ambientes diferentes.
    """
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='participacoes')
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, related_name='participantes')
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True, related_name='participantes')
    data_entrada = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['usuario', 'ambiente']
        verbose_name = 'Participante'
        verbose_name_plural = 'Participantes'
    
    def __str__(self):
        role_nome = self.role.get_nome_display() if self.role else 'Sem role'
        return f"{self.usuario.username} - {self.ambiente.nome} ({role_nome})"


class Notificacao(models.Model):
    """
    Notificações para usuários sobre ações no sistema.
    """
    TIPO_ALOCACAO_ATIVIDADE = 'alocacao_atividade'
    TIPO_CHOICES = [
        (TIPO_ALOCACAO_ATIVIDADE, 'Alocação em Atividade'),
    ]
    
    usuario = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='notificacoes')
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    titulo = models.CharField(max_length=200)
    mensagem = models.TextField()
    link = models.CharField(max_length=500, blank=True)  # URL para onde redirecionar ao clicar
    lida = models.BooleanField(default=False)
    criada_em = models.DateTimeField(auto_now_add=True)
    
    # Referências opcionais
    atividade = models.ForeignKey('atividade.Atividade', on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes')
    ambiente = models.ForeignKey(Ambiente, on_delete=models.CASCADE, null=True, blank=True, related_name='notificacoes')
    
    class Meta:
        ordering = ['-criada_em']
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
    
    def __str__(self):
        return f"{self.usuario.username} - {self.titulo}"