from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Avg, Max, Min, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Produit, Categorie, Commande, Vente, Panier, ItemPanier
import json
from collections import defaultdict


@staff_member_required
def dashboard(request):
    """Dashboard principal avec toutes les statistiques"""
    
    # Périodes de temps
    aujourdhui = timezone.now().date()
    cette_semaine = aujourdhui - timedelta(days=7)
    ce_mois = aujourdhui - timedelta(days=30)
    cette_annee = aujourdhui - timedelta(days=365)
    
    # Statistiques générales
    total_produits = Produit.objects.filter(active=True).count()
    total_categories = Categorie.objects.filter(active=True).count()
    total_commandes = Commande.objects.count()
    total_paniers = Panier.objects.filter(statut='valide').count()
    
    # Statistiques financières
    ventes_aujourdhui = Vente.objects.filter(date_vente__date=aujourdhui).aggregate(
        total=Sum('montant_total'),
        nombre=Count('id')
    )
    
    ventes_semaine = Vente.objects.filter(date_vente__date__gte=cette_semaine).aggregate(
        total=Sum('montant_total'),
        nombre=Count('id')
    )
    
    ventes_mois = Vente.objects.filter(date_vente__date__gte=ce_mois).aggregate(
        total=Sum('montant_total'),
        nombre=Count('id')
    )
    
    ventes_annee = Vente.objects.filter(date_vente__date__gte=cette_annee).aggregate(
        total=Sum('montant_total'),
        nombre=Count('id')
    )
    
    # Valeur du stock
    valeur_stock_total = sum(p.valeur_stock for p in Produit.objects.filter(active=True))
    
    # Produits en stock faible
    produits_stock_faible = Produit.objects.filter(
        active=True,
        quantite_stock__lte=F('quantite_minimum')
    ).count()
    
    # Statistiques par catégorie
    stats_categories = []
    for categorie in Categorie.objects.filter(active=True):
        produits_cat = Produit.objects.filter(categorie=categorie, active=True)
        stats_categories.append({
            'nom': categorie.nom,
            'nombre_produits': produits_cat.count(),
            'valeur_stock': sum(p.valeur_stock for p in produits_cat),
            'ventes_mois': Vente.objects.filter(
                produit__categorie=categorie,
                date_vente__date__gte=ce_mois
            ).aggregate(total=Sum('montant_total'))['total'] or 0
        })
    
    # Top produits vendus (ce mois)
    top_produits = Vente.objects.filter(
        date_vente__date__gte=ce_mois
    ).values('produit__nom').annotate(
        total_ventes=Sum('montant_total'),
        quantite_vendue=Sum('quantite')
    ).order_by('-total_ventes')[:10]
    
    # Statistiques min/max
    produits_stats = Produit.objects.filter(active=True).aggregate(
        prix_min=Min('prix_vente'),
        prix_max=Max('prix_vente'),
        prix_moyen=Avg('prix_vente'),
        stock_min=Min('quantite_stock'),
        stock_max=Max('quantite_stock'),
        stock_moyen=Avg('quantite_stock'),
        marge_min=Min(F('prix_vente') - F('prix_achat')),
        marge_max=Max(F('prix_vente') - F('prix_achat'))
    )
    
    # Prévisions (basées sur les tendances)
    ventes_derniers_mois = []
    for i in range(6):
        date_debut = ce_mois - timedelta(days=30 * (i + 1))
        date_fin = ce_mois - timedelta(days=30 * i)
        total = Vente.objects.filter(
            date_vente__date__gte=date_debut,
            date_vente__date__lt=date_fin
        ).aggregate(total=Sum('montant_total'))['total'] or 0
        ventes_derniers_mois.append(float(total))
    
    # Prévision simple (moyenne des 3 derniers mois)
    if len(ventes_derniers_mois) >= 3:
        moyenne_3_mois = sum(ventes_derniers_mois[:3]) / 3
    else:
        moyenne_3_mois = sum(ventes_derniers_mois) / len(ventes_derniers_mois) if ventes_derniers_mois else 0
    
    # Tendances des ventes par jour (7 derniers jours)
    ventes_par_jour = []
    for i in range(7):
        date = aujourdhui - timedelta(days=i)
        total = Vente.objects.filter(date_vente__date=date).aggregate(
            total=Sum('montant_total')
        )['total'] or 0
        ventes_par_jour.append({
            'date': date.strftime('%d/%m'),
            'total': float(total)
        })
    ventes_par_jour.reverse()
    
    # Commandes en attente
    commandes_en_attente = Commande.objects.filter(statut='en_attente').count()
    
    context = {
        'total_produits': total_produits,
        'total_categories': total_categories,
        'total_commandes': total_commandes,
        'total_paniers': total_paniers,
        'ventes_aujourdhui': ventes_aujourdhui['total'] or 0,
        'nombre_ventes_aujourdhui': ventes_aujourdhui['nombre'] or 0,
        'ventes_semaine': ventes_semaine['total'] or 0,
        'nombre_ventes_semaine': ventes_semaine['nombre'] or 0,
        'ventes_mois': ventes_mois['total'] or 0,
        'nombre_ventes_mois': ventes_mois['nombre'] or 0,
        'ventes_annee': ventes_annee['total'] or 0,
        'nombre_ventes_annee': ventes_annee['nombre'] or 0,
        'valeur_stock_total': valeur_stock_total,
        'produits_stock_faible': produits_stock_faible,
        'stats_categories': stats_categories,
        'top_produits': top_produits,
        'produits_stats': produits_stats,
        'prevision_mois': moyenne_3_mois,
        'ventes_par_jour': json.dumps(ventes_par_jour),
        'commandes_en_attente': commandes_en_attente,
    }
    
    return render(request, 'admin/dashboard.html', context)

