# Nh?p các th? vi?n c?n thi?t
import copy

class SokobanGame:
    def __init__(self, grid, player_pos, box_positions, targets):
        # Kh?i t?o l??i trò ch?i
        self.grid = [row[:] for row in grid]
        # V? trí ng??i ch?i
        self.player_pos = player_pos
        # T?p h?p các v? trí c?a h?p
        self.box_positions = set(tuple(pos) for pos in box_positions)
        # T?p h?p các v? trí m?c tiêu
        self.targets = set(tuple(pos) for pos in targets)
        # L?ch s? các tr?ng thái ?? h? tr? undo
        self.history = []
        
    def copy(self):
        # T?o m?t b?n sao c?a tr?ng thái trò ch?i hi?n t?i
        return SokobanGame(self.grid, self.player_pos, self.box_positions, self.targets)