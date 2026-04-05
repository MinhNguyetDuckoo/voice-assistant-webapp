import tkinter as tk
from tkinter import messagebox, scrolledtext
from datetime import datetime
from typing import List, Dict

class SessionViewerWindow:
    def __init__(self, parent, session_data: Dict, assistant):
        """
        Cửa sổ xem chi tiết phiên trò chuyện
        """
        self.parent = parent
        self.session_data = session_data
        self.assistant = assistant
        
        self.create_window()
    
    def create_window(self):
        """Tạo cửa sổ xem phiên"""
        self.window = tk.Toplevel(self.parent)
        self.window.title(f"📖 Chi tiết phiên - {self.session_data.get('_id', 'Unknown')}")
        self.window.geometry("600x500")
        self.window.resizable(True, True)
        self.window.configure(bg="white")
        
        # Header
        self.create_header()
        
        # Messages area
        self.create_messages_area()
        
        # Footer buttons
        self.create_footer()
        
        # Load messages
        self.load_messages()
        
        # Center window
        self.center_window()
    
    def create_header(self):
        """Tạo header với thông tin phiên"""
        header_frame = tk.Frame(self.window, bg="#2196F3", height=80)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)
        
        # Session info
        created_time = self.session_data.get('created_at', datetime.now())
        if isinstance(created_time, datetime):
            time_str = created_time.strftime("%d/%m/%Y %H:%M:%S")
        else:
            time_str = str(created_time)
        
        message_count = len(self.session_data.get('messages', []))
        
        info_text = f"📅 Tạo lúc: {time_str}\n💬 Số tin nhắn: {message_count}"
        
        info_label = tk.Label(
            header_frame,
            text=info_text,
            font=("Segoe UI", 12),
            fg="white",
            bg="#2196F3",
            justify="left"
        )
        info_label.pack(pady=15, padx=20, anchor="w")
    
    def create_messages_area(self):
        """Tạo khu vực hiển thị tin nhắn"""
        # Frame container
        messages_frame = tk.Frame(self.window, bg="white")
        messages_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ScrolledText for messages
        self.messages_text = scrolledtext.ScrolledText(
            messages_frame,
            font=("Segoe UI", 10),
            bg="#fafafa",
            fg="#333",
            wrap="word",
            state="disabled",
            relief="flat",
            bd=1
        )
        self.messages_text.pack(fill="both", expand=True)
        
        # Configure text tags for styling
        self.messages_text.tag_configure("user", foreground="#1976D2", font=("Segoe UI", 10, "bold"))
        self.messages_text.tag_configure("assistant", foreground="#388E3C", font=("Segoe UI", 10, "bold"))
        self.messages_text.tag_configure("timestamp", foreground="#666", font=("Segoe UI", 8))
        self.messages_text.tag_configure("content", foreground="#333", font=("Segoe UI", 10))
    
    def create_footer(self):
        """Tạo footer với các nút"""
        footer_frame = tk.Frame(self.window, bg="white", height=60)
        footer_frame.pack(fill="x", padx=10, pady=10)
        footer_frame.pack_propagate(False)
        
        # Export button
        export_btn = tk.Button(
            footer_frame,
            text="💾 Xuất ra file",
            font=("Segoe UI", 10),
            bg="#FF9800",
            fg="white",
            relief="flat",
            padx=20,
            command=self.export_session
        )
        export_btn.pack(side="left", padx=(0, 10))
        
        # Delete button
        delete_btn = tk.Button(
            footer_frame,
            text="🗑️ Xóa phiên",
            font=("Segoe UI", 10),
            bg="#f44336",
            fg="white",
            relief="flat",
            padx=20,
            command=self.delete_session
        )
        delete_btn.pack(side="left", padx=(0, 10))
        
        # Close button
        close_btn = tk.Button(
            footer_frame,
            text="❌ Đóng",
            font=("Segoe UI", 10),
            bg="#9E9E9E",
            fg="white",
            relief="flat",
            padx=20,
            command=self.window.destroy
        )
        close_btn.pack(side="right")
    
    def load_messages(self):
        """Load và hiển thị tin nhắn"""
        self.messages_text.config(state="normal")
        self.messages_text.delete(1.0, tk.END)
        
        messages = self.session_data.get('messages', [])
        
        if not messages:
            self.messages_text.insert(tk.END, "📭 Phiên này chưa có tin nhắn nào.\n", "content")
        else:
            for i, msg in enumerate(messages):
                # Timestamp
                timestamp = msg.get('timestamp', datetime.now())
                if isinstance(timestamp, datetime):
                    time_str = timestamp.strftime("%H:%M:%S")
                else:
                    time_str = str(timestamp)
                
                # Role
                role = msg.get('role', 'unknown')
                role_display = "👤 Bạn" if role == "user" else "🤖 AI"