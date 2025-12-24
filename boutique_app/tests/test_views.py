"""
Tests unitaires pour les vues
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from boutique_app.models import (
    Categorie, Modele, Produit, Panier, ItemPanier, 
    Commande, Vente
)


class AccueilViewTest(TestCase):
    """Tests pour la vue d'accueil"""
    
    def setUp(self):
        self.client = Client()
    
    def test_accueil_view(self):
        """Test l'accès à la page d'accueil"""
        response = self.client.get(reverse('accueil'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "La Gloire de Dieu")
    
    def test_accueil_redirect_if_authenticated(self):
        """Test la redirection si l'utilisateur est connecté"""
        user = User.objects.create_user(username='testuser', password='test123')
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('accueil'))
        self.assertEqual(response.status_code, 302)  # Redirection


class CatalogueViewTest(TestCase):
    """Tests pour la vue catalogue"""
    
    def setUp(self):
        self.client = Client()
        self.categorie = Categorie.objects.create(nom="Boissons", active=True)
        self.produit = Produit.objects.create(
            nom="Eau minérale",
            categorie=self.categorie,
            prix_achat=Decimal('200.00'),
            prix_vente=Decimal('300.00'),
            quantite_stock=100,
            active=True
        )
    
    def test_catalogue_view(self):
        """Test l'accès au catalogue"""
        response = self.client.get(reverse('catalogue'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Notre Catalogue")
    
    def test_catalogue_filter_by_category(self):
        """Test le filtre par catégorie"""
        response = self.client.get(reverse('catalogue'), {'categorie': self.categorie.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produit.nom)
    
    def test_catalogue_search(self):
        """Test la recherche dans le catalogue"""
        response = self.client.get(reverse('catalogue'), {'recherche': 'Eau'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eau minérale")
    
    def test_catalogue_promotion_filter(self):
        """Test le filtre par promotions"""
        self.produit.en_promotion = True
        self.produit.prix_promo = Decimal('250.00')
        self.produit.save()
        
        response = self.client.get(reverse('catalogue'), {'promotion': '1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eau minérale")


class DetailProduitViewTest(TestCase):
    """Tests pour la vue détail produit"""
    
    def setUp(self):
        self.client = Client()
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50,
            active=True
        )
    
    def test_detail_produit_view(self):
        """Test l'accès à la page détail produit"""
        response = self.client.get(reverse('detail_produit', args=[self.produit.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.produit.nom)
    
    def test_detail_produit_404(self):
        """Test 404 pour un produit inexistant"""
        response = self.client.get(reverse('detail_produit', args=[99999]))
        self.assertEqual(response.status_code, 404)
    
    def test_detail_produit_inactive(self):
        """Test qu'un produit inactif n'est pas accessible"""
        self.produit.active = False
        self.produit.save()
        response = self.client.get(reverse('detail_produit', args=[self.produit.id]))
        self.assertEqual(response.status_code, 404)


class PanierViewTest(TestCase):
    """Tests pour les vues panier"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50,
            active=True
        )
    
    def test_panier_requires_login(self):
        """Test que le panier nécessite une connexion"""
        response = self.client.get(reverse('panier'))
        self.assertEqual(response.status_code, 302)  # Redirection vers login
    
    def test_panier_view_authenticated(self):
        """Test l'accès au panier pour un utilisateur connecté"""
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('panier'))
        self.assertEqual(response.status_code, 200)
    
    def test_ajouter_au_panier(self):
        """Test l'ajout d'un produit au panier"""
        self.client.login(username='testuser', password='test123')
        response = self.client.post(
            reverse('ajouter_au_panier', args=[self.produit.id]),
            {'quantite': 2}
        )
        self.assertEqual(response.status_code, 302)  # Redirection
        
        panier = Panier.objects.get(utilisateur=self.user, statut='en_cours')
        self.assertEqual(panier.items.count(), 1)
        item = panier.items.first()
        self.assertEqual(item.quantite, 2)
    
    def test_ajouter_au_panier_stock_insuffisant(self):
        """Test l'ajout avec stock insuffisant"""
        self.client.login(username='testuser', password='test123')
        response = self.client.post(
            reverse('ajouter_au_panier', args=[self.produit.id]),
            {'quantite': 1000}  # Plus que le stock disponible
        )
        # Devrait rester sur la page avec un message d'erreur
        self.assertEqual(response.status_code, 302)


class CommandeViewTest(TestCase):
    """Tests pour les vues commande"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='test123')
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50,
            active=True
        )
        self.panier = Panier.objects.create(utilisateur=self.user, statut='en_cours')
        ItemPanier.objects.create(
            panier=self.panier,
            produit=self.produit,
            quantite=2,
            prix_unitaire=Decimal('150.00')
        )
    
    def test_mes_commandes_requires_login(self):
        """Test que mes_commandes nécessite une connexion"""
        response = self.client.get(reverse('mes_commandes'))
        self.assertEqual(response.status_code, 302)
    
    def test_passer_commande(self):
        """Test le passage d'une commande"""
        self.client.login(username='testuser', password='test123')
        response = self.client.post(reverse('passer_commande'))
        self.assertEqual(response.status_code, 302)  # Redirection
        
        commande = Commande.objects.filter(panier__utilisateur=self.user).first()
        self.assertIsNotNone(commande)
        self.assertEqual(commande.montant_total, Decimal('300.00'))
        self.assertEqual(commande.statut, 'en_attente')
        
        # Le panier doit être marqué comme validé
        self.panier.refresh_from_db()
        self.assertEqual(self.panier.statut, 'valide')
    
    def test_passer_commande_panier_vide(self):
        """Test le passage d'une commande avec panier vide"""
        self.client.login(username='testuser', password='test123')
        # Vider le panier
        self.panier.items.all().delete()
        
        response = self.client.post(reverse('passer_commande'))
        self.assertEqual(response.status_code, 302)  # Redirection avec message d'erreur
        
        # Aucune commande ne doit être créée
        self.assertEqual(Commande.objects.filter(panier__utilisateur=self.user).count(), 0)


class AdminViewsTest(TestCase):
    """Tests pour les vues admin"""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.regular_user = User.objects.create_user(
            username='user',
            password='user123'
        )
    
    def test_dashboard_requires_staff(self):
        """Test que le dashboard nécessite les droits staff"""
        # Utilisateur normal
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Admin
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_export_ventes_requires_staff(self):
        """Test que l'export nécessite les droits staff"""
        # Utilisateur normal
        self.client.login(username='user', password='user123')
        response = self.client.get(reverse('export_ventes'))
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Admin
        self.client.login(username='admin', password='admin123')
        response = self.client.get(reverse('export_ventes'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')


class InscriptionViewTest(TestCase):
    """Tests pour la vue d'inscription"""
    
    def setUp(self):
        self.client = Client()
    
    def test_inscription_view_get(self):
        """Test l'accès au formulaire d'inscription"""
        response = self.client.get(reverse('inscription'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Créer un compte")
    
    def test_inscription_view_post(self):
        """Test l'inscription d'un nouvel utilisateur"""
        response = self.client.post(reverse('inscription'), {
            'username': 'newuser',
            'first_name': 'New',
            'last_name': 'User',
            'email': 'newuser@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        })
        self.assertEqual(response.status_code, 302)  # Redirection après succès
        
        # Vérifier que l'utilisateur a été créé
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_inscription_redirect_if_authenticated(self):
        """Test la redirection si déjà connecté"""
        User.objects.create_user(username='testuser', password='test123')
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('inscription'))
        self.assertEqual(response.status_code, 302)

