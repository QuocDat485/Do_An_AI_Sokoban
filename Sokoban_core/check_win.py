def has_won(game):
    # Kiểm tra xem tất cả các hộp đã ở trên mục tiêu chưa
    return all(pos in game.targets for pos in game.box_positions)