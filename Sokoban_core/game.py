# Nhập các thư viện cần thiết
import copy

class SokobanGame:
    def __init__(self, grid, player_pos, box_positions, targets):
        # Khởi tạo lưới trò chơi
        self.grid = [row[:] for row in grid]
        # Vị trí người chơi
        self.player_pos = player_pos
        # Tập hợp các vị trí của hộp
        self.box_positions = set(tuple(pos) for pos in box_positions)
        # Tập hợp các vị trí mục tiêu
        self.targets = set(tuple(pos) for pos in targets)
        # Lịch sử các trạng thái hỗ trợ undo
        self.history = []
        
    def copy(self):
        # Tạo một bản sao của trạng thái trò chơi hiện tại
        return copy.deepcopy(self)