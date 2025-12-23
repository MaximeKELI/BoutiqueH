# 🛒 La Gloire de Dieu - Boutique d'Alimentation Générale

Site web Django moderne avec PostgreSQL pour la gestion complète d'une boutique d'alimentation générale.

## ✨ Fonctionnalités

### 🎨 Interface Ultra Moderne
- Design moderne avec animations fluides
- Dégradés de lumière et effets visuels avancés
- Interface responsive et intuitive
- Dashboard interactif avec graphiques

### 📊 Gestion Complète
- **Produits** : Ajout, modification, gestion des stocks
- **Catégories** : Organisation des produits par catégories
- **Modèles** : Gestion des variantes de produits
- **Paniers** : Suivi des paniers d'achat
- **Commandes** : Gestion complète des commandes
- **Ventes** : Enregistrement et suivi des ventes

### 📈 Statistiques et Analyses
- Statistiques financières (ventes quotidiennes, hebdomadaires, mensuelles, annuelles)
- Statistiques Min/Max (prix, stock, marges)
- Prévisions basées sur les tendances
- Top produits vendus
- Statistiques par catégorie
- Graphiques interactifs des ventes
- Alertes de stock faible

## 🚀 Installation

### Prérequis
- Python 3.8+
- PostgreSQL 12+
- pip

### Étapes d'installation

1. **Cloner le projet**
```bash
cd /home/maxime/BoutiqueH
```

2. **Créer un environnement virtuel (recommandé)**
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# ou
venv\Scripts\activate  # Sur Windows
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer PostgreSQL**
```bash
# Créer la base de données
sudo -u postgres psql
CREATE DATABASE boutique_db;
CREATE USER boutique_user WITH PASSWORD 'votre_mot_de_passe';
GRANT ALL PRIVILEGES ON DATABASE boutique_db TO boutique_user;
\q
```

5. **Configurer les variables d'environnement**
```bash
# Créer un fichier .env à la racine du projet
cp .env.example .env
# Éditer .env avec vos paramètres
```

Exemple de `.env`:
```
SECRET_KEY=votre-secret-key-tres-securise
DEBUG=True
DB_NAME=boutique_db
DB_USER=boutique_user
DB_PASSWORD=votre_mot_de_passe
DB_HOST=localhost
DB_PORT=5432
```

6. **Appliquer les migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

7. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

8. **Collecter les fichiers statiques**
```bash
python manage.py collectstatic --noinput
```

9. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

10. **Accéder à l'interface d'administration**
```
http://localhost:8000/admin/
```

11. **Accéder au dashboard complet**
```
http://localhost:8000/dashboard/
```

## 📁 Structure du Projet

```
BoutiqueH/
├── boutique/              # Configuration du projet Django
│   ├── settings.py        # Paramètres Django
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # Configuration WSGI
├── boutique_app/          # Application principale
│   ├── models.py          # Modèles de données
│   ├── admin.py           # Interface d'administration
│   ├── views.py           # Vues et logique métier
│   └── urls.py            # URLs de l'application
├── templates/             # Templates HTML
│   └── admin/             # Templates d'administration
├── static/                # Fichiers statiques
│   ├── css/               # Feuilles de style
│   ├── js/                # JavaScript
│   └── images/            # Images
├── media/                 # Fichiers média uploadés
├── requirements.txt       # Dépendances Python
└── manage.py             # Script de gestion Django
```

## 🎯 Utilisation

### Ajouter des produits

1. Connectez-vous à l'interface d'administration (`/admin/`)
2. Allez dans **Produits** > **Ajouter un produit**
3. Remplissez les informations :
   - Nom du produit
   - Catégorie (créez-en une si nécessaire)
   - Modèle (optionnel)
   - Prix d'achat et prix de vente
   - Quantité en stock
   - Image du produit (optionnel)
   - Code-barres (optionnel)

### Gérer les catégories

1. Allez dans **Catégories** dans l'admin
2. Ajoutez ou modifiez les catégories
3. Vous pouvez ajouter une image pour chaque catégorie

### Consulter les statistiques

1. Accédez au **Dashboard** depuis l'admin ou directement via `/dashboard/`
2. Visualisez :
   - Statistiques générales
   - Statistiques financières
   - Graphiques des ventes
   - Statistiques Min/Max
   - Prévisions
   - Top produits
   - Statistiques par catégorie
   - Alertes

## 🔧 Configuration Avancée

### Personnaliser le design

Les styles CSS sont dans `static/css/dashboard.css`. Vous pouvez modifier :
- Les couleurs des dégradés
- Les animations
- Les effets de lumière
- La mise en page

### Ajouter des fonctionnalités

Les modèles sont dans `boutique_app/models.py`. Vous pouvez :
- Ajouter de nouveaux champs
- Créer de nouvelles relations
- Ajouter des méthodes personnalisées

## 📝 Notes

- Le dashboard nécessite des données pour afficher les statistiques
- Les prévisions sont basées sur la moyenne des 3 derniers mois
- Les alertes de stock faible apparaissent automatiquement
- Toutes les images sont stockées dans le dossier `media/`

## 🐛 Dépannage

### Erreur de connexion à PostgreSQL
- Vérifiez que PostgreSQL est démarré
- Vérifiez les identifiants dans `.env`
- Vérifiez que la base de données existe

### Erreur de migrations
```bash
python manage.py migrate --run-syncdb
```

### Erreur de fichiers statiques
```bash
python manage.py collectstatic --noinput
```

## 📄 Licence

Ce projet est développé pour "La Gloire de Dieu" - Boutique d'Alimentation Générale.

## 👨‍💻 Support

Pour toute question ou problème, consultez la documentation Django ou contactez l'administrateur.

---

**Développé avec ❤️ pour La Gloire de Dieu**
