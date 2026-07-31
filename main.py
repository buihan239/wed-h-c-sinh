from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__, template_folder='.')

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

conversation_histories = {}

SUBJECT_RULES = {
    "Ngữ Văn": "Tuyệt đối không dùng từ 'Bài toán/Giải bài'. Không viết bài văn mẫu. Khi học sinh bí, gợi ý 1 nét nghệ thuật rồi đặt câu hỏi ngắn.",
    "Toán": "QUAN TRỌNG: Chỉ đặt MỘT câu hỏi gợi mở bước đầu tiên (ví dụ: hỏi điều kiện của mẫu số hoặc căn thức) rồi DỪNG LẠI NGAY LẬP TỨC. TUYỆT ĐỐI KHÔNG tự giải tiếp, không đưa ra kết quả.",
    "Vật Lý": "QUAN TRỌNG: Chỉ đặt câu hỏi phân tích hiện tượng/công thức bước 1 rồi DỪNG LẠI. Không tự giải hộ.",
    "Hóa Học": "QUAN TRỌNG: Chỉ hỏi học sinh về bản chất phản ứng bước 1 rồi DỪNG LẬP TỨC.",
    "Sinh Học": "Gợi mở qua cơ chế di truyền, chỉ hỏi 1 ý rồi dừng lại chờ học sinh.",
    "Lịch Sử": "Đặt câu hỏi gợi ý sự kiện bước 1, không tóm tắt trọn gói.",
    "Địa Lý": "Hướng dẫn khai thác Atlat bước 1 bằng câu hỏi ngắn rồi dừng lại.",
    "Kinh Tế & Pháp Luật": "Đặt câu hỏi xử lý tình huống bước 1 rồi dừng lại.",
    "Tiếng Anh": "Không dịch hộ. Chỉ ra từ khóa và đặt câu hỏi gợi mở bước 1 rồi dừng lại.",
    "Tin Học": "TUYỆT ĐỐI KHÔNG viết mã code. Chỉ hỏi ý tưởng thuật toán bước 1 rồi dừng lại.",
    "Công Nghệ": "Gợi mở quy trình bước 1 rồi dừng lại.",
    "QPAN": "Đặt câu hỏi nhận thức bước 1 rồi dừng lại."
}


@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        raw_message = data.get('message', '').strip()
        user_message = raw_message.lower()
        selected_subject = data.get('subject', 'Ngữ Văn')

        session_id = request.remote_addr
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        history = conversation_histories[session_id]

        if not raw_message:
            return jsonify({'reply': 'Vui lòng nhập nội dung câu hỏi!'})

        greetings = ['chào', 'hi', 'hello', 'chào thầy', 'chào cô', 'chào bạn', 'xin chào']
        if user_message in greetings:
            reply_text = f"Chào em! Thầy/Cô là Trợ lý Sư phạm môn {selected_subject}. Hôm nay em muốn cùng thầy/cô trao đổi và chinh phục bài tập nào vậy nhỉ?"
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
        4. SAU KHI ĐẶT CÂU HỎI PHẢI DỪNG LẠI NGAY. TUYỆT ĐỐI KHÔNG tự trả lời câu hỏi của mình, không giải tiếp các bước sau. Bắt buộc phải chờ học sinh nhắn lại.
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

@app.route('/notebook.html')
def notebook():
    return render_template('notebook.html')

@app.route('/upload.html')
def upload():
    return render_template('upload.html')

@app.route('/analytics.html')
def analytics():
    return render_template('analytics.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)