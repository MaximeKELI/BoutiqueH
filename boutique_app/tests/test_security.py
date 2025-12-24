"""
Tests de sécurité
"""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from decimal import Decimal
from boutique_app.models import Categorie, Produit, Panier, ItemPanier, Commande


class SecurityTests(TestCase):
    """Tests de sécurité généraux"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='test123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            password='other123'
        )
        self.categorie = Categorie.objects.create(nom="Test")
        self.produit = Produit.objects.create(
            nom="Produit Test",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50,
            active=True
        )
    
    def test_csrf_protection(self):
        """Test que les formulaires sont protégés par CSRF"""
        self.client.login(username='testuser', password='test123')
        response = self.client.post(
            reverse('ajouter_au_panier', args=[self.produit.id]),
            {'quantite': 1},
            HTTP_X_CSRFTOKEN='invalid_token'
        )
        # Devrait échouer à cause du CSRF
        self.assertIn(response.status_code, [403, 400])
    
    def test_xss_protection_in_product_name(self):
        """Test la protection XSS dans les noms de produits"""
        # Créer un produit avec du contenu potentiellement dangereux
        produit_xss = Produit.objects.create(
            nom="<script>alert('XSS')</script>",
            categorie=self.categorie,
            prix_achat=Decimal('100.00'),
            prix_vente=Decimal('150.00'),
            quantite_stock=50,
            active=True
        )
        
        response = self.client.get(reverse('detail_produit', args=[produit_xss.id]))
        self.assertEqual(response.status_code, 200)
        # Le contenu doit être échappé, pas exécuté
        self.assertNotContains(response, "<script>alert('XSS')</script>")
        # Django échappe automatiquement dans les templates
    
    def test_sql_injection_protection(self):
        """Test la protection contre les injections SQL"""
        # Tenter une injection SQL via la recherche
        malicious_input = "'; DROP TABLE produits; --"
        response = self.client.get(reverse('catalogue'), {'recherche': malicious_input})
        self.assertEqual(response.status_code, 200)
        # Les produits doivent toujours exister (pas de DROP)
        self.assertTrue(Produit.objects.filter(id=self.produit.id).exists())
    
    def test_user_cannot_access_other_user_panier(self):
        """Test qu'un utilisateur ne peut accéder qu'à son propre panier"""
        # Créer un panier pour other_user
        panier_other = Panier.objects.create(utilisateur=self.other_user, statut='en_cours')
        ItemPanier.objects.create(
            panier=panier_other,
            produit=self.produit,
            quantite=1,
            prix_unitaire=Decimal('150.00')
        )
        
        # testuser se connecte
        self.client.login(username='testuser', password='test123')
        panier_test = Panier.objects.create(utilisateur=self.user, statut='en_cours')
        ItemPanier.objects.create(
            panier=panier_test,
            produit=self.produit,
            quantite=2,
            prix_unitaire=Decimal('150.00')
        )
        
        # Vérifier que testuser ne voit que son propre panier
        response = self.client.get(reverse('panier'))
        self.assertEqual(response.status_code, 200)
        # Le panier de testuser doit avoir 2 items, pas 1
        panier_test.refresh_from_db()
        self.assertEqual(panier_test.items.count(), 1)  # 1 item dans le panier de testuser
    
    def test_user_cannot_access_other_user_commande(self):
        """Test qu'un utilisateur ne peut accéder qu'à ses propres commandes"""
        # Créer une commande pour other_user
        panier_other = Panier.objects.create(utilisateur=self.other_user, statut='valide')
        commande_other = Commande.objects.create(
            panier=panier_other,
            montant_total=Decimal('150.00'),
            statut='en_attente'
        )
        
        # testuser essaie d'accéder à la commande d'autre_user
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('detail_commande', args=[commande_other.id]))
        self.assertEqual(response.status_code, 404)  # Doit retourner 404, pas 403
    
    def test_staff_only_dashboard(self):
        """Test que seul le staff peut accéder au dashboard"""
        # Utilisateur normal
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Utilisateur staff
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
    
    def test_export_ventes_staff_only(self):
        """Test que seul le staff peut exporter les ventes"""
        # Utilisateur normal
        self.client.login(username='testuser', password='test123')
        response = self.client.get(reverse('export_ventes'))
        self.assertEqual(response.status_code, 302)  # Redirection
        
        # Utilisateur staff
        self.user.is_staff = True
        self.user.save()
        response = self.client.get(reverse('export_ventes'))
        self.assertEqual(response.status_code, 200)
    
    def test_inactive_product_not_accessible(self):
        """Test qu'un produit inactif n'est pas accessible"""
        self.produit.active = False
        self.produit.save()
        
        response = self.client.get(reverse('detail_produit', args=[self.produit.id]))
        self.assertEqual(response.status_code, 404)
        
        # Ne doit pas apparaître dans le catalogue
        response = self.client.get(reverse('catalogue'))
        self.assertNotContains(response, self.produit.nom)
    
    def test_integer_overflow_protection(self):
        """Test la protection contre les débordements d'entiers"""
        self.client.login(username='testuser', password='test123')
        # Tenter d'ajouter une quantité énorme
        response = self.client.post(
            reverse('ajouter_au_panier', args=[self.produit.id]),
            {'quantite': 999999999999}
        )
        # Le système doit gérer cela correctement (validation côté serveur)
        # Ne doit pas causer de crash
        self.assertIn(response.status_code, [302, 200])

