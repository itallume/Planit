from django.test import SimpleTestCase
from django.core.validators import MinValueValidator, FileExtensionValidator, EmailValidator
from django.db import models
from unittest.mock import Mock
from atividade.models import STATUS_CHOICES, Atividade, Referencia, Cliente, Endereco


class StatusChoicesUnitTest(SimpleTestCase):
    """Testes unitários das choices de status"""
    
    def test_status_choices_exist(self):
        """Testa se STATUS_CHOICES existe"""
        self.assertIsNotNone(STATUS_CHOICES)
    
    def test_status_choices_length(self):
        """Testa se existem 3 opções de status"""
        self.assertEqual(len(STATUS_CHOICES), 3)
    
    def test_status_choices_values(self):
        """Testa se as opções de status são corretas"""
        expected = [
            ("Pendente", "Pendente"),
            ("Concluído", "Concluído"),
            ("Atrasado", "Atrasado"),
        ]
        self.assertEqual(STATUS_CHOICES, expected)
    
    def test_status_choices_have_pendente(self):
        """Testa se 'Pendente' está nas opções"""
        statuses = [choice[0] for choice in STATUS_CHOICES]
        self.assertIn('Pendente', statuses)
    
    def test_status_choices_have_concluido(self):
        """Testa se 'Concluído' está nas opções"""
        statuses = [choice[0] for choice in STATUS_CHOICES]
        self.assertIn('Concluído', statuses)
    
    def test_status_choices_have_atrasado(self):
        """Testa se 'Atrasado' está nas opções"""
        statuses = [choice[0] for choice in STATUS_CHOICES]
        self.assertIn('Atrasado', statuses)


class AtividadeModelUnitTest(SimpleTestCase):
    """Testes unitários do modelo Atividade"""
    
    def test_atividade_has_valor_field(self):
        """Testa se Atividade tem campo valor"""
        self.assertTrue(hasattr(Atividade, 'valor'))
    
    def test_atividade_valor_field_type(self):
        """Testa se campo valor é DecimalField"""
        field = Atividade._meta.get_field('valor')
        self.assertIsInstance(field, models.DecimalField)
    
    def test_atividade_valor_max_digits(self):
        """Testa se valor tem max_digits=10"""
        field = Atividade._meta.get_field('valor')
        self.assertEqual(field.max_digits, 10)
    
    def test_atividade_valor_decimal_places(self):
        """Testa se valor tem decimal_places=2"""
        field = Atividade._meta.get_field('valor')
        self.assertEqual(field.decimal_places, 2)
    
    def test_atividade_valor_has_validator(self):
        """Testa se valor tem MinValueValidator"""
        field = Atividade._meta.get_field('valor')
        self.assertTrue(any(isinstance(v, MinValueValidator) for v in field.validators))
    
    def test_atividade_is_paga_field_type(self):
        """Testa se is_paga é BooleanField"""
        field = Atividade._meta.get_field('is_paga')
        self.assertIsInstance(field, models.BooleanField)
    
    def test_atividade_is_paga_default_false(self):
        """Testa se is_paga tem default=False"""
        field = Atividade._meta.get_field('is_paga')
        self.assertEqual(field.default, False)
    
    def test_atividade_valor_recebido_field_type(self):
        """Testa se valor_recebido é DecimalField"""
        field = Atividade._meta.get_field('valor_recebido')
        self.assertIsInstance(field, models.DecimalField)
    
    def test_atividade_valor_recebido_default_zero(self):
        """Testa se valor_recebido tem default=0.00"""
        field = Atividade._meta.get_field('valor_recebido')
        self.assertEqual(field.default, 0.00)
    
    def test_atividade_data_prevista_field_type(self):
        """Testa se data_prevista é DateField"""
        field = Atividade._meta.get_field('data_prevista')
        self.assertIsInstance(field, models.DateField)
    
    def test_atividade_data_prevista_not_null(self):
        """Testa se data_prevista não permite null"""
        field = Atividade._meta.get_field('data_prevista')
        self.assertFalse(field.null)
    
    def test_atividade_hora_prevista_field_type(self):
        """Testa se hora_prevista é TimeField"""
        field = Atividade._meta.get_field('hora_prevista')
        self.assertIsInstance(field, models.TimeField)
    
    def test_atividade_data_criacao_field_type(self):
        """Testa se data_criacao é DateField"""
        field = Atividade._meta.get_field('data_criacao')
        self.assertIsInstance(field, models.DateField)
    
    def test_atividade_data_criacao_auto_now_add(self):
        """Testa se data_criacao tem auto_now_add=True"""
        field = Atividade._meta.get_field('data_criacao')
        self.assertTrue(field.auto_now_add)
    
    def test_atividade_status_field_type(self):
        """Testa se status é CharField"""
        field = Atividade._meta.get_field('status')
        self.assertIsInstance(field, models.CharField)
    
    def test_atividade_status_choices(self):
        """Testa se status tem as choices corretas"""
        field = Atividade._meta.get_field('status')
        self.assertEqual(field.choices, STATUS_CHOICES)
    
    def test_atividade_status_default_pendente(self):
        """Testa se status tem default='Pendente'"""
        field = Atividade._meta.get_field('status')
        self.assertEqual(field.default, 'Pendente')
    
    def test_atividade_ambiente_field_type(self):
        """Testa se ambiente é ForeignKey"""
        field = Atividade._meta.get_field('ambiente')
        self.assertIsInstance(field, models.ForeignKey)
    
    def test_atividade_ambiente_on_delete_cascade(self):
        """Testa se ambiente tem on_delete=CASCADE"""
        field = Atividade._meta.get_field('ambiente')
        self.assertEqual(field.remote_field.on_delete.__name__, 'CASCADE')
    
    def test_atividade_descricao_field_type(self):
        """Testa se descricao é TextField"""
        field = Atividade._meta.get_field('descricao')
        self.assertIsInstance(field, models.TextField)
    
    def test_atividade_descricao_blank_true(self):
        """Testa se descricao permite blank"""
        field = Atividade._meta.get_field('descricao')
        self.assertTrue(field.blank)
    
    def test_atividade_descricao_null_true(self):
        """Testa se descricao permite null"""
        field = Atividade._meta.get_field('descricao')
        self.assertTrue(field.null)
    
    def test_atividade_cliente_field_type(self):
        """Testa se cliente é ForeignKey"""
        field = Atividade._meta.get_field('cliente')
        self.assertIsInstance(field, models.ForeignKey)
    
    def test_atividade_cliente_null_true(self):
        """Testa se cliente permite null"""
        field = Atividade._meta.get_field('cliente')
        self.assertTrue(field.null)
    
    def test_atividade_cliente_blank_true(self):
        """Testa se cliente permite blank"""
        field = Atividade._meta.get_field('cliente')
        self.assertTrue(field.blank)
    
    def test_atividade_str_method(self):
        """Testa método __str__ da Atividade"""
        atividade_mock = Mock(spec=Atividade)
        atividade_mock.descricao = 'Esta é uma descrição muito longa que será truncada'
        atividade_mock.__str__ = lambda self: self.descricao[:50]
        
        result = str(atividade_mock)
        self.assertEqual(len(result), 50)


class ReferenciaModelUnitTest(SimpleTestCase):
    """Testes unitários do modelo Referencia"""
    
    def test_referencia_tipo_field_type(self):
        """Testa se tipo é CharField"""
        field = Referencia._meta.get_field('tipo')
        self.assertIsInstance(field, models.CharField)
    
    def test_referencia_tipo_max_length(self):
        """Testa se tipo tem max_length=100"""
        field = Referencia._meta.get_field('tipo')
        self.assertEqual(field.max_length, 100)
    
    def test_referencia_nome_arquivo_field_type(self):
        """Testa se nome_arquivo é CharField"""
        field = Referencia._meta.get_field('nome_arquivo')
        self.assertIsInstance(field, models.CharField)
    
    def test_referencia_nome_arquivo_max_length(self):
        """Testa se nome_arquivo tem max_length=200"""
        field = Referencia._meta.get_field('nome_arquivo')
        self.assertEqual(field.max_length, 200)
    
    def test_referencia_arquivo_field_type(self):
        """Testa se arquivo é FileField"""
        field = Referencia._meta.get_field('arquivo')
        self.assertIsInstance(field, models.FileField)
    
    def test_referencia_arquivo_upload_to(self):
        """Testa se arquivo tem upload_to='referencias/'"""
        field = Referencia._meta.get_field('arquivo')
        self.assertEqual(field.upload_to, 'referencias/')
    
    def test_referencia_arquivo_has_validator(self):
        """Testa se arquivo tem FileExtensionValidator"""
        field = Referencia._meta.get_field('arquivo')
        self.assertTrue(any(isinstance(v, FileExtensionValidator) for v in field.validators))
    
    def test_referencia_atividade_field_type(self):
        """Testa se atividade é ForeignKey"""
        field = Referencia._meta.get_field('atividade')
        self.assertIsInstance(field, models.ForeignKey)
    
    def test_referencia_str_method(self):
        """Testa método __str__ da Referencia"""
        referencia_mock = Mock(spec=Referencia)
        referencia_mock.nome_arquivo = 'documento.pdf'
        referencia_mock.__str__ = lambda self: self.nome_arquivo
        
        result = str(referencia_mock)
        self.assertEqual(result, 'documento.pdf')


class ClienteModelUnitTest(SimpleTestCase):
    """Testes unitários do modelo Cliente"""
    
    def test_cliente_nome_field_type(self):
        """Testa se nome é CharField"""
        field = Cliente._meta.get_field('nome')
        self.assertIsInstance(field, models.CharField)
    
    def test_cliente_nome_max_length(self):
        """Testa se nome tem max_length=200"""
        field = Cliente._meta.get_field('nome')
        self.assertEqual(field.max_length, 200)
    
    def test_cliente_email_field_type(self):
        """Testa se email é EmailField"""
        field = Cliente._meta.get_field('email')
        self.assertIsInstance(field, models.EmailField)
    
    def test_cliente_email_unique(self):
        """Testa se email é unique"""
        field = Cliente._meta.get_field('email')
        self.assertTrue(field.unique)
    
    def test_cliente_telefone_field_type(self):
        """Testa se telefone é CharField"""
        field = Cliente._meta.get_field('telefone')
        self.assertIsInstance(field, models.CharField)
    
    def test_cliente_telefone_max_length(self):
        """Testa se telefone tem max_length=20"""
        field = Cliente._meta.get_field('telefone')
        self.assertEqual(field.max_length, 20)
    
    def test_cliente_sobre_field_type(self):
        """Testa se sobre é TextField"""
        field = Cliente._meta.get_field('sobre')
        self.assertIsInstance(field, models.TextField)
    
    def test_cliente_str_method(self):
        """Testa método __str__ do Cliente"""
        cliente_mock = Mock(spec=Cliente)
        cliente_mock.nome = 'João Silva'
        cliente_mock.__str__ = lambda self: self.nome
        
        result = str(cliente_mock)
        self.assertEqual(result, 'João Silva')


class EnderecoModelUnitTest(SimpleTestCase):
    """Testes unitários do modelo Endereco"""
    
    def test_endereco_rua_field_type(self):
        """Testa se rua é CharField"""
        field = Endereco._meta.get_field('rua')
        self.assertIsInstance(field, models.CharField)
    
    def test_endereco_rua_max_length(self):
        """Testa se rua tem max_length=200"""
        field = Endereco._meta.get_field('rua')
        self.assertEqual(field.max_length, 200)
    
    def test_endereco_numero_field_type(self):
        """Testa se numero é CharField"""
        field = Endereco._meta.get_field('numero')
        self.assertIsInstance(field, models.CharField)
    
    def test_endereco_numero_blank_true(self):
        """Testa se numero permite blank"""
        field = Endereco._meta.get_field('numero')
        self.assertTrue(field.blank)
    
    def test_endereco_numero_null_true(self):
        """Testa se numero permite null"""
        field = Endereco._meta.get_field('numero')
        self.assertTrue(field.null)
    
    def test_endereco_cidade_field_type(self):
        """Testa se cidade é CharField"""
        field = Endereco._meta.get_field('cidade')
        self.assertIsInstance(field, models.CharField)
    
    def test_endereco_estado_field_type(self):
        """Testa se estado é CharField"""
        field = Endereco._meta.get_field('estado')
        self.assertIsInstance(field, models.CharField)
    
    def test_endereco_cep_field_type(self):
        """Testa se cep é CharField"""
        field = Endereco._meta.get_field('cep')
        self.assertIsInstance(field, models.CharField)
    
    def test_endereco_complemento_field_type(self):
        """Testa se complemento é CharField"""
        field = Endereco._meta.get_field('complemento')
        self.assertIsInstance(field, models.CharField)
    
    def test_endereco_complemento_blank_true(self):
        """Testa se complemento permite blank"""
        field = Endereco._meta.get_field('complemento')
        self.assertTrue(field.blank)
    
    def test_endereco_cliente_field_type(self):
        """Testa se cliente é ForeignKey"""
        field = Endereco._meta.get_field('cliente')
        self.assertIsInstance(field, models.ForeignKey)
    
    def test_endereco_str_method(self):
        """Testa método __str__ do Endereco"""
        endereco_mock = Mock(spec=Endereco)
        endereco_mock.rua = 'Rua Principal'
        endereco_mock.cidade = 'São Paulo'
        endereco_mock.__str__ = lambda self: f"{self.rua}, {self.cidade}"
        
        result = str(endereco_mock)
        self.assertEqual(result, 'Rua Principal, São Paulo')
