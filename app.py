#!/usr/bin/env python3
"""
Image Upscaler - Backend Python
Upscale via Freepik API + Conversion WebP
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

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
FREEPIK_API_KEY = os.getenv('FREEPIK_API_KEY', 'TA_CLE_API_ICI')
# URLs API Freepik
FREEPIK_API_URL = 'https://api.freepik.com/v1/ai/image-upscaler'
FREEPIK_PRECISION_URL = 'https://api.freepik.com/v1/ai/image-upscaler-precision'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Page HTML intégrée (interface simple)
HTML_INTERFACE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎨 Upscale Images Pro</title>
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
        .api-key-section { 
            background: #fff3cd; 
            border: 1px solid #ffc107; 
            border-radius: 10px; 
            padding: 15px; 
            margin-bottom: 25px; 
        }
        .api-key-section input {
            width: 100%;
            padding: 10px;
            border: 2px solid #ddd;
            border-radius: 8px;
            margin-top: 8px;
            font-size: 14px;
        }
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
        .error { background: #f8d7da; border-color: #f5c6cb; color: #721c24; }
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
        <p class="subtitle">Améliorez vos photos avec Freepik AI + WebP optimisé</p>
        
        <div class="api-key-section">
            <label>🔑 Clé API Freepik</label>
            <input type="password" id="apiKey" placeholder="Entrez votre clé API Freepik...">
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
                <label>🎨 Mode d'upscale</label>
                <select id="mode">
                    <option value="precision" selected>🔒 Precision (préserve le texte)</option>
                    <option value="creative">✨ Creative (ajoute des détails)</option>
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
            <div class="option-group">
                <label>📐 Largeur max (px, optionnel)</label>
                <input type="number" id="maxWidth" placeholder="ex: 2000 (laissez vide pour auto)">
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
                
                const img = document.createElement('img');
                img.className = 'file-preview';
                img.src = URL.createObjectURL(file);
                
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
            
            const apiKey = document.getElementById('apiKey').value.trim();
            if (!apiKey) {
                alert('⚠️ Veuillez entrer votre clé API Freepik');
                document.getElementById('apiKey').focus();
                return;
            }
            
            progress.classList.add('active');
            results.classList.remove('active');
            processBtn.disabled = true;
            processBtn.innerHTML = '<span class="spinner"></span>Traitement en cours...';
            
            const formData = new FormData();
            files.forEach(file => formData.append('images', file));
            formData.append('scaleFactor', document.getElementById('scaleFactor').value);
            formData.append('mode', document.getElementById('mode').value);
            formData.append('quality', document.getElementById('quality').value);
            formData.append('apiKey', apiKey);
            
            const maxWidth = document.getElementById('maxWidth').value;
            if (maxWidth) formData.append('maxWidth', maxWidth);
            
            try {
                updateProgress(10, 'Upload des images...');
                
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


def call_freepik_upscale(image_data, api_key, scale=2, prompt="", creativity=0.5, mode='precision'):
    """Appelle l'API Freepik/Magnific pour upscaler une image
    
    Modes:
    - 'precision': Préserve le texte, fidélité maximale (RECOMMANDÉ pour photos produit)
    - 'creative': Ajoute des détails, modifie l'image (détruit le texte)
    """
    headers = {
        'x-freepik-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    # Convertir l'image en Base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Choisir l'endpoint selon le mode
    if mode == 'precision':
        api_url = FREEPIK_PRECISION_URL
        # Payload pour Precision (plus simple, pas de creativity/prompt)
        payload = {
            'image': image_base64,
            'scale': scale
        }
        print(f"  → Mode PRECISION (préserve le texte)")
    else:
        api_url = FREEPIK_API_URL
        # Payload pour Creative
        payload = {
            'image': image_base64,
            'scale': scale,
            'prompt': prompt if prompt else 'upscale',
            'creativity': int(creativity * 10)  # Convertir 0.5 -> 5
        }
        print(f"  → Mode CREATIVE (modifie l'image)")
    
    response = requests.post(
        api_url,
        headers=headers,
        json=payload,
        timeout=120
    )
    
    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")
    
    result = response.json()
    
    # L'API Freepik/Magnific est asynchrone - retourne un task_id dans 'data'
    if 'data' in result and 'task_id' in result['data']:
        task_id = result['data']['task_id']
        # Attendre et poll le résultat
        return poll_task_result(task_id, api_key)
    else:
        raise Exception(f"Unexpected API response: {result}")


def poll_task_result(task_id, api_key, max_attempts=30, delay=2):
    """Poll le statut de la tâche jusqu'à completion"""
    headers = {
        'x-freepik-api-key': api_key
    }
    
    for attempt in range(max_attempts):
        response = requests.get(
            f"{FREEPIK_API_URL}/{task_id}",
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            # Le statut peut être dans result.status ou result.data.status
            status = (result.get('status') or result.get('data', {}).get('status', '')).upper()
            
            print(f"  → Poll {attempt+1}/{max_attempts}: status = {status}")
            
            if status == 'COMPLETED':
                # Télécharger l'image upscalée
                # Chercher l'URL dans différents emplacements possibles
                data = result.get('data', {})
                image_url = None
                
                # Essayer différents emplacements possibles pour l'URL
                if 'url' in data:
                    image_url = data['url']
                elif 'generated' in data and len(data['generated']) > 0:
                    image_url = data['generated'][0]
                elif 'image_url' in data:
                    image_url = data['image_url']
                elif 'output_url' in data:
                    image_url = data['output_url']
                elif 'result' in result and 'url' in result['result']:
                    image_url = result['result']['url']
                
                if image_url:
                    print(f"  → Téléchargement de l'image: {image_url[:50]}...")
                    img_response = requests.get(image_url, timeout=60)
                    if img_response.status_code == 200:
                        return img_response.content, data
                    else:
                        raise Exception(f"Failed to download image: {img_response.status_code}")
                
                # Debug: afficher la structure reçue
                print(f"  ⚠️ Structure reçue: {list(data.keys())}")
                raise Exception(f"Result URL not found. Keys: {list(data.keys())}")
            elif status == 'FAILED':
                error_msg = result.get('error') or result.get('data', {}).get('error', 'Unknown error')
                raise Exception(f"Task failed: {error_msg}")
            # Sinon CREATED, PENDING, PROCESSING → continuer à poll
        
        time.sleep(delay)
    
    raise Exception("Task timeout - took too long to complete")


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
        max_width = request.form.get('maxWidth')
        max_width = int(max_width) if max_width else None
        api_key = request.form.get('apiKey')
        mode = request.form.get('mode', 'precision')  # 'precision' ou 'creative'
        
        if not api_key:
            return jsonify({'success': False, 'error': 'Clé API Freepik requise'}), 400
        
        results = []
        
        for file in files:
            try:
                original_data = file.read()
                original_size = len(original_data)
                original_name = secure_filename(file.filename)
                
                # Obtenir dimensions originales
                img_temp = Image.open(io.BytesIO(original_data))
                original_dims = f"{img_temp.width}x{img_temp.height}"
                
                # Étape 1: Upscale via Freepik
                upscaled_data, api_info = call_freepik_upscale(original_data, api_key, scale_factor, mode=mode)
                
                # Étape 2: Conversion WebP
                webp_data, final_size = convert_to_webp(upscaled_data, quality, max_width)
                
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
                
            except Exception as e:
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
    print("🎨 Image Upscaler Pro - Démarrage...")
    print("📁 Uploads:", os.path.abspath(UPLOAD_FOLDER))
    print("📁 Outputs:", os.path.abspath(OUTPUT_FOLDER))
    print("")
    print("🌐 Interface web: http://localhost:5000")
    print("✨ Ouvrez votre navigateur et allez sur http://localhost:5000")
    print("")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
