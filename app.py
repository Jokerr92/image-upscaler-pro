#!/usr/bin/env python3
"""
Image Upscaler Pro - Real-ESRGAN Version
Upscale local avec Real-ESRGAN + Conversion WebP
100% offline, gratuit, préserve le texte
"""

import os
import io
import base64
import time
import requests
from PIL import Image
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename

# Essayer d'importer Real-ESRGAN
try:
    import torch
    from realesrgan import RealESRGANer
    from basicsr.archs.rrdbnet_arch import RRDBNet
    REALESRGAN_AVAILABLE = True
except ImportError:
    REALESRGAN_AVAILABLE = False
    print("⚠️ Real-ESRGAN non installé. Utilisez 'pip install realesrgan'")

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
MODELS_FOLDER = 'models'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(MODELS_FOLDER, exist_ok=True)

# Initialiser Real-ESRGAN
upsampler = None

def init_realesrgan():
    """Initialise le modèle Real-ESRGAN"""
    global upsampler
    
    if not REALESRGAN_AVAILABLE:
        return False
    
    if upsampler is not None:
        return True
    
    try:
        # Vérifier si CUDA est disponible
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🖥️  Device utilisé: {device}")
        
        # Chemin du modèle
        model_path = os.path.join(MODELS_FOLDER, 'RealESRGAN_x4plus.pth')
        
        # Télécharger le modèle s'il n'existe pas
        if not os.path.exists(model_path):
            print("📥 Téléchargement du modèle Real-ESRGAN...")
            url = 'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth'
            r = requests.get(url, timeout=120)
            with open(model_path, 'wb') as f:
                f.write(r.content)
            print("✅ Modèle téléchargé")
        
        # Créer l'upsampler
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        upsampler = RealESRGANer(
            scale=4,
            model_path=model_path,
            model=model,
            tile=0,
            tile_pad=10,
            pre_pad=0,
            half=torch.cuda.is_available(),  # half precision si CUDA
            device=device
        )
        print("✅ Real-ESRGAN initialisé")
        return True
        
    except Exception as e:
        print(f"❌ Erreur initialisation Real-ESRGAN: {e}")
        return False

# Page HTML intégrée (interface simple)
HTML_INTERFACE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Upscale Images Pro - Real-ESRGAN</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            min-height: 100vh; 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            padding: 20px; 
        }
        .container { 
            background: white; 
            border-radius: 20px; 
            padding: 40px; 
            max-width: 700px; 
            width: 100%; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
        }
        h1 { text-align: center; color: #333; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }
        .info-box {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 25px;
            color: #155724;
        }
        .info-box strong { color: #28a745; }
        .drop-zone { 
            border: 3px dashed #667eea; 
            border-radius: 15px; 
            padding: 50px 20px; 
            text-align: center; 
            transition: all 0.3s ease; 
            cursor: pointer; 
            background: #f8f9ff; 
        }
        .drop-zone:hover, .drop-zone.dragover { 
            background: #e8ebff; 
            border-color: #764ba2; 
            transform: scale(1.02); 
        }
        .drop-zone-icon { font-size: 48px; margin-bottom: 15px; }
        #fileInput { display: none; }
        .options { 
            margin: 25px 0; 
            padding: 20px; 
            background: #f5f5f5; 
            border-radius: 10px; 
        }
        .option-group { margin-bottom: 15px; }
        .option-group:last-child { margin-bottom: 0; }
        label { display: block; margin-bottom: 5px; color: #333; font-weight: 600; font-size: 14px; }
        select, input[type="number"] { 
            width: 100%; 
            padding: 10px; 
            border: 2px solid #ddd; 
            border-radius: 8px; 
            font-size: 14px; 
        }
        .btn { 
            width: 100%; 
            padding: 15px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
            color: white; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            font-weight: 600; 
            cursor: pointer; 
            transition: transform 0.2s; 
        }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(102, 126, 234, 0.4); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }
        .file-list { margin: 20px 0; max-height: 200px; overflow-y: auto; }
        .file-item { 
            display: flex; 
            align-items: center; 
            padding: 12px; 
            background: #f8f9ff; 
            border-radius: 8px; 
            margin-bottom: 8px; 
        }
        .file-preview { width: 50px; height: 50px; object-fit: cover; border-radius: 5px; margin-right: 12px; }
        .file-info { flex: 1; }
        .file-name { font-weight: 600; color: #333; font-size: 14px; }
        .file-size { color: #888; font-size: 12px; }
        .file-remove { 
            background: #ff4757; 
            color: white; 
            border: none; 
            padding: 5px 12px; 
            border-radius: 5px; 
            cursor: pointer; 
            font-size: 12px; 
        }
        .progress { display: none; margin: 20px 0; }
        .progress.active { display: block; }
        .progress-bar { height: 10px; background: #e0e0e0; border-radius: 5px; overflow: hidden; }
        .progress-fill { 
            height: 100%; 
            background: linear-gradient(90deg, #667eea, #764ba2); 
            width: 0%; 
            transition: width 0.3s; 
        }
        .progress-text { text-align: center; margin-top: 10px; color: #667eea; font-weight: 600; }
        .results { display: none; margin-top: 20px; }
        .results.active { display: block; }
        .result-item { 
            display: flex; 
            align-items: center; 
            padding: 15px; 
            background: #d4edda; 
            border-radius: 10px; 
            margin-bottom: 10px; 
            border: 1px solid #c3e6cb; 
        }
        .result-item.error { background: #f8d7da; border-color: #f5c6cb; color: #721c24; }
        .result-preview { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; margin-right: 15px; }
        .result-info { flex: 1; }
        .result-name { font-weight: 600; color: #155724; margin-bottom: 5px; }
        .result-meta { color: #28a745; font-size: 13px; }
        .download-btn {
            background: #28a745;
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 5px;
            font-size: 13px;
            font-weight: 600;
        }
        .download-btn:hover { background: #218838; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
            margin-right: 10px;
        }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Upscale Images Pro</h1>
        <p class="subtitle">Real-ESRGAN - 100% Offline - Préserve le texte</p>
        
        <div class="info-box">
            <strong>✅ Mode offline activé</strong><br>
            Real-ESRGAN fonctionne sans internet. Vos images restent sur votre PC.<br>
            <small>Le modèle sera téléchargé automatiquement (64 MB) au premier lancement.</small>
        </div>

        <div class="drop-zone" id="dropZone">
            <div class="drop-zone-icon">📁</div>
            <div style="color: #667eea; font-size: 18px; font-weight: 600;">Glissez vos images ici</div>
            <div style="color: #888; font-size: 13px; margin-top: 5px;">ou cliquez pour sélectionner (JPG, PNG, WebP)</div>
        </div>
        
        <input type="file" id="fileInput" multiple accept="image/*">
        
        <div class="file-list" id="fileList"></div>
        
        <div class="options">
            <div class="option-group">
                <label>🎯 Niveau d'upscale</label>
                <select id="scaleFactor">
                    <option value="2" selected>2x (Double résolution)</option>
                    <option value="4">4x (Quadruple résolution)</option>
                </select>
            </div>
            <div class="option-group">
                <label>🖼️ Qualité WebP (compression)</label>
                <select id="quality">
                    <option value="80">80% (Fichier léger)</option>
                    <option value="85" selected>85% (Équilibré)</option>
                    <option value="90">90% (Haute qualité)</option>
                    <option value="95">95% (Qualité maximale)</option>
                </select>
            </div>
        </div>
        
        <button class="btn" id="processBtn" disabled>
            🚀 Lancer le traitement
        </button>
        
        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div class="progress-text" id="progressText">Préparation...</div>
        </div>
        
        <div class="results" id="results"></div>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const processBtn = document.getElementById('processBtn');
        const progress = document.getElementById('progress');
        const results = document.getElementById('results');
        
        let files = [];
        
        dropZone.addEventListener('click', () => fileInput.click());
        
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('dragover');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('dragover');
        });
        
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropZone.classList.remove('dragover');
            handleFiles(e.dataTransfer.files);
        });
        
        fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
        
        function handleFiles(newFiles) {
            const imageFiles = Array.from(newFiles).filter(f => f.type.startsWith('image/'));
            files = [...files, ...imageFiles];
            updateFileList();
        }
        
        function updateFileList() {
            fileList.innerHTML = '';
            files.forEach((file, index) => {
                const item = document.createElement('div');
                item.className = 'file-item';
                item.innerHTML = `
                    <img class="file-preview" src="${URL.createObjectURL(file)}">
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatBytes(file.size)}</div>
                    </div>
                    <button class="file-remove" onclick="removeFile(${index})">✕</button>
                `;
                fileList.appendChild(item);
            });
            processBtn.disabled = files.length === 0;
        }
        
        function removeFile(index) {
            files.splice(index, 1);
            updateFileList();
        }
        
        function formatBytes(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        }
        
        processBtn.addEventListener('click', async () => {
            if (files.length === 0) return;
            
            progress.classList.add('active');
            results.classList.remove('active');
            processBtn.disabled = true;
            processBtn.innerHTML = '<span class="spinner"></span>Traitement en cours...';
            
            const formData = new FormData();
            files.forEach(file => formData.append('images', file));
            formData.append('scaleFactor', document.getElementById('scaleFactor').value);
            formData.append('quality', document.getElementById('quality').value);
            
            try {
                updateProgress(10, 'Upscaling avec Real-ESRGAN...');
                
                const response = await fetch('/upscale', {
                    method: 'POST',
                    body: formData
                });
                
                updateProgress(80, 'Finalisation...');
                
                const data = await response.json();
                
                if (data.success) {
                    updateProgress(100, 'Terminé !');
                    setTimeout(() => {
                        progress.classList.remove('active');
                        showResults(data.results);
                        processBtn.innerHTML = '🚀 Lancer le traitement';
                        processBtn.disabled = false;
                    }, 500);
                } else {
                    throw new Error(data.error || 'Erreur inconnue');
                }
            } catch (error) {
                progress.classList.remove('active');
                processBtn.innerHTML = '🚀 Lancer le traitement';
                processBtn.disabled = false;
                alert('❌ Erreur: ' + error.message);
            }
        });
        
        function updateProgress(percent, text) {
            document.getElementById('progressFill').style.width = percent + '%';
            document.getElementById('progressText').textContent = text;
        }
        
        function showResults(resultsData) {
            results.innerHTML = '<h3 style="margin-bottom: 15px; color: #28a745;">✅ Images traitées avec succès !</h3>';
            
            resultsData.forEach(result => {
                const item = document.createElement('div');
                item.className = 'result-item';
                if (result.error) {
                    item.classList.add('error');
                    item.innerHTML = `
                        <div class="result-info">
                            <div class="result-name">❌ ${result.original_name}</div>
                            <div class="result-meta">Erreur: ${result.error}</div>
                        </div>
                    `;
                } else {
                    item.innerHTML = `
                        <img class="result-preview" src="${result.preview_url}">
                        <div class="result-info">
                            <div class="result-name">${result.original_name}</div>
                            <div class="result-meta">
                                ${result.original_size} → ${result.upscaled_size} | 
                                ${result.original_dims} → ${result.upscaled_dims}
                            </div>
                        </div>
                        <a href="${result.download_url}" class="download-btn" download>📥 Télécharger</a>
                    `;
                }
                results.appendChild(item);
            });
            
            results.classList.add('active');
        }
    </script>
</body>
</html>
'''


def convert_to_webp(image_data, quality=85, max_width=None):
    """Convertit une image en WebP optimisé"""
    img = Image.open(io.BytesIO(image_data))
    
    # Conversion RGBA → RGB si nécessaire pour la compatibilité WebP
    if img.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', img.size, (255, 255, 255))
        if img.mode == 'P':
            img = img.convert('RGBA')
        background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
        img = background
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Redimensionnement si max_width spécifié
    if max_width and img.width > max_width:
        ratio = max_width / img.width
        new_height = int(img.height * ratio)
        img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
    
    # Sauvegarde en WebP
    output = io.BytesIO()
    img.save(output, format='WebP', quality=quality, method=6)
    output.seek(0)
    
    return output.getvalue(), img.size


def upscale_with_realesrgan(image_data, scale=2):
    """Upscale une image avec Real-ESRGAN"""
    if not REALESRGAN_AVAILABLE:
        raise Exception("Real-ESRGAN n'est pas installé. Exécutez: pip install realesrgan")
    
    # Initialiser si besoin
    if not init_realesrgan():
        raise Exception("Impossible d'initialiser Real-ESRGAN")
    
    # Charger l'image
    img = Image.open(io.BytesIO(image_data))
    
    # Convertir en RGB si nécessaire
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convertir en numpy array
    import numpy as np
    img_array = np.array(img)
    
    # Upscaling
    print(f"  → Upscaling {img.width}x{img.height} → {img.width*scale}x{img.height*scale}...")
    
    # Pour le scale 2, on fait 4 puis on réduit
    output, _ = upsampler.enhance(img_array, outscale=4)
    
    # Si on veut du 2x au lieu de 4x, on réduit
    if scale == 2:
        h, w = output.shape[:2]
        output_img = Image.fromarray(output)
        output_img = output_img.resize((w//2, h//2), Image.Resampling.LANCZOS)
        output = np.array(output_img)
    
    # Convertir en bytes
    output_img = Image.fromarray(output)
    output_bytes = io.BytesIO()
    output_img.save(output_bytes, format='PNG')
    output_bytes.seek(0)
    
    return output_bytes.getvalue(), output_img.size


@app.route('/')
def index():
    """Page d'accueil avec l'interface"""
    return render_template_string(HTML_INTERFACE)


@app.route('/upscale', methods=['POST'])
def upscale_images():
    """Endpoint pour traiter les images"""
    try:
        if 'images' not in request.files:
            return jsonify({'success': False, 'error': 'Aucune image fournie'}), 400
        
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'Aucune image sélectionnée'}), 400
        
        # Paramètres
        scale_factor = int(request.form.get('scaleFactor', 2))
        quality = int(request.form.get('quality', 85))
        
        results = []
        
        for file in files:
            try:
                original_data = file.read()
                original_size = len(original_data)
                original_name = secure_filename(file.filename)
                
                # Obtenir dimensions originales
                img_temp = Image.open(io.BytesIO(original_data))
                original_dims = f"{img_temp.width}x{img_temp.height}"
                
                # Étape 1: Upscale avec Real-ESRGAN
                print(f"🖼️  Traitement de {original_name}...")
                upscaled_data, (upscaled_w, upscaled_h) = upscale_with_realesrgan(original_data, scale_factor)
                
                # Étape 2: Conversion WebP
                webp_data, final_size = convert_to_webp(upscaled_data, quality)
                
                # Sauvegarder le fichier
                output_filename = f"upscaled_{original_name.rsplit('.', 1)[0]}.webp"
                output_path = os.path.join(OUTPUT_FOLDER, output_filename)
                
                with open(output_path, 'wb') as f:
                    f.write(webp_data)
                
                results.append({
                    'success': True,
                    'original_name': original_name,
                    'output_name': output_filename,
                    'original_size': format_bytes(original_size),
                    'upscaled_size': format_bytes(len(webp_data)),
                    'original_dims': original_dims,
                    'upscaled_dims': f"{final_size[0]}x{final_size[1]}",
                    'download_url': f'/download/{output_filename}',
                    'preview_url': f'/preview/{output_filename}'
                })
                
                print(f"  ✅ Terminé: {output_filename}")
                
            except Exception as e:
                print(f"  ❌ Erreur sur {file.filename}: {e}")
                results.append({
                    'success': False,
                    'original_name': file.filename,
                    'error': str(e)
                })
        
        return jsonify({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<filename>')
def download_file(filename):
    """Télécharger un fichier traité"""
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)


@app.route('/preview/<filename>')
def preview_file(filename):
    """Afficher un aperçu"""
    return send_file(os.path.join(OUTPUT_FOLDER, filename))


def format_bytes(bytes_value):
    """Formater la taille en bytes lisible"""
    if bytes_value == 0:
        return '0 B'
    k = 1024
    sizes = ['B', 'KB', 'MB', 'GB']
    i = int(bytes_value // k ** 0)
    for size in sizes:
        if bytes_value < k:
            return f"{bytes_value:.1f} {size}"
        bytes_value /= k
    return f"{bytes_value:.1f} TB"


if __name__ == '__main__':
    print("🎨 Image Upscaler Pro - Real-ESRGAN")
    print("📁 Uploads:", os.path.abspath(UPLOAD_FOLDER))
    print("📁 Outputs:", os.path.abspath(OUTPUT_FOLDER))
    print("")
    
    # Vérifier Real-ESRGAN au démarrage
    if REALESRGAN_AVAILABLE:
        print("✅ Real-ESRGAN disponible")
        print("🌐 Interface web: http://localhost:5000")
        print("")
    else:
        print("⚠️  Real-ESRGAN non installé.")
        print("   Exécutez: pip install realesrgan")
        print("")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
