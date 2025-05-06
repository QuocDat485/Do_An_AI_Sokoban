# Nhập các thư viện cần thiết
import tkinter as tk
from tkinter import messagebox, ttk
import os
import glob
import sys
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
from Sokoban_core.game import SokobanGame
from Sokoban_core.movement import move
from Sokoban_core.check_win import has_won
from Sokoban_core.save_load import save_state, load_state
from Sokoban_graphics.render import SokobanRenderer
from Sokoban_algorithms.solver import bfs_solver, a_star_solver, greedy_solver, beam_search_solver

class CustomButton(tk.Button):
    def __init__(self, master, text, width=180, height=45, command=None, 
                 bg_color="#444", hover_color="#666", text_color="white", 
                 font=("Arial", 11)):
        super().__init__(
            master, 
            text=text,
            width=width//15,  # Chuyển đổi pixel sang ký tự
            height=height//15,
            bg=bg_color,
            fg=text_color,
            font=font,
            command=command,
            activebackground=hover_color,
            borderwidth=2,
            relief="raised"
        )
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
    
    def _on_enter(self, event):
        self.config(bg=self.hover_color)
    
    def _on_leave(self, event):
        self.config(bg=self.bg_color)

class MenuFrame(tk.Frame):
    def __init__(self, master, on_start, on_level_select, on_quit):
        super().__init__(master, bg="#000032")
        
        self.master = master
        self.image_references = []
        
        # In thư mục làm việc hiện tại
        print(f"Thư mục làm việc hiện tại: {os.getcwd()}")
        
        # Đường dẫn đến thư mục sprites
        self.sprite_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Sokoban_graphics", "sprites"))
        print(f"Đường dẫn thư mục sprites: {self.sprite_dir}")
        
        # Kiểm tra thư mục sprites
        if not os.path.exists(self.sprite_dir):
            print(f"Lỗi: Thư mục sprites không tồn tại tại {self.sprite_dir}")
            return
        
        # Liệt kê tệp ảnh
        sprite_files = glob.glob(os.path.join(self.sprite_dir, "*.[pP][nN][gG]")) + \
                       glob.glob(os.path.join(self.sprite_dir, "*.[jJ][pP][gG]")) + \
                       glob.glob(os.path.join(self.sprite_dir, "*.[jJ][pP][eE][gG]")) + \
                       glob.glob(os.path.join(self.sprite_dir, "*.[gG][iI][fF]"))
        print("Các tệp ảnh trong thư mục sprites:")
        if not sprite_files:
            print(" - Không tìm thấy tệp ảnh nào")
        for f in sprite_files:
            try:
                img = Image.open(f)
                print(f" - {os.path.basename(f)} (Kích thước: {img.size}, Định dạng: {img.format})")
                img.close()
            except Exception as e:
                print(f" - {os.path.basename(f)} (Lỗi: Không thể mở - {e})")
        
        # Tạo container chính
        main_container = tk.Frame(self, bg="#000032", width=800, height=600)  # Kích thước mặc định
        main_container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Tải logo full khung
        logo_loaded = False
        logo_patterns = ["logo.[pP][nN][gG]", "Logo.[pP][nN][gG]"]
        for pattern in logo_patterns:
            logo_files = glob.glob(os.path.join(self.sprite_dir, pattern))
            for logo_path in logo_files:
                try:
                    logo_img = Image.open(logo_path)
                    if logo_img.size[0] <= 0 or logo_img.size[1] <= 0:
                        print(f"Hình ảnh {os.path.basename(logo_path)} không hợp lệ: kích thước không hợp lệ")
                        logo_img.close()
                        continue
                    # Resize logo để gần full khung
                    win_width = min(1024, self.master.winfo_screenwidth())
                    logo_width = int(win_width * 0.9)
                    aspect_ratio = logo_img.size[1] / logo_img.size[0]
                    logo_height = int(logo_width * aspect_ratio)
                    logo_img = logo_img.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                    logo_photo = ImageTk.PhotoImage(logo_img)
                    self.image_references.append(logo_photo)
                    
                    logo_label = tk.Label(main_container, image=logo_photo, bg="#000032")
                    logo_label.place(relx=0.5, rely=0.5, anchor="center")
                    logo_loaded = True
                    print(f"Đã tải logo: {logo_path} (Kích thước: {logo_img.size}, Định dạng: {logo_img.format})")
                    logo_img.close()
                    break
                except Exception as e:
                    print(f"Lỗi khi tải {os.path.basename(logo_path)}: {e}")
            if logo_loaded:
                break
        
        if not logo_loaded:
            print("Không tìm thấy logo phù hợp, sử dụng văn bản fallback")
            title_label = tk.Label(
                main_container, 
                text="SOKOBAN", 
                font=("Arial", 36, "bold"), 
                bg="#000032", 
                fg="#FFD700"
            )
            title_label.place(relx=0.5, rely=0.4, anchor="center")
            shadow_label = tk.Label(
                main_container, 
                text="GAME", 
                font=("Arial", 24, "bold"), 
                bg="#000032", 
                fg="#FF8C00"
            )
            shadow_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Đặt các nút với vị trí cố định
        play_btn = CustomButton(
            main_container, 
            "Chơi Ngay", 
            width=180, 
            height=45,
            bg_color="#28a745", 
            hover_color="#218838",
            font=("Arial", 11),
            command=on_start
        )
        play_btn.place(relx=0.5, rely=0.35, anchor="center")
        
        level_btn = CustomButton(
            main_container, 
            "Chọn Cấp Độ", 
            width=180, 
            height=45,
            bg_color="#007bff", 
            hover_color="#0069d9",
            font=("Arial", 11),
            command=on_level_select
        )
        level_btn.place(relx=0.5, rely=0.50, anchor="center")
        
        quit_btn = CustomButton(
            main_container, 
            "Thoát", 
            width=180, 
            height=45,
            bg_color="#dc3545", 
            hover_color="#c82333",
            font=("Arial", 11),
            command=on_quit
        )
        quit_btn.place(relx=0.5, rely=0.65, anchor="center")
        
        # Thông tin trò chơi
        info_label = tk.Label(
            self, 
            text="Chọn cấp độ và thuật toán để xem AI giải\n© 2023 Sokoban Game",
            font=("Arial", 8),
            bg="#000032",
            fg="#aaa"
        )
        info_label.place(relx=0.5, rely=0.95, anchor="center")

class LevelSelectFrame(tk.Frame):
    def __init__(self, master, levels, on_select, on_back):
        super().__init__(master)
        self.master = master
        self.image_references = []
        self.bg_image = None
        self.bg_label = None
        
        self.config(bg="#000032")
        self.load_background()
        
        # Tiêu đề
        title_label = tk.Label(
            self, 
            text="CHỌN CẤP ĐỘ & THUẬT TOÁN", 
            font=("Arial", 20, "bold"), 
            bg=None, 
            fg="white"
        )
        title_label.pack(pady=20)
        
        # Khung chứa các level
        levels_container = tk.Frame(self, bg=None)
        levels_container.pack(pady=20, fill="both", expand=True)
        
        # Danh sách thuật toán
        solvers = [
            {"name": "BFS", "color": "#007bff", "hover": "#0069d9", "func": "bfs"},
            {"name": "A*", "color": "#28a745", "hover": "#218838", "func": "astar"},
            {"name": "Greedy", "color": "#fd7e14", "hover": "#e76b00", "func": "greedy"},
            {"name": "Beam", "color": "#6f42c1", "hover": "#5e37a6", "func": "beam"}
        ]
        
        # Tạo grid cho các level
        row, col = 0, 0
        max_cols = 2
        
        for i, level in enumerate(levels):
            level_frame = tk.Frame(levels_container, bg="#111144", bd=2, relief="raised")
            level_frame.grid(row=row, column=col, padx=20, pady=20, sticky="n")
            
            level_title = tk.Label(
                level_frame, 
                text=f"Cấp độ {i+1}", 
                font=("Arial", 14, "bold"), 
                bg="#111144", 
                fg="white"
            )
            level_title.pack(pady=10)
            
            grid = level["grid"]
            boxes = len(level["box_starts"])
            optimal_steps = level.get("optimal_steps", "Chưa tính")
            level_info = tk.Label(
                level_frame, 
                text=f"Kích thước: {len(grid)}x{len(grid[0])}\nSố hộp: {boxes}\nBước tối ưu: {optimal_steps}", 
                font=("Arial", 10), 
                bg="#111144", 
                fg="#aaa"
            )
            level_info.pack(pady=5)
            
            solver_frame = tk.Frame(level_frame, bg="#111144")
            solver_frame.pack(pady=10)
            for solver in solvers:
                solver_btn = CustomButton(
                    solver_frame, 
                    solver["name"], 
                    width=80, 
                    height=30,
                    bg_color=solver["color"], 
                    hover_color=solver["hover"],
                    font=("Arial", 10),
                    command=lambda idx=i, func=solver["func"]: on_select(idx, func)
                )
                solver_btn.pack(side="left", padx=5)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
                
        back_btn = CustomButton(
            self, 
            "Quay Lại", 
            width=150, 
            height=40,
            bg_color="#6c757d", 
            hover_color="#5a6268",
            font=("Arial", 12),
            command=on_back
        )
        back_btn.pack(pady=20)
    
    def load_background(self):
        sprite_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Sokoban_graphics", "sprites"))
        bg_patterns = ["background.[jJ][pP][gG]", "background.[jJ][pP][eE][gG]", 
                       "background.[pP][nN][gG]", "Background.[jJ][pP][gG]", 
                       "Background.[jJ][pP][eE][gG]", "Background.[pP][nN][gG]"]
        for pattern in bg_patterns:
            bg_files = glob.glob(os.path.join(sprite_dir, pattern))
            for bg_path in bg_files:
                try:
                    bg_img = Image.open(bg_path)
                    if bg_img.size[0] <= 0 or bg_img.size[1] <= 0:
                        print(f"Hình ảnh {os.path.basename(bg_path)} không hợp lệ: kích thước không hợp lệ")
                        bg_img.close()
                        continue
                    max_size = (1920, 1080)
                    bg_img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    win_width = self.master.winfo_screenwidth()
                    win_height = self.master.winfo_screenheight()
                    bg_img = bg_img.resize((win_width, win_height), Image.Resampling.LANCZOS)
                    bg_img = bg_img.filter(ImageFilter.GaussianBlur(3))
                    bg_img = ImageEnhance.Brightness(bg_img).enhance(0.7)
                    self.bg_image = ImageTk.PhotoImage(bg_img)
                    self.image_references.append(self.bg_image)
                    self.bg_label = tk.Label(self, image=self.bg_image)
                    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    self.bg_label.lower()
                    print(f"Đã tải background: {bg_path} (Kích thước: {bg_img.size}, Định dạng: {bg_img.format})")
                    bg_img.close()
                    return
                except Exception as e:
                    print(f"Lỗi khi tải {os.path.basename(bg_path)}: {e}")
        print("Không tìm thấy background phù hợp trong thư mục sprites")

class StatusFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="#222")
        self.status_var = tk.StringVar()
        self.status_var.set("Sẵn sàng")
        self.status_label = tk.Label(self, textvariable=self.status_var, 
                                   font=("Arial", 10), bg="#222", fg="white")
        self.status_label.pack(fill="x", padx=10, pady=5)
    
    def set_status(self, text):
        self.status_var.set(text)
        self.update()

class SokobanApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Trò chơi Sokoban")
        
        # Đặt kích thước cửa sổ
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = min(1024, screen_width)
        window_height = min(768, screen_height)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Đặt biểu tượng ứng dụng
        sprite_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Sokoban_graphics", "sprites"))
        self.sprite_dir = sprite_dir
        icon_patterns = ["icon.[pP][nN][gG]", "Icon.[pP][nN][gG]"]
        self.image_references = []
        
        for pattern in icon_patterns:
            icon_files = glob.glob(os.path.join(sprite_dir, pattern))
            for icon_path in icon_files:
                try:
                    icon_img = Image.open(icon_path)
                    if icon_img.size[0] <= 0 or icon_img.size[1] <= 0:
                        print(f"Hình ảnh {os.path.basename(icon_path)} không hợp lệ: kích thước không hợp lệ")
                        icon_img.close()
                        continue
                    icon_img = icon_img.resize((64, 64), Image.Resampling.LANCZOS)
                    icon_photo = ImageTk.PhotoImage(icon_img)
                    self.image_references.append(icon_photo)
                    self.root.iconphoto(True, icon_photo)
                    print(f"Đã tải icon: {icon_path} (Kích thước: {icon_img.size}, Định dạng: {icon_img.format})")
                    icon_img.close()
                    break
                except Exception as e:
                    print(f"Lỗi khi tải {os.path.basename(icon_path)}: {e}")
            else:
                continue
            break
        else:
            print("Không tìm thấy icon phù hợp trong thư mục sprites")
        
        try:
            self.levels = self.create_levels()
            self.current_level = 0
            self.game = SokobanGame(
                self.levels[self.current_level]["grid"],
                self.levels[self.current_level]["player_start"],
                self.levels[self.current_level]["box_starts"],
                self.levels[self.current_level]["targets"]
            )
            
            self.main_frame = tk.Frame(root)
            self.main_frame.pack(fill="both", expand=True)
            
            self.menu_frame = MenuFrame(
                self.main_frame, 
                self.start_game,
                self.show_level_select,
                self.quit_game
            )
            self.menu_frame.pack(fill="both", expand=True)
            
            self.level_select_frame = LevelSelectFrame(
                self.main_frame,
                self.levels,
                self.select_level_and_solver,
                self.back_to_main_menu
            )
            
            self.game_frame = tk.Frame(self.main_frame)
            self.renderer = None
            self.bg_image = None
            self.bg_label = None
            
            # Thanh tải và mèo chạy
            self.progress_bar = None
            self.cat_canvas = None
            self.cat_frames = []
            self.cat_index = 0
            self.cat_id = None
            self.cat_x = 0
            
            self.status_frame = StatusFrame(root)
            self.status_frame.pack(fill="x", side="bottom")
            
            self.ai_mode = None
            self.ai_path = []
            self.ai_step = 0
            
            self.root.bind("<KeyPress>", self.handle_keypress)
        except Exception as e:
            print(f"Lỗi khởi tạo SokobanApp: {e}")
            raise
    
    def load_background(self):
        bg_patterns = ["background.[jJ][pP][gG]", "background.[jJ][pP][eE][gG]", 
                       "background.[pP][nN][gG]", "Background.[jJ][pP][gG]", 
                       "Background.[jJ][pP][eE][gG]", "Background.[pP][nN][gG]"]
        for pattern in bg_patterns:
            bg_files = glob.glob(os.path.join(self.sprite_dir, pattern))
            for bg_path in bg_files:
                try:
                    bg_img = Image.open(bg_path)
                    if bg_img.size[0] <= 0 or bg_img.size[1] <= 0:
                        print(f"Hình ảnh {os.path.basename(bg_path)} không hợp lệ: kích thước không hợp lệ")
                        bg_img.close()
                        continue
                    max_size = (1920, 1080)
                    bg_img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    win_width = self.root.winfo_screenwidth()
                    win_height = self.root.winfo_screenheight()
                    bg_img = bg_img.resize((win_width, win_height), Image.Resampling.LANCZOS)
                    bg_img = bg_img.filter(ImageFilter.GaussianBlur(3))
                    bg_img = ImageEnhance.Brightness(bg_img).enhance(0.7)
                    self.bg_image = ImageTk.PhotoImage(bg_img)
                    self.image_references.append(self.bg_image)
                    self.bg_label = tk.Label(self.game_frame, image=self.bg_image)
                    self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                    self.bg_label.lower()
                    print(f"Đã tải background: {bg_path} (Kích thước: {bg_img.size}, Định dạng: {bg_img.format})")
                    bg_img.close()
                    return
                except Exception as e:
                    print(f"Lỗi khi tải {os.path.basename(bg_path)}: {e}")
        print("Không tìm thấy background phù hợp trong thư mục sprites")
    
    def load_cat_animation(self):
        cat_path = os.path.join(self.sprite_dir, "cat.gif")
        self.cat_frames = []
        try:
            img = Image.open(cat_path)
            if img.size[0] <= 0 or img.size[1] <= 0:
                print(f"Hình ảnh cat.gif không hợp lệ: kích thước không hợp lệ")
                img.close()
                return
            for frame in range(img.n_frames):
                img.seek(frame)
                frame_img = img.copy().resize((50, 50), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(frame_img)
                self.image_references.append(photo)
                self.cat_frames.append(photo)
            print(f"Đã tải cat.gif: {cat_path} ({img.n_frames} khung hình)")
            img.close()
        except Exception as e:
            print(f"Lỗi khi tải cat.gif: {e}")
    
    def start_cat_animation(self):
        if not self.cat_frames or not self.cat_canvas:
            return
        self.cat_index = (self.cat_index + 1) % len(self.cat_frames)
        self.cat_x += 10
        if self.cat_x > 400:
            self.cat_x = -50
        self.cat_canvas.itemconfig(self.cat_id, image=self.cat_frames[self.cat_index])
        self.cat_canvas.coords(self.cat_id, self.cat_x, 25)
        self.root.after(100, self.start_cat_animation)
    
    def stop_cat_animation(self):
        self.cat_index = 0
        self.cat_x = 0
        if self.cat_canvas and self.cat_id:
            self.cat_canvas.delete(self.cat_id)
            self.cat_id = None
    
    def create_levels(self):
        return [
            {
                "grid": [
                    [1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 1],
                    [1, 0, 0, 0, 1],
                    [1, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 2)],
                "targets": [(3, 3)],
                "optimal_steps": 4
            },
            {
                "grid": [
                    [1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 1],
                    [1, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 2), (2, 3)],
                "targets": [(4, 2), (4, 3)],
                "optimal_steps": 8
            },
            {
                "grid": [
                    [1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 1, 1, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 0, 0, 1, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 2), (3, 3)],
                "targets": [(5, 4), (5, 5)],
                "optimal_steps": 12
            },
            {
                "grid": [
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 1, 1, 0, 1, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 1, 0, 1, 1, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 2), (3, 3), (4, 4)],
                "targets": [(5, 5), (5, 6), (4, 5)],
                "optimal_steps": 18
            },
            {
                "grid": [
                    [1, 1, 1, 1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 0, 1, 0, 1, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 1, 1],
                    [1, 0, 1, 0, 1, 0, 0, 1],
                    [1, 0, 0, 0, 0, 0, 0, 1],
                    [1, 1, 1, 1, 1, 1, 1, 1]
                ],
                "player_start": (1, 1),
                "box_starts": [(2, 3), (3, 3), (4, 3)],
                "targets": [(5, 5), (5, 6), (4, 6)],
                "optimal_steps": 22
            }
        ]

    def start_game(self):
        self._hide_all_frames()
        
        try:
            if not self.renderer:
                self.load_background()
                self.renderer = SokobanRenderer(self.game_frame, self.game)
                self.renderer.pack(fill="both", expand=True)
            else:
                self.renderer.game = self.game
        except Exception as e:
            self.status_frame.set_status(f"Lỗi khởi tạo renderer: {e}")
            self.back_to_main_menu()
            return
        
        self.game_frame.pack(fill="both", expand=True)
        self.root.title(f"Sokoban - Cấp độ {self.current_level + 1}")
        self.renderer.draw()
        self.status_frame.set_status(f"Chơi cấp độ {self.current_level + 1}")
        
        if self.ai_mode:
            # Tạo thanh tải
            self.progress_bar = ttk.Progressbar(
                self.game_frame, 
                length=400, 
                mode='determinate', 
                maximum=100
            )
            self.progress_bar.pack(side="bottom", pady=10)
            
            # Tạo canvas cho mèo
            self.cat_canvas = tk.Canvas(self.game_frame, width=400, height=50, bg=None, highlightthickness=0)
            self.cat_canvas.pack(side="bottom")
            self.load_cat_animation()
            if self.cat_frames:
                self.cat_id = self.cat_canvas.create_image(-50, 25, image=self.cat_frames[0], anchor="center")
                self.start_cat_animation()
            
            self.run_solver(self.ai_mode)

    def _hide_all_frames(self):
        for frame in [self.menu_frame, self.level_select_frame, self.game_frame]:
            frame.pack_forget()
        if self.progress_bar:
            self.progress_bar.destroy()
            self.progress_bar = None
        if self.cat_canvas:
            self.stop_cat_animation()
            self.cat_canvas.destroy()
            self.cat_canvas = None

    def show_level_select(self):
        self._hide_all_frames()
        self.level_select_frame.pack(fill="both", expand=True)
        self.status_frame.set_status("Chọn cấp độ và thuật toán")

    def select_level_and_solver(self, level_idx, solver_type):
        self.current_level = level_idx
        self.ai_mode = solver_type
        self.game = SokobanGame(
            self.levels[self.current_level]["grid"],
            self.levels[self.current_level]["player_start"],
            self.levels[self.current_level]["box_starts"],
            self.levels[self.current_level]["targets"]
        )
        self.start_game()

    def back_to_main_menu(self):
        self._hide_all_frames()
        self.menu_frame.pack(fill="both", expand=True)
        self.status_frame.set_status("Sẵn sàng")
        self.ai_mode = None
        self.ai_path = []
        self.ai_step = 0

    def quit_game(self):
        if messagebox.askokcancel("Thoát", "Bạn có muốn thoát trò chơi?"):
            self.root.destroy()

    def handle_keypress(self, event):
        key = event.keysym.lower()
        if key == 'm':
            self.back_to_main_menu()
        elif key == 's':
            save_state(self.game, f"save_level_{self.current_level}.json")
            self.status_frame.set_status("Đã lưu trạng thái")
        elif key == 'l':
            try:
                load_state(self.game, f"save_level_{self.current_level}.json")
                self.status_frame.set_status("Đã tải trạng thái")
                if self.renderer:
                    self.renderer.draw()
            except Exception as e:
                self.status_frame.set_status(f"Lỗi tải trạng thái: {e}")

    def run_solver(self, solver_type):
        self.ai_mode = solver_type
        self.ai_path = []
        self.ai_step = 0

        solver_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Sokoban_algorithms"))
        sys.path.append(solver_path)

        solver_map = {
            'bfs': bfs_solver,
            'astar': a_star_solver,
            'greedy': greedy_solver,
            'beam': beam_search_solver
        }

        solver_func = solver_map.get(solver_type)
        if not solver_func:
            self.status_frame.set_status("Thuật toán không hợp lệ")
            self.stop_cat_animation()
            return

        self.status_frame.set_status(f"Đang chạy {solver_type.upper()}...")
        
        def update_progress(value):
            if self.progress_bar and value <= 100:
                self.progress_bar['value'] = value
                self.root.after(50, update_progress, value + 1)
        
        update_progress(0)
        
        try:
            path = solver_func(self.game)
            self.stop_cat_animation()
            if self.progress_bar:
                self.progress_bar['value'] = 100
            if path:
                self.ai_path = path
                self.status_frame.set_status(f"Đã tìm thấy đường đi với {len(path)} bước")
                self._run_ai_step()
            else:
                self.status_frame.set_status("Không tìm thấy đường đi")
                self.ai_mode = None
        except Exception as e:
            self.stop_cat_animation()
            self.status_frame.set_status(f"Lỗi khi chạy {solver_type.upper()}: {e}")
            self.ai_mode = None

    def _run_ai_step(self):
        if self.ai_step < len(self.ai_path):
            direction = self.ai_path[self.ai_step]
            move(self.game, direction)
            self.renderer.draw()
            self.status_frame.set_status(f"AI bước {self.ai_step + 1}: {direction}")
            self.ai_step += 1

            if has_won(self.game):
                messagebox.showinfo("Thắng", f"AI đã hoàn thành cấp độ {self.current_level + 1}!")
                self.back_to_main_menu()
                return

            self.root.after(500, self._run_ai_step)
        else:
            self.status_frame.set_status("AI hoàn thành")
            self.ai_mode = None