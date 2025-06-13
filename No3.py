import tkinter as tk
import random
import time

CELL_SIZE = 30
COLS = 10
ROWS = 20
DELAY = 500  # ms
TIME_LIMIT = 300  # 秒（5分）
GOAL_SCORE = 10000

TETROMINOS = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]],
}

COLORS = {
    'I': 'cyan', 'O': 'yellow', 'T': 'purple',
    'S': 'green', 'Z': 'red', 'J': 'blue', 'L': 'orange'
}


class Tetris:
    def __init__(self, root):
        self.root = root
        self.root.title("Tetris")
        self.canvas = tk.Canvas(root, width=COLS * CELL_SIZE + 150, height=ROWS * CELL_SIZE, bg='black')
        self.canvas.pack()

        self.start_button = tk.Button(root, text="Start Game", font=("Helvetica", 16), command=self.start_game)
        self.start_button.place(x=COLS * CELL_SIZE + 25, y=ROWS * CELL_SIZE // 2)

        self.restart_button = None
        self.running = False
        
        self.init_game()
        self.root.bind("<Key>", self.key_pressed)

    def start_game(self):
        self.start_button.destroy()
        self.running = True
        self.init_game()

    def init_game(self):
        self.board = [[None for _ in range(COLS)] for _ in range(ROWS)]
        self.score = 0
        self.start_time = time.time()
        self.game_over_flag = False
        self.game_clear_flag = False
        self.spawn_block()
        self.draw_board()
        self.schedule_game_loop()

    def schedule_game_loop(self):
        self.root.after(DELAY, self.game_loop)

    def spawn_block(self):
        self.block_type = random.choice(list(TETROMINOS.keys()))
        self.block = TETROMINOS[self.block_type]
        self.color = COLORS[self.block_type]
        self.block_row = 0
        self.block_col = COLS // 2 - len(self.block[0]) // 2
        if self.check_collision():
            self.game_over_flag = True

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1 = c * CELL_SIZE
                y1 = r * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="#333333")  # 薄い線
                color = self.board[r][c]
                if color:
                    self.draw_cell(r, c, color)
        for r, row in enumerate(self.block):
            for c, val in enumerate(row):
                if val:
                    self.draw_cell(self.block_row + r, self.block_col + c, self.color)

        self.draw_score_and_time()

     # ゲームフィールドの外枠を描画
        x1 = 0
        y1 = 0
        x2 = COLS * CELL_SIZE
        y2 = ROWS * CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=2)

        if self.game_over_flag:
            self.canvas.create_text(COLS * CELL_SIZE // 2, ROWS * CELL_SIZE // 2,
                                    text="GAME OVER", fill="white", font=("Helvetica", 24))
            self.show_restart_button()

        elif self.game_clear_flag:
            self.canvas.create_text(COLS * CELL_SIZE // 2, ROWS * CELL_SIZE // 2,
                                    text="YOU WIN!", fill="lightgreen", font=("Helvetica", 24))
            self.show_restart_button()

    def draw_score_and_time(self):
        self.canvas.create_text(COLS * CELL_SIZE + 75, 30, text="SCORE", fill="white", font=("Helvetica", 16))
        self.canvas.create_text(COLS * CELL_SIZE + 75, 60, text=str(self.score), fill="white", font=("Helvetica", 20))

        elapsed = int(time.time() - self.start_time)
        remaining = max(0, TIME_LIMIT - elapsed)
        minutes = remaining // 60
        seconds = remaining % 60
        self.canvas.create_text(COLS * CELL_SIZE + 75, 110, text="TIME", fill="white", font=("Helvetica", 16))
        self.canvas.create_text(COLS * CELL_SIZE + 75, 140,
                                text=f"{minutes:02}:{seconds:02}", fill="white", font=("Helvetica", 20))

        if remaining <= 0:
            self.game_over_flag = True

        if self.score >= GOAL_SCORE:
            self.game_clear_flag = True

    def draw_cell(self, row, col, color):
        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="gray")

    def game_loop(self):
        if not self.running:
            return
        if not self.game_over_flag and not self.game_clear_flag:
            if not self.move_block(1, 0):
                self.lock_block()
                self.draw_board()
                #追加
                self.root.update()
                time.sleep(0.1)
                self.clear_lines()
                
                self.spawn_block()
        self.draw_board()
        if not self.game_over_flag and not self.game_clear_flag:
            self.schedule_game_loop()

    def move_block(self, dr, dc):
        self.block_row += dr
        self.block_col += dc
        if self.check_collision():
            self.block_row -= dr
            self.block_col -= dc
            return False
        return True

    def check_collision(self):
        for r, row in enumerate(self.block):
            for c, val in enumerate(row):
                if val:
                    nr = self.block_row + r
                    nc = self.block_col + c
                    if nr >= ROWS or nc < 0 or nc >= COLS or (nr >= 0 and self.board[nr][nc]):
                        return True
        return False

    def lock_block(self):
        for r, row in enumerate(self.block):
            for c, val in enumerate(row):
                if val:
                    self.board[self.block_row + r][self.block_col + c] = self.color

    def clear_lines(self):
        lines_cleared = 0
        new_board = []
        for row in self.board:
            if all(row):
                lines_cleared += 1
            else:
                new_board.append(row)
        while len(new_board) < ROWS:
            new_board.insert(0, [None for _ in range(COLS)])
        self.board = new_board
        self.score += lines_cleared * 100

    def rotate_block(self):
        rotated = list(zip(*self.block[::-1]))
        original = self.block
        self.block = [list(row) for row in rotated]
        if self.check_collision():
            self.block = original

    def key_pressed(self, event):
        if self.game_over_flag or self.game_clear_flag:
            return
        if event.keysym == 'Left':
            self.move_block(0, -1)
        elif event.keysym == 'Right':
            self.move_block(0, 1)
        elif event.keysym == 'Down':
            self.move_block(1, 0)
        elif event.keysym == 'Up':
            self.rotate_block()
        self.draw_board()

    def show_restart_button(self):
        if not self.restart_button:
            self.restart_button = tk.Button(self.root, text="Restart", font=("Helvetica", 14), command=self.restart_game)
            self.restart_button.place(x=COLS * CELL_SIZE + 25, y=ROWS * CELL_SIZE // 2 + 50)

    def restart_game(self):
        if self.restart_button:
            self.restart_button.destroy()
            self.restart_button = None
            self.running = True
        self.init_game()


if __name__ == "__main__":
    root = tk.Tk()
    game = Tetris(root)
    root.mainloop()
