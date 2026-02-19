#!/usr/bin/env python3
"""
Image Upscaler Pro - Version Simple & Efficace
Upscale avec PIL (Lanczos) + Conversion WebP
100% offline, gratuit, préserve le texte parfaitement
"""

import os
import io
from PIL import Image, ImageFilter
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Page HTML intégrée
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
        select { 
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
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
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
        }
        .result-item.error { background: #f8d7da; }
        .result-preview { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; margin-right: 15px; }
        .result-info { flex: 1; }
        .result-name { font-weight: 600; color: #155724; }
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
        <p class="subtitle">Upscale haute qualité - Préserve le texte</p>
        
        <div class="info-box">
            <strong>✅ Mode Lanczos activé</strong><br>
            Algorithme d'upscaling de haute qualité qui préserve parfaitement les détails et le texte.<br>
            <small>100% offline, rapide, et gratuit.</small>
        </div>

        <div class="drop-zone" id="dropZone">
            <div class="drop-zone-icon">📁</div>
            <div style="color: #667eea; font-size: 18px; font-weight: 600;">Glissez vos images ici</div>
            <div style="color: #888; font-size: 13px;">JPG, PNG, WebP</div>
        </div>
        
        <input type="file" id="fileInput" multiple accept="image/*">
        
        <div class="file-list" id="fileList"></div>
        
        <div class="options">
            <div class="option-group">
                <label>🎯 Niveau d'upscale</label>
                <select id="scaleFactor">
                    <option value="2" selected>2x (Double résolution)</option>
                    <option value="3">3x (Triple résolution)</option>
                    <option value="4">4x (Quadruple résolution)</option>
                </select>
            </div>
            <div class="option-group">
                <label>🖼️ Qualité WebP</label>
                <select id="quality">
                    <option value="85" selected>85% (Équilibré)</option>
                    <option value="90">90% (Haute qualité)</option>
                    <option value="95">95% (Maximum)</option>
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
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => { e.preventDefault(); dropZone.classList.remove('dragover'); handleFiles(e.dataTransfer.files); });
        fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
        
        function handleFiles(newFiles) {
            files = [...files, ...Array.from(newFiles).filter(f => f.type.startsWith('image/'))];
            updateFileList();
        }
        
        function updateFileList() {
            fileList.innerHTML = files.map((file, i) => `
                <div class="file-item">
                    <img class="file-preview" src="${URL.createObjectURL(file)}">
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatBytes(file.size)}</div>
                    </div>
                    <button class="file-remove" onclick="removeFile(${i})">✕</button>
                </div>
            `).join('');
            processBtn.disabled = files.length === 0;
        }
        
        function removeFile(index) { files.splice(index, 1); updateFileList(); }
        
        function formatBytes(b) { if (b === 0) return '0 B'; const k = 1024; const s = ['B','KB','MB']; const i = Math.floor(Math.log(b)/Math.log(k)); return parseFloat((b/Math.pow(k,i)).toFixed(2))+' '+s[i]; }
        
        processBtn.addEventListener('click', async () => {
            if (files.length === 0) return;
            progress.classList.add('active');
            results.classList.remove('active');
            processBtn.disabled = true;
            processBtn.innerHTML = '<span class="spinner"></span>Traitement...';
            
            const formData = new FormData();
            files.forEach(f => formData.append('images', f));
            formData.append('scaleFactor', document.getElementById('scaleFactor').value);
            formData.append('quality', document.getElementById('quality').value);
            
            try {
                const res = await fetch('/upscale', { method: 'POST', body: formData });
                const data = await res.json();
                if (data.success) {
                    progress.classList.remove('active');
                    showResults(data.results);
                    processBtn.innerHTML = '🚀 Lancer le traitement';
                    processBtn.disabled = false;
                } else throw new Error(data.error);
            } catch (e) {
                progress.classList.remove('active');
                processBtn.innerHTML = '🚀 Lancer le traitement';
                processBtn.disabled = false;
                alert('❌ ' + e.message);
            }
        });
        
        function showResults(r) {
            results.innerHTML = '<h3 style="margin-bottom:15px;color:#28a745;">✅ Terminé !</h3>' + 
                r.map(x => x.error ? 
                    `<div class="result-item error"><div class="result-info"><div class="result-name">❌ ${x.original_name}</div><div class="result-meta">${x.error}</div></div></div>` :
                    `<div class="result-item"><img class="result-preview" src="${x.preview_url}"><div class="result-info"><div class="result-name">${x.original_name}</div><div class="result-meta">${x.original_dims} → ${x.upscaled_dims}</div></div><a href="${x.download_url}" class="download-btn" download>📥</a></div>`
                ).join('');
            results.classList.add('active');
        }
    </script>
</body>
</html>
'''


def upscale_image_pil(image_data, scale=2):
    """Upscale avec PIL Lanczos - haute qualité, préserve le texte"""
    img = Image.open(io.BytesIO(image_data))
    
    # Convertir en RGB si nécessaire
    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGB')
    
    original_size = img.size
    new_size = (img.width * scale, img.height * scale)
    
    # Upscale avec Lanczos (meilleure qualité pour préserver les détails)
    upscaled = img.resize(new_size, Image.Resampling.LANCZOS)
    
    # Amélioration légère pour les contours (préserve le texte)
    upscaled = upscaled.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
    
    # Convertir en bytes
    output = io.BytesIO()
    upscaled.save(output, format='PNG')
    output.seek(0)
    
    return output.getvalue(), upscaled.size


def convert_to_webp(image_data, quality=85):
    """Convertit en WebP optimisé"""
    img = Image.open(io.BytesIO(image_data))
    
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    output = io.BytesIO()
    img.save(output, format='WebP', quality=quality, method=6)
    output.seek(0)
    
    return output.getvalue(), img.size


@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)


@app.route('/upscale', methods=['POST'])
def upscale_images():
    try:
        if 'images' not in request.files:
            return jsonify({'success': False, 'error': 'Aucune image'}), 400
        
        files = request.files.getlist('images')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'Aucune image sélectionnée'}), 400
        
        scale = int(request.form.get('scaleFactor', 2))
        quality = int(request.form.get('quality', 85))
        
        results = []
        
        for file in files:
            try:
                original = file.read()
                img_temp = Image.open(io.BytesIO(original))
                orig_dims = f"{img_temp.width}x{img_temp.height}"
                
                # Upscale
                upscaled, (w, h) = upscale_image_pil(original, scale)
                
                # WebP
                webp, final_size = convert_to_webp(upscaled, quality)
                
                # Sauvegarder
                out_name = f"upscaled_{secure_filename(file.filename).rsplit('.', 1)[0]}.webp"
                out_path = os.path.join(OUTPUT_FOLDER, out_name)
                
                with open(out_path, 'wb') as f:
                    f.write(webp)
                
                results.append({
                    'success': True,
                    'original_name': file.filename,
                    'upscaled_dims': f"{final_size[0]}x{final_size[1]}",
                    'original_dims': orig_dims,
                    'download_url': f'/download/{out_name}',
                    'preview_url': f'/preview/{out_name}'
                })
                
            except Exception as e:
                results.append({'success': False, 'original_name': file.filename, 'error': str(e)})
        
        return jsonify({'success': True, 'results': results})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)


@app.route('/preview/<filename>')
def preview(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename))


if __name__ == '__main__':
    print("🎨 Image Upscaler Pro")
    print("🌐 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
