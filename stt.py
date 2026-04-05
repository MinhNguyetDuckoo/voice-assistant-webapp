import speech_recognition as sr
import pyaudio

def listen(update_status=None): 
    r = sr.Recognizer()
    with sr.Microphone() as mic: #sử dụng mic thu âm
        if update_status: update_status("Đang lắng nghe...")

# Điều chỉnh với tiếng ồn xung quanh (1 giây)
        r.adjust_for_ambient_noise(mic, duration=1) 
        try:
            # thời gian chờ 3 giây, nói 5 giây 
            audio = r.listen(mic, timeout=3, phrase_time_limit=5)
            # Nhận dạng giọng nói tiếng Việt bằng google Speech Recognition
            text = r.recognize_google(audio, language='vi-VI') # đồi thành tiếng anh thì en-EN
            return text
        except:
            # không nhận thấy âm thanh hãy lỗi trả về none
            return None 
