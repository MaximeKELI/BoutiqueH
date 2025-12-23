from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Commande, Panier, Vente, ItemPanier


@receiver(post_save, sender=Commande)
def creer_ventes_commande(sender, instance, created, **kwargs):
    """Crée des enregistrements de vente lorsqu'une commande est créée"""
    if created and instance.panier:
        # Créer une vente pour chaque article du panier
        for item in instance.panier.items.all():
            Vente.objects.create(
                produit=item.produit,
                quantite=item.quantite,
                prix_unitaire=item.prix_unitaire,
                montant_total=item.sous_total,
                commande=instance
            )
            # Mettre à jour le stock
            item.produit.quantite_stock -= item.quantite
            if item.produit.quantite_stock < 0:
                item.produit.quantite_stock = 0
            item.produit.save()


@receiver(pre_save, sender=Commande)
def calculer_montant_total(sender, instance, **kwargs):
    """Calcule automatiquement le montant total de la commande"""
    if instance.panier:
        instance.montant_total = instance.panier.total


@receiver(pre_save, sender=ItemPanier)
def calculer_sous_total(sender, instance, **kwargs):
    """Calcule automatiquement le sous-total de l'article"""
    if instance.prix_unitaire and instance.quantite:
        # Si le prix unitaire n'est pas défini, utiliser le prix de vente du produit
        if not instance.prix_unitaire:
            instance.prix_unitaire = instance.produit.prix_vente

