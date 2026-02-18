#!/bin/bash

# Script d'installation et de lancement rapide

echo "🎨 Image Upscaler Pro - Installation"
echo "======================================"
echo ""

# Vérifier si Python est installé
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo "✅ Python trouvé: $(python3 --version)"

# Créer l'environnement virtuel si nécessaire
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement
echo "🚀 Activation de l'environnement..."
source venv/bin/activate

# Installer les dépendances
echo "📥 Installation des dépendances..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Créer les dossiers
mkdir -p uploads outputs

echo ""
echo "✅ Installation terminée !"
echo ""
echo "📝 Pour obtenir une clé API Freepik:"
echo "   1. Allez sur https://www.freepik.com/api"
echo "   2. Créez un compte ou connectez-vous"
echo "   3. Générez une clé API"
echo ""
echo "🚀 Lancement du serveur..."
echo "   → Interface web: http://localhost:5000"
echo ""

# Lancer l'application
python3 app.py
