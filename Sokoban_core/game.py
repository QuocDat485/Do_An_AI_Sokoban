# Nh?p c�c th? vi?n c?n thi?t
import copy

class SokobanGame:
    def __init__(self, grid, player_pos, box_positions, targets):
        # Kh?i t?o l??i tr� ch?i
        self.grid = [row[:] for row in grid]
        # V? tr� ng??i ch?i
        self.player_pos = player_pos
        # T?p h?p c�c v? tr� c?a h?p
        self.box_positions = set(tuple(pos) for pos in box_positions)
        # T?p h?p c�c v? tr� m?c ti�u
        self.targets = set(tuple(pos) for pos in targets)
        # L?ch s? c�c tr?ng th�i ?? h? tr? undo
        self.history = []
        
    def copy(self):
        # T?o m?t b?n sao c?a tr?ng th�i tr� ch?i hi?n t?i
        return SokobanGame(self.grid, self.player_pos, self.box_positions, self.targets)