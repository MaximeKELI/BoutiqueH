#!/usr/bin/env python
"""
Script de test pour l'inscription et la connexion
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique.settings')
django.setup()

from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from boutique_app.forms import InscriptionForm

def test_inscription():
    """Test de l'inscription d'un nouvel utilisateur"""
    print("=" * 60)
    print("TEST D'INSCRIPTION")
    print("=" * 60)
    
    # Données de test
    test_data = {
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com',
        'password1': 'testpass123',
        'password2': 'testpass123',
    }
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=test_data['username']).exists():
        print(f"⚠️  L'utilisateur '{test_data['username']}' existe déjà.")
        print("   Suppression de l'ancien utilisateur...")
        User.objects.filter(username=test_data['username']).delete()
        print("   ✓ Ancien utilisateur supprimé")
    
    # Créer le formulaire
    form = InscriptionForm(data=test_data)
    
    if form.is_valid():
        print("\n✓ Formulaire valide")
        user = form.save()
        print(f"✓ Utilisateur créé avec succès:")
        print(f"  - Nom d'utilisateur: {user.username}")
        print(f"  - Nom complet: {user.first_name} {user.last_name}")
        print(f"  - Email: {user.email}")
        print(f"  - ID: {user.id}")
        return user
    else:
        print("\n✗ Erreurs dans le formulaire:")
        for field, errors in form.errors.items():
            print(f"  - {field}: {errors}")
        return None


def test_connexion(username, password):
    """Test de connexion"""
    print("\n" + "=" * 60)
    print("TEST DE CONNEXION")
    print("=" * 60)
    
    user = authenticate(username=username, password=password)
    
    if user is not None:
        print(f"\n✓ Connexion réussie!")
        print(f"  - Utilisateur: {user.username}")
        print(f"  - Nom complet: {user.get_full_name()}")
        print(f"  - Email: {user.email}")
        print(f"  - Actif: {user.is_active}")
        print(f"  - Staff: {user.is_staff}")
        print(f"  - Superuser: {user.is_superuser}")
        return True
    else:
        print("\n✗ Échec de la connexion")
        print("  - Nom d'utilisateur ou mot de passe incorrect")
        return False


def test_liste_utilisateurs():
    """Afficher la liste des utilisateurs"""
    print("\n" + "=" * 60)
    print("LISTE DES UTILISATEURS")
    print("=" * 60)
    
    users = User.objects.all().order_by('id')
    
    if users.exists():
        print(f"\nTotal: {users.count()} utilisateur(s)\n")
        for user in users:
            print(f"  [{user.id}] {user.username}")
            print(f"      Nom: {user.get_full_name()}")
            print(f"      Email: {user.email}")
            print(f"      Staff: {'Oui' if user.is_staff else 'Non'}")
            print()
    else:
        print("\nAucun utilisateur trouvé")


def main():
    """Fonction principale"""
    print("\n🧪 TESTS D'AUTHENTIFICATION - La Gloire de Dieu")
    print("=" * 60)
    
    # Test d'inscription
    user = test_inscription()
    
    if user:
        # Test de connexion
        test_connexion('testuser', 'testpass123')
    
    # Afficher tous les utilisateurs
    test_liste_utilisateurs()
    
    print("\n" + "=" * 60)
    print("TESTS TERMINÉS")
    print("=" * 60)


if __name__ == '__main__':
    main()


