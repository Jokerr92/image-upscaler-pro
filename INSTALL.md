# 📦 Guide d'Installation Complète - Image Upscaler Pro

## 🎯 Ce que vous allez installer

Une application web pour **upscaler vos images** avec l'IA Freepik + conversion WebP optimisée.

---

## 📋 Prérequis

- **Windows 10/11**, **macOS** ou **Linux**
- **Python 3.9 ou plus récent** (3.10+ recommandé)
- **~100 Mo** d'espace disque
- Une **connexion internet** (pour l'API Freepik)

---

## ÉTAPE 1 : Installer Python

### Windows
1. Allez sur 👉 https://www.python.org/downloads/
2. Cliquez sur **"Download Python 3.12.x"**
3. Lancez l'installateur
4. ⚠️ **IMPORTANT** : Cochez la case **"Add Python to PATH"**
5. Cliquez sur **"Install Now"**
6. Vérifiez l'installation :
   ```
   Win + R → tapez "cmd" → Entrée
   ```
   Dans le terminal :
   ```bash
   python --version
   ```
   → Vous devez voir `Python 3.12.x` (ou supérieur)

### macOS
```bash
# Vérifiez si Python est installé
python3 --version

# Si non installé, utilisez Homebrew :
brew install python

# Ou téléchargez sur python.org
```

### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv -y
```

---

## ÉTAPE 2 : Extraire l'archive

1. **Téléchargez** le fichier `image_upscaler.zip`
2. **Créez un dossier** sur votre Bureau :
   ```
   C:\Users\VotreNom\Desktop\ImageUpscaler
   ```
3. **Extrayez** le ZIP dans ce dossier
4. Vous devez voir ces fichiers :
   ```
   ImageUpscaler/
   ├── app.py              ← Application principale
   ├── requirements.txt    ← Dépendances
   ├── start.sh            ← Lanceur Mac/Linux
   ├── start.bat           ← Lanceur Windows
   ├── README.md           ← Documentation
   └── Dockerfile          ← Pour Docker (optionnel)
   ```

---

## ÉTAPE 3 : Installation

### 🪟 Windows

1. **Ouvrez PowerShell** ou **CMD** :
   - Faites `Win + X` → "Terminal" ou "Invite de commandes"

2. **Allez dans le dossier** :
   ```powershell
   cd C:\Users\VotreNom\Desktop\ImageUpscaler
   ```

3. **Créez l'environnement virtuel** :
   ```powershell
   python -m venv venv
   ```

4. **Activez l'environnement** :
   ```powershell
   venv\Scripts\activate
   ```
   → Vous devez voir `(venv)` au début de la ligne

5. **Installez les dépendances** :
   ```powershell
   pip install -r requirements.txt
   ```
   → Attendez que l'installation se termine (~1-2 minutes)

### 🍎 macOS / 🐧 Linux

1. **Ouvrez le Terminal**

2. **Allez dans le dossier** :
   ```bash
   cd ~/Desktop/ImageUpscaler
   ```

3. **Rendez le script exécutable** :
   ```bash
   chmod +x start.sh
   ```

4. **Lancez l'installation** :
   ```bash
   ./start.sh
   ```
   → Ce script fait tout automatiquement !

---

## ÉTAPE 4 : Lancer l'application

### Windows
```powershell
# Assurez-vous d'être dans le dossier et l'environnement activé
python app.py
```

### Mac/Linux
```bash
./start.sh
# ou
python3 app.py
```

✅ **Vous verrez ce message** :
```
🎨 Image Upscaler Pro - Démarrage...
📁 Uploads: /.../uploads
📁 Outputs: /.../outputs

🌐 Interface web: http://localhost:5000
✨ Ouvrez votre navigateur et allez sur http://localhost:5000
```

---

## ÉTAPE 5 : Utiliser l'application

### 1. Obtenir une clé API Freepik

1. Allez sur 👉 https://www.freepik.com/api
2. Créez un compte gratuit ou connectez-vous
3. Allez dans **"API Keys"** ou **"Developer"**
4. Cliquez sur **"Create API Key"**
5. Copiez la clé (elle ressemble à `fpk_xxxxxxxxxxxx`)

⚠️ **Conservez cette clé précieusement !**

### 2. Ouvrir l'interface

1. **Ouvrez votre navigateur** (Chrome, Firefox, Edge...)
2. Allez sur 👉 **http://localhost:5000**
3. **Collez votre clé API** dans le champ prévu

### 3. Uploader des images

- **Glissez-déposez** vos images dans la zone pointillée
- OU cliquez pour sélectionner des fichiers
- Formats supportés : **JPG, PNG, WebP**

### 4. Configurer les options

| Option | Description | Recommandation |
|--------|-------------|----------------|
| **Niveau d'upscale** | 2x ou 4x | 2x pour la plupart des images |
| **Qualité WebP** | 80% à 95% | 85% (équilibré) |
| **Largeur max** | Redimensionnement | Laissez vide sauf besoin spécifique |

### 5. Traiter

- Cliquez sur **"🚀 Lancer le traitement"**
- Attendez (1-3 minutes par image)
- Téléchargez vos images upscalées !

---

## 🐛 Résolution de problèmes

### "python n'est pas reconnu..."
→ Python n'est pas dans le PATH. Réinstallez Python en cochant **"Add Python to PATH"**

### "pip n'est pas reconnu..."
→ Utilisez `python -m pip` au lieu de `pip`

### "Permission denied" sur Mac/Linux
→ Exécutez : `chmod +x start.sh` avant `./start.sh`

### "Module not found"
→ Vérifiez que l'environnement virtuel est activé (vous devez voir `(venv)`)

### Le port 5000 est déjà utilisé
→ Modifiez la dernière ligne de `app.py` :
```python
app.run(host='0.0.0.0', port=8080)  # Changez 8080 par un autre port
```

### Erreur API "Unauthorized"
→ Votre clé API Freepik est invalide ou expirée. Générez-en une nouvelle.

---

## 📁 Où sont mes images ?

| Dossier | Contenu |
|---------|---------|
| `uploads/` | Images uploadées (temporaire) |
| `outputs/` | Images traitées (WebP upscalées) |

**Sur Windows** : `C:\Users\VotreNom\Desktop\ImageUpscaler\outputs\
**Sur Mac** : `~/Desktop/ImageUpscaler/outputs/`

---

## 🛑 Arrêter l'application

- **Dans le terminal** : Appuyez sur `Ctrl + C`
- **Fermez la fenêtre du terminal**

Pour relancer : refaites `python app.py` (ou `./start.sh`)

---

## 🔄 Mettre à jour

```bash
# Allez dans le dossier
cd ImageUpscaler

# Activez l'environnement
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Mettez à jour les dépendances
pip install --upgrade -r requirements.txt
```

---

## 🐳 Option Docker (avancé)

Si vous avez Docker installé :

```bash
docker build -t image-upscaler .
docker run -p 5000:5000 image-upscaler
```

---

## 💡 Astuces

- **Images lourdes** : Traitez par lots de 3-5 images maximum
- **Qualité vs Poids** : 85% est le sweet spot pour le web
- **Format source** : Privilégiez PNG ou JPG de bonne qualité
- **Backup** : Gardez toujours les images originales

---

## 📞 Besoin d'aide ?

Vérifiez :
1. Python est bien installé (`python --version`)
2. L'environnement virtuel est activé (`(venv)` visible)
3. Les dépendances sont installées (`pip list`)
4. La clé API Freepik est valide

---

**Bon upscaling ! 🎨✨**