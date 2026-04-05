from langchain_ollama import OllamaLLM
from conversation_memory import ConversationMemory
from datetime import datetime, timedelta
import re
import locale

class ImprovedLLMHandler:
    def __init__(self, model_name: str = "llama3:8b", mongo_uri: str = "mongodb://localhost:27017/"):
        """
        Khởi tạo LLM handler với memory
        """
        self.model = OllamaLLM(model=model_name)
        self.memory = ConversationMemory(mongo_uri)
        self.current_session = None
        
        # Thiết lập locale tiếng Việt (fallback nếu không có)
        try:
            locale.setlocale(locale.LC_TIME, 'vi_VN.UTF-8')
        except:
            try:
                locale.setlocale(locale.LC_TIME, 'Vietnamese_Vietnam.1258')
            except:
                pass  # Sử dụng default locale
        
        # Từ khóa để nhận diện câu hỏi về thời gian
        self.time_keywords = [
            'mấy giờ', 'bây giờ', 'hiện tại', 'thời gian',
            'ngày', 'tháng', 'năm', 'hôm nay', 'bữa nay',
            'thứ mấy', 'thứ', 'chủ nhật', 'chú nhật',
            'giờ', 'phút', 'giây', 'sáng', 'chiều', 'tối', 'đêm'
        ]
        
        # System prompt được tối ưu cho câu trả lời ngắn gọn
        self.system_prompt = """Bạn là trợ lý AI người Việt Nam thông minh và thân thiện.

QUAN TRỌNG - LUẬT TRỰC TIẾP:
1. LUÔN trả lời bằng tiếng Việt
2. Trả lời NGẮN GỌN, tối đa 1-2 câu
3. Đi thẳng vào vấn đề, không lan man
4. Nếu câu hỏi phức tạp, hỏi lại để làm rõ
5. Giữ giọng điệu tự nhiên, thân thiện

Ví dụ tốt:
- "Hôm nay trời đẹp quá!" → "Vâng, thời tiết hôm nay thật tuyệt!"
- "Cảm ơn bạn!" → "Không có gì, tôi luôn sẵn sàng giúp bạn!"

Tránh câu trả lời dài dòng hay giải thích chi tiết trừ khi được yêu cầu."""

    def start_new_session(self, user_id: str = "default_user") -> str:
        """
        Bắt đầu session mới
        """
        self.current_session = self.memory.create_session(user_id)
        return self.current_session
    
    def set_session(self, session_id: str):
        """
        Thiết lập session hiện tại
        """
        self.current_session = session_id
    
    def _is_time_question(self, message: str) -> bool:
        """
        Kiểm tra xem câu hỏi có liên quan đến thời gian không
        """
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.time_keywords)
    
    def _get_current_time_info(self) -> dict:
        """
        Lấy thông tin thời gian hiện tại
        """
        now = datetime.now()
        
        # Tên các thứ trong tuần
        weekdays = [
            'Thứ Hai', 'Thứ Ba', 'Thứ Tư', 'Thứ Năm', 
            'Thứ Sáu', 'Thứ Bảy', 'Chủ Nhật'
        ]
        
        # Tên các tháng
        months = [
            '', 'Tháng Một', 'Tháng Hai', 'Tháng Ba', 'Tháng Tư',
            'Tháng Năm', 'Tháng Sáu', 'Tháng Bảy', 'Tháng Tám',
            'Tháng Chín', 'Tháng Mười', 'Tháng Mười Một', 'Tháng Mười Hai'
        ]
        
        # Xác định buổi trong ngày
        hour = now.hour
        if 5 <= hour < 12:
            period = "sáng"
        elif 12 <= hour < 18:
            period = "chiều"
        elif 18 <= hour < 22:
            period = "tối"
        else:
            period = "đêm"
        
        return {
            'datetime': now,
            'time': now.strftime("%H:%M:%S"),
            'time_12h': now.strftime("%I:%M %p"),
            'date': now.strftime("%d/%m/%Y"),
            'weekday': weekdays[now.weekday()],
            'day': now.day,
            'month': months[now.month],
            'year': now.year,
            'period': period,
            'full_date': f"{weekdays[now.weekday()]}, ngày {now.day} {months[now.month]} năm {now.year}"
        }
    
    def _handle_time_question(self, message: str) -> str:
        """
        Xử lý câu hỏi về thời gian
        """
        message_lower = message.lower()
        time_info = self._get_current_time_info()
        
        # Các pattern câu hỏi phổ biến
        if any(word in message_lower for word in ['mấy giờ', 'bây giờ', 'hiện tại', 'giờ']):
            return f"Bây giờ là {time_info['time']} ({time_info['period']})."
        
        elif any(word in message_lower for word in ['hôm nay', 'bữa nay', 'ngày']):
            if 'thứ' in message_lower:
                return f"Hôm nay là {time_info['full_date']}."
            else:
                return f"Hôm nay là ngày {time_info['date']}."
        
        elif any(word in message_lower for word in ['thứ mấy', 'thứ']):
            return f"Hôm nay là {time_info['weekday']}."
        
        elif 'tháng' in message_lower:
            return f"Hiện tại là {time_info['month']} năm {time_info['year']}."
        
        elif 'năm' in message_lower:
            return f"Năm nay là năm {time_info['year']}."
        
        # Trả về thông tin tổng quát
        return f"Hiện tại là {time_info['time']}, {time_info['full_date']}."
    
    def ask_llm(self, message: str) -> str:
        """
        Hỏi LLM với ngữ cảnh và constraints
        """
        if not self.current_session:
            self.start_new_session()
        
        try:
            # Lưu câu hỏi của user
            self.memory.add_message(self.current_session, "user", message)
            
            # Kiểm tra xem có phải câu hỏi về thời gian không
            if self._is_time_question(message):
                response = self._handle_time_question(message)
                # Lưu câu trả lời
                self.memory.add_message(self.current_session, "assistant", response)
                return response
            
            # Lấy ngữ cảnh gần đây
            context = self.memory.get_context_string(self.current_session, limit=4)
            
            # Thêm thông tin thời gian vào system prompt nếu cần
            current_time = self._get_current_time_info()
            time_context = f"\nThông tin thời gian hiện tại: {current_time['time']}, {current_time['full_date']}"
            
            # Tạo prompt với ngữ cảnh
            if context:
                full_prompt = f"""{self.system_prompt}{time_context}

Ngữ cảnh cuộc trò chuyện gần đây: {context}

Câu hỏi mới: {message}

Trả lời (nhớ: NGẮN GỌN, 1-2 câu):"""
            else:
                full_prompt = f"""{self.system_prompt}{time_context}

Câu hỏi: {message}

Trả lời (nhớ: NGẮN GỌN, 1-2 câu):"""
            
            # Gọi model
            response = self.model.invoke(full_prompt)
            
            # Làm sạch response và giới hạn độ dài
            cleaned_response = self._clean_response(response)
            
            # Lưu câu trả lời
            self.memory.add_message(self.current_session, "assistant", cleaned_response)
            
            return cleaned_response
            
        except Exception as e:
            error_msg = "Xin lỗi, tôi gặp sự cố. Bạn có thể thử lại không?"
            if self.current_session:
                self.memory.add_message(self.current_session, "assistant", error_msg)
            return error_msg
    
    def _clean_response(self, response: str) -> str:
        """
        Làm sạch và rút gọn response
        """
        # Xóa các phần thừa
        response = response.strip()
        
        # Loại bỏ các pattern không mong muốn
        patterns_to_remove = [
            r"^(Trả lời:|Câu trả lời:|Response:)",
            r"^(Xin chào|Hello)",
            r"\n\n+",  # Nhiều dòng trống
        ]
        
        for pattern in patterns_to_remove:
            response = re.sub(pattern, "", response, flags=re.IGNORECASE | re.MULTILINE)
        
        response = response.strip()
        
        # Giới hạn độ dài (tối đa 2 câu)
        sentences = re.split(r'[.!?]+', response)
        if len(sentences) > 2:
            response = '. '.join(sentences[:2]) + '.'
        
        # Giới hạn ký tự (tối đa 200 ký tự)
        if len(response) > 200:
            response = response[:197] + "..."
        
        return response
    
    def get_conversation_history(self, limit: int = 10) -> list:
        """
        Lấy lịch sử hội thoại
        """
        if not self.current_session:
            return []
        return self.memory.get_recent_context(self.current_session, limit)
    
    def clear_conversation(self):
        """
        Xóa hội thoại hiện tại
        """
        if self.current_session:
            self.memory.clear_session(self.current_session)
            self.current_session = None
    
    def close(self):
        """
        Đóng kết nối
        """
        self.memory.close()

def create_voice_assistant():
    return ImprovedLLMHandler()

