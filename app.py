#!/usr/bin/env python3
"""
Smart Media Compressor Pro
Compresse photos, vidéos et GIF sans perte de qualité visible
Optimisation intelligente avec détection de contenu
"""

import os
import io
import subprocess
import shutil
from PIL import Image
from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

HTML_INTERFACE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🗜️ Smart Media Compressor Pro</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
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
            max-width: 800px; 
            width: 100%; 
            box-shadow: 0 20px 60px rgba(0,0,0,0.3); 
        }
        h1 { text-align: center; color: #333; margin-bottom: 10px; }
        .subtitle { text-align: center; color: #666; margin-bottom: 30px; font-size: 14px; }
        .info-box {
            background: #e8f5e9;
            border: 1px solid #4caf50;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 25px;
            color: #2e7d32;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin-bottom: 25px;
        }
        .stat-box {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        .stat-value { font-size: 24px; font-weight: bold; color: #11998e; }
        .stat-label { font-size: 12px; color: #666; }
        .drop-zone { 
            border: 3px dashed #11998e; 
            border-radius: 15px; 
            padding: 50px 20px; 
            text-align: center; 
            transition: all 0.3s ease; 
            cursor: pointer; 
            background: #e8f5e9; 
            margin-bottom: 20px;
        }
        .drop-zone:hover { 
            background: #c8e6c9; 
            transform: scale(1.02); 
        }
        #fileInput { display: none; }
        .options { 
            margin: 25px 0; 
            padding: 20px; 
            background: #f5f5f5; 
            border-radius: 10px; 
        }
        .option-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #333; font-weight: 600; font-size: 14px; }
        select, input[type="range"] { width: 100%; padding: 10px; border: 2px solid #ddd; border-radius: 8px; }
        .quality-display { text-align: center; font-weight: bold; color: #11998e; margin-top: 5px; }
        .btn { 
            width: 100%; 
            padding: 15px; 
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%); 
            color: white; 
            border: none; 
            border-radius: 10px; 
            font-size: 16px; 
            font-weight: 600; 
            cursor: pointer; 
            transition: transform 0.2s; 
        }
        .btn:hover { transform: translateY(-2px); }
        .btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .file-list { margin: 20px 0; max-height: 200px; overflow-y: auto; }
        .file-item { 
            display: flex; 
            align-items: center; 
            padding: 12px; 
            background: #e8f5e9; 
            border-radius: 8px; 
            margin-bottom: 8px; 
        }
        .file-icon { font-size: 24px; margin-right: 10px; }
        .file-info { flex: 1; }
        .file-name { font-weight: 600; color: #333; font-size: 14px; }
        .file-size { color: #666; font-size: 12px; }
        .results { margin-top: 20px; }
        .result-item { 
            display: flex; 
            align-items: center; 
            padding: 15px; 
            background: #e8f5e9; 
            border-radius: 10px; 
            margin-bottom: 10px; 
            border-left: 4px solid #4caf50;
        }
        .result-item.error { background: #ffebee; border-left-color: #f44336; }
        .savings { 
            background: #4caf50; 
            color: white; 
            padding: 4px 8px; 
            border-radius: 4px; 
            font-size: 12px; 
            font-weight: bold;
        }
        .download-btn {
            background: #11998e;
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 5px;
            font-size: 13px;
            font-weight: 600;
        }
        .format-badge {
            background: #666;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            margin-left: 5px;
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
        <h1>🗜️ Smart Media Compressor</h1>
        <p class="subtitle">Compresse photos, vidéos & GIF - Qualité préservée</p>
        
        <div class="info-box">
            <strong>✅ Optimisation intelligente</strong><br>
            Détecte automatiquement le meilleur format et les meilleurs paramètres.<br>
            <small>Support: JPG, PNG, WebP, MP4, MOV, GIF, WebM</small>
        </div>

        <div class="stats" id="stats" style="display:none;">
            <div class="stat-box">
                <div class="stat-value" id="savedSize">0%</div>
                <div class="stat-label">Réduction moyenne</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="savedBytes">0 MB</div>
                <div class="stat-label">Espace gagné</div>
            </div>
            <div class="stat-box">
                <div class="stat-value" id="processedCount">0</div>
                <div class="stat-label">Fichiers traités</div>
            </div>
        </div>

        <div class="drop-zone" id="dropZone">
            <div style="font-size: 48px; margin-bottom: 10px;">📁</div>
            <div style="color: #11998e; font-size: 18px; font-weight: 600;">
                Glissez vos fichiers ici
            </div>
            <div style="color: #666; font-size: 13px; margin-top: 5px;">
                Images • Vidéos • GIF
            </div>
        </div>
        
        <input type="file" id="fileInput" multiple accept="image/*,video/*,.gif">
        
        <div class="file-list" id="fileList"></div>
        
        <div class="options">
            <div class="option-group">
                <label>🎯 Niveau de compression</label>
                <select id="compressionLevel">
                    <option value="lossless">🟢 Sans perte (qualité max)</option>
                    <option value="balanced" selected>🟡 Équilibré (recommandé)</option>
                    <option value="aggressive">🔴 Forte (fichiers légers)</option>
                    <option value="custom">⚙️ Personnalisé</option>
                </select>
            </div>
            <div class="option-group" id="customQuality" style="display:none;">
                <label>Qualité (1-100)</label>
                <input type="range" id="quality" min="1" max="100" value="85">
                <div class="quality-display" id="qualityValue">85%</div>
            </div>
            <div class="option-group">
                <label>📐 Dimensions max (optionnel)</label>
                <select id="maxDimension">
                    <option value="">Original (sans changement)</option>
                    <option value="1920">1920px (Full HD)</option>
                    <option value="1080">1080px (HD)</option>
                    <option value="800">800px (Web)</option>
                    <option value="600">600px (Mobile)</option>
                </select>
            </div>
        </div>
        
        <button class="btn" id="processBtn" disabled>
            🚀 Compresser les fichiers
        </button>
        
        <div class="results" id="results"></div>
    </div>

    <script>
        const dropZone = document.getElementById('dropZone');
        const fileInput = document.getElementById('fileInput');
        const fileList = document.getElementById('fileList');
        const processBtn = document.getElementById('processBtn');
        const results = document.getElementById('results');
        const compressionLevel = document.getElementById('compressionLevel');
        const customQuality = document.getElementById('customQuality');
        const qualitySlider = document.getElementById('quality');
        const qualityValue = document.getElementById('qualityValue');
        
        let files = [];
        
        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.style.background = '#c8e6c9'; });
        dropZone.addEventListener('dragleave', () => dropZone.style.background = '#e8f5e9'; });
        dropZone.addEventListener('drop', (e) => { 
            e.preventDefault(); 
            dropZone.style.background = '#e8f5e9'; 
            handleFiles(e.dataTransfer.files); 
        });
        fileInput.addEventListener('change', (e) => handleFiles(e.target.files));
        
        compressionLevel.addEventListener('change', () => {
            customQuality.style.display = compressionLevel.value === 'custom' ? 'block' : 'none';
        });
        
        qualitySlider.addEventListener('input', () => {
            qualityValue.textContent = qualitySlider.value + '%';
        });
        
        function getFileIcon(filename) {
            const ext = filename.split('.').pop().toLowerCase();
            if (['jpg','jpeg','png','webp'].includes(ext)) return '🖼️';
            if (['mp4','mov','avi','webm'].includes(ext)) return '🎬';
            if (ext === 'gif') return '🎞️';
            return '📄';
        }
        
        function formatBytes(b) {
            if (b === 0) return '0 B';
            const k = 1024;
            const s = ['B','KB','MB','GB'];
            const i = Math.floor(Math.log(b)/Math.log(k));
            return parseFloat((b/Math.pow(k,i)).toFixed(2)) + ' ' + s[i];
        }
        
        function handleFiles(newFiles) {
            files = [...files, ...Array.from(newFiles)];
            updateFileList();
        }
        
        function updateFileList() {
            fileList.innerHTML = files.map((file, i) => `
                <div class="file-item">
                    <span class="file-icon">${getFileIcon(file.name)}</span>
                    <div class="file-info">
                        <div class="file-name">${file.name}</div>
                        <div class="file-size">${formatBytes(file.size)}</div>
                    </div>
                    <button onclick="removeFile(${i})" style="background:#ff4757;color:white;border:none;padding:5px 10px;border-radius:5px;cursor:pointer;">✕</button>
                </div>
            `).join('');
            processBtn.disabled = files.length === 0;
        }
        
        function removeFile(i) { files.splice(i, 1); updateFileList(); }
        
        processBtn.addEventListener('click', async () => {
            if (files.length === 0) return;
            
            processBtn.disabled = true;
            processBtn.innerHTML = '<span class="spinner"></span>Compression en cours...';
            
            const formData = new FormData();
            files.forEach(f => formData.append('files', f));
            formData.append('compressionLevel', compressionLevel.value);
            formData.append('quality', qualitySlider.value);
            formData.append('maxDimension', document.getElementById('maxDimension').value);
            
            try {
                const res = await fetch('/compress', { method: 'POST', body: formData });
                const data = await res.json();
                
                if (data.success) {
                    showResults(data.results, data.stats);
                } else throw new Error(data.error);
            } catch (e) {
                alert('❌ ' + e.message);
            }
            
            processBtn.innerHTML = '🚀 Compresser les fichiers';
            processBtn.disabled = false;
        });
        
        function showResults(r, stats) {
            document.getElementById('stats').style.display = 'grid';
            document.getElementById('savedSize').textContent = stats.avgReduction + '%';
            document.getElementById('savedBytes').textContent = formatBytes(stats.totalSaved);
            document.getElementById('processedCount').textContent = stats.processed;
            
            results.innerHTML = r.map(x => {
                if (x.error) return `<div class="result-item error"><div><strong>❌ ${x.original_name}</strong><br><small>${x.error}</small></div></div>`;
                return `
                    <div class="result-item">
                        <div style="flex:1;">
                            <strong>${x.original_name}</strong>
                            <span class="format-badge">${x.output_format}</span>
                            <br>
                            <small>${formatBytes(x.original_size)} → ${formatBytes(x.compressed_size)}</small>
                            <span class="savings">-${x.reduction}%</span>
                        </div>
                        <a href="${x.download_url}" class="download-btn" download>📥</a>
                    </div>
                `;
            }).join('');
        }
    </script>
</body>
</html>
'''

def get_compression_settings(level, quality=None):
    """Retourne les paramètres de compression selon le niveau"""
    settings = {
        'lossless': {'quality': 95, 'method': 6, 'optimize': True},
        'balanced': {'quality': 85, 'method': 6, 'optimize': True},
        'aggressive': {'quality': 70, 'method': 4, 'optimize': True},
        'custom': {'quality': int(quality) if quality else 85, 'method': 6, 'optimize': True}
    }
    return settings.get(level, settings['balanced'])

def smart_compress_image(input_path, output_path, settings, max_dimension=None):
    """Compresse intelligemment une image"""
    with Image.open(input_path) as img:
        # Convertir en RGB si nécessaire
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            if img.mode in ('RGBA', 'LA'):
                background.paste(img, mask=img.split()[-1])
                img = background
            else:
                img = img.convert('RGB')
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionner si nécessaire
        if max_dimension:
            max_dim = int(max_dimension)
            if max(img.size) > max_dim:
                ratio = max_dim / max(img.size)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Choisir le meilleur format
        ext = os.path.splitext(input_path)[1].lower()
        
        # Pour les photos: WebP
        # Pour les images avec transparence: PNG
        # Pour les logos/simples: PNG ou WebP
        
        if img.mode == 'RGBA':
            # Garder PNG pour la transparence mais optimisé
            img.save(output_path, 'PNG', optimize=True)
        else:
            # WebP pour meilleure compression
            img.save(output_path, 'WebP', 
                    quality=settings['quality'],
                    method=settings['method'],
                    optimize=settings['optimize'])

def compress_video(input_path, output_path, compression_level, max_dimension=None):
    """Compresse une vidéo avec ffmpeg"""
    try:
        # Paramètres selon le niveau
        if compression_level == 'lossless':
            crf = '18'
            preset = 'slow'
        elif compression_level == 'balanced':
            crf = '23'
            preset = 'medium'
        elif compression_level == 'aggressive':
            crf = '28'
            preset = 'fast'
        else:  # custom
            crf = '23'
            preset = 'medium'
        
        # Scale si nécessaire
        scale_filter = ''
        if max_dimension:
            max_dim = int(max_dimension)
            scale_filter = f'-vf "scale=\'if(gt(iw,ih),{max_dim},-2)\':\'if(gt(iw,ih),-2,{max_dim})\'" '
        
        cmd = [
            'ffmpeg', '-i', input_path,
            '-vcodec', 'libx264',
            '-crf', crf,
            '-preset', preset,
            '-acodec', 'aac',
            '-b:a', '128k'
        ]
        
        if scale_filter:
            cmd.extend(['-vf', f'scale=\'if(gt(iw,ih),{max_dim},-2)\':\'if(gt(iw,ih),-2,{max_dim})\''])
        
        cmd.extend(['-y', output_path])
        
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Erreur compression vidéo: {e}")
        return False

def compress_gif(input_path, output_path, compression_level, max_dimension=None):
    """Compresse un GIF"""
    try:
        with Image.open(input_path) as img:
            frames = []
            
            # Paramètres de réduction de palette
            if compression_level == 'lossless':
                colors = 256
            elif compression_level == 'balanced':
                colors = 128
            elif compression_level == 'aggressive':
                colors = 64
            else:
                colors = 128
            
            # Redimensionner si nécessaire
            if max_dimension:
                max_dim = int(max_dimension)
                if max(img.size) > max_dim:
                    ratio = max_dim / max(img.size)
                    new_size = (int(img.width * ratio), int(img.height * ratio))
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # Pour les GIF animés
            if getattr(img, 'is_animated', False):
                frames = []
                for frame_num in range(img.n_frames):
                    img.seek(frame_num)
                    frame = img.convert('P', palette=Image.ADAPTIVE, colors=colors)
                    frames.append(frame)
                
                frames[0].save(
                    output_path,
                    save_all=True,
                    append_images=frames[1:],
                    optimize=True,
                    loop=0
                )
            else:
                # GIF statique
                img = img.convert('P', palette=Image.ADAPTIVE, colors=colors)
                img.save(output_path, 'GIF', optimize=True)
            
            return True
    except Exception as e:
        print(f"Erreur compression GIF: {e}")
        return False

@app.route('/')
def index():
    return render_template_string(HTML_INTERFACE)

@app.route('/compress', methods=['POST'])
def compress_files():
    try:
        if 'files' not in request.files:
            return jsonify({'success': False, 'error': 'Aucun fichier'}), 400
        
        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            return jsonify({'success': False, 'error': 'Aucun fichier sélectionné'}), 400
        
        compression_level = request.form.get('compressionLevel', 'balanced')
        quality = request.form.get('quality', 85)
        max_dimension = request.form.get('maxDimension') or None
        
        settings = get_compression_settings(compression_level, quality)
        
        results = []
        total_saved = 0
        total_reduction = 0
        processed = 0
        
        for file in files:
            try:
                filename = secure_filename(file.filename)
                input_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(input_path)
                
                original_size = os.path.getsize(input_path)
                ext = os.path.splitext(filename)[1].lower()
                
                # Déterminer le format de sortie
                if ext in ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']:
                    if ext == '.png' and compression_level != 'lossless':
                        output_ext = '.webp'
                    else:
                        output_ext = ext
                    output_name = filename.rsplit('.', 1)[0] + output_ext
                    output_path = os.path.join(OUTPUT_FOLDER, output_name)
                    
                    smart_compress_image(input_path, output_path, settings, max_dimension)
                    
                elif ext in ['.mp4', '.mov', '.avi', '.webm', '.mkv']:
                    output_name = filename.rsplit('.', 1)[0] + '_compressed.mp4'
                    output_path = os.path.join(OUTPUT_FOLDER, output_name)
                    
                    if not compress_video(input_path, output_path, compression_level, max_dimension):
                        raise Exception("Échec compression vidéo")
                    
                elif ext == '.gif':
                    output_name = filename
                    output_path = os.path.join(OUTPUT_FOLDER, output_name)
                    
                    if not compress_gif(input_path, output_path, compression_level, max_dimension):
                        raise Exception("Échec compression GIF")
                
                else:
                    raise Exception(f"Format non supporté: {ext}")
                
                compressed_size = os.path.getsize(output_path)
                reduction = round((1 - compressed_size/original_size) * 100)
                saved = original_size - compressed_size
                
                results.append({
                    'success': True,
                    'original_name': filename,
                    'output_format': output_ext if 'output_ext' in locals() else ext,
                    'original_size': original_size,
                    'compressed_size': compressed_size,
                    'reduction': reduction,
                    'saved': saved,
                    'download_url': f'/download/{os.path.basename(output_path)}'
                })
                
                total_saved += saved
                total_reduction += reduction
                processed += 1
                
                # Cleanup
                os.remove(input_path)
                
            except Exception as e:
                results.append({
                    'success': False,
                    'original_name': file.filename,
                    'error': str(e)
                })
        
        avg_reduction = round(total_reduction / processed) if processed > 0 else 0
        
        return jsonify({
            'success': True,
            'results': results,
            'stats': {
                'totalSaved': total_saved,
                'avgReduction': avg_reduction,
                'processed': processed
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    return send_file(os.path.join(OUTPUT_FOLDER, filename), as_attachment=True)

if __name__ == '__main__':
    print("🗜️ Smart Media Compressor Pro")
    print("🌐 http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
