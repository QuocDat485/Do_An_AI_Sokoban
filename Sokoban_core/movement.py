def is_valid_move(x, y, grid):
    # Kiểm tra xem vị trí (x, y) có hợp lệ để di chuyển không
    return 0 <= x < len(grid) and 0 <= y < len(grid[0]) and grid[x][y] != 1

def move(game, direction):
    # Thực hiện di chuyển người chơi hoặc đẩy hộp
    px, py = game.player_pos
    dx, dy = direction
    new_px, new_py = px + dx, py + dy
    new_box_x, new_box_y = new_px + dx, new_py + dy

    if not is_valid_move(new_px, new_py, game.grid):
        return False

    game.history.append(game.copy())

    if (new_px, new_py) in game.box_positions:
        if not is_valid_move(new_box_x, new_box_y, game.grid) or (new_box_x, new_box_y) in game.box_positions:
            game.history.pop()  # Xóa trạng thái đã lưu vì di chuyển không hợp lệ
            return False
        game.box_positions.remove((new_px, new_py))
        game.box_positions.add((new_box_x, new_box_y))
        game.player_pos = (new_px, new_py)
        return True

    game.player_pos = (new_px, new_py)
    return True

def undo(game):
    # Hoàn tác di chuyển trước đó
    if game.history:
        prev_state = game.history.pop()
        game.grid = prev_state.grid
        game.player_pos = prev_state.player_pos
        game.box_positions = prev_state.box_positions
        game.targets = prev_state.targets
        return True
    return False