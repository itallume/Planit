from rest_framework import serializers
from .models import Cliente, Endereco

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente 
        fields = '__all__'
        read_only_fields = ['id']

        def validate_email(self, value):
            if Cliente.objects.filter(email=value).exists():
                raise serializers.ValidationError("Este email já está em uso.")
            return value

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco 
        fields = ['rua', 'numero', 'cidade', 'estado', 'cep', 'complemento']
        read_only_fields = ['id']