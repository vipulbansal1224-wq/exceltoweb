from flask import Flask, request, render_template_string, send_file
import os, sys, shutil, zipfile, tempfile
from auto_cloner import AutoWebCloner

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), "autowebcloner_uploads")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Auto Web Cloner</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: linear-gradient(135deg, #0f0c29, #302b63, #24243e); padding: 40px; margin: 0; min-height: 100vh; }
        .container { max-width: 720px; margin: auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 12px 50px rgba(0,0,0,0.5); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 5px; font-size: 26px; }
        .subtitle { text-align: center; color: #888; font-size: 14px; margin-bottom: 30px; }
        label { font-weight: bold; color: #444; display: block; margin-bottom: 6px; margin-top: 18px; font-size: 14px; }
        
        input[type="text"] { width: 100%; padding: 12px 14px; border: 2px solid #e0e0e0; border-radius: 8px; font-size: 14px; transition: border 0.2s; }
        input[type="text"]:focus { border-color: #6c63ff; outline: none; }

        /* File Upload Drop Zone */
        .upload-zone {
            border: 2px dashed #6c63ff;
            border-radius: 10px;
            padding: 22px 20px;
            text-align: center;
            background: #f8f7ff;
            cursor: pointer;
            transition: all 0.2s;
            position: relative;
        }
        .upload-zone:hover, .upload-zone.dragover { background: #ededff; border-color: #4a42d0; }
        .upload-zone input[type="file"] {
            position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
        }
        .upload-zone .icon { font-size: 32px; margin-bottom: 6px; }
        .upload-zone .hint { font-size: 13px; color: #888; margin-top: 4px; }
        .upload-zone .selected-info { font-size: 13px; color: #6c63ff; font-weight: bold; margin-top: 8px; display: none; }

        /* Tabs for txt vs images */
        .upload-tabs { display: flex; gap: 10px; margin-bottom: 10px; }
        .tab-btn { flex: 1; padding: 9px; border: 2px solid #e0e0e0; border-radius: 8px; background: white; cursor: pointer; font-size: 13px; color: #555; transition: all 0.2s; }
        .tab-btn.active { border-color: #6c63ff; background: #f0efff; color: #6c63ff; font-weight: bold; }

        button[type="submit"] { margin-top: 24px; background: linear-gradient(135deg, #6c63ff, #4a42d0); color: white; border: none; padding: 14px; font-size: 16px; border-radius: 10px; cursor: pointer; width: 100%; font-weight: bold; letter-spacing: 0.5px; transition: opacity 0.2s; }
        button[type="submit"]:hover { opacity: 0.88; }
        button[type="submit"]:disabled { background: #aaa; cursor: not-allowed; }

        .error { color: #dc3545; margin-top: 15px; padding: 14px; background: #fff5f5; border: 1px solid #f5c6cb; border-radius: 8px; font-size: 14px; }
        .success-box { margin-top: 20px; padding: 24px; background: #f0fff4; border: 1px solid #c3e6cb; border-radius: 10px; text-align: center; }
        .success-box h3 { color: #155724; margin: 0 0 10px; }
        .success-box p { color: #555; font-size: 14px; margin-bottom: 16px; }
        .download-btn { display: inline-block; background: #28a745; color: white; padding: 13px 35px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 15px; transition: background 0.2s; }
        .download-btn:hover { background: #218838; }

        .steps { background: #f8f9fa; border-radius: 10px; padding: 16px 20px; margin-top: 24px; font-size: 13px; color: #555; border: 1px solid #eee; }
        .steps b { color: #2c3e50; }
        .steps ol { margin: 8px 0 0 0; padding-left: 20px; }
        .steps li { margin-bottom: 5px; line-height: 1.5; }
        .badge { display: inline-block; background: #6c63ff; color: white; border-radius: 4px; font-size: 11px; padding: 1px 6px; margin-left: 4px; }

        .loading { display: none; text-align: center; margin-top: 16px; color: #6c63ff; font-size: 14px; }
        .spinner { border: 3px solid #f0efff; border-top: 3px solid #6c63ff; border-radius: 50%; width: 22px; height: 22px; animation: spin 0.9s linear infinite; display: inline-block; vertical-align: middle; margin-right: 8px; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
<div class="container">
    <h1>&#x1F310; Auto Web Cloner</h1>
    <p class="subtitle">Clone any website's design &amp; auto-inject your customer's data</p>

    <form method="POST" action="/clone" enctype="multipart/form-data" id="cloneForm">

        <!-- Step 1: URL -->
        <label>&#x1F517; Step 1 — Target Website URL <span class="badge">Design to Clone</span></label>
        <input type="text" name="target_url" placeholder="https://example.com" value="{{ last_url or '' }}" required>

        <!-- Step 2: Text Files Upload -->
        <label>&#x1F4DD; Step 2 — Upload Customer Text Files <span class="badge">.txt</span></label>
        <div class="upload-zone" id="txtZone">
            <input type="file" name="txt_files" id="txtInput" accept=".txt" multiple onchange="updateInfo('txtInfo', this)">
            <div class="icon">&#x1F4C4;</div>
            <div><b>Click to Browse</b> or Drag &amp; Drop</div>
            <div class="hint">Select one or more .txt files (about us, services, headings etc.)</div>
            <div class="selected-info" id="txtInfo"></div>
        </div>

        <!-- Step 3: Images Upload -->
        <label>&#x1F5BC;&#xFE0F; Step 3 — Upload Customer Images <span class="badge">optional</span></label>
        <div class="upload-zone" id="imgZone">
            <input type="file" name="img_files" id="imgInput" accept="image/*" multiple onchange="updateInfo('imgInfo', this)">
            <div class="icon">&#x1F4F8;</div>
            <div><b>Click to Browse</b> or Drag &amp; Drop</div>
            <div class="hint">Select logo, banner, product images (jpg, png, webp)</div>
            <div class="selected-info" id="imgInfo"></div>
        </div>

        <button type="submit" id="submitBtn" onclick="showLoading()">&#x1F680; Clone &amp; Generate Website</button>
    </form>

    <div class="loading" id="loadingBox">
        <div class="spinner"></div> Cloning website &amp; injecting data... please wait
    </div>

    {% if error %}
        <div class="error">&#x274C; {{ error }}</div>
    {% endif %}

    {% if download_ready %}
    <div class="success-box">
        <h3>&#x2705; Website Generated Successfully!</h3>
        <p>Your cloned website with customer data is ready. Download the complete folder as a ZIP.</p>
        <a href="/download_output" class="download-btn">&#x1F4E5; Download Website (ZIP)</a>
    </div>
    {% endif %}

    <div class="steps">
        <b>&#x1F4CC; How it works:</b>
        <ol>
            <li>Upload your customer's <b>text files</b> (about us, headings, services etc.)</li>
            <li>Upload customer <b>images</b> (logo, banner etc.) — optional</li>
            <li>Enter any website URL whose <b>design/layout</b> you want to clone</li>
            <li>Click <b>Clone &amp; Generate</b> — data auto-injects into the design</li>
            <li>Download the complete website as a <b>ZIP</b> ready to deploy anywhere</li>
        </ol>
    </div>
</div>

<script>
function updateInfo(infoId, input) {
    const info = document.getElementById(infoId);
    if (input.files.length > 0) {
        const names = Array.from(input.files).map(f => f.name).join(', ');
        info.textContent = input.files.length + ' file(s) selected: ' + names;
        info.style.display = 'block';
    } else {
        info.style.display = 'none';
    }
}

function compressImage(file, maxWidth, maxHeight, quality) {
    return new Promise((resolve) => {
        if (file.size < 300 * 1024) { resolve(file); return; }
        const reader = new FileReader();
        reader.onload = (e) => {
            const img = new Image();
            img.onload = () => {
                let w = img.width, h = img.height;
                if (w > maxWidth) { h = Math.round(h * maxWidth / w); w = maxWidth; }
                if (h > maxHeight) { w = Math.round(w * maxHeight / h); h = maxHeight; }
                const canvas = document.createElement('canvas');
                canvas.width = w; canvas.height = h;
                canvas.getContext('2d').drawImage(img, 0, 0, w, h);
                canvas.toBlob((blob) => {
                    resolve(new File([blob], file.name.replace(/\.[^.]+$/, '.jpg'), { type: 'image/jpeg' }));
                }, 'image/jpeg', quality);
            };
            img.src = e.target.result;
        };
        reader.readAsDataURL(file);
    });
}

document.getElementById('cloneForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const btn = document.getElementById('submitBtn');
    const loading = document.getElementById('loadingBox');
    const targetUrl = document.querySelector('input[name="target_url"]').value.trim();
    if (!targetUrl) { alert('Please enter a Target URL.'); return; }
    const txtInput = document.getElementById('txtInput');
    if (!txtInput.files.length) { alert('Please upload at least one .txt file.'); return; }

    btn.disabled = true;
    loading.style.display = 'block';
    loading.innerHTML = '<span style="border:3px solid #f0efff;border-top:3px solid #6c63ff;border-radius:50%;width:18px;height:18px;display:inline-block;animation:spin 0.9s linear infinite;vertical-align:middle;margin-right:8px;"></span> Compressing images...';

    const formData = new FormData();
    formData.append('target_url', targetUrl);
    for (const f of txtInput.files) { formData.append('txt_files', f); }

    const imgInput = document.getElementById('imgInput');
    let totalSize = Array.from(txtInput.files).reduce((s, f) => s + f.size, 0);
    for (const f of imgInput.files) {
        const c = await compressImage(f, 1200, 900, 0.72);
        totalSize += c.size;
        formData.append('img_files', c);
    }

    if (totalSize > 3.8 * 1024 * 1024) {
        loading.style.display = 'none'; btn.disabled = false;
        alert('Files too large even after compression. Please use fewer or smaller images (max total ~3.5MB).');
        return;
    }

    loading.innerHTML = '<span style="border:3px solid #f0efff;border-top:3px solid #6c63ff;border-radius:50%;width:18px;height:18px;display:inline-block;animation:spin 0.9s linear infinite;vertical-align:middle;margin-right:8px;"></span> Cloning & injecting data... please wait';

    try {
        const res = await fetch('/clone', { method: 'POST', body: formData });
        const ct = res.headers.get('Content-Type') || '';
        if (ct.includes('html')) {
            document.open(); document.write(await res.text()); document.close();
        } else {
            const blob = await res.blob();
            const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: 'cloned_website.zip' });
            document.body.appendChild(a); a.click(); a.remove();
            loading.style.display = 'none'; btn.disabled = false;
        }
    } catch(err) {
        loading.style.display = 'none'; btn.disabled = false;
        alert('Error: ' + err.message);
    }
});

['txtZone','imgZone'].forEach(id => {
    const zone = document.getElementById(id);
    zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragover'); });
    zone.addEventListener('dragleave', () => zone.classList.remove('dragover'));
    zone.addEventListener('drop', () => zone.classList.remove('dragover'));
});
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, last_url='')

@app.route('/clone', methods=['POST'])
def clone():
    target_url = request.form.get('target_url', '').strip()
    txt_files  = request.files.getlist('txt_files')
    img_files  = request.files.getlist('img_files')

    if not target_url:
        return render_template_string(HTML, error="Please enter a Target URL.", last_url=target_url)

    if not txt_files or txt_files[0].filename == '':
        return render_template_string(HTML, error="Please upload at least one .txt file with customer content.", last_url=target_url)

    if not target_url.startswith('http'):
        target_url = 'https://' + target_url

    # Save uploaded files to a temp folder
    if os.path.exists(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    img_dir = os.path.join(UPLOAD_FOLDER, "images")
    os.makedirs(img_dir, exist_ok=True)

    for f in txt_files:
        if f.filename.endswith('.txt'):
            f.save(os.path.join(UPLOAD_FOLDER, f.filename))

    for f in img_files:
        if f.filename:
            f.save(os.path.join(img_dir, f.filename))

    output_folder = os.path.join(tempfile.gettempdir(), "autowebcloner_output")

    print(f"[*] Cloning {target_url} ...", flush=True)
    cloner = AutoWebCloner(target_url, UPLOAD_FOLDER, output_folder)
    cloner.run()

    if os.path.exists(os.path.join(output_folder, "index.html")):
        return render_template_string(HTML, download_ready=True, last_url=target_url)
    else:
        return render_template_string(HTML, error="Cloning failed. Please try a different URL.", last_url=target_url)

@app.route('/download_output')
def download_output():
    output_folder = os.path.join(tempfile.gettempdir(), "autowebcloner_output")
    zip_path = os.path.join(tempfile.gettempdir(), "cloned_website.zip")

    if os.path.exists(zip_path):
        os.remove(zip_path)

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(output_folder):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, output_folder)
                zf.write(file_path, arcname)

    return send_file(zip_path, as_attachment=True, download_name="cloned_website.zip")

if __name__ == '__main__':
    print("[+] Auto Web Cloner running on http://127.0.0.1:8080", flush=True)
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
