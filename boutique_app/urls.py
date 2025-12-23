from django.urls import path
from . import views

urlpatterns = [
    # Pages générales
    path('', views.accueil, name='accueil'),
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Authentification client
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion_client, name='connexion'),
    path('deconnexion/', views.deconnexion_client, name='deconnexion'),
    
    # Catalogue et produits
    path('catalogue/', views.catalogue, name='catalogue'),
    path('produit/<int:produit_id>/', views.detail_produit, name='detail_produit'),
    
    # Panier
    path('panier/', views.panier, name='panier'),
    path('panier/ajouter/<int:produit_id>/', views.ajouter_au_panier, name='ajouter_au_panier'),
    path('panier/modifier/<int:item_id>/', views.modifier_quantite_panier, name='modifier_quantite_panier'),
    path('panier/retirer/<int:item_id>/', views.retirer_du_panier, name='retirer_du_panier'),
    path('panier/commander/', views.passer_commande, name='passer_commande'),
    
    # Commandes
    path('mes-commandes/', views.mes_commandes, name='mes_commandes'),
    path('commande/<int:commande_id>/', views.detail_commande, name='detail_commande'),
]

