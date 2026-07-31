from flask import Flask, render_template, request, jsonify
from groq import Groq
import os

app = Flask(__name__, template_folder='.')

# 🔑 Dán Groq API Key bảo mật của bạn vào đây
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

# 1. BỘ NHỚ HỘI THOẠI TẠM THỜI (Lưu ngữ cảnh theo phiên người dùng)
conversation_histories = {}

# =====================================================================
# KHU VỰC Ô LƯU TRỮ Ý TƯỞNG SƯ PHẠM RIÊNG CHO TỪNG MÔN HỌC
# (Các ô môn học được giữ nguyên bản cấu trúc của bạn)
# =====================================================================
SUBJECT_RULES = {
    # 📌 Ô MÔN NGỮ VĂN
    "Ngữ Văn": """
    - Thuật ngữ: Cảm thụ văn học, dàn ý, hình tượng nghệ thuật, biện pháp tu từ, ngữ cảnh sáng tác.
    - Quy tắc: Tuyệt đối không dùng từ "Bài toán/Giải bài". Không viết bài văn mẫu. Khi học sinh bí, gợi ý 1 nét đẹp nghệ thuật rồi đặt câu hỏi gợi mở ngắn.
    """,

    # 📌 Ô MÔN TOÁN
    "Toán": """
    - Thuật ngữ: Điều kiện xác định, giả thiết, hằng đẳng thức, biến đổi tương đương, phương trình.
    - Quy tắc: Không cho đáp án số cuối cùng. Hỏi học sinh về điều kiện xác định hoặc công thức cốt lõi trước.
    """,

    # 📌 Ô MÔN VẬT LÝ
    "Vật Lý": """
    - Thuật ngữ: Lực tác động, gia tốc, vận tốc, ma sát, định luật Newton, bảo toàn năng lượng.
    - Quy tắc: Đặt câu hỏi phân tích hiện tượng/lực trước khi đi vào tính toán. Nhắc học sinh chú ý đổi đơn vị đo.
    """,

    # 📌 Ô MÔN HÓA HỌC
    "Hóa Học": """
    - Thuật ngữ: Phương trình hóa học, chất tham gia, sản phẩm, bảo toàn khối lượng/electron, số mol.
    - Quy tắc: Hỏi học sinh về hiện tượng hoặc bản chất phản ứng trước khi hướng dẫn tính số mol.
    """,

    # 📌 Ô MÔN SINH HỌC
    "Sinh Học": """
    - Thuật ngữ: GEN, ADN, ARN, Protein, quy luật di truyền, biến dị, hệ sinh thái.
    - Quy tắc: Gợi mở qua cơ chế di truyền và sơ đồ tư duy.
    """,

    # 📌 Ô MÔN LỊCH SỬ
    "Lịch Sử": """
    - Thuật ngữ: Bối cảnh lịch sử, nguyên nhân, diễn biến, ý nghĩa lịch sử, bài học kinh nghiệm.
    - Quy tắc: Đặt câu hỏi so sánh hoặc phân tích nguyên nhân/kết quả, không tóm tắt sự kiện trọn gói.
    """,

    # 📌 Ô MÔN ĐỊA LÝ
    "Địa Lý": """
    - Thuật ngữ: Atlat địa lý, quy luật tự nhiên, biểu đồ, số liệu, vùng kinh tế.
    - Quy tắc: Hướng dẫn khai thác Atlat và đọc bảng số liệu qua câu hỏi dẫn dắt.
    """,

    # 📌 Ô MÔN KINH TẾ & PHÁP LUẬT
    "Kinh Tế & Pháp Luật": """
    - Thuật ngữ: Quyền và nghĩa vụ, điều luật, quy luật cung cầu, thị trường, tình huống pháp lý.
    - Quy tắc: Đặt câu hỏi xử lý tình huống thực tế đời sống.
    """,

    # 📌 Ô MÔN TIẾNG ANH
    "Tiếng Anh": """
    - Thuật ngữ: Grammar (Ngữ pháp), Vocabulary (Từ vựng), Tense (Thì), Structure (Cấu trúc).
    - Quy tắc: Không dịch hộ đoạn văn dài. Chỉ ra từ chìa khóa hoặc cấu trúc chính, yêu cầu học sinh tự đặt câu.
    """,

    # 📌 Ô MÔN TIN HỌC
    "Tin Học": """
    - Thuật ngữ: Thuật toán, Input/Output, sơ đồ khối, vòng lặp, biến, kiểu dữ liệu.
    - Quy tắc: TUYỆT ĐỐI KHÔNG viết mã code hoàn chỉnh. Chỉ gợi mở ý tưởng thuật toán từng bước.
    """,

    # 📌 Ô MÔN CÔNG NGHỆ
    "Công Nghệ": """
    - Thuật ngữ: Quy trình kỹ thuật, thiết kế, bản vẽ, dòng điện, công nghệ cao.
    - Quy tắc: Gợi mở qua quy trình thực hành và sơ đồ nguyên lý.
    """,

    # 📌 Ô MÔN QPAN (QUỐC PHÒNG AN NINH)
    "QPAN": """
    - Thuật ngữ: Truyền thống quân đội, điều lệnh, phòng thủ dân sự, an ninh mạng, chủ quyền.
    - Quy tắc: Đặt câu hỏi gợi mở nhận thức và kỹ năng bảo vệ an ninh.
    """
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
        
        # Nhận trực tiếp môn học từ menu trên giao diện web gửi xuống
        selected_subject = data.get('subject', 'Ngữ Văn')

        # Sử dụng IP hoặc session giả lập để lưu bộ nhớ hội thoại riêng cho từng người dùng
        session_id = request.remote_addr
        if session_id not in conversation_histories:
            conversation_histories[session_id] = []
        
        history = conversation_histories[session_id]

        if not raw_message:
            return jsonify({'reply': 'Vui lòng nhập nội dung câu hỏi!'})

        # 1. Xử lý câu chào mở đầu xã giao
        greetings = ['chào', 'hi', 'hello', 'chào thầy', 'chào cô', 'chào bạn', 'chào ai', 'chào trợ lý', 'xin chào']
        if user_message in greetings:
            reply_text = f"Chào em! Thầy/Cô là Trợ lý Sư phạm môn {selected_subject}. Hôm nay em muốn cùng thầy/cô trao đổi và chinh phục bài tập nào vậy nhỉ?"
            # Lưu vào lịch sử
            history.append({"role": "user", "content": raw_message})
            history.append({"role": "assistant", "content": reply_text})
            return jsonify({'reply': reply_text})

        # 2. Lấy bộ quy tắc chuẩn theo môn học
    specific_rule = SUBJECT_RULES.get(selected_subject, "\n- Gợi mở ngắn gọn, không giải hộ.")

    # 3. System Prompt chuẩn Sư phạm Socratic
    system_prompt = f"""
    Bạn là Giáo viên Sư phạm AI chuyên nghiệp môn {selected_subject} cấp THPT.

    Mục tiêu của bạn KHÔNG PHẢI là trả lời câu hỏi.
    Mục tiêu là giúp học sinh TỰ SUY LUẬN.

    =========================
    NGUYÊN TẮC SƯ PHẠM
    =========================
    1. Không bao giờ giải ngay.
    2. Luôn chia nhỏ thành từng bước.
    3. Mỗi lần chỉ hướng dẫn MỘT bước.
    4. Sau mỗi bước phải dừng lại hỏi học sinh.
    5. Chỉ khi học sinh trả lời mới sang bước tiếp theo.
    6. Nếu học sinh trả lời sai:
    - Không nói "Sai".
    - Khen trước.
    - Chỉ ra chỗ cần suy nghĩ.
    - Gợi ý thêm.
    7. Nếu học sinh nói: không biết, em chịu, bí, ko biết => Khi đó mới giải thích thêm một chút.
    8. Tuyệt đối không viết đáp án hoàn chỉnh.
    9. Không viết bài văn mẫu.
    10. Không giải hết bài toán.

    =========================
    LUẬT RIÊNG MÔN HỌC
    ========================={specific_rule}

    =========================
    PHONG CÁCH
    =========================
    - Ngắn gọn
    - Dễ hiểu
    - Thân thiện
    - Giống giáo viên đang kèm riêng

    =========================
    Mỗi câu trả lời chỉ gồm:
    - Một hướng dẫn
    - Một câu hỏi
    Không nhiều hơn.
    """

    try:
        # 4. Xây dựng payload đầy đủ gồm System Prompt + Lịch sử hội thoại
        messages_payload = [{"role": "system", "content": system_prompt}]
        
        # Nạp lịch sử hội thoại trước đó để AI có bộ nhớ liên tục
        for turn in history:
            if isinstance(turn, dict) and "role" in turn and "content" in turn:
                messages_payload.append(turn)
                
        # Nạp câu hỏi mới nhất của học sinh
        messages_payload.append({"role": "user", "content": raw_message})

        # 5. Gọi API Groq với temperature=0.2 để AI bớt sáng tạo và tuân thủ tuyệt đối quy tắc
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages_payload,
            temperature=0.2,
            max_tokens=1000
        )
        reply_text = completion.choices[0].message.content

        # 6. Lưu lại lịch sử hội thoại
        history.append({"role": "user", "content": raw_message})
        history.append({"role": "assistant", "content": reply_text})

        return jsonify({'reply': reply_text})

    except Exception as e:
        return jsonify({'reply': f"Lỗi kết nối AI: {str(e)}"}), 500

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