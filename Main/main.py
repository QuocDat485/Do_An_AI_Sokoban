# Nhập các thư viện cần thiết
import tkinter as tk
import os
import sys
# Thêm thư mục gốc vào sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Sokoban_ui_menu.menu import SokobanApp

def main():
    # Kiểm tra xem PIL/Pillow đã được cài đặt chưa
    try:
        import PIL
        print(f"Phiên bản PIL/Pillow: {PIL.__version__}")
    except ImportError:
        print("PIL/Pillow chưa được cài đặt. Vui lòng cài đặt bằng:")
        print("pip install pillow")
        print("Sau đó chạy lại trò chơi.")
        import sys
        sys.exit(1)
        
    # Khởi tạo cửa sổ chính và ứng dụng
    root = tk.Tk()
    app = SokobanApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()