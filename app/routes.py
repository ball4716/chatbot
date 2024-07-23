from flask import Blueprint, render_template, request, jsonify
import os

app = Blueprint('routes', __name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    message = request.json.get('message')
    # 여기에 채팅 로직 추가
    return jsonify({'message': message})

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file_path = os.path.join(os.getcwd(), 'uploads', filename)
        file.save(file_path)
        return jsonify({'success': 'File uploaded successfully', 'filename': filename}), 200

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf', 'xlsx', 'docx'}
