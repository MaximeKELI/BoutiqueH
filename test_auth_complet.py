#!/usr/bin/env python
"""
Test complet d'inscription et connexion via les vues Django
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

def test_inscription_vue():
    """Test de l'inscription via la vue"""
    print("=" * 60)
    print("TEST D'INSCRIPTION VIA LA VUE")
    print("=" * 60)
    
    client = Client()
    
    # Données de test
    test_data = {
        'username': 'client_test',
        'first_name': 'Client',
        'last_name': 'Test',
        'email': 'client@test.com',
        'password1': 'SecurePass123!',
        'password2': 'SecurePass123!',
    }
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=test_data['username']).exists():
        print(f"⚠️  Suppression de l'utilisateur existant...")
        User.objects.filter(username=test_data['username']).delete()
    
    # Accéder à la page d'inscription
    print("\n1. Accès à la page d'inscription...")
    response = client.get(reverse('inscription'))
    print(f"   ✓ Code HTTP: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Page d'inscription accessible")
    else:
        print("   ✗ Erreur lors de l'accès à la page")
        return False
    
    # Soumettre le formulaire
    print("\n2. Soumission du formulaire d'inscription...")
    response = client.post(reverse('inscription'), data=test_data, follow=True)
    
    if response.status_code == 200:
        # Vérifier si l'utilisateur a été créé
        if User.objects.filter(username=test_data['username']).exists():
            user = User.objects.get(username=test_data['username'])
            print(f"   ✓ Utilisateur créé: {user.username}")
            print(f"   ✓ Nom complet: {user.get_full_name()}")
            print(f"   ✓ Email: {user.email}")
            
            # Vérifier si l'utilisateur est connecté (redirection après inscription)
            if response.redirect_chain:
                print(f"   ✓ Redirection vers: {response.redirect_chain[-1][0]}")
            
            return True
        else:
            print("   ✗ L'utilisateur n'a pas été créé")
            if hasattr(response, 'context') and 'form' in response.context:
                form = response.context['form']
                if form.errors:
                    print("   Erreurs du formulaire:")
                    for field, errors in form.errors.items():
                        print(f"     - {field}: {errors}")
            return False
    else:
        print(f"   ✗ Erreur HTTP: {response.status_code}")
        return False


def test_connexion_vue():
    """Test de la connexion via la vue"""
    print("\n" + "=" * 60)
    print("TEST DE CONNEXION VIA LA VUE")
    print("=" * 60)
    
    client = Client()
    
    # Données de connexion
    username = 'client_test'
    password = 'SecurePass123!'
    
    # Vérifier que l'utilisateur existe
    if not User.objects.filter(username=username).exists():
        print(f"⚠️  L'utilisateur '{username}' n'existe pas.")
        print("   Création de l'utilisateur pour le test...")
        User.objects.create_user(
            username=username,
            email='client@test.com',
            password=password,
            first_name='Client',
            last_name='Test'
        )
        print("   ✓ Utilisateur créé")
    
    # Accéder à la page de connexion
    print("\n1. Accès à la page de connexion...")
    response = client.get(reverse('connexion'))
    print(f"   ✓ Code HTTP: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✓ Page de connexion accessible")
    else:
        print("   ✗ Erreur lors de l'accès à la page")
        return False
    
    # Soumettre le formulaire de connexion
    print("\n2. Soumission du formulaire de connexion...")
    response = client.post(reverse('connexion'), {
        'username': username,
        'password': password
    }, follow=True)
    
    if response.status_code == 200:
        # Vérifier si l'utilisateur est connecté
        if '_auth_user_id' in client.session:
            user_id = client.session['_auth_user_id']
            user = User.objects.get(id=user_id)
            print(f"   ✓ Connexion réussie!")
            print(f"   ✓ Utilisateur connecté: {user.username}")
            print(f"   ✓ Nom complet: {user.get_full_name()}")
            
            if response.redirect_chain:
                print(f"   ✓ Redirection vers: {response.redirect_chain[-1][0]}")
            
            return True
        else:
            print("   ✗ L'utilisateur n'est pas connecté")
            return False
    else:
        print(f"   ✗ Erreur HTTP: {response.status_code}")
        return False


def test_acces_protege():
    """Test d'accès aux pages protégées"""
    print("\n" + "=" * 60)
    print("TEST D'ACCÈS AUX PAGES PROTÉGÉES")
    print("=" * 60)
    
    client = Client()
    
    # Test sans connexion
    print("\n1. Test d'accès au panier sans connexion...")
    response = client.get(reverse('panier'), follow=True)
    
    if response.status_code == 200:
        # Devrait rediriger vers la page de connexion
        if response.redirect_chain:
            redirect_url = response.redirect_chain[-1][0]
            if 'connexion' in redirect_url:
                print("   ✓ Redirection vers la page de connexion (comportement attendu)")
            else:
                print(f"   ⚠️  Redirection vers: {redirect_url}")
        else:
            print("   ⚠️  Pas de redirection (peut être normal selon la config)")
    
    # Test avec connexion
    print("\n2. Test d'accès au panier avec connexion...")
    username = 'client_test'
    password = 'SecurePass123!'
    
    # S'assurer que l'utilisateur existe
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(
            username=username,
            email='client@test.com',
            password=password,
            first_name='Client',
            last_name='Test'
        )
    
    # Se connecter
    client.post(reverse('connexion'), {
        'username': username,
        'password': password
    })
    
    # Accéder au panier
    response = client.get(reverse('panier'))
    
    if response.status_code == 200:
        print("   ✓ Accès au panier autorisé")
        print("   ✓ Page du panier accessible")
        return True
    else:
        print(f"   ✗ Erreur HTTP: {response.status_code}")
        return False


def main():
    """Fonction principale"""
    print("\n🧪 TESTS COMPLETS D'AUTHENTIFICATION")
    print("=" * 60)
    
    # Test d'inscription
    inscription_ok = test_inscription_vue()
    
    # Test de connexion
    connexion_ok = test_connexion_vue()
    
    # Test d'accès protégé
    acces_ok = test_acces_protege()
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    print(f"Inscription: {'✓ Réussi' if inscription_ok else '✗ Échoué'}")
    print(f"Connexion: {'✓ Réussi' if connexion_ok else '✗ Échoué'}")
    print(f"Accès protégé: {'✓ Réussi' if acces_ok else '✗ Échoué'}")
    
    if inscription_ok and connexion_ok and acces_ok:
        print("\n🎉 Tous les tests sont réussis!")
    else:
        print("\n⚠️  Certains tests ont échoué")
    
    print("=" * 60)


if __name__ == '__main__':
    main()

