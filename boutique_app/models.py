from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class Categorie(models.Model):
    """Catégorie de produits"""
    nom = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Catégorie"
        verbose_name_plural = "Catégories"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Modele(models.Model):
    """Modèle/Variante de produit"""
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Modèle"
        verbose_name_plural = "Modèles"
        ordering = ['nom']

    def __str__(self):
        return self.nom


class Produit(models.Model):
    """Produit de la boutique"""
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='produits')
    modele = models.ForeignKey(Modele, on_delete=models.SET_NULL, null=True, blank=True, related_name='produits')
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    quantite_stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    quantite_minimum = models.IntegerField(default=10, validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    code_barre = models.CharField(max_length=100, unique=True, blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Produit"
        verbose_name_plural = "Produits"
        ordering = ['-date_creation']

    def __str__(self):
        return f"{self.nom} - {self.categorie.nom}"

    @property
    def marge_benefice(self):
        """Calcule la marge de bénéfice"""
        if self.prix_achat > 0:
            return ((self.prix_vente - self.prix_achat) / self.prix_achat) * 100
        return 0

    @property
    def valeur_stock(self):
        """Valeur totale du stock"""
        return self.quantite_stock * self.prix_achat

    @property
    def stock_faible(self):
        """Vérifie si le stock est faible"""
        return self.quantite_stock <= self.quantite_minimum


class Panier(models.Model):
    """Panier d'achat"""
    STATUT_CHOICES = [
        ('en_cours', 'En cours'),
        ('valide', 'Validé'),
        ('annule', 'Annulé'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='paniers', null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_cours')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Panier"
        verbose_name_plural = "Paniers"
        ordering = ['-date_creation']

    def __str__(self):
        return f"Panier #{self.id} - {self.get_statut_display()}"

    @property
    def total(self):
        """Calcule le total du panier"""
        return sum(item.sous_total for item in self.items.all())


class ItemPanier(models.Model):
    """Article dans le panier"""
    panier = models.ForeignKey(Panier, on_delete=models.CASCADE, related_name='items')
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    date_ajout = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Article du panier"
        verbose_name_plural = "Articles du panier"
        unique_together = ['panier', 'produit']

    def __str__(self):
        return f"{self.produit.nom} x{self.quantite}"

    @property
    def sous_total(self):
        """Calcule le sous-total"""
        return self.quantite * self.prix_unitaire


class Commande(models.Model):
    """Commande validée"""
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('en_preparation', 'En préparation'),
        ('livree', 'Livrée'),
        ('annulee', 'Annulée'),
    ]

    panier = models.OneToOneField(Panier, on_delete=models.CASCADE, related_name='commande')
    numero_commande = models.CharField(max_length=50, unique=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    date_commande = models.DateTimeField(auto_now_add=True)
    date_livraison = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Commande"
        verbose_name_plural = "Commandes"
        ordering = ['-date_commande']

    def __str__(self):
        return f"Commande #{self.numero_commande}"

    def save(self, *args, **kwargs):
        if not self.numero_commande:
            self.numero_commande = f"CMD-{timezone.now().strftime('%Y%m%d')}-{self.id or 'NEW'}"
        super().save(*args, **kwargs)


class Vente(models.Model):
    """Enregistrement de vente"""
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='ventes')
    quantite = models.IntegerField(validators=[MinValueValidator(1)])
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    montant_total = models.DecimalField(max_digits=10, decimal_places=2)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE, related_name='ventes', null=True, blank=True)
    date_vente = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vente"
        verbose_name_plural = "Ventes"
        ordering = ['-date_vente']

    def __str__(self):
        return f"Vente {self.produit.nom} - {self.date_vente.strftime('%d/%m/%Y')}"

