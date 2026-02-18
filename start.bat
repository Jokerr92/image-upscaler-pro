@echo off
echo ==========================================
echo    🎨 Image Upscaler Pro - Installation
echo ==========================================
echo.

:: Verifier Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python n'est pas installe ou pas dans le PATH
    echo    Allez sur https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✅ Python detecte

:: Creer environnement virtuel
if not exist "venv" (
    echo 📦 Creation de l'environnement virtuel...
    python -m venv venv
)

:: Activer l'environnement
echo 🚀 Activation de l'environnement...
call venv\Scripts\activate

:: Installer les dependances
echo 📥 Installation des dependances...
pip install -q --upgrade pip
pip install -q -r requirements.txt

:: Creer les dossiers
if not exist "uploads" mkdir uploads
if not exist "outputs" mkdir outputs

echo.
echo ==========================================
echo    ✅ Installation terminee !
echo ==========================================
echo.
echo 📝 Pour obtenir une cle API Freepik:
echo    1. Allez sur https://www.freepik.com/api
echo    2. Creez un compte
echo    3. Generez une cle API
echo.
echo 🚀 Lancement du serveur...
echo    → Interface web: http://localhost:5000
echo.

python app.py

pause