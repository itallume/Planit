from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Ambiente, AmbienteInvitations
import secrets


class AmbienteInvitationSerializer(serializers.ModelSerializer):
    inviter_name = serializers.CharField(source='inviter.username', read_only=True)
    ambiente_name = serializers.CharField(source='ambiente.nome', read_only=True)
    
    class Meta:
        model = AmbienteInvitations
        fields = ['id', 'email', 'token', 'inviter_name', 'ambiente_name', 'accepted', 'created_at']
        read_only_fields = ['id', 'token', 'inviter', 'ambiente', 'guest', 'inviter_name', 'ambiente_name', 'accepted', 'created_at']
    
    def validate_email(self, value):
        """Valida o email e todas as regras de negócio"""
        ambiente = self.context.get('ambiente')
        inviter = self.context.get('inviter')
        
        try:
            guest = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError('Usuário com este email não encontrado.')
        
        if not ambiente:
            raise serializers.ValidationError('Ambiente não especificado.')
        
        if inviter and guest == inviter:
            raise serializers.ValidationError('Você não pode enviar convite para si mesmo.')
    
        if ambiente.usuario_administrador == guest:
            raise serializers.ValidationError('Este usuário já é o administrador do ambiente.')
        
        if ambiente.usuarios_participantes.filter(id=guest.id).exists():
            raise serializers.ValidationError('Este usuário já é participante do ambiente.')
        
        if AmbienteInvitations.objects.filter(
            ambiente=ambiente,
            guest=guest,
            accepted=False
        ).exists():
            raise serializers.ValidationError('Já existe um convite pendente para este usuário.')
        
        return value
    
    def create(self, validated_data):
        """Cria o convite"""
        ambiente = self.context.get('ambiente')
        inviter = self.context.get('inviter')
        email = validated_data['email']
        
        guest = User.objects.get(email=email)
        token = secrets.token_hex(32)
        
        invitation = AmbienteInvitations.objects.create(
            inviter=inviter,
            ambiente=ambiente,
            email=email,
            token=token,
            guest=guest
        )
        
        return invitation

