import json
import firebase_admin
from firebase_admin import credentials, storage
import os

firebase_json = os.environ.get('FIREBASE_KEY')  # 환경 변수에서 JSON 문자열 가져오기

# 임시로 JSON 파일을 만들어줌
with open("temp_key.json", "w") as f:
    f.write(firebase_json)

# Firebase 초기화
cred = credentials.Certificate("temp_key.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'sharefolder-f4ed6.appspot.com'
})


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
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)

        # ✅ Firebase Storage에 업로드
        bucket = storage.bucket()
        blob = bucket.blob(f"uploads/{file.filename}")  # Firebase 경로
        blob.upload_from_filename(file_path)
        blob.make_public()  # 파일을 공개로 설정해서 누구나 접근 가능하게

        print(f"✅ Firebase 업로드 완료! URL: {blob.public_url}")

    return redirect(url_for('home'))


@app.route('/files')
def list_files():
    bucket = storage.bucket()
    blobs = bucket.list_blobs(prefix="uploads/")  # Firebase의 uploads/ 폴더 목록 가져오기

    links = []
    for blob in blobs:
        if blob.name.endswith("/"):  # 폴더 무시
            continue
        blob.make_public()
        links.append(f'<li><a href="{blob.public_url}" target="_blank">{os.path.basename(blob.name)}</a></li>')

    return f'<h2>Firebase 파일 목록</h2><ul>{"".join(links)}</ul><a href="/">← 업로드</a>'


@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Render가 제공하는 포트를 사용
    app.run(host='0.0.0.0', port=port)
