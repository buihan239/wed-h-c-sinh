from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, RedirectResponse
from pydantic import BaseModel
from google import genai
import json
import os

app = FastAPI()

# CẤU HÌNH GEMINI AI (Hãy thay bằng API Key thật của bạn)
GEMINI_API_KEY = "AIzaSy..." 

# Khởi tạo client kết nối Gemini AI (Theo chuẩn SDK google-genai mới nhất năm 2026)
try:
    ai_client = genai.Client(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"Cảnh báo cấu hình AI: {e}")
    ai_client = None

# Cấu trúc dữ liệu nhận từ frontend
class StudentLogin(BaseModel):
    ho_ten: str
    lop: str
    truong: str

class ChatMessage(BaseModel):
    message: str

# 1. API Đăng nhập và tạo file dữ liệu
@app.post("/api/login")
async def login(student: StudentLogin):
    if not student.ho_ten or not student.lop or not student.truong:
        raise HTTPException(status_code=400, detail="Vui lòng điền đầy đủ thông tin!")
    
    data_file = "hoc_sinh.json"
    student_data = {
        "ho_ten": student.ho_ten,
        "lop": student.lop,
        "truong": student.truong,
        "ai_dependency_index": 0,
        "chat_count": 0
    }
    
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(student_data, f, ensure_ascii=False, indent=4)
        
    return {"status": "success", "message": f"Chào mừng {student.ho_ten} đã đăng nhập thành công!"}

# 2. API Lấy thông tin học sinh hiện tại để hiển thị lời chào trên Dashboard
@app.get("/api/student-info")
async def get_student_info():
    data_file = "hoc_sinh.json"
    if not os.path.exists(data_file):
        raise HTTPException(status_code=404, detail="Chưa có dữ liệu học sinh. Hãy đăng nhập trước!")
    
    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

# 3. API xử lý Chat với Gemini AI và tăng chỉ số đếm số lần chat
@app.post("/api/chat")
async def chat_with_gemini(chat: ChatMessage):
    data_file = "hoc_sinh.json"
    if not os.path.exists(data_file):
        raise HTTPException(status_code=400, detail="Vui lòng đăng nhập trước khi chat!")
    
    # Đọc dữ liệu cũ lên để cập nhật số lần chat (Hành vi học tập)
    with open(data_file, "r", encoding="utf-8") as f:
        student_data = json.load(f)
    
    # Cộng dồn số lần chat của học sinh
    student_data["chat_count"] += 1
    
    # Tính toán nhanh chỉ số Lệ thuộc AI tượng trưng (Sẽ nâng cấp công thức khoa học ở các bước sau)
    # Ví dụ: Cứ chat thêm 1 lần thì độ lệ thuộc tăng lên 5%
    student_data["ai_dependency_index"] = min(100, student_data["chat_count"] * 5)
    
    # Ghi lại dữ liệu mới vào file
    with open(data_file, "w", encoding="utf-8") as f:
        json.dump(student_data, f, ensure_ascii=False, indent=4)

    # Gọi Gemini AI thật xử lý câu hỏi câu trả lời
    if not GEMINI_API_KEY or GEMINI_API_KEY == "AIzaSy...":
        return {"reply": f"[Chế độ Demo] Bạn vừa hỏi: '{chat.message}'. Hãy cấu hình API Key thật ở main.py để nhận phản hồi từ Gemini nhé!"}

    try:
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=chat.message,
        )
        return {"reply": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi gọi Gemini AI: {str(e)}")

# Điều hướng mặc định
@app.get("/")
async def read_index():
    return FileResponse("index.html")

app.mount("/", StaticFiles(directory="."), name="static")
