// ====== CHỨC NĂNG 1: XỬ LÝ ĐĂNG NHẬP VÀ CHUYỂN TRANG ======
async function xuLyDangNhap() {
    const hoTen = document.getElementById('hoTen').value;
    const lop = document.getElementById('lop').value;
    const truong = document.getElementById('truong').value;

    if (!hoTen || !lop || !truong) {
        alert("Vui lòng nhập đầy đủ thông tin trước khi đăng nhập!");
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ ho_ten: hoTen, lop: lop, truong: truong })
        });

        const result = await response.json();
        
        if (response.ok) {
            alert(result.message);
            // TỰ ĐỘNG CHUYỂN SANG TRANG DASHBOARD KHI ĐĂNG NHẬP XONG
            window.location.href = "/dashboard.html";
        } else {
            alert("Lỗi: " + result.detail);
        }
    } catch (error) {
        console.error("Lỗi kết nối server:", error);
        alert("Không thể kết nối đến hệ thống Backend Python!");
    }
}

// ====== CHỨC NĂNG 2: XỬ LÝ CHAT VỚI GEMINI AI ======
async function guiCauHoiAI() {
    const inputElement = document.getElementById('user-input');
    const question = inputElement.value.trim();
    if (!question) return;

    const chatMessages = document.getElementById('chat-messages');

    // Hiển thị câu hỏi của học sinh lên màn hình chat
    chatMessages.innerHTML += `<div class="message user-msg">${question}</div>`;
    inputElement.value = ''; 
    chatMessages.scrollTop = chatMessages.scrollHeight; 

    // Hiển thị trạng thái AI đang suy nghĩ...
    const loadingId = 'loading-' + Date.now();
    chatMessages.innerHTML += `<div class="message ai-msg" id="${loadingId}">Gemini AI đang suy nghĩ...</div>`;
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        // Gửi câu hỏi lên Backend Python để gọi Gemini AI thật
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: question })
        });

        const result = await response.json();
        const loadingElement = document.getElementById(loadingId);
        
        if (response.ok) {
            loadingElement.innerText = result.reply; 
        } else {
            loadingElement.innerText = "Lỗi hệ thống: " + result.detail;
        }
    } catch (error) {
        console.error("Lỗi:", error);
        document.getElementById(loadingId).innerText = "Không thể kết nối đến máy chủ AI!";
    }
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

