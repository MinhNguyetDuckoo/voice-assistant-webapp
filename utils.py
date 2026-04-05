# utils.py - Các hàm tiện ích
import threading
from datetime import datetime

def update_status(status_label, message):
    """Cập nhật trạng thái trên GUI"""
    if status_label:
        status_label.config(text=message)

def add_message(chat_frame, sender, message, chat_canvas=None):
    """Thêm tin nhắn vào chat (legacy function)"""
    # Hàm này được thay thế bởi method trong main class
    pass

def handle_interaction(user_input, add_message_func, speak_func, ask_llm_func):
    """Xử lý tương tác giữa user và AI"""
    try:
        if user_input:
            # Hiển thị input của user
            add_message_func("Bạn", user_input)
            
            # Lấy response từ AI
            ai_response = ask_llm_func(user_input)
            
            # Hiển thị và đọc response
            add_message_func("AI", ai_response)
            speak_func(ai_response)
            
            return ai_response
    except Exception as e:
        error_msg = "Xin lỗi, có lỗi xảy ra."
        add_message_func("AI", error_msg)
        speak_func(error_msg)
        return error_msg

def start_listening(listen_func, handle_interaction_func, update_status_func):
    """Bắt đầu quá trình lắng nghe (legacy function)"""
    # Hàm này được thay thế bởi method trong main class
    pass

def format_timestamp():
    """Tạo timestamp cho tin nhắn"""
    return datetime.now().strftime("%H:%M:%S")

def safe_thread_run(target_func, *args, **kwargs):
    """Chạy function trong thread an toàn"""
    try:
        thread = threading.Thread(target=target_func, args=args, kwargs=kwargs, daemon=True)
        thread.start()
        return thread
    except Exception as e:
        print(f"Thread error: {e}")
        return None