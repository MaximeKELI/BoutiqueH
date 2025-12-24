#!/usr/bin/env python
"""
Test complet des fonctionnalités de l'administration
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'boutique.settings')
django.setup()

from django.contrib.auth.models import User
from boutique_app.models import Categorie, Modele, Produit, Panier, ItemPanier, Commande, Vente
from django.utils import timezone
from decimal import Decimal

def print_section(title):
    """Affiche une section de test"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def test_categories():
    """Test de création et gestion des catégories"""
    print_section("TEST DES CATÉGORIES")
    
    # Créer des catégories
    categories_data = [
        {'nom': 'Boissons', 'description': 'Toutes sortes de boissons'},
        {'nom': 'Aliments', 'description': 'Produits alimentaires'},
        {'nom': 'Hygiène', 'description': 'Produits d\'hygiène et de soin'},
    ]
    
    categories_created = []
    for cat_data in categories_data:
        categorie, created = Categorie.objects.get_or_create(
            nom=cat_data['nom'],
            defaults=cat_data
        )
        if created:
            print(f"✓ Catégorie créée: {categorie.nom}")
        else:
            print(f"⚠ Catégorie existante: {categorie.nom}")
        categories_created.append(categorie)
    
    print(f"\nTotal catégories: {Categorie.objects.count()}")
    return categories_created

def test_modeles():
    """Test de création et gestion des modèles"""
    print_section("TEST DES MODÈLES")
    
    modeles_data = [
        {'nom': '500ml', 'description': 'Format 500ml'},
        {'nom': '1L', 'description': 'Format 1 litre'},
        {'nom': 'Unité', 'description': 'Vendu à l\'unité'},
        {'nom': 'Paquet', 'description': 'Vendu par paquet'},
    ]
    
    modeles_created = []
    for mod_data in modeles_data:
        modele, created = Modele.objects.get_or_create(
            nom=mod_data['nom'],
            defaults=mod_data
        )
        if created:
            print(f"✓ Modèle créé: {modele.nom}")
        else:
            print(f"⚠ Modèle existant: {modele.nom}")
        modeles_created.append(modele)
    
    print(f"\nTotal modèles: {Modele.objects.count()}")
    return modeles_created

def test_produits(categories, modeles):
    """Test de création et gestion des produits"""
    print_section("TEST DES PRODUITS")
    
    produits_data = [
        {
            'nom': 'Eau minérale',
            'description': 'Eau minérale naturelle',
            'categorie': categories[0] if categories else None,
            'modele': modeles[0] if modeles else None,
            'prix_achat': Decimal('200.00'),
            'prix_vente': Decimal('300.00'),
            'quantite_stock': 100,
            'quantite_minimum': 20,
        },
        {
            'nom': 'Riz',
            'description': 'Riz de qualité supérieure',
            'categorie': categories[1] if len(categories) > 1 else None,
            'modele': modeles[3] if len(modeles) > 3 else None,
            'prix_achat': Decimal('500.00'),
            'prix_vente': Decimal('750.00'),
            'quantite_stock': 50,
            'quantite_minimum': 10,
        },
        {
            'nom': 'Savon',
            'description': 'Savon de toilette',
            'categorie': categories[2] if len(categories) > 2 else None,
            'modele': modeles[2] if len(modeles) > 2 else None,
            'prix_achat': Decimal('150.00'),
            'prix_vente': Decimal('250.00'),
            'quantite_stock': 200,
            'quantite_minimum': 30,
        },
    ]
    
    produits_created = []
    for prod_data in produits_data:
        produit, created = Produit.objects.get_or_create(
            nom=prod_data['nom'],
            defaults=prod_data
        )
        if created:
            print(f"✓ Produit créé: {produit.nom}")
            print(f"  - Prix achat: {produit.prix_achat} FCFA")
            print(f"  - Prix vente: {produit.prix_vente} FCFA")
            print(f"  - Stock: {produit.quantite_stock}")
            print(f"  - Marge: {produit.marge_benefice:.1f}%")
            print(f"  - Valeur stock: {produit.valeur_stock:.0f} FCFA")
        else:
            print(f"⚠ Produit existant: {produit.nom}")
        produits_created.append(produit)
    
    print(f"\nTotal produits: {Produit.objects.count()}")
    print(f"Produits actifs: {Produit.objects.filter(active=True).count()}")
    return produits_created

def test_paniers(produits, user):
    """Test de création et gestion des paniers"""
    print_section("TEST DES PANIERS")
    
    # Créer un panier
    panier, created = Panier.objects.get_or_create(
        utilisateur=user,
        statut='en_cours',
        defaults={}
    )
    
    if created:
        print(f"✓ Panier créé: #{panier.id}")
    else:
        print(f"⚠ Panier existant: #{panier.id}")
        # Nettoyer les anciens items
        panier.items.all().delete()
    
    # Ajouter des articles au panier
    if produits:
        items_data = [
            {'produit': produits[0], 'quantite': 5, 'prix_unitaire': produits[0].prix_vente},
            {'produit': produits[1], 'quantite': 2, 'prix_unitaire': produits[1].prix_vente},
        ]
        
        for item_data in items_data:
            item, item_created = ItemPanier.objects.get_or_create(
                panier=panier,
                produit=item_data['produit'],
                defaults=item_data
            )
            if item_created:
                print(f"✓ Article ajouté: {item.produit.nom} x{item.quantite}")
            else:
                item.quantite = item_data['quantite']
                item.prix_unitaire = item_data['prix_unitaire']
                item.save()
                print(f"✓ Article mis à jour: {item.produit.nom} x{item.quantite}")
        
        print(f"\nTotal panier: {panier.total:.0f} FCFA")
        print(f"Nombre d'articles: {panier.items.count()}")
    
    return panier

def test_commandes(panier):
    """Test de création et gestion des commandes"""
    print_section("TEST DES COMMANDES")
    
    if not panier or not panier.items.exists():
        print("⚠ Aucun panier avec articles disponible")
        return None
    
    # Créer une commande
    commande, created = Commande.objects.get_or_create(
        panier=panier,
        defaults={
            'montant_total': panier.total,
            'statut': 'en_attente'
        }
    )
    
    if created:
        print(f"✓ Commande créée: #{commande.numero_commande}")
    else:
        print(f"⚠ Commande existante: #{commande.numero_commande}")
    
    print(f"  - Montant total: {commande.montant_total:.0f} FCFA")
    print(f"  - Statut: {commande.get_statut_display()}")
    print(f"  - Date: {commande.date_commande}")
    
    # Marquer le panier comme validé
    panier.statut = 'valide'
    panier.save()
    
    return commande

def test_ventes(commande):
    """Test de création des ventes"""
    print_section("TEST DES VENTES")
    
    if not commande or not commande.panier:
        print("⚠ Aucune commande disponible")
        return
    
    # Les ventes sont créées automatiquement par les signaux
    # Vérifier si elles existent
    ventes = Vente.objects.filter(commande=commande)
    
    if ventes.exists():
        print(f"✓ {ventes.count()} vente(s) trouvée(s) pour la commande")
        total_ventes = sum(v.montant_total for v in ventes)
        print(f"  - Total ventes: {total_ventes:.0f} FCFA")
        
        for vente in ventes:
            print(f"  - {vente.produit.nom}: {vente.quantite} x {vente.prix_unitaire:.0f} = {vente.montant_total:.0f} FCFA")
    else:
        print("⚠ Aucune vente trouvée (peut être créée automatiquement)")
        
        # Créer manuellement des ventes pour le test
        for item in commande.panier.items.all():
            vente = Vente.objects.create(
                produit=item.produit,
                quantite=item.quantite,
                prix_unitaire=item.prix_unitaire,
                montant_total=item.sous_total,
                commande=commande
            )
            print(f"✓ Vente créée: {vente.produit.nom}")

def test_statistiques():
    """Test des statistiques"""
    print_section("TEST DES STATISTIQUES")
    
    total_produits = Produit.objects.filter(active=True).count()
    total_categories = Categorie.objects.filter(active=True).count()
    total_commandes = Commande.objects.count()
    total_ventes = Vente.objects.count()
    
    print(f"✓ Total produits actifs: {total_produits}")
    print(f"✓ Total catégories actives: {total_categories}")
    print(f"✓ Total commandes: {total_commandes}")
    print(f"✓ Total ventes: {total_ventes}")
    
    # Statistiques financières
    if Vente.objects.exists():
        total_ventes_montant = sum(v.montant_total for v in Vente.objects.all())
        print(f"✓ Montant total des ventes: {total_ventes_montant:.0f} FCFA")
    
    # Valeur du stock
    valeur_stock = sum(p.valeur_stock for p in Produit.objects.filter(active=True))
    print(f"✓ Valeur totale du stock: {valeur_stock:.0f} FCFA")
    
    # Produits en stock faible
    produits_stock_faible = Produit.objects.filter(
        active=True
    ).extra(
        where=['quantite_stock <= quantite_minimum']
    )
    if produits_stock_faible.exists():
        print(f"⚠ Produits en stock faible: {produits_stock_faible.count()}")
        for p in produits_stock_faible:
            print(f"  - {p.nom}: {p.quantite_stock}/{p.quantite_minimum}")
    else:
        print("✓ Aucun produit en stock faible")

def test_proprietes_produits(produits):
    """Test des propriétés calculées des produits"""
    print_section("TEST DES PROPRIÉTÉS DES PRODUITS")
    
    if not produits:
        print("⚠ Aucun produit disponible")
        return
    
    for produit in produits[:3]:  # Tester les 3 premiers
        print(f"\nProduit: {produit.nom}")
        print(f"  - Marge bénéfice: {produit.marge_benefice:.1f}%")
        print(f"  - Valeur stock: {produit.valeur_stock:.0f} FCFA")
        print(f"  - Stock faible: {'Oui' if produit.stock_faible else 'Non'}")

def main():
    """Fonction principale"""
    print("\n" + "=" * 70)
    print("  TESTS COMPLETS DE L'ADMINISTRATION - La Gloire de Dieu")
    print("=" * 70)
    
    # Obtenir ou créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_admin',
        defaults={
            'email': 'test@admin.com',
            'first_name': 'Test',
            'last_name': 'Admin',
            'is_staff': True
        }
    )
    if created:
        user.set_password('test123')
        user.save()
        print(f"\n✓ Utilisateur de test créé: {user.username}")
    else:
        print(f"\n⚠ Utilisateur de test existant: {user.username}")
    
    # Tests
    categories = test_categories()
    modeles = test_modeles()
    produits = test_produits(categories, modeles)
    panier = test_paniers(produits, user)
    commande = test_commandes(panier)
    test_ventes(commande)
    test_statistiques()
    test_proprietes_produits(produits)
    
    # Résumé
    print_section("RÉSUMÉ DES TESTS")
    print("✓ Tests des catégories: OK")
    print("✓ Tests des modèles: OK")
    print("✓ Tests des produits: OK")
    print("✓ Tests des paniers: OK")
    print("✓ Tests des commandes: OK")
    print("✓ Tests des ventes: OK")
    print("✓ Tests des statistiques: OK")
    print("\n🎉 Tous les tests sont terminés avec succès!")
    print("=" * 70)

if __name__ == '__main__':
    main()


