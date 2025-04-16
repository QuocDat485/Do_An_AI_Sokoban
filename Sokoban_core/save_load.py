# Nhập các thư viện cần thiết
import json

def save_state(game, filename="game_save.json"):
    # Lưu trạng thái trò chơi vào tệp JSON
    state = {
        "grid": game.grid,
        "player_pos": game.player_pos,
        "box_positions": list(game.box_positions),
        "targets": list(game.targets)
    }
    with open(filename, "w") as f:
        json.dump(state, f)
    return True

def load_state(game, filename="game_save.json"):
    # Tải trạng thái trò chơi từ tệp JSON
    try:
        with open(filename, "r") as f:
            state = json.load(f)
            game.grid = state["grid"]
            game.player_pos = tuple(state["player_pos"])
            game.box_positions = set(tuple(pos) for pos in state["box_positions"])
            game.targets = set(tuple(pos) for pos in state["targets"])
        return True
    except (FileNotFoundError, json.JSONDecodeError):
        return False