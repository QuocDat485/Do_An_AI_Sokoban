# Nhập các thư viện cần thiết
from collections import deque
import heapq
from Sokoban_core.movement import move
from Sokoban_core.check_win import has_won
from Sokoban_core.game import SokobanGame

def manhattan_distance(pos1, pos2):
    # Tính khoảng cách Manhattan giữa hai điểm
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])

def heuristic(box_positions, targets):
    # Hàm heuristic cho A*: tính tổng khoảng cách Manhattan tối thiểu
    total_cost = 0
    remaining_targets = list(targets)
    for box in box_positions:
        distances = [manhattan_distance(box, target) for target in remaining_targets]
        if distances:
            min_dist = min(distances)
            total_cost += min_dist
            closest_target_idx = distances.index(min_dist)
            remaining_targets.pop(closest_target_idx)
    return total_cost

def generate_next_states(game):
    # Tạo các trạng thái tiếp theo có thể từ trạng thái hiện tại
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    next_states = []
    for dx, dy in directions:
        new_game = game.copy()
        if move(new_game, (dx, dy)):
            next_states.append((new_game, (dx, dy)))
    return next_states

def bfs_solver(game, status_callback=None):
    # Thuật toán BFS để tìm đường đi giải trò chơi
    queue = deque([(game.copy(), [])])
    visited = {(game.player_pos, tuple(sorted(game.box_positions)))}
    
    max_iterations = 10000
    iterations = 0
    
    while queue and iterations < max_iterations:
        iterations += 1
        if iterations % 1000 == 0 and status_callback:
            status_callback(f"BFS iterations: {iterations}")
            
        current_game, path = queue.popleft()
        if has_won(current_game):
            if status_callback:
                status_callback(f"Tìm thấy lời giải sau {iterations} lần lặp với {len(path)} bước")
            return path

        for next_game, direction in generate_next_states(current_game):
            state_tuple = (next_game.player_pos, tuple(sorted(next_game.box_positions)))
            if state_tuple not in visited:
                visited.add(state_tuple)
                queue.append((next_game, path + [direction]))
    
    if status_callback:
        status_callback(f"Không tìm thấy lời giải sau {iterations} lần lặp")
    return None

def a_star_solver(game, status_callback=None):
    # Thuật toán A* để tìm đường đi giải trò chơi
    queue = [(0, 0, game.copy(), [])]
    visited = set()
    
    max_iterations = 10000
    iterations = 0
    
    while queue and iterations < max_iterations:
        iterations += 1
        if iterations % 1000 == 0 and status_callback:
            status_callback(f"A* iterations: {iterations}")
            
        f_score, g_score, current_game, path = heapq.heappop(queue)
        state_tuple = (current_game.player_pos, tuple(sorted(current_game.box_positions)))

        if state_tuple in visited:
            continue
        visited.add(state_tuple)

        if has_won(current_game):
            if status_callback:
                status_callback(f"Tìm thấy lời giải sau {iterations} lần lặp với {len(path)} bước")
            return path

        for next_game, direction in generate_next_states(current_game):
            next_state_tuple = (next_game.player_pos, tuple(sorted(next_game.box_positions)))
            if next_state_tuple not in visited:
                new_g_score = g_score + 1
                new_h_score = heuristic(next_game.box_positions, next_game.targets)
                new_f_score = new_g_score + new_h_score
                heapq.heappush(queue, (new_f_score, new_g_score, next_game, path + [direction]))
    
    if status_callback:
        status_callback(f"Không tìm thấy lời giải sau {iterations} lần lặp")
    return None