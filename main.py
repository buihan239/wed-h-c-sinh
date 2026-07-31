from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__, template_folder='.')

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

conversation_histories = {}

SUBJECT_RULES = {
    "Ngữ Văn": "Tuyệt đối không dùng từ 'Bài toán/Giải bài'. Không viết bài văn mẫu. Khi học sinh bí, gợi ý 1 nét nghệ thuật rồi đặt câu hỏi ngắn.",
    "Toán": "Không cho đáp án số cuối cùng. Hỏi học sinh về điều kiện xác định hoặc công thức cốt lõi trước.",
    "Vật Lý": "Đặt câu hỏi phân tích hiện tượng trước khi đi vào tính toán. Nhắc học sinh chú ý đổi đơn vị.",
    "Hóa Học": "Hỏi học sinh về hiện tượng hoặc bản chất phản ứng trước khi hướng dẫn tính số mol.",
    "Sinh Học": "Gợi mở qua cơ chế di truyền và sơ đồ tư duy.",
    "Lịch Sử": "Đặt câu hỏi so sánh hoặc phân tích nguyên nhân/kết quả, không tóm tắt sự kiện trọn gói.",
    "Địa Lý": "Hướng dẫn khai thác Atlat và đọc bảng số liệu qua câu hỏi dẫn dắt.",
    "Kinh Tế & Pháp Luật": "Đặt câu hỏi xử lý tình huống thực tế đời sống.",
    "Tiếng Anh": "Không dịch hộ đoạn văn dài. Chỉ ra từ chìa khóa hoặc cấu trúc chính.",
    "Tin Học": "TUYỆT ĐỐI KHÔNG viết mã code hoàn chỉnh. Chỉ gợi mở ý tưởng thuật toán.",
    "Công Nghệ": "Gợi mở qua quy trình thực hành và sơ đồ nguyên lý.",
    "QPAN": "Đặt câu hỏi gợi mở nhận thức và kỹ năng bảo vệ an ninh."
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

NGUYÊN TẮC SƯ PHẠM:
1. Không bao giờ giải ngay.
2. Luôn chia nhỏ thành từng bước.
3. Mỗi lần chỉ hướng dẫn MỘT bước và đặt 1 câu hỏi ngắn gọn.
4. Chỉ khi học sinh trả lời mới sang bước tiếp theo.
5. Nếu học sinh trả lời sai: Không nói 'Sai', hãy khen, chỉ ra chỗ cần suy nghĩ và gợi ý thêm.
6. Nếu học sinh nói: không biết, em chịu, bí, ko biết => Mới giải thích thêm một chút.
7. Tuyệt đối không viết đáp án hoàn chỉnh hay bài văn mẫu.

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