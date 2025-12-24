from django.contrib import admin
from django.utils.html import format_html
from .models import Categorie, Modele, Produit, Panier, ItemPanier, Commande, Vente


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nombre_produits', 'image_preview', 'active', 'date_creation']
    list_filter = ['active', 'date_creation']
    search_fields = ['nom', 'description']
    readonly_fields = ['date_creation', 'image_preview']
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = "Image"
    
    def nombre_produits(self, obj):
        return obj.produits.count()
    nombre_produits.short_description = "Nombre de produits"


@admin.register(Modele)
class ModeleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'nombre_produits', 'date_creation']
    search_fields = ['nom', 'description']
    readonly_fields = ['date_creation']
    
    def nombre_produits(self, obj):
        return obj.produits.count()
    nombre_produits.short_description = "Nombre de produits"


class ItemPanierInline(admin.TabularInline):
    model = ItemPanier
    extra = 0
    fields = ['produit', 'quantite', 'prix_unitaire']


@admin.register(Panier)
class PanierAdmin(admin.ModelAdmin):
    list_display = ['id', 'utilisateur', 'statut', 'total_panier', 'nombre_items', 'date_creation']
    list_filter = ['statut', 'date_creation']
    search_fields = ['id', 'utilisateur__username']
    readonly_fields = ['date_creation', 'date_modification', 'total_panier']
    inlines = [ItemPanierInline]
    
    def total_panier(self, obj):
        return f"{obj.total:.2f} FCFA"
    total_panier.short_description = "Total"
    
    def nombre_items(self, obj):
        return obj.items.count()
    nombre_items.short_description = "Articles"


@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'modele', 'prix_vente', 'quantite_stock', 'stock_status', 'marge_display', 'image_preview']
    list_filter = ['categorie', 'modele', 'active', 'date_creation']
    search_fields = ['nom', 'description', 'code_barre']
    readonly_fields = ['date_creation', 'date_modification', 'image_preview', 'stock_status']
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'description', 'categorie', 'modele', 'code_barre', 'image', 'image_preview')
        }),
        ('Prix et stock', {
            'fields': ('prix_achat', 'prix_vente', 'quantite_stock', 'quantite_minimum', 'stock_status')
        }),
        ('Statistiques (calculées automatiquement)', {
            'fields': (),
            'classes': ('collapse',),
            'description': 'La marge de bénéfice et la valeur du stock sont calculées automatiquement après la sauvegarde.'
        }),
        ('Paramètres', {
            'fields': ('active', 'date_creation', 'date_modification')
        }),
    )
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 200px; object-fit: cover; border-radius: 5px;" />', obj.image.url)
        return "Aucune image"
    image_preview.short_description = "Aperçu"
    
    def stock_status(self, obj):
        if obj.stock_faible:
            return format_html('<span style="color: red; font-weight: bold;">⚠ Stock faible</span>')
        return format_html('<span style="color: green;">✓ En stock</span>')
    stock_status.short_description = "État du stock"
    
    def marge_display(self, obj):
        marge = obj.marge_benefice
        if marge is None:
            marge = 0
        # S'assurer que marge est un nombre (pas un SafeString)
        try:
            marge_float = float(marge)
        except (TypeError, ValueError):
            marge_float = 0
        color = 'green' if marge_float > 30 else 'orange' if marge_float > 15 else 'red'
        return format_html('<span style="color: {}; font-weight: bold;">{:.1f}%</span>', color, marge_float)
    marge_display.short_description = "Marge"


@admin.register(Commande)
class CommandeAdmin(admin.ModelAdmin):
    list_display = ['numero_commande', 'panier', 'statut', 'montant_total', 'date_commande', 'statut_badge']
    list_filter = ['statut', 'date_commande']
    search_fields = ['numero_commande', 'panier__id']
    readonly_fields = ['numero_commande', 'date_commande', 'montant_total']
    
    def statut_badge(self, obj):
        colors = {
            'en_attente': 'orange',
            'en_preparation': 'blue',
            'livree': 'green',
            'annulee': 'red'
        }
        color = colors.get(obj.statut, 'gray')
        return format_html('<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 5px;">{}</span>', 
                          color, obj.get_statut_display())
    statut_badge.short_description = "Statut"


@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ['produit', 'quantite', 'prix_unitaire', 'montant_total', 'date_vente']
    list_filter = ['date_vente', 'produit__categorie']
    search_fields = ['produit__nom']
    readonly_fields = ['montant_total', 'date_vente']
    date_hierarchy = 'date_vente'


# Personnalisation de l'interface d'administration
admin.site.site_header = "La Gloire de Dieu - Administration"
admin.site.site_title = "La Gloire de Dieu"
admin.site.index_title = "Tableau de bord"

