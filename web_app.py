from flask import Flask, request, render_template_string, send_file
import os, sys, shutil, zipfile
from auto_cloner import AutoWebCloner

app = Flask(__name__)

DEFAULT_DATA_FOLDER = r"C:\Users\admin\Downloads\AutoWebCloner\customer_data"

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Auto Web Cloner</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background: #0f0c29; background: linear-gradient(to right, #302b63, #0f0c29); padding: 40px; margin: 0; min-height: 100vh; }
        .container { max-width: 700px; margin: auto; background: white; padding: 40px; border-radius: 14px; box-shadow: 0 10px 40px rgba(0,0,0,0.5); }
        h1 { color: #2c3e50; text-align: center; margin-bottom: 5px; }
        .subtitle { text-align: center; color: #888; font-size: 14px; margin-bottom: 30px; }
        label { font-weight: bold; color: #333; display: block; margin-bottom: 5px; margin-top: 15px; }
        input[type="text"] { width: 100%; padding: 12px; border: 2px solid #ddd; border-radius: 6px; font-size: 14px; }
        input[type="text"]:focus { border-color: #6c63ff; outline: none; }
        button[type="submit"] { margin-top: 20px; background: #6c63ff; color: white; border: none; padding: 14px; font-size: 16px; border-radius: 8px; cursor: pointer; width: 100%; font-weight: bold; letter-spacing: 0.5px; }
        button[type="submit"]:hover { background: #574fd6; }
        .error { color: #dc3545; margin-top: 15px; padding: 12px; background: #f8d7da; border-radius: 6px; }
        .success-box { margin-top: 20px; padding: 20px; background: #d4edda; border-radius: 8px; text-align: center; }
        .success-box h3 { color: #155724; margin: 0 0 15px; }
        .download-btn { display: inline-block; background: #28a745; color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: bold; font-size: 15px; }
        .download-btn:hover { background: #218838; }
        .steps { background: #f8f9fa; border-radius: 8px; padding: 15px 20px; margin-top: 20px; font-size: 13px; color: #555; }
        .steps b { color: #2c3e50; }
        .steps ol { margin: 8px 0 0 0; padding-left: 18px; }
        .steps li { margin-bottom: 4px; }
    </style>
</head>
<body>
<div class="container">
    <h1>🌐 Auto Web Cloner</h1>
    <p class="subtitle">Clone any website's design and inject your customer's data automatically</p>

    <form method="POST" action="/clone">
        <label>📎 Target Website URL (Design to Clone)</label>
        <input type="text" name="target_url" placeholder="https://example.com" value="{{ last_url or '' }}" required>

        <label>&#x1F4C1; Customer Data Folder Path</label>
        <input type="text" name="data_folder" placeholder="C:\Users\admin\Downloads\AutoWebCloner\customer_data" value="{{ last_folder }}" required>

        <button type="submit">🚀 Clone & Generate Website</button>
    </form>

    {% if error %}
        <div class="error">❌ {{ error }}</div>
    {% endif %}

    {% if download_ready %}
    <div class="success-box">
        <h3>✅ Website Generated Successfully!</h3>
        <p>Your cloned website with customer data is ready. Click below to download the complete folder as a ZIP file.</p>
        <a href="/download_output" class="download-btn">📥 Download Website (ZIP)</a>
    </div>
    {% endif %}

    <div class="steps">
        <b>📌 How it works:</b>
        <ol>
            <li>Put customer's <b>.txt files</b> (content) and <b>images/</b> folder in the data folder.</li>
            <li>Enter the URL of any website whose <b>design/layout</b> you want to clone.</li>
            <li>Click <b>Clone & Generate</b> — the script injects customer data into the design.</li>
            <li>Download the complete website as a <b>ZIP file</b> ready to deploy.</li>
        </ol>
    </div>
</div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML, last_folder=DEFAULT_DATA_FOLDER, last_url='')

@app.route('/clone', methods=['POST'])
def clone():
    target_url = request.form.get('target_url', '').strip()
    data_folder = request.form.get('data_folder', '').strip()

    if not target_url:
        return render_template_string(HTML, error="Please enter a Target URL.", last_url=target_url, last_folder=data_folder)
    if not os.path.exists(data_folder):
        return render_template_string(HTML, error=f"Data folder not found: {data_folder}", last_url=target_url, last_folder=data_folder)

    if not target_url.startswith('http'):
        target_url = 'https://' + target_url

    output_folder = os.path.join(os.path.dirname(data_folder), "output_website")

    print(f"[*] Cloning {target_url} with data from {data_folder} ...", flush=True)

    cloner = AutoWebCloner(target_url, data_folder, output_folder)
    cloner.run()

    if os.path.exists(os.path.join(output_folder, "index.html")):
        return render_template_string(HTML, download_ready=True, last_url=target_url, last_folder=data_folder)
    else:
        return render_template_string(HTML, error="Cloning failed. Could not generate the website. Please try a different URL.", last_url=target_url, last_folder=data_folder)

@app.route('/download_output')
def download_output():
    output_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output_website")
    zip_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "cloned_website.zip")

    # Create ZIP of output_website folder
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
