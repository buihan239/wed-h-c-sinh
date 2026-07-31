from flask import Blueprint, render_template, request, jsonify
import os
from werkzeug.utils import secure_filename

# Tạo Blueprint cho phần tài liệu
documents_bp = Blueprint('documents_bp', __name__)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Cơ sở dữ liệu mẫu lưu danh sách tài liệu kèm trạng thái
document_database = []

@documents_bp.route('/upload.html')
def upload_page():
    return render_template('upload.html')

@documents_bp.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'Không tìm thấy tệp gửi lên'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Chưa chọn tệp'}), 400
    
    if file and (file.filename.endswith('.pdf') or file.filename.endswith('.docx')):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        
        # Thêm vào danh sách với trạng thái chờ duyệt
        document_database.append({
            'filename': filename,
            'status': 'pending' 
        })
        
        return jsonify({'message': 'Tải lên thành công', 'filename': filename}), 200
    
    return jsonify({'error': 'Chỉ chấp nhận định dạng tệp .pdf hoặc .docx'}), 400

@documents_bp.route('/api/files', methods=['GET'])
def list_files():
    return jsonify(document_database)

@documents_bp.route('/api/approve/<filename>', methods=['POST'])
def approve_file(filename):
    for doc in document_database:
        if doc['filename'] == filename:
            doc['status'] = 'approved'
            return jsonify({'message': f'Đã phê duyệt tài liệu {filename}'}), 200
    return jsonify({'error': 'Không tìm thấy tài liệu'}), 404