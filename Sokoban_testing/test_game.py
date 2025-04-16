# Nhập các thư viện cần thiết
import unittest
from Sokoban_core.game import SokobanGame
from Sokoban_core.movement import move, undo
from Sokoban_core.check_win import has_won
from Sokoban_algorithms.solver import bfs_solver, a_star_solver

class TestSokoban(unittest.TestCase):
    def setUp(self):
        # Thiết lập cấp độ đơn giản để kiểm tra
        self.grid = [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ]
        self.player_pos = (1, 1)
        self.box_positions = [(2, 2)]
        self.targets = [(3, 3)]
        self.game = SokobanGame(self.grid, self.player_pos, self.box_positions, self.targets)

    def test_move_player(self):
        # Kiểm tra di chuyển người chơi đến không gian trống
        result = move(self.game, (0, 1))  # Di chuyển sang phải
        self.assertTrue(result)
        self.assertEqual(self.game.player_pos, (1, 2))

    def test_move_box(self):
        # Di chuyển người chơi đến hộp và đẩy nó
        self.game.player_pos = (2, 1)
        result = move(self.game, (0, 1))  # Di chuyển sang phải để đẩy hộp
        self.assertTrue(result)
        self.assertEqual(self.game.player_pos, (2, 2))
        self.assertIn((2, 3), self.game.box_positions)

    def test_invalid_move_wall(self):
        # Thử di chuyển vào tường
        result = move(self.game, (-1, 0))  # Di chuyển lên vào tường
        self.assertFalse(result)
        self.assertEqual(self.game.player_pos, (1, 1))

    def test_undo(self):
        # Thực hiện di chuyển và hoàn tác
        move(self.game, (0, 1))  # Di chuyển sang phải
        self.assertEqual(self.game.player_pos, (1, 2))
        undo(self.game)
        self.assertEqual(self.game.player_pos, (1, 1))

    def test_has_won(self):
        # Đặt hộp lên mục tiêu
        self.game.box_positions = {(3, 3)}
        self.assertTrue(has_won(self.game))
        
        # Di chuyển hộp ra khỏi mục tiêu
        self.game.box_positions = {(2, 2)}
        self.assertFalse(has_won(self.game))

    def test_bfs_solver(self):
        # Kiểm tra solver BFS trên cấp độ đơn giản
        path = bfs_solver(self.game)
        self.assertIsNotNone(path)
        self.assertTrue(isinstance(path, list))

    def test_a_star_solver(self):
        # Kiểm tra solver A* trên cấp độ đơn giản
        path = a_star_solver(self.game)
        self.assertIsNotNone(path)
        self.assertTrue(isinstance(path, list))

if __name__ == '__main__':
    unittest.main()