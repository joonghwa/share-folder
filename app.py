from flask import Flask, request, send_from_directory, redirect, url_for

import os
app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return '''
    <h2>파일 업로드</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
      <input type="file" name="file">
      <input type="submit" value="업로드">
    </form>
    <br>
    <a href="/files">파일 목록 보기</a>
    '''

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file']
    if file:
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return redirect(url_for('home'))

@app.route('/files')
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    links = [f'<li><a href="/download/{f}">{f}</a></li>' for f in files]
    return f'<h2>파일 목록</h2><ul>{"".join(links)}</ul><a href="/">← 업로드</a>'

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render가 제공하는 포트를 사용
    app.run(host='0.0.0.0', port=port)
