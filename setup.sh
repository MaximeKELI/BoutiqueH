#!/bin/bash

echo "🚀 Installation de La Gloire de Dieu - Boutique"
echo "================================================"

# Vérifier Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Créer l'environnement virtuel
echo "📦 Création de l'environnement virtuel..."
python3 -m venv venv

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Créer le fichier .env s'il n'existe pas
if [ ! -f .env ]; then
    echo "📝 Création du fichier .env..."
    cat > .env << EOF
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
DB_NAME=boutique_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
EOF
    echo "✅ Fichier .env créé. Veuillez le modifier avec vos paramètres PostgreSQL."
fi

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p media/products media/categories staticfiles

# Appliquer les migrations
echo "🗄️  Application des migrations..."
python manage.py makemigrations
python manage.py migrate

echo ""
echo "✅ Installation terminée!"
echo ""
echo "📋 Prochaines étapes:"
echo "1. Configurez PostgreSQL et créez la base de données 'boutique_db'"
echo "2. Modifiez le fichier .env avec vos paramètres de base de données"
echo "3. Créez un superutilisateur: python manage.py createsuperuser"
echo "4. Lancez le serveur: python manage.py runserver"
echo ""
echo "🌐 Accès:"
echo "   - Admin: http://localhost:8000/admin/"
echo "   - Dashboard: http://localhost:8000/dashboard/"
echo ""

