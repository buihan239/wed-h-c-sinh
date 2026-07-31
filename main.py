from flask import Flask, render_template, request, jsonify
from groq import Groq

app = Flask(__name__, template_folder='.')

# 🔑 Dán Groq API Key bảo mật của bạn vào đây
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# =====================================================================
# KHU VỰC Ô LƯU TRỮ Ý TƯỞNG SƯ PHẠM RIÊNG CHO TỪNG MÔN HỌC
# (Sau này bạn có ý tưởng môn nào, mình sẽ viết code dán đè vào ô môn đó)
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
    - Thuật ngữ: Lực tác dụng, gia tốc, vận tốc, ma sát, định luật Newton, bảo toàn năng lượng.
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
    data = request.json
    raw_message = data.get('message', '')
    user_message = raw_message.strip().lower()
    
    # Nhận trực tiếp môn học từ menu trên giao diện web gửi xuống
    selected_subject = data.get('subject', 'Ngữ Văn')

    # 1. Xử lý câu chào mở đầu xã giao
    greetings = ['chào', 'hi', 'hello', 'chào thầy', 'chào cô', 'chào bạn', 'chào ai', 'chào trợ lý', 'xin chào']
    if user_message in greetings:
        reply_text = f"Chào em! Thầy/Cô là Trợ lý Sư phạm môn {selected_subject}. Hôm nay em muốn cùng thầy/cô trao đổi và chinh phục bài tập nào vậy nhỉ?"
        return jsonify({'reply': reply_text})

    # 2. Lấy bộ quy tắc chuẩn theo môn học đã được nhận diện
    specific_rule = SUBJECT_RULES.get(selected_subject, "Gợi mở ngắn gọn, không giải hộ.")
    
    # 3. System prompt hoàn chỉnh
    system_prompt = f"""
    Bạn là Giáo viên Sư phạm chuyên nghiệp môn {selected_subject} cấp THPT.
    Học sinh đang học môn: {selected_subject}.

    Đặc thù và bộ luật riêng dành cho môn {selected_subject}:
    {specific_rule}

    HƯỚNG DẪN GIAO TIẾP:
    - Trò chuyện tự nhiên, trực tiếp đi thẳng vào nội dung học sinh đang hỏi hoặc trả lời. KHÔNG lặp lại câu chào hay câu xác nhận môn học ở đầu mỗi câu trả lời.
    - Chuẩn ngữ cảnh môn {selected_subject}.
    - Trả lời cực kỳ ngắn gọn (dưới 70 từ), ngôn ngữ sư phạm ân cần, động viên.
    - Nếu học sinh trả lời là "không biết", "ko biết" hoặc lúng túng, bạn PHẢI chủ động giải thích rõ ràng và đưa ra đáp án/gợi ý cụ thể ngay lập tức, tuyệt đối không tiếp tục hỏi vặn lại học sinh.
    - Luôn kết thúc bằng DUY NHẤT 1 CÂU HỎI gợi mở để học sinh tự suy nghĩ. Tuyệt đối không giải hộ đáp án.
    """

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": raw_message}
            ],
            temperature=0.4,
        )
        reply_text = completion.choices[0].message.content
        return jsonify({'reply': reply_text})
    except Exception as e:
        return jsonify({'reply': f"Lỗi kết nối AI: {str(e)}"}), 500

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
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
# Đảm bảo đoạn này luôn nằm ở cuối cùng của file main.py
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)