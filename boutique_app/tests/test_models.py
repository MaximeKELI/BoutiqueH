"""
Tests unitaires pour les modèles
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal
from boutique_app.models import (
    Categorie, Modele, Fournisseur, Produit, Panier, 
    ItemPanier, Commande, Vente, AvisProduit
)


class CategorieModelTest(TestCase):
    """Tests pour le modèle Categorie"""
    
    def setUp(self):
        self.categorie = Categorie.objects.create(
            nom="Boissons",
            description="Toutes sortes de boissons",
            active=True
        )
    
    def test_categorie_creation(self):
        """Test la création d'une catégorie"""
        self.assertEqual(self.categorie.nom, "Boissons")
        self.assertTrue(self.categorie.active)
        self.assertIsNotNone(self.categorie.date_creation)
    
    def test_categorie_str(self):
        """Test la méthode __str__"""
        self.assertEqual(str(self.categorie), "Boissons")
    
    def test_categorie_unique_name(self):
        """Test que le nom de catégorie est unique"""
        with self.assertRaises(Exception):
            Categorie.objects.create(nom="Boissons")


class ModeleModelTest(TestCase):
    """Tests pour le modèle Modele"""
    
    def setUp(self):
        self.modele = Modele.objects.create(
            nom="500ml",
            description="Format 500ml"
        )
    
    def test_modele_creation(self):
        """Test la création d'un modèle"""
        self.assertEqual(self.modele.nom, "500ml")
        self.assertIsNotNone(self.modele.date_creation)


class FournisseurModelTest(TestCase):
    """Tests pour le modèle Fournisseur"""
    
    def setUp(self):
        self.fournisseur = Fournisseur.objects.create(
            nom="Distributeur ABC",
            contact="Jean Dupont",
            telephone="+225 07 12 34 56 78",
            email="contact@distributeur-abc.com",
            actif=True
        )
    
    def test_fournisseur_creation(self):
        """Test la création d'un fournisseur"""
        self.assertEqual(self.fournisseur.nom, "Distributeur ABC")
        self.assertTrue(self.fournisseur.actif)
        self.assertIsNotNone(self.fournisseur.date_creation)
    
    def test_fournisseur_str(self):
        """Test la méthode __str__"""
        self.assertEqual(str(self.fournisseur), "Distributeur ABC")


class ProduitModelTest(TestCase):
    """Tests pour le modèle Produit"""
    
    def setUp(self):
        self.categorie = Categorie.objects.create(nom="Boissons")
        self.fournisseur = Fournisseur.objects.create(nom="Fournisseur Test")
        self.produit = Produit.objects.create(
            nom="Eau minérale",
            description="Eau minérale naturelle",
            categorie=self.categorie,
            fournisseur=self.fournisseur,
            prix_achat=Decimal('200.00'),
            prix_vente=Decimal('300.00'),
            quantite_stock=100,
            quantite_minimum=10,
            active=True
        )
    
    def test_produit_creation(self):
        """Test la création d'un produit"""
        self.assertEqual(self.produit.nom, "Eau minérale")
        self.assertEqual(self.produit.prix_achat, Decimal('200.00'))
        self.assertEqual(self.produit.quantite_stock, 100)
        self.assertTrue(self.produit.active)
    
    def test_prix_affichage_normal(self):
        """Test prix_affichage sans promotion"""
        self.assertEqual(self.produit.prix_affichage, Decimal('300.00'))
    
    def test_prix_affichage_promotion(self):
        """Test prix_affichage avec promotion"""
        self.produit.en_promotion = True
        self.produit.prix_promo = Decimal('250.00')
        self.produit.save()
        self.assertEqual(self.produit.prix_affichage, Decimal('250.00'))
    
    def test_reduction_calculation(self):
        """Test le calcul de la réduction"""
        self.produit.en_promotion = True
        self.produit.prix_promo = Decimal('240.00')  # 20% de réduction
        self.produit.save()
        self.assertAlmostEqual(self.produit.reduction, 20.0, places=1)
    
    def test_marge_benefice(self):
        """Test le calcul de la marge de bénéfice"""
        # Marge = ((300 - 200) / 200) * 100 = 50%
        self.assertAlmostEqual(self.produit.marge_benefice, 50.0, places=1)
    
    def test_valeur_stock(self):
        """Test le calcul de la valeur du stock"""
        # Valeur = 100 * 200 = 20000
        self.assertEqual(self.produit.valeur_stock, Decimal('20000.00'))
    
    def test_stock_faible(self):
        """Test la détection de stock faible"""
        self.produit.quantite_stock = 5  # En dessous du minimum (10)
        self.produit.save()
        self.assertTrue(self.produit.stock_faible)
        
        self.produit.quantite_stock = 15
        self.produit.save()
        self.assertFalse(self.produit.stock_faible)
    
    def test_produit_prix_achat_minimum(self):
        """Test que le prix d'achat doit être positif"""
        produit = Produit(
            nom="Test",
            categorie=self.categorie,
            prix_achat=Decimal('0.00'),  # Prix invalide
            prix_vente=Decimal('100.00')
        )
        with self.assertRaises(ValidationError):
            produit.full_clean()


class PanierModelTest(TestCase):
    """Tests pour le modèle Panier"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50
        )
        self.panier = Panier.objects.create(
            utilisateur=self.user,
            statut='en_cours'
        )
    
    def test_panier_creation(self):
        """Test la création d'un panier"""
        self.assertEqual(self.panier.utilisateur, self.user)
        self.assertEqual(self.panier.statut, 'en_cours')
    
    def test_panier_total_empty(self):
        """Test le total d'un panier vide"""
        self.assertEqual(self.panier.total, 0)
    
    def test_panier_total_with_items(self):
        """Test le total d'un panier avec articles"""
        ItemPanier.objects.create(
            panier=self.panier,
            produit=self.produit,
            quantite=2,
            prix_unitaire=Decimal('150.00')
        )
        # Total = 2 * 150 = 300
        self.assertEqual(self.panier.total, Decimal('300.00'))


class ItemPanierModelTest(TestCase):
    """Tests pour le modèle ItemPanier"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50
        )
        self.panier = Panier.objects.create(utilisateur=self.user)
        self.item = ItemPanier.objects.create(
            panier=self.panier,
            produit=self.produit,
            quantite=3,
            prix_unitaire=Decimal('150.00')
        )
    
    def test_item_creation(self):
        """Test la création d'un item de panier"""
        self.assertEqual(self.item.produit, self.produit)
        self.assertEqual(self.item.quantite, 3)
    
    def test_item_sous_total(self):
        """Test le calcul du sous-total"""
        # Sous-total = 3 * 150 = 450
        self.assertEqual(self.item.sous_total, Decimal('450.00'))
    
    def test_item_unique_produit_panier(self):
        """Test qu'un produit ne peut être qu'une fois dans un panier"""
        with self.assertRaises(Exception):
            ItemPanier.objects.create(
                panier=self.panier,
                produit=self.produit,
                quantite=1,
                prix_unitaire=Decimal('150.00')
            )


class CommandeModelTest(TestCase):
    """Tests pour le modèle Commande"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50
        )
        self.panier = Panier.objects.create(utilisateur=self.user, statut='en_cours')
        ItemPanier.objects.create(
            panier=self.panier,
            produit=self.produit,
            quantite=2,
            prix_unitaire=Decimal('150.00')
        )
    
    def test_commande_creation(self):
        """Test la création d'une commande"""
        commande = Commande.objects.create(
            panier=self.panier,
            montant_total=Decimal('300.00'),
            statut='en_attente'
        )
        self.assertIsNotNone(commande.numero_commande)
        self.assertIn('CMD-', commande.numero_commande)
        self.assertEqual(commande.statut, 'en_attente')


class AvisProduitModelTest(TestCase):
    """Tests pour le modèle AvisProduit"""
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser')
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50
        )
    
    def test_avis_creation(self):
        """Test la création d'un avis"""
        avis = AvisProduit.objects.create(
            produit=self.produit,
            utilisateur=self.user,
            note=5,
            commentaire="Excellent produit!",
            approuve=True
        )
        self.assertEqual(avis.note, 5)
        self.assertEqual(avis.commentaire, "Excellent produit!")
        self.assertTrue(avis.approuve)
    
    def test_avis_unique_per_user(self):
        """Test qu'un utilisateur ne peut donner qu'un avis par produit"""
        AvisProduit.objects.create(
            produit=self.produit,
            utilisateur=self.user,
            note=5
        )
        with self.assertRaises(Exception):
            AvisProduit.objects.create(
                produit=self.produit,
                utilisateur=self.user,
                note=4
            )

