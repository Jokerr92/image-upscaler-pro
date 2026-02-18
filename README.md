# 🎨 Image Upscaler Pro

Application Python simple pour upscaler des images via l'API Freepik + conversion WebP optimisée.

## 🚀 Démarrage rapide

### 1. Installation automatique

```bash
chmod +x start.sh
./start.sh
```

### 2. Ou installation manuelle

```bash
# Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer
python app.py
```

### 3. Accéder à l'interface

Ouvrez votre navigateur : **http://localhost:5000**

---

## 🔑 Configuration API Freepik

1. Allez sur [freepik.com/api](https://www.freepik.com/api)
2. Créez un compte / connectez-vous
3. Générez une clé API
4. Collez la clé dans l'interface web

---

## ✨ Fonctionnalités

- ✅ Upload multiple (drag & drop)
- ✅ Upscale 2x ou 4x via Freepik AI
- ✅ Conversion automatique WebP
- ✅ Réduction de taille optimisée
- ✅ Redimensionnement optionnel
- ✅ Aperçu avant/après
- ✅ Téléchargement individuel

---

## 📁 Structure

```
image_upscaler/
├── app.py              # Backend Flask
├── requirements.txt    # Dépendances
├── start.sh            # Script de lancement
├── README.md           # Ce fichier
├── uploads/            # Images uploadées (temp)
└── outputs/            # Images traitées
```

---

## 🐳 Docker (optionnel)

```bash
# Build et run
docker build -t image-upscaler .
docker run -p 5000:5000 image-upscaler
```

---

## 📝 Notes

- Les fichiers uploadés sont stockés temporairement dans `uploads/`
- Les résultats sont sauvegardés dans `outputs/`
- Format de sortie : WebP optimisé
- Taille max upload : configurée par Flask (16MB par défaut)

---

## 🛠️ Personnalisation

Pour changer le port (par défaut 5000) :

```bash
export PORT=8080
python app.py
```

Ou modifiez la dernière ligne de `app.py` :
```python
app.run(host='0.0.0.0', port=8080)
```
