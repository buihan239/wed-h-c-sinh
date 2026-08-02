from flask import Blueprint, request, jsonify
from groq import Groq
import os

chat_bp = Blueprint('chat_bp', __name__)

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

conversation_histories = {}

SUBJECT_RULES = {
    "Ngữ Văn": "Tuyệt đối không dùng từ 'Bài toán/Giải bài'. Không viết bài văn mẫu. Khi học sinh bí, gợi ý 1 nét nghệ thuật rồi đặt câu hỏi ngắn.",
    "Toán": "QUAN TRỌNG: Chỉ đặt MỘT câu hỏi gợi mở bước đầu tiên rồi DỪNG LẠI NGAY. TUYỆT ĐỐI KHÔNG tự giải tiếp.",
    "Vật Lý": "QUAN TRỌNG: Chỉ đặt câu hỏi phân tích hiện tượng/công thức bước 1 rồi DỪNG LẠI. Không tự giải hộ.",
    "Hóa Học": "QUAN TRỌNG: Chỉ hỏi học sinh về bản chất phản ứng bước 1 rồi DỪNG LẠI.",
    "Sinh Học": "Gợi mở qua cơ chế di truyền, chỉ hỏi 1 ý rồi dừng lại chờ học sinh.",
    "Lịch Sử": "Đặt câu hỏi gợi ý sự kiện bước 1, không tóm tắt trọn gói.",
    "Địa Lý": "Hướng dẫn khai thác Atlat bước 1 bằng câu hỏi ngắn rồi dừng lại.",
    "Kinh Tế & Pháp Luật": "Đặt câu hỏi xử lý tình huống bước 1 rồi dừng lại.",
    "Tiếng Anh": "Không dịch hộ. Chỉ ra từ khóa và đặt câu hỏi gợi mở bước 1 rồi dừng lại.",
    "Tin Học": "TUYỆT ĐỐI KHÔNG viết mã code. Chỉ hỏi ý tưởng thuật toán bước 1 rồi dừng lại.",
    "Công Nghệ": "Gợi mở quy trình bước 1 rồi dừng lại.",
    "QPAN": "Đặt câu hỏi nhận thức bước 1 rồi dừng lại."
}

@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        raw_message = data.get('message', '').strip()
        user_message = raw_message.lower()
        selected_subject = data.get('subject', 'Ngữ Văn').strip()

        session_id = request.remote_addr
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        history = conversation_histories[session_id]

        if not raw_message:
            return jsonify({'reply': 'Vui lòng nhập nội dung câu hỏi!'})

        greetings = ['chào', 'hi', 'hello', 'chào thầy', 'chào cô', 'chào bạn', 'xin chào']
        if user_message in greetings:
            reply_text = f"Chào bạn! Mình là Trợ lý AI môn {selected_subject}. Hôm nay, bạn muốn cùng mình trao đổi và chinh phục bài tập nào vậy nhỉ?"
            history.append({"role": "user", "content": raw_message})
            history.append({"role": "assistant", "content": reply_text})
            return jsonify({'reply': reply_text})

        specific_rule = SUBJECT_RULES.get(selected_subject, "Gợi mở ngắn gọn, không giải hộ.")

        system_prompt = f"""
        Bạn là Giáo viên Sư phạm AI chuyên nghiệp môn {selected_subject} cấp THPT.
        Mục tiêu của bạn KHÔNG PHẢI là trả lời câu hỏi mà là giúp học sinh TỰ SUY LUẬN.

        NGUYÊN TẮC SƯ PHẠM BẮT BUỘC:
        1. Không bao giờ giải ngay.
        2. Luôn chia nhỏ thành từng bước.
        3. Mỗi lần chỉ hướng dẫn MỘT bước và đặt 1 câu hỏi ngắn gọn.
        4. SAU KHI ĐẶT CÂU HỎI PHẢI DỪNG LẠI NGAY. TUYỆT ĐỐI KHÔNG tự trả lời câu hỏi của mình. Bắt buộc phải chờ học sinh nhắn lại.
        5. Nếu học sinh trả lời sai: Không nói 'Sai', hãy khen và gợi ý thêm.
        6. Nếu học sinh nói: không biết, em chịu, bí, ko biết => Mới giải thích thêm một chút.
        7. Tuyệt đối không viết đáp án hoàn chỉnh.

        LUẬT RIÊNG MÔN HỌC:
        {specific_rule}
        """

        messages_payload = [{"role": "system", "content": system_prompt}]
        
        for turn in history:
            if isinstance(turn, dict) and "role" in turn and "content" in turn:
                messages_payload.append(turn)
                
        messages_payload.append({"role": "user", "content": raw_message})

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload,
            temperature=0.2,
            max_tokens=1000
        )
        reply_text = completion.choices[0].message.content

        history.append({"role": "user", "content": raw_message})
        history.append({"role": "assistant", "content": reply_text})

        if len(history) > 20:
            conversation_histories[session_id] = history[-20:]

        return jsonify({'reply': reply_text})

    except Exception as e:
        return jsonify({'reply': f"Lỗi hệ thống AI: {str(e)}"}), 500
import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

# Thư mục riêng lưu file của Notebook
NOTEBOOK_FOLDER = 'notebook_uploads'
os.makedirs(NOTEBOOK_FOLDER, exist_ok=True)

@chat_bp.route('/api/notebook/files', methods=['GET'])
def get_notebook_files():
    files = os.listdir(NOTEBOOK_FOLDER)
    return jsonify({'files': files})

@chat_bp.route('/api/notebook/upload', methods=['POST'])
def upload_notebook_file():
    if 'file' not in request.files:
        return jsonify({'message': 'Không tìm thấy file!'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'Chưa chọn file!'}), 400
    
    filename = secure_filename(file.filename)
    file.save(os.path.join(NOTEBOOK_FOLDER, filename))
    return jsonify({'message': 'Tải tài liệu lên Notebook thành công!'})

@chat_bp.route('/api/notebook/chat', methods=['POST'])
def notebook_chat():
    data = request.json
    filename = data.get('filename')
    message = data.get('message')

    file_path = os.path.join(NOTEBOOK_FOLDER, filename)
    file_content = ""
    
    # Đọc nội dung file (hỗ trợ file text/txt hoặc đọc tên file cơ bản)
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()[:4000] # Giới hạn 4000 ký tự đầu để AI đọc
    except Exception as e:
        file_content = "Không thể đọc nội dung file trực tiếp."

    prompt = f"""
    Bạn là trợ lý học tập AI thông minh. Dưới đây là nội dung tài liệu cá nhân của học sinh từ file '{filename}':
    ---
    {file_content}
    ---
    Câu hỏi của học sinh dựa trên tài liệu trên: {message}
    Hãy trả lời ngắn gọn, chính xác, tập trung phân tích dựa vào tài liệu được cung cấp.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2
        }
        reply = completion.choices[0].message.content
        return jsonify({'reply': reply})
    except Exception as e:
        return jsonify({'reply': f'Lỗi xử lý AI: {str(e)}'})