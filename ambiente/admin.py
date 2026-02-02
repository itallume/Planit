from django.contrib import admin
from .models import Ambiente, AmbienteInvitations, Role, Participante

# Register your models here.

@admin.register(Ambiente)
class AmbienteAdmin(admin.ModelAdmin):
    list_display = ['nome', 'usuario_administrador', 'tema']
    search_fields = ['nome', 'usuario_administrador__username']
    list_filter = ['usuario_administrador']

@admin.register(AmbienteInvitations)
class AmbienteInvitationsAdmin(admin.ModelAdmin):
    list_display = ['ambiente', 'email', 'accepted', 'created_at', 'inviter']
    list_filter = ['accepted', 'created_at']
    search_fields = ['email', 'ambiente__nome']

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ambiente', 'pode_visualizar_atividades', 'pode_criar_atividades', 
                    'pode_editar_atividades', 'pode_deletar_atividades']
    list_filter = ['nome', 'ambiente']
    search_fields = ['ambiente__nome']

@admin.register(Participante)
class ParticipanteAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'ambiente', 'role', 'data_entrada']
    list_filter = ['role', 'data_entrada']
    search_fields = ['usuario__username', 'ambiente__nome']
    raw_id_fields = ['usuario', 'ambiente', 'role']
