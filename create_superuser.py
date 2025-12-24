#!/usr/bin/env python
"""
Script pour créer un superutilisateur
"""
import os
import sys
import django
import getpass

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

def create_superuser():
    print("=" * 60)
    print("CRÉATION D'UN SUPERUTILISATEUR")
    print("=" * 60)
    
    # Afficher les superutilisateurs existants
    existing_superusers = User.objects.filter(is_superuser=True)
    if existing_superusers.exists():
        print("\nSuperutilisateurs existants:")
        for user in existing_superusers:
            print(f"  - {user.username} ({user.email})")
        print()
    
    # Demander les informations
    print("Entrez les informations pour le nouveau superutilisateur:")
    print()
    
    username = input("Nom d'utilisateur: ").strip()
    if not username:
        print("❌ Le nom d'utilisateur est requis")
        return
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"\n⚠️  L'utilisateur '{username}' existe déjà.")
        response = input("Voulez-vous le transformer en superutilisateur? (o/n): ").strip().lower()
        
        if response == 'o':
            user.is_superuser = True
            user.is_staff = True
            email = input(f"Email (actuel: {user.email}): ").strip() or user.email
            user.email = email
            password = getpass.getpass("Nouveau mot de passe (laissez vide pour garder l'ancien): ")
            if password:
                user.set_password(password)
            user.save()
            print(f"\n✓ Superutilisateur '{username}' mis à jour avec succès!")
            print(f"  Email: {user.email}")
            return
        else:
            print("Opération annulée")
            return
    
    # Créer un nouvel utilisateur
    email = input("Email: ").strip()
    if not email:
        email = f"{username}@lagloirededieu.com"
        print(f"Email par défaut utilisé: {email}")
    
    password = getpass.getpass("Mot de passe: ")
    if not password:
        print("❌ Le mot de passe est requis")
        return
    
    password_confirm = getpass.getpass("Confirmer le mot de passe: ")
    if password != password_confirm:
        print("❌ Les mots de passe ne correspondent pas")
        return
    
    # Créer le superutilisateur
    try:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"\n✓ Superutilisateur '{username}' créé avec succès!")
        print(f"  Email: {email}")
        print(f"  ID: {user.id}")
    except Exception as e:
        print(f"\n❌ Erreur lors de la création: {e}")

if __name__ == '__main__':
    create_superuser()


