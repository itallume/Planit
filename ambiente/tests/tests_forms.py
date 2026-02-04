from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ambiente.forms import AmbienteForm, SendInvitationForm
from ambiente.models import Ambiente, AmbienteInvitations


class AmbienteFormsTestCase(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='ambiente_forms_admin',
            email='admin@email.com',
            password='123456'
        )

        self.user = User.objects.create_user(
            username='ambiente_forms_user',
            email='user@email.com',
            password='123456'
        )

        self.ambiente = Ambiente.objects.create(
            nome='Ambiente Teste Forms',
            usuario_administrador=self.admin
        )

    # =====================
    # AmbienteForm
    # =====================

    def test_ambiente_form_valido(self):
        form = AmbienteForm(
            data={
                'nome': 'Novo Ambiente',
                'tema': '#AABBCC'
            }
        )

        self.assertTrue(form.is_valid())

    def test_ambiente_form_invalido_tema(self):
        form = AmbienteForm(
            data={
                'nome': 'Ambiente',
                'tema': '123456'
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn('tema', form.errors)

    def test_ambiente_form_labels(self):
        form = AmbienteForm()
        self.assertEqual(form.fields['nome'].label, 'Nome do Ambiente')
        self.assertEqual(form.fields['tema'].label, 'Cor do Tema')

    def test_ambiente_form_widget_tema(self):
        form = AmbienteForm()
        widget = form.fields['tema'].widget

        self.assertEqual(widget.input_type, 'color')
        self.assertIn('form-control-color', widget.attrs.get('class'))

    # =====================
    # SendInvitationForm
    # =====================

    def test_send_invitation_email_valido(self):
        form = SendInvitationForm(
            data={'email': self.user.email}
        )

        self.assertTrue(form.is_valid())

    def test_email_ja_convidado(self):
        AmbienteInvitations.objects.create(
            ambiente=self.ambiente,
            email=self.user.email,
            token='token123',
            inviter=self.admin,
            guest=self.user
        )

        form = SendInvitationForm(
            data={'email': self.user.email}
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Este email já foi convidado.',
            form.errors['email']
        )

    def test_email_ja_participante(self):
        self.ambiente.usuarios_participantes.add(self.user)

        form = SendInvitationForm(
            data={'email': self.user.email}
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Este email já pertence a um participante do ambiente.',
            form.errors['email']
        )

    def test_email_admin(self):
        form = SendInvitationForm(
            data={'email': self.admin.email}
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Este email já pertence ao administrador do ambiente.',
            form.errors['email']
        )

    def test_email_nao_registrado(self):
        form = SendInvitationForm(
            data={'email': 'inexistente@email.com'}
        )

        self.assertFalse(form.is_valid())
        self.assertIn(
            'Este email não está registrado no sistema.',
            form.errors['email']
        )

    def test_email_vazio(self):
        form = SendInvitationForm(
            data={'email': ''}
        )

        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
