# Nhập các thư viện cần thiết
import tkinter as tk
from tkinter import messagebox, filedialog
import os
from PIL import Image, ImageTk
from Sokoban_core.game import SokobanGame
from Sokoban_core.movement import move, undo
from Sokoban_core.check_win import has_won
from Sokoban_core.save_load import save_state, load_state
from Sokoban_graphics.render import SokobanRenderer
from Sokoban_algorithms.solver import bfs_solver, a_star_solver, greedy_solver, beam_search_solver

def add_hover_effect(button):
    button.bind("<Enter>", lambda e: button.config(bg="#666"))
    button.bind("<Leave>", lambda e: button.config(bg="#444"))

class MenuFrame(tk.Frame):
    def __init__(self, master, on_start, on_bfs, on_astar, on_greedy, on_beam, on_quit):
        # Khởi tạo khung menu
        super().__init__(master, bg="#000032")
        
        self.master = master
        
        # Tiêu đề
        title_label = tk.Label(self, text="SOKOBAN GAME", font=("Arial", 24, "bold"), 
                              bg="#000032", fg="white")
        title_label.pack(pady=20)
        
        # Thử tải logo nếu tồn tại
        try:
            logo_path = os.path.join("sprites", "logo.png")
            if os.path.exists(logo_path):
                logo_img = Image.open(logo_path)
                logo_img = logo_img.resize((300, 150), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                
                logo_label = tk.Label(self, image=logo_photo, bg="#000032")
                logo_label.image = logo_photo  # Giữ tham chiếu để tránh garbage collection
                logo_label.pack(pady=10)
        except Exception as e:
            print(f"Không thể tải logo: {e}")
        
        # Các nút điều khiển
        button_frame = tk.Frame(self, bg="#000032")
        button_frame.pack(pady=20)
        
        start_button = tk.Button(button_frame, text="Bắt đầu trò chơi", command=on_start,
                               font=("Arial", 14), bg="#444", fg="white", width=15)
        start_button.pack(pady=10)
        
        bfs_button = tk.Button(button_frame, text="Chạy BFS Solver", command=on_bfs,
                             font=("Arial", 14), bg="#444", fg="white", width=15)
        bfs_button.pack(pady=10)
        
        astar_button = tk.Button(button_frame, text="Chạy A* Solver", command=on_astar,
                               font=("Arial", 14), bg="#444", fg="white", width=15)
        astar_button.pack(pady=10)
        
        greedy_button = tk.Button(button_frame, text="Chạy Greedy Solver", command=on_greedy,
                                font=("Arial", 14), bg="#444", fg="white", width=15)
        greedy_button.pack(pady=10)
        
        beam_button = tk.Button(button_frame, text="Chạy Beam Search", command=on_beam,
                              font=("Arial", 14), bg="#444", fg="white", width=15)
        beam_button.pack(pady=10)

        quit_button = tk.Button(button_frame, text="Thoát", command=on_quit,
                              font=("Arial", 14), bg="#444", fg="white", width=15)
        quit_button.pack(pady=10)
        
        # Hướng dẫn
        instructions = [
            "Điều khiển trong trò chơi:",
            "Phím mũi tên - Di chuyển người chơi",
            "M - Quay lại menu",
            "R - Đặt lại cấp độ",
            "S - Lưu trò chơi",
            "L - Tải trò chơi",
            "U - Hoàn tác di chuyển"
        ]
        
        instruction_frame = tk.Frame(self, bg="#000032")
        instruction_frame.pack(pady=20)
        
        for line in instructions:
            instruction_label = tk.Label(instruction_frame, text=line, font=("Arial", 12),
                                       bg="#000032", fg="#b4b4b4")
            instruction_label.pack()

        add_hover_effect(start_button)
        add_hover_effect(bfs_button)
        add_hover_effect(astar_button)
        add_hover_effect(greedy_button)
        add_hover_effect(beam_button)
        add_hover_effect(quit_button)

class StatusFrame(tk.Frame):
    def __init__(self, master):
        # Khởi tạo khung trạng thái
        super().__init__(master, bg="#222")
        
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        
        self.status_label = tk.Label(self, textvariable=self.status_var, 
                                   font=("Arial", 10), bg="#222", fg="white")
        self.status_label.pack(fill="x", padx=10, pady=5)
    
    def set_status(self, text):
        # Cập nhật văn bản trạng thái
        self.status_var.set(text)
        self.update()

class SokobanApp:
    def __init__(self, root):
        # Khởi tạo ứng dụng
        self.root = root
        self.root.title("Trò chơi Sokoban")
        self.root.resizable(False, False)
        
        # Thử đặt biểu tượng ứng dụng
        try:
            icon_path = os.path.join("sprites", "icon.png")
            if os.path.exists(icon_path):
                icon_img = Image.open(icon_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.root.iconphoto(True, icon_photo)
        except Exception as e:
            print(f"Không thể tải biểu tượng: {e}")
        
        self.levels = self.create_levels()
        self.current_level = 0
        
        # Tạo instance trò chơi
        self.game = SokobanGame(
            self.levels[self.current_level]["grid"],
            self.levels[self.current_level]["player_start"],
            self.levels[self.current_level]["box_starts"],
            self.levels[self.current_level]["targets"]
        )
        
        # Thiết lập khung chính
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)
        
        # Khung menu
        self.menu_frame = MenuFrame(
            self.main_frame, 
            self.start_game,
            self.run_bfs_solver,
            self.run_astar_solver,
            self.run_greedy_solver,
            self.run_beam_search_solver,
            self.quit_game
        )
        self.menu_frame.pack(fill="both", expand=True)
        
        # Khung trò chơi (ẩn ban đầu)
        self.game_frame = tk.Frame(self.main_frame)
        self.renderer = None
        
        # Thanh trạng thái
        self.status_frame = StatusFrame(root)
        self.status_frame.pack(fill="x", side="bottom")
        
        # Biến cho solver AI
        self.ai_mode = None
        self.ai_path = []
        self.ai_step = 0
        
        # Gắn sự kiện bàn phím
        self.root.bind("<KeyPress>", self.handle_keypress)
    
    def create_levels(self):
        # Định nghĩa các cấp độ với độ khó tăng dần
        return [
            # Cấp độ 1 - Đơn giản
            {
                "grid": [
                    [1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 2)],
                "targets": [(4, 4)]
            },
            
            # Cấp độ 2 - Hai hộp
            {
                "grid": [
                    [1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 2), (3, 3)],
                "targets": [(4, 4), (5, 5)]
            },
            
            # Cấp độ 3 - Có chướng ngại vật
            {
                "grid": [
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 1, 1, 1, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 1, 1, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 1), (5, 3)],
                "targets": [(5, 5), (5, 6)]
            }
        ]
    
    def start_game(self):
        # Bắt đầu trò chơi, ẩn menu và hiển thị khung trò chơi
        self.menu_frame.pack_forget()
        
        # Khởi tạo khung trò chơi và renderer nếu chưa được tạo
        if not self.renderer:
            self.renderer = SokobanRenderer(self.game_frame, self.game)
            self.renderer.pack(fill="both", expand=True)
        else:
            self.renderer.game = self.game
        
        self.game_frame.pack(fill="both", expand=True)
        self.root.title(f"Sokoban - Cấp độ {self.current_level + 1}")
        self.renderer.draw()
        
        # Đặt lại chế độ AI
        self.ai_mode = None
        self.ai_path = []
        self.ai_step = 0
    
    def run_bfs_solver(self):
        # Chạy solver BFS
        self.start_game()
        self.root.title("Sokoban - Đang giải bằng BFS...")
        self.status_frame.set_status("Đang chạy solver BFS...")
        
        # Chạy BFS trong một luồng riêng để tránh đóng băng giao diện
        def run_bfs():
            self.ai_mode = "bfs"
            self.ai_path = bfs_solver(self.game, self.status_frame.set_status)
            self.ai_step = 0
            
            if not self.ai_path:
                self.status_frame.set_status("BFS không tìm thấy lời giải")
                self.ai_mode = None
            else:
                self.status_frame.set_status(f"BFS tìm thấy lời giải: {len(self.ai_path)} bước")
                self.execute_ai_move()
        
        self.root.after(100, run_bfs)
    
    def run_astar_solver(self):
        # Chạy solver A*
        self.start_game()
        self.root.title("Sokoban - Đang giải bằng A*...")
        self.status_frame.set_status("Đang chạy solver A*...")
        
        # Chạy A* trong một luồng riêng
        def run_astar():
            self.ai_mode = "astar"
            self.ai_path = a_star_solver(self.game, self.status_frame.set_status)
            self.ai_step = 0
            
            if not self.ai_path:
                self.status_frame.set_status("A* không tìm thấy lời giải")
                self.ai_mode = None
            else:
                self.status_frame.set_status(f"A* tìm thấy lời giải: {len(self.ai_path)} bước")
                self.execute_ai_move()
        
        self.root.after(100, run_astar)
    
    def run_greedy_solver(self):
        # Chạy solver Greedy
        self.start_game()
        self.root.title("Sokoban - Đang giải bằng Greedy...")
        self.status_frame.set_status("Đang chạy solver Greedy...")
        
        # Chạy Greedy trong một luồng riêng
        def run_greedy():
            self.ai_mode = "greedy"
            self.ai_path = greedy_solver(self.game, self.status_frame.set_status)
            self.ai_step = 0
            
            if not self.ai_path:
                self.status_frame.set_status("Greedy không tìm thấy lời giải")
                self.ai_mode = None
            else:
                self.status_frame.set_status(f"Greedy tìm thấy lời giải: {len(self.ai_path)} bước")
                self.execute_ai_move()
        
        self.root.after(100, run_greedy)
    
    def run_beam_search_solver(self):
        # Chạy solver Beam Search
        self.start_game()
        self.root.title("Sokoban - Đang giải bằng Beam Search...")
        self.status_frame.set_status("Đang chạy solver Beam Search...")
        
        # Chạy Beam Search trong một luồng riêng
        def run_beam():
            self.ai_mode = "beam"
            self.ai_path = beam_search_solver(self.game, self.status_frame.set_status)
            self.ai_step = 0
            
            if not self.ai_path:
                self.status_frame.set_status("Beam Search không tìm thấy lời giải")
                self.ai_mode = None
            else:
                self.status_frame.set_status(f"Beam Search tìm thấy lời giải: {len(self.ai_path)} bước")
                self.execute_ai_move()
        
        self.root.after(100, run_beam)

    def execute_ai_move(self):
        # Thực hiện bước di chuyển của AI
        if self.ai_mode and self.ai_path and self.ai_step < len(self.ai_path):
            move(self.game, self.ai_path[self.ai_step])
            self.ai_step += 1
            self.renderer.draw()
            
            # Kiểm tra chiến thắng trước bước tiếp theo
            if has_won(self.game):
                self.handle_win()
                return
            
            # Lên lịch bước tiếp theo
            self.root.after(300, self.execute_ai_move)
    
    def handle_keypress(self, event):
        # Xử lý sự kiện bàn phím
        if self.menu_frame.winfo_ismapped():
            # Ở chế độ menu, bỏ qua các điều khiển trò chơi
            return
            
        # Không xử lý phím khi AI đang chạy
        if self.ai_mode:
            return
            
        key = event.keysym.lower()
        
        if key == "m":
            # Quay lại menu
            self.game_frame.pack_forget()
            self.menu_frame.pack(fill="both", expand=True)
            self.root.title("Menu Sokoban")
        elif key == "r":
            # Đặt lại cấp độ
            self.game = SokobanGame(
                self.levels[self.current_level]["grid"],
                self.levels[self.current_level]["player_start"],
                self.levels[self.current_level]["box_starts"],
                self.levels[self.current_level]["targets"]
            )
            self.renderer.game = self.game
            self.renderer.draw()
            self.status_frame.set_status("Đã đặt lại cấp độ")
        elif key == "s":
            # Lưu trò chơi
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Tệp JSON", "*.json")],
                title="Lưu trò chơi"
            )
            if file_path:
                save_state(self.game, file_path)
                self.status_frame.set_status(f"Trò chơi đã được lưu vào {os.path.basename(file_path)}")
        elif key == "l":
            # Tải trò chơi
            file_path = filedialog.askopenfilename(
                defaultextension=".json",
                filetypes=[("Tệp JSON", "*.json")],
                title="Tải trò chơi"
            )
            if file_path:
                if load_state(self.game, file_path):
                    self.renderer.game = self.game
                    self.renderer.draw()
                    self.status_frame.set_status(f"Trò chơi đã được tải từ {os.path.basename(file_path)}")
                else:
                    self.status_frame.set_status("Không thể tải trò chơi")
        elif key == "u":
            # Hoàn tác di chuyển
            if undo(self.game):
                self.renderer.draw()
                self.status_frame.set_status("Đã hoàn tác di chuyển")
            else:
                self.status_frame.set_status("Không có di chuyển để hoàn tác")
        else:
            # Di chuyển
            direction = None
            if key == "up":
                direction = (-1, 0)
            elif key == "down":
                direction = (1, 0)
            elif key == "left":
                direction = (0, -1)
            elif key == "right":
                direction = (0, 1)
                
            if direction:
                if move(self.game, direction):
                    self.renderer.draw()
                    
                    # Kiểm tra điều kiện chiến thắng
                    if has_won(self.game):
                        self.handle_win()
    
    def handle_win(self):
        # Xử lý khi thắng cấp độ
        self.status_frame.set_status(f"Cấp độ {self.current_level + 1} hoàn thành!")
        
        # Chuyển sang cấp độ tiếp theo sau một khoảng thời gian
        def next_level():
            self.current_level = (self.current_level + 1) % len(self.levels)
            self.game = SokobanGame(
                self.levels[self.current_level]["grid"],
                self.levels[self.current_level]["player_start"],
                self.levels[self.current_level]["box_starts"],
                self.levels[self.current_level]["targets"]
            )
            self.renderer.game = self.game
            self.renderer.draw()
            self.ai_mode = None
            self.root.title(f"Sokoban - Cấp độ {self.current_level + 1}")
            self.status_frame.set_status(f"Bắt đầu cấp độ {self.current_level + 1}")
        
        self.root.after(1000, next_level)
    
    def quit_game(self):
        # Thoát trò chơi
        self.root.destroy()