import tkinter as tk
import copy
import time

class MancalaGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Mancala Game")
        self.root.geometry("800x400")

        self.play_again_menu = None

        self.new_game()

    def new_game(self):
        if self.play_again_menu is not None:
            self.play_again_menu.destroy()

        self.game = MancalaGame()
        self.buttons = []

        player_frame = tk.Frame(self.root)
        player_frame.pack(pady=20)

        for i in range(6, -1, -1):  # Counterclockwise direction for the player
            button = tk.Button(player_frame, text=str(self.game.board[i]), font=("Arial", 20),
                               command=lambda i=i: self.make_move(i))
            button.grid(row=0, column=6 - i, padx=10)
            self.buttons.append(button)

        ai_frame = tk.Frame(self.root)
        ai_frame.pack(pady=20)

        for i in range(7, 14):
            button = tk.Button(ai_frame, text=str(self.game.board[i]), font=("Arial", 20),
                               command=lambda i=i: self.make_move(i))
            button.grid(row=0, column=i - 7, padx=10)
            self.buttons.append(button)

        self.player_mancala_label = tk.Label(self.root, text=f"Player's Mancala: {self.game.board[6]}",
                                             font=("Arial", 18), bg="blue")
        self.player_mancala_label.pack()

        self.ai_mancala_label = tk.Label(self.root, text=f"AI's Mancala: {self.game.board[13]}", font=("Arial", 18),
                                         bg="red")
        self.ai_mancala_label.pack()

        self.turn_label = tk.Label(self.root, text="Player's Turn!", font=("Arial", 24))
        self.turn_label.pack(pady=20)

    def make_move(self, move):
        if not self.game.is_game_over():
            if self.game.make_move(move):
                self.update_buttons()
                self.update_mancala_labels()

                if self.game.is_game_over():
                    self.end_game()
                else:
                    if self.game.current_player == 2:
                        self.turn_label.config(text="AI's Turn!")
                        self.root.update()  # Force GUI update
                        time.sleep(3)  # Wait for 3 seconds before AI's turn
                        self.ai_play()
                    else:
                        self.turn_label.config(text="Player's Turn!")

    def ai_play(self):
        move = self.game.find_best_move()
        if not self.game.is_game_over():
            if self.game.make_move(move):
                self.update_buttons()
                self.update_mancala_labels()

                if self.game.is_game_over():
                    self.end_game()
                else:
                    self.turn_label.config(text="Player's Turn!")

    def end_game(self):
        player_score = self.game.board[0]
        ai_score = self.game.board[7]
        if player_score > ai_score:
            result = "Player wins!"
        elif player_score < ai_score:
            result = "AI wins!"
        else:
            result = "It's a tie!"

        self.play_again_menu = tk.Toplevel(self.root)
        play_again_label = tk.Label(self.play_again_menu, text=f"Game Over\n{result}\n\nPlay again?", font=("Arial", 18))
        play_again_label.pack()
        play_again_button = tk.Button(self.play_again_menu, text="Yes", command=self.new_game)
        play_again_button.pack()
        quit_button = tk.Button(self.play_again_menu, text="Quit", command=self.root.destroy)
        quit_button.pack()

    def update_buttons(self):
        for i, button in enumerate(self.buttons):
            button.config(text=str(self.game.board[i]))

    def update_mancala_labels(self):
        self.player_mancala_label.config(text=f"Player's Mancala: {self.game.board[6]}")
        self.ai_mancala_label.config(text=f"AI's Mancala: {self.game.board[13]}")


class MancalaGame:
    def __init__(self):
        self.board = [4, 4, 4, 4, 4, 4, 0, 4, 4, 4, 4, 4, 4, 0]
        self.current_player = 1

    def is_game_over(self):
        return all(x == 0 for x in self.board[0:6]) or all(x == 0 for x in self.board[7:13])

    def make_move(self, move):
        if self.current_player == 1:
            if move not in range(6):
                return False
            if self.board[move] == 0:
                return False
        elif self.current_player == 2:
            if move not in range(7, 13):
                return False
            if self.board[move] == 0:
                return False

        num_stones = self.board[move]
        self.board[move] = 0

        current_pocket = move
        while num_stones > 0:
            current_pocket = (current_pocket + 1) % 14
            if current_pocket == 0 and self.current_player == 1:
                current_pocket = (current_pocket + 1) % 14
            elif current_pocket == 7 and self.current_player == 2:
                current_pocket = (current_pocket + 1) % 14

            self.board[current_pocket] += 1
            num_stones -= 1

        if current_pocket != 0 and self.board[current_pocket] == 1 and self.board[14 - current_pocket] > 0:
            if self.current_player == 1 and current_pocket in range(1, 7):
                self.board[0] += self.board[current_pocket] + self.board[14 - current_pocket]
                self.board[current_pocket] = 0
                self.board[14 - current_pocket] = 0
            elif self.current_player == 2 and current_pocket in range(8, 14):
                self.board[7] += self.board[current_pocket] + self.board[14 - current_pocket]
                self.board[current_pocket] = 0
                self.board[14 - current_pocket] = 0

        if current_pocket == 0 and self.current_player == 1:
            return True
        elif current_pocket == 7 and self.current_player == 2:
            return True

        self.switch_player()
        return True

    def switch_player(self):
        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1

    def get_possible_moves(self):
        if self.current_player == 1:
            return [i for i in range(1, 7) if self.board[i] > 0]
        else:
            return [i for i in range(8, 14) if self.board[i] > 0]

    def evaluate(self):
        return self.board[0] - self.board[7]

    def find_best_move(self):
        best_move = -1
        best_eval = float('-inf')
        alpha = float('-inf')
        beta = float('inf')

        for move in self.get_possible_moves():
            board_copy = copy.deepcopy(self)
            if board_copy.make_move(move):
                eval = board_copy.minimax(3, False, alpha, beta)  # Adjust depth as needed
                if eval > best_eval:
                    best_eval = eval
                    best_move = move
                alpha = max(alpha, eval)

        return best_move

    def minimax(self, depth, max_player, alpha, beta):
        if depth == 0 or self.is_game_over():
            return self.evaluate()

        if max_player:
            max_eval = float('-inf')
            for move in self.get_possible_moves():
                board_copy = copy.deepcopy(self)
                if board_copy.make_move(move):
                    eval = board_copy.minimax(depth - 1, False, alpha, beta)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for move in self.get_possible_moves():
                board_copy = copy.deepcopy(self)
                if board_copy.make_move(move):
                    eval = board_copy.minimax(depth - 1, True, alpha, beta)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval


if __name__ == "__main__":
    root = tk.Tk()
    game = MancalaGUI(root)
    root.mainloop()
