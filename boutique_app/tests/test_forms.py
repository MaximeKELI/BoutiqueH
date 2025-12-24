"""
Tests unitaires pour les formulaires
"""
from django.test import TestCase
from django.contrib.auth.models import User
from boutique_app.forms import InscriptionForm, AjoutPanierForm


class InscriptionFormTest(TestCase):
    """Tests pour le formulaire d'inscription"""
    
    def test_form_valid(self):
        """Test un formulaire valide"""
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }
        form = InscriptionForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_password_mismatch(self):
        """Test avec mots de passe différents"""
        form_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User',
            'email': 'test@example.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }
        form = InscriptionForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_required_fields(self):
        """Test que les champs requis sont obligatoires"""
        form = InscriptionForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)

