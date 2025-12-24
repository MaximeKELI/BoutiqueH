from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Max, Min, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Produit, Categorie, Commande, Vente, Panier, ItemPanier, Fournisseur, AvisProduit
from .forms import InscriptionForm, AjoutPanierForm
import json
from collections import defaultdict


def accueil(request):
    """Page d'accueil publique - uniquement pour les clients"""
    # Rediriger vers le catalogue si l'utilisateur est déjà connecté
    if request.user.is_authenticated:
        return redirect('catalogue')
    return render(request, 'accueil.html')


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
        active=True
    ).extra(
        where=['quantite_stock <= quantite_minimum']
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
    produits_actifs = Produit.objects.filter(active=True)
    produits_stats = produits_actifs.aggregate(
        prix_min=Min('prix_vente'),
        prix_max=Max('prix_vente'),
        prix_moyen=Avg('prix_vente'),
        stock_min=Min('quantite_stock'),
        stock_max=Max('quantite_stock'),
        stock_moyen=Avg('quantite_stock')
    )
    
    # Calculer marge min/max manuellement
    if produits_actifs.exists():
        marges = [(p.prix_vente - p.prix_achat) for p in produits_actifs]
        produits_stats['marge_min'] = min(marges) if marges else 0
        produits_stats['marge_max'] = max(marges) if marges else 0
    else:
        produits_stats['marge_min'] = 0
        produits_stats['marge_max'] = 0
    
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


# ==================== VUES CLIENT ====================

def inscription(request):
    """Page d'inscription pour les clients"""
    if request.user.is_authenticated:
        return redirect('catalogue')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} ! Votre compte a été créé avec succès.')
            return redirect('catalogue')
    else:
        form = InscriptionForm()
    
    return render(request, 'client/inscription.html', {'form': form})


def connexion_client(request):
    """Page de connexion pour les clients"""
    if request.user.is_authenticated:
        return redirect('catalogue')
    
    if request.method == 'POST':
        from django.contrib.auth import authenticate
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.first_name} !')
            next_url = request.GET.get('next', 'catalogue')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'client/connexion.html')


def deconnexion_client(request):
    """Déconnexion du client"""
    logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('accueil')


def catalogue(request):
    """Catalogue des produits pour les clients"""
    produits = Produit.objects.filter(active=True)
    categories = Categorie.objects.filter(active=True)
    
    # Filtres
    categorie_id = request.GET.get('categorie')
    recherche = request.GET.get('recherche')
    promotion = request.GET.get('promotion') == '1'
    
    if categorie_id:
        produits = produits.filter(categorie_id=categorie_id)
    
    if recherche:
        produits = produits.filter(
            Q(nom__icontains=recherche) | Q(description__icontains=recherche)
        )
    
    if promotion:
        produits = produits.filter(en_promotion=True)
    
    # Pagination simple
    from django.core.paginator import Paginator
    paginator = Paginator(produits, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'produits': page_obj,
        'categories': categories,
        'categorie_actuelle': int(categorie_id) if categorie_id else None,
        'recherche': recherche,
        'promotion_filter': promotion,
    }
    
    return render(request, 'client/catalogue.html', context)


def detail_produit(request, produit_id):
    """Page de détail d'un produit"""
    produit = get_object_or_404(Produit, id=produit_id, active=True)
    form = AjoutPanierForm()
    
    # Produits similaires (même catégorie)
    produits_similaires = Produit.objects.filter(
        categorie=produit.categorie,
        active=True
    ).exclude(id=produit.id)[:4]
    
    # Avis approuvés
    avis = AvisProduit.objects.filter(produit=produit, approuve=True).order_by('-date_creation')[:10]
    note_moyenne = avis.aggregate(Avg('note'))['note__avg'] if avis.exists() else None
    
    context = {
        'produit': produit,
        'form': form,
        'produits_similaires': produits_similaires,
        'avis': avis,
        'note_moyenne': note_moyenne,
    }
    
    return render(request, 'client/detail_produit.html', context)


@login_required
def ajouter_au_panier(request, produit_id):
    """Ajouter un produit au panier"""
    produit = get_object_or_404(Produit, id=produit_id, active=True)
    
    if request.method == 'POST':
        quantite = int(request.POST.get('quantite', 1))
        
        if quantite > produit.quantite_stock:
            messages.error(request, f'Stock insuffisant. Stock disponible: {produit.quantite_stock}')
            return redirect('detail_produit', produit_id=produit_id)
        
        # Récupérer ou créer un panier en cours pour l'utilisateur
        panier, created = Panier.objects.get_or_create(
            utilisateur=request.user,
            statut='en_cours',
            defaults={}
        )
        
        # Vérifier si le produit est déjà dans le panier
        item, item_created = ItemPanier.objects.get_or_create(
            panier=panier,
            produit=produit,
            defaults={'quantite': quantite, 'prix_unitaire': produit.prix_vente}
        )
        
        if not item_created:
            # Si l'item existe déjà, augmenter la quantité
            nouvelle_quantite = item.quantite + quantite
            if nouvelle_quantite > produit.quantite_stock:
                messages.error(request, f'Stock insuffisant. Stock disponible: {produit.quantite_stock}')
                return redirect('detail_produit', produit_id=produit_id)
            item.quantite = nouvelle_quantite
            item.save()
        
        messages.success(request, f'{produit.nom} ajouté au panier !')
        return redirect('panier')
    
    return redirect('detail_produit', produit_id=produit_id)


@login_required
def panier(request):
    """Page du panier du client"""
    panier_obj, created = Panier.objects.get_or_create(
        utilisateur=request.user,
        statut='en_cours',
        defaults={}
    )
    
    items = panier_obj.items.all()
    total = panier_obj.total
    
    context = {
        'panier': panier_obj,
        'items': items,
        'total': total,
    }
    
    return render(request, 'client/panier.html', context)


@login_required
def modifier_quantite_panier(request, item_id):
    """Modifier la quantité d'un article dans le panier"""
    item = get_object_or_404(ItemPanier, id=item_id, panier__utilisateur=request.user)
    
    if request.method == 'POST':
        quantite = int(request.POST.get('quantite', 1))
        
        if quantite <= 0:
            item.delete()
            messages.success(request, 'Article retiré du panier.')
        elif quantite > item.produit.quantite_stock:
            messages.error(request, f'Stock insuffisant. Stock disponible: {item.produit.quantite_stock}')
        else:
            item.quantite = quantite
            item.save()
            messages.success(request, 'Quantité mise à jour.')
    
    return redirect('panier')


@login_required
def retirer_du_panier(request, item_id):
    """Retirer un article du panier"""
    item = get_object_or_404(ItemPanier, id=item_id, panier__utilisateur=request.user)
    item.delete()
    messages.success(request, 'Article retiré du panier.')
    return redirect('panier')


@login_required
def passer_commande(request):
    """Passer une commande depuis le panier"""
    panier_obj = get_object_or_404(
        Panier,
        utilisateur=request.user,
        statut='en_cours'
    )
    
    if not panier_obj.items.exists():
        messages.error(request, 'Votre panier est vide.')
        return redirect('panier')
    
    # Vérifier le stock de tous les articles
    for item in panier_obj.items.all():
        if item.quantite > item.produit.quantite_stock:
            messages.error(
                request,
                f'Stock insuffisant pour {item.produit.nom}. Stock disponible: {item.produit.quantite_stock}'
            )
            return redirect('panier')
    
    # Créer la commande
    commande = Commande.objects.create(
        panier=panier_obj,
        montant_total=panier_obj.total,
        statut='en_attente'
    )
    
    # Marquer le panier comme validé
    panier_obj.statut = 'valide'
    panier_obj.save()
    
    messages.success(request, f'Commande #{commande.numero_commande} passée avec succès !')
    return redirect('mes_commandes')


@login_required
def mes_commandes(request):
    """Liste des commandes du client"""
    commandes = Commande.objects.filter(
        panier__utilisateur=request.user
    ).order_by('-date_commande')
    
    context = {
        'commandes': commandes,
    }
    
    return render(request, 'client/mes_commandes.html', context)


@login_required
def detail_commande(request, commande_id):
    """Détail d'une commande"""
    commande = get_object_or_404(
        Commande,
        id=commande_id,
        panier__utilisateur=request.user
    )
    
    context = {
        'commande': commande,
        'items': commande.panier.items.all(),
    }
    
    return render(request, 'client/detail_commande.html', context)


@staff_member_required
def export_ventes(request):
    """Export des ventes en CSV"""
    import csv
    from django.http import HttpResponse
    from datetime import datetime
    
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="ventes_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Date', 'Produit', 'Catégorie', 'Quantité', 'Prix unitaire', 'Montant total'])
    
    ventes = Vente.objects.select_related('produit', 'produit__categorie').all().order_by('-date_vente')
    for vente in ventes:
        writer.writerow([
            vente.date_vente.strftime('%Y-%m-%d %H:%M'),
            vente.produit.nom,
            vente.produit.categorie.nom,
            vente.quantite,
            vente.prix_unitaire,
            vente.montant_total
        ])
    
    return response


@login_required
def ajouter_avis(request, produit_id):
    """Ajouter un avis sur un produit"""
    produit = get_object_or_404(Produit, id=produit_id, active=True)
    
    if request.method == 'POST':
        note = int(request.POST.get('note', 5))
        commentaire = request.POST.get('commentaire', '').strip()
        
        if 1 <= note <= 5:
            avis, created = AvisProduit.objects.get_or_create(
                produit=produit,
                utilisateur=request.user,
                defaults={
                    'note': note,
                    'commentaire': commentaire,
                    'approuve': False  # Nécessite validation admin
                }
            )
            
            if not created:
                avis.note = note
                avis.commentaire = commentaire
                avis.approuve = False
                avis.save()
            
            messages.success(request, 'Votre avis a été enregistré. Il sera visible après validation.')
            return redirect('detail_produit', produit_id=produit_id)
    
    return redirect('detail_produit', produit_id=produit_id)

