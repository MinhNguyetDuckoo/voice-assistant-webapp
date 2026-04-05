import tkinter as tk
from tkinter import Canvas, messagebox, ttk
import threading
import time
from datetime import datetime

import pyaudio
from tts import speak
from stt import listen
from improved_llm_handler import create_voice_assistant
import os

class VoiceAssistantGUI:
    def __init__(self):
        # Khởi tạo LLM Assistant với memory
        self.assistant = create_voice_assistant()
        self.session_id = self.assistant.start_new_session("main_user")
        
        # Trạng thái
        self.is_listening = False
        self.chat_messages = []
        self.current_session_name = f"Phiên {datetime.now().strftime('%d/%m %H:%M')}"
        
        # Khởi tạo GUI
        self.setup_gui()
        
    def setup_gui(self):
        """Thiết lập giao diện người dùng"""
        self.root = tk.Tk()
        self.root.title("Trợ lý ảo thông minh - Voice Assistant")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        self.root.configure(bg="#f0f2f5")
        
        # Main container
        self.setup_main_layout()
        
        # Left panel - Chat area
        self.setup_left_panel()
        
        # Right panel - History
        self.setup_right_panel()
        
        # Welcome message
        self.add_message("AI", "Xin chào! Tôi là trợ lý ảo của bạn. Hãy nhấn nút mic để nói nhé! 🎤✨")
        
    def setup_main_layout(self):
        """Thiết lập layout chính"""
        # Main frame
        self.main_frame = tk.Frame(self.root, bg="#f0f2f5")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Left frame (Chat)
        self.left_frame = tk.Frame(self.main_frame, bg="white", relief="raised", bd=1)
        self.left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Right frame (History)
        self.right_frame = tk.Frame(self.main_frame, bg="white", relief="raised", bd=1, width=280)
        self.right_frame.pack(side="right", fill="y", padx=(5, 0))
        self.right_frame.pack_propagate(False)
    
    def setup_left_panel(self):
        """Thiết lập panel trái - khu vực chat"""
        # Header
        header_frame = tk.Frame(self.left_frame, bg="#2196F3", height=60)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="💬 Trò chuyện với AI",
            font=("Segoe UI", 16, "bold"),
            fg="white",
            bg="#2196F3"
        )
        title_label.pack(pady=15)
        
        # Chat area
        chat_container = tk.Frame(self.left_frame, bg="white")
        chat_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Scrollable chat zone
        self.chat_canvas = tk.Canvas(chat_container, bg="#fafafa", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(chat_container, orient="vertical", command=self.chat_canvas.yview)
        self.chat_frame = tk.Frame(self.chat_canvas, bg="#fafafa")
        
        self.chat_frame.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Control area
        control_frame = tk.Frame(self.left_frame, bg="white", height=120)
        control_frame.pack(fill="x", padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        # Status bar
        self.status_label = tk.Label(
            control_frame,
            text="🎙️ Nhấn nút để nói...",
            font=("Segoe UI", 12),
            fg="#666",
            bg="white"
        )
        self.status_label.pack(pady=(0, 10))
        
        # Voice button
        self.setup_voice_button(control_frame)
    
    def setup_right_panel(self):
        """Thiết lập panel phải - lịch sử cuộc trò chuyện"""
        # Header
        history_header = tk.Frame(self.right_frame, bg="#4CAF50", height=60)
        history_header.pack(fill="x")
        history_header.pack_propagate(False)
        
        history_title = tk.Label(
            history_header,
            text="📚 Lịch sử trò chuyện",
            font=("Segoe UI", 14, "bold"),
            fg="white",
            bg="#4CAF50"
        )
        history_title.pack(pady=15)
        
        # Current session info
        session_info_frame = tk.Frame(self.right_frame, bg="#e8f5e8", height=50)
        session_info_frame.pack(fill="x", padx=5, pady=5)
        session_info_frame.pack_propagate(False)
        
        current_session_label = tk.Label(
            session_info_frame,
            text="📝 Phiên hiện tại:",
            font=("Segoe UI", 10, "bold"),
            fg="#2e7d32",
            bg="#e8f5e8"
        )
        current_session_label.pack(anchor="w", padx=10, pady=2)
        
        self.current_session_label = tk.Label(
            session_info_frame,
            text=self.current_session_name,
            font=("Segoe UI", 9),
            fg="#4caf50",
            bg="#e8f5e8"
        )
        self.current_session_label.pack(anchor="w", padx=20)
        
        # Buttons frame
        buttons_frame = tk.Frame(self.right_frame, bg="white")
        buttons_frame.pack(fill="x", padx=10, pady=5)
        
        # New session button
        self.new_session_btn = tk.Button(
            buttons_frame,
            text="🆕 Phiên mới",
            font=("Segoe UI", 10, "bold"),
            bg="#FF9800",
            fg="white",
            relief="flat",
            padx=20,
            pady=5,
            command=self.start_new_session
        )
        self.new_session_btn.pack(fill="x", pady=2)
        
        # Clear history button
        self.clear_btn = tk.Button(
            buttons_frame,
            text="🗑️ Xóa lịch sử",
            font=("Segoe UI", 10),
            bg="#f44336",
            fg="white",
            relief="flat",
            padx=20,
            pady=5,
            command=self.clear_history
        )
        self.clear_btn.pack(fill="x", pady=2)
        
        # Sessions list
        sessions_label = tk.Label(
            self.right_frame,
            text="📋 Các phiên trước:",
            font=("Segoe UI", 11, "bold"),
            fg="#333",
            bg="white"
        )
        sessions_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Sessions listbox with scrollbar
        listbox_frame = tk.Frame(self.right_frame, bg="white")
        listbox_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.sessions_listbox = tk.Listbox(
            listbox_frame,
            font=("Segoe UI", 9),
            bg="#f9f9f9",
            fg="#333",
            selectbackground="#2196F3",
            selectforeground="white",
            relief="flat",
            bd=1
        )
        
        listbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical", command=self.sessions_listbox.yview)
        self.sessions_listbox.configure(yscrollcommand=listbox_scrollbar.set)
        
        self.sessions_listbox.pack(side="left", fill="both", expand=True)
        listbox_scrollbar.pack(side="right", fill="y")
        
        # Bind double-click to view session
        self.sessions_listbox.bind("<Double-Button-1>", self.view_selected_session)
        
        # Load existing sessions
        self.refresh_sessions_list()
        
        # Stats frame
        stats_frame = tk.Frame(self.right_frame, bg="#f0f0f0", height=60)
        stats_frame.pack(fill="x", padx=5, pady=5)
        stats_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            stats_frame,
            text="📊 Tin nhắn trong phiên: 0",
            font=("Segoe UI", 9),
            fg="#666",
            bg="#f0f0f0"
        )
        self.stats_label.pack(pady=15)
    
    def setup_voice_button(self, parent):
        """Thiết lập nút voice"""
        button_frame = tk.Frame(parent, bg="white")
        button_frame.pack()
        
        self.button_canvas = Canvas(button_frame, width=80, height=80, bg="white", highlightthickness=0)
        self.button_canvas.pack()
        
        self.create_round_button(self.button_canvas, 40, 40, 30, command=self.start_listening)
    
    def create_round_button(self, canvas, x, y, r, command=None):
        """Tạo nút tròn với hiệu ứng đẹp"""
        # Gradient shadow
        for i in range(3):
            shadow_alpha = 0.1 + (i * 0.05)
            shadow_color = f"#{int(33 * shadow_alpha):02x}{int(150 * shadow_alpha):02x}{int(243 * shadow_alpha):02x}"
            canvas.create_oval(
                x - r + i + 2, y - r + i + 2, 
                x + r + i + 2, y + r + i + 2, 
                fill=shadow_color, outline=""
            )
        
        # Main button with gradient effect
        self.button_item = canvas.create_oval(x - r, y - r, x + r, y + r, fill="#2196F3", outline="", width=0)
        
        # Inner glow
        inner_glow = canvas.create_oval(x - r + 3, y - r + 3, x + r - 3, y + r - 3, fill="#42A5F5", outline="")
        
        # Icon mic
        self.mic_icon = canvas.create_text(x, y, text="🎤", font=("Segoe UI", 18, "bold"), fill="white")
        
        def on_click(event):
            if command:
                # Animation effect
                canvas.itemconfig(self.button_item, fill="#1976D2")
                canvas.after(100, lambda: canvas.itemconfig(self.button_item, fill="#2196F3"))
                command()
        
        # Hover effects
        def on_enter(event):
            canvas.itemconfig(self.button_item, fill="#1E88E5")
        
        def on_leave(event):
            if not self.is_listening:
                canvas.itemconfig(self.button_item, fill="#2196F3")
        
        # Bind events
        for item in [self.button_item, inner_glow, self.mic_icon]:
            canvas.tag_bind(item, "<Button-1>", on_click)
            canvas.tag_bind(item, "<Enter>", on_enter)
            canvas.tag_bind(item, "<Leave>", on_leave)
    
    def update_status(self, message):
        """Cập nhật trạng thái"""
        self.status_label.config(text=message)
        self.root.update()
    
    def add_message(self, sender, message):
        """Thêm tin nhắn vào chat với style đẹp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Frame cho message
        msg_frame = tk.Frame(self.chat_frame, bg="#fafafa")
        msg_frame.pack(fill="x", padx=15, pady=8)
        
        # Style cho user và AI khác nhau
        if sender == "Bạn":
            # Message của user - căn phải, màu xanh
            bubble_color = "#E3F2FD"
            text_color = "#1565C0"
            border_color = "#2196F3"
            anchor = "e"
            emoji = "👤"
        else:
            # Message của AI - căn trái, màu xanh lá
            bubble_color = "#E8F5E8"
            text_color = "#2E7D32"
            border_color = "#4CAF50"
            anchor = "w"
            emoji = "🤖"
        
        # Bubble message với border đẹp
        bubble_frame = tk.Frame(
            msg_frame, 
            bg=bubble_color, 
            relief="solid", 
            bd=1
        )
        bubble_frame.pack(anchor=anchor, padx=(0 if anchor=="w" else 80, 80 if anchor=="w" else 0))
        
        # Header với avatar và time
        header_frame = tk.Frame(bubble_frame, bg=bubble_color)
        header_frame.pack(fill="x", padx=12, pady=(8, 2))
        
        sender_info = tk.Label(
            header_frame,
            text=f"{emoji} {sender}",
            font=("Segoe UI", 9, "bold"),
            fg=text_color,
            bg=bubble_color
        )
        sender_info.pack(side="left")
        
        time_label = tk.Label(
            header_frame,
            text=timestamp,
            font=("Segoe UI", 8),
            fg="#666",
            bg=bubble_color
        )
        time_label.pack(side="right")
        
        # Message content với wrapping
        msg_label = tk.Label(
            bubble_frame,
            text=message,
            font=("Segoe UI", 11),
            fg=text_color,
            bg=bubble_color,
            wraplength=350,
            justify="left"
        )
        msg_label.pack(anchor="w", padx=12, pady=(0, 8))
        
        # Update stats
        self.update_message_stats()
        
        # Auto scroll to bottom
        self.root.update()
        self.chat_canvas.yview_moveto(1)
    
    def start_listening(self):
        """Bắt đầu lắng nghe giọng nói"""
        if self.is_listening:
            return
        
        self.is_listening = True
        # Đổi icon thành đang ghi âm với hiệu ứng
        self.button_canvas.itemconfig(self.mic_icon, text="🔴")
        self.button_canvas.itemconfig(self.button_item, fill="#F44336")
        
        # Chạy trong thread riêng để không block UI
        threading.Thread(target=self.handle_voice_interaction, daemon=True).start()
    
    def handle_voice_interaction(self):
        """Xử lý tương tác giọng nói"""
        try:
            # Lắng nghe
            self.update_status("🎧 Đang lắng nghe... Hãy nói điều gì đó!")
            
            user_input = listen(self.update_status)
            
            if user_input:
                # Hiển thị input của user
                self.add_message("Bạn", user_input)
                
                # Xử lý với LLM
                self.update_status("🤖 Đang suy nghĩ...")
                
                try:
                    ai_response = self.assistant.ask_llm(user_input)
                    
                    # Hiển thị response
                    self.add_message("AI", ai_response)
                    
                    # Đọc response
                    self.update_status("🔊 Đang trả lời...")
                    speak(ai_response)
                    
                except Exception as e:
                    error_msg = "Xin lỗi, tôi gặp sự cố khi xử lý câu hỏi."
                    self.add_message("AI", error_msg)
                    speak(error_msg)
                    print(f"LLM Error: {e}")
            
            else:
                self.update_status("❌ Không nghe được. Thử lại nhé!")
                
        except Exception as e:
            self.update_status("🔧 Lỗi microphone. Kiểm tra thiết bị!")
            print(f"Voice Error: {e}")
        
        finally:
            # Reset button state
            self.is_listening = False
            self.button_canvas.itemconfig(self.mic_icon, text="🎤")
            self.button_canvas.itemconfig(self.button_item, fill="#2196F3")
            self.update_status("🎙️ Nhấn nút để nói...")
    
    def start_new_session(self):
        """Bắt đầu phiên trò chuyện mới"""
        # Lưu session cũ vào lịch sử
        if hasattr(self, 'session_id') and self.session_id:
            old_session_name = self.current_session_name
            self.sessions_listbox.insert(0, f"📝 {old_session_name}")
        
        # Tạo session mới
        self.session_id = self.assistant.start_new_session("main_user")
        self.current_session_name = f"Phiên {datetime.now().strftime('%d/%m %H:%M')}"
        self.current_session_label.config(text=self.current_session_name)
        
        # Clear chat area
        for widget in self.chat_frame.winfo_children():
            widget.destroy()
        
        # Welcome message
        self.add_message("AI", "✨ Phiên trò chuyện mới bắt đầu! Tôi có thể giúp gì cho bạn?")
        
        messagebox.showinfo("Thành công", "🆕 Đã tạo phiên trò chuyện mới!")
    
    def clear_history(self):
        """Xóa lịch sử cuộc trò chuyện"""
        result = messagebox.askyesno(
            "Xác nhận", 
            "🗑️ Bạn có chắc muốn xóa toàn bộ lịch sử?\n\nHành động này không thể hoàn tác!"
        )
        if result:
            self.sessions_listbox.delete(0, tk.END)
            try:
                self.assistant.clear_conversation()
            except:
                pass
            messagebox.showinfo("Hoàn tất", "✅ Đã xóa lịch sử trò chuyện!")
    
    def view_selected_session(self, event):
        """Xem phiên được chọn"""
        selection = self.sessions_listbox.curselection()
        if selection:
            session_name = self.sessions_listbox.get(selection[0])
            messagebox.showinfo(
                "Lịch sử phiên", 
                f"📖 Đang xem: {session_name}\n\n💡 Tính năng xem chi tiết sẽ được cập nhật trong phiên bản tiếp theo!"
            )
    
    def refresh_sessions_list(self):
        """Làm mới danh sách phiên"""
        try:
            # Lấy danh sách sessions từ database
            sessions = self.assistant.memory.get_all_sessions("main_user")
            
            self.sessions_listbox.delete(0, tk.END)
            for session in sessions[:10]:  # Hiển thị 10 phiên gần nhất
                created_time = session['created_at'].strftime('%d/%m %H:%M')
                message_count = len(session.get('messages', []))
                display_text = f"📝 Phiên {created_time} ({message_count} tin nhắn)"
                self.sessions_listbox.insert(tk.END, display_text)
                
        except Exception as e:
            print(f"Error loading sessions: {e}")
    
    def update_message_stats(self):
        """Cập nhật thống kê tin nhắn"""
        try:
            if hasattr(self, 'session_id') and self.session_id:
                history = self.assistant.get_conversation_history(100)
                message_count = len(history)
                self.stats_label.config(text=f"📊 Tin nhắn trong phiên: {message_count}")
        except:
            pass
    
    def on_closing(self):
        """Xử lý khi đóng app"""
        try:
            self.assistant.close()
        except:
            pass
        self.root.destroy()
    
    def run(self):
        """Chạy ứng dụng"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

def main():
    """Hàm main chính"""
    try:
        # Kiểm tra dependencies
        required_files = ['tts.py', 'stt.py', 'improved_llm_handler.py', 'conversation_memory.py']
        for file in required_files:
            if not os.path.exists(file):
                print(f"Thiếu file: {file}")
                return
        
        print("Khởi động Voice Assistant...")
        
        # Tạo và chạy ứng dụng
        print("Đang khởi động GUI...")
        app = VoiceAssistantGUI()
        app.run()
        
    except Exception as e:
        print(f"Lỗi khởi động: {e}")
        messagebox.showerror("Lỗi", f"Không thể khởi động ứng dụng:\n{e}")

if __name__ == "__main__":
    main()