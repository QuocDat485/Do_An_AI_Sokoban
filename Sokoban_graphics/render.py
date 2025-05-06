# Nhập các thư viện cần thiết
import tkinter as tk
import os
from PIL import Image, ImageTk

class SokobanRenderer(tk.Canvas):
    def __init__(self, master, game, tile_size=50):
        # Khởi tạo renderer với trò chơi và kích thước ô
        self.game = game
        self.tile_size = tile_size
        self.width = len(game.grid[0]) * tile_size
        self.height = len(game.grid) * tile_size
        
        super().__init__(master, width=self.width, height=self.height, bg="black")
        
        # Định nghĩa màu sắc dự phòng khi không có hình ảnh
        self.colors = {
            "wall": "#646464",        # Xám
            "empty": "#C8C8C8",       # Xám nhạt
            "target": "#00C800",      # Xanh lá
            "player": "#0000C8",      # Xanh dương
            "box": "#964B00",         # Nâu
            "box_on_target": "#006400" # Xanh lá đậm
        }
        
        # Từ điển chứa hình ảnh
        self.images = {}
        self.load_images()
    
    def load_images(self):
        """Tải hình ảnh từ thư mục sprites, sử dụng hình dạng màu nếu không tìm thấy"""
        # Danh sách các thư mục sprites có thể có
        sprite_dirs = [
            "sprites",
            os.path.join("Sokoban_graphics", "sprites"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "sprites"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sprites"),
            os.path.join(os.getcwd(), "sprites")
        ]
        
        # Tên tệp hình ảnh
        image_files = {
            "wall": "wall.png",
            "empty": "empty.png",
            "target": "target.png",
            "player": "player.png",
            "box": "box.png",
            "box_on_target": "box_on_target.png"
        }
        
        # Tạo thư mục sprite nếu chưa tồn tại
        sprites_dir = os.path.join(os.getcwd(), "sprites")
        if not os.path.exists(sprites_dir):
            os.makedirs(sprites_dir)
            print(f"Đã tạo thư mục sprites: {sprites_dir}")
        
        # Thử tìm và tải từng hình ảnh
        for sprite_dir in sprite_dirs:
            if os.path.exists(sprite_dir):
                print(f"Tìm thấy thư mục sprite: {sprite_dir}")
                for key, filename in image_files.items():
                    try:
                        img_path = os.path.join(sprite_dir, filename)
                        if os.path.exists(img_path):
                            # Tải hình ảnh bằng PIL, thay đổi kích thước để phù hợp với ô
                            img = Image.open(img_path)
                            if img.size[0] <= 0 or img.size[1] <= 0:
                                print(f"Hình ảnh {filename} không hợp lệ: kích thước không hợp lệ")
                                continue
                            img = img.resize((self.tile_size, self.tile_size), Image.Resampling.LANCZOS)
                            self.images[key] = ImageTk.PhotoImage(img)
                            print(f"Đã tải hình ảnh: {img_path}")
                    except Exception as e:
                        print(f"Lỗi khi tải hình ảnh {filename} từ {img_path}: {e}")
                
                # Nếu tìm thấy tất cả hình ảnh cần thiết, ngừng tìm kiếm
                if len(self.images) == len(image_files):
                    break
        
        # Nếu không tìm thấy tất cả hình ảnh, thông báo người dùng
        missing_images = [key for key in image_files if key not in self.images]
        if missing_images:
            print(f"Không tìm thấy các hình ảnh: {', '.join(missing_images)}. Sử dụng hình dạng màu làm dự phòng.")
            print(f"Vui lòng đặt các hình ảnh PNG ({', '.join(image_files.values())}) vào thư mục {sprites_dir}.")
    
    def draw(self):
        # Xóa canvas
        self.delete("all")
        
        # Vẽ lưới trò chơi
        for x in range(len(self.game.grid)):
            for y in range(len(self.game.grid[0])):
                # Tính toán vị trí trên màn hình
                x1 = y * self.tile_size
                y1 = x * self.tile_size
                x2 = x1 + self.tile_size
                y2 = y1 + self.tile_size
                
                # Vẽ phần tử phù hợp dựa trên trạng thái trò chơi
                if self.game.grid[x][y] == 1:  # Tường
                    if "wall" in self.images:
                        self.create_image(x1 + self.tile_size//2, y1 + self.tile_size//2, 
                                         image=self.images["wall"])
                    else:
                        self.create_rectangle(x1, y1, x2, y2, fill=self.colors["wall"], outline="")
                else:  # Sàn
                    if "empty" in self.images:
                        self.create_image(x1 + self.tile_size//2, y1 + self.tile_size//2, 
                                         image=self.images["empty"])
                    else:
                        self.create_rectangle(x1, y1, x2, y2, fill=self.colors["empty"], outline="")
                    
                    # Vẽ mục tiêu nếu có
                    if (x, y) in self.game.targets:
                        if "target" in self.images:
                            self.create_image(x1 + self.tile_size//2, y1 + self.tile_size//2, 
                                             image=self.images["target"])
                        else:
                            self.create_oval(x1+5, y1+5, x2-5, y2-5, fill=self.colors["target"], outline="")
                    
                    # Vẽ hộp nếu có
                    if (x, y) in self.game.box_positions:
                        if (x, y) in self.game.targets:
                            if "box_on_target" in self.images:
                                self.create_image(x1 + self.tile_size//2, y1 + self.tile_size//2, 
                                                 image=self.images["box_on_target"])
                            else:
                                self.create_rectangle(x1+5, y1+5, x2-5, y2-5, fill=self.colors["box_on_target"], 
                                                    outline="black", width=2)
                        else:
                            if "box" in self.images:
                                self.create_image(x1 + self.tile_size//2, y1 + self.tile_size//2, 
                                                 image=self.images["box"])
                            else:
                                self.create_rectangle(x1+5, y1+5, x2-5, y2-5, fill=self.colors["box"], 
                                                    outline="black", width=2)
                    
                    # Vẽ người chơi nếu có
                    if (x, y) == self.game.player_pos:
                        if "player" in self.images:
                            self.create_image(x1 + self.tile_size//2, y1 + self.tile_size//2, 
                                             image=self.images["player"])
                        else:
                            self.create_oval(x1+10, y1+10, x2-10, y2-10, fill=self.colors["player"], 
                                           outline="black", width=2)
        
        self.update()