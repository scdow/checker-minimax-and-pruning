import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk, Image
from chess import Pieces, Locations

def set_depth_limit(value):
    global depth_set
    depth_set = value
    window2.destroy()
    return depth_set

# create difficult level setting window
def difficulty_window():
    global window2
    window2 = tk.Tk()
    window2.title('Difficult Level Setting')
    window2.geometry("320x260")
    window2['padx'] = 20
    window2['pady'] = 20

    option1 = tk.Button(window2, text="Easy", command=lambda: set_depth_limit(4))
    option1.pack(pady=10)

    option2 = tk.Button(window2, text="Normal", command=lambda: set_depth_limit(5))
    option2.pack(pady=10)

    option3 = tk.Button(window2, text="Difficult", command=lambda: set_depth_limit(6))
    option3.pack(pady=10)

    window2.mainloop()
    return depth_set

# add game rule menu
def show_game_rules():
    rules = """Checker rules：
    Checker is played on an 8x8 checkered board. Each player has 12 pieces and takes turns moving diagonally forward. Regular moves involve moving one square diagonally, while capture moves involve jumping over an opponent's piece to remove it from the board. Forced capture rule requires players to make any available capture moves, as capturing is mandatory. If multiple capture options are available, players must choose the move that captures the maximum number of pieces. When a piece reaches the last row of the opponent's side, it becomes a King and gains the ability to move backward as well. The objective is to capture or block all of the opponent's pieces. The game ends when one player achieves this goal or when a stalemate occurs.
    """
    messagebox.showinfo("Checker rules", rules)

def create_menu(window):
    menu_bar = tk.Menu(window)
    # create game menu
    game_menu = tk.Menu(menu_bar, tearoff=0)
    game_menu.add_command(label="show rules", command=show_game_rules)
    menu_bar.add_cascade(label="Game Rules", menu=game_menu)
    # add menu to window
    window.config(menu=menu_bar)


class Game:
    
    def __init__(self) :
        super().__init__()
        self.game = Pieces(CHECKER_SIZE)
        self.history = [self.game.getBoard()]
        self.historyPtr = 0   # numbers of totally human player operation
        self.depthLimit = DEPTH_LIMIT
        self.player = STARTING_PLAYER
        self.playerTurn = True

        self.lastX = None
        self.lastY = None
        self.willCapture = False
        self.cnt = 0
        self.btn = [[None]*self.game.size for _ in range(self.game.size)]

        # Create turn frame
        turn_frame = tk.Frame(master=window)
        turn_frame.pack(expand=True)
        self.turn_state = tk.Label(master=turn_frame)
        self.turn_state.pack()

        # Create board frame
        board_frame = tk.Frame(master=window)
        board_frame.pack(fill=tk.BOTH, expand=True)
        for i in range(self.game.size):
            board_frame.columnconfigure(i, weight=1, minsize=SQUARE_SIZE)
            board_frame.rowconfigure(i, weight=1, minsize=SQUARE_SIZE)

            for j in range(self.game.size):
                frame = tk.Frame(master=board_frame)
                frame.grid(row=i, column=j, sticky="nsew")

                self.btn[i][j] = tk.Button(master=frame, width=SQUARE_SIZE, height=SQUARE_SIZE, relief=tk.FLAT)
                self.btn[i][j].bind("<Button-1>", self.click)
                self.btn[i][j].pack(expand=True, fill=tk.BOTH)

        # Create counter frame
        counter_frame = tk.Frame(master=window)
        counter_frame.pack(expand=True)
        self.nocapture_counter = tk.Label(master=counter_frame)
        self.nocapture_counter.pack()

        self.update()
        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        self.highlight_hints(nextPositions)
        window.mainloop()

    def update(self):
        for i in range(self.game.size):
            is_odd_row = i % 2 == 1
            for j in range(self.game.size):
                # Set background color of the button based on the row index
                if is_odd_row:
                    self.btn[i][j]['bg'] = 'mediumaquamarine'
                else:
                    self.btn[i][j]['bg'] = 'white'

                # Set the image of the button based on the piece type on the board
                img = no_piece
                piece = self.game.board[i][j]
                if piece == Pieces.BLACK_NORMAL:
                    img = b_norm_peice
                elif piece == Pieces.BLACK_KING:
                    img = b_king_peice
                elif piece == Pieces.WHITE_NORMAL:
                    img = w_norm_peice
                elif piece == Pieces.WHITE_KING:
                    img = w_king_peice

                self.btn[i][j]["image"] = img

                is_odd_row = not is_odd_row

        # Update the turn state label based on the player's turn
        if self.playerTurn:
            self.turn_state['text'] = 'Your turn'
        else:
            self.turn_state['text'] = 'AI thinking...'

        self.playerTurn = not self.playerTurn

        # Update the no capture moves counter label
        self.nocapture_counter['text'] = f'No capture moves: {self.cnt}'

        # Update the window to reflect the changes
        window.update()


    def highlight_hints(self, positions: Locations):
        # Reset the highlight_hints of all buttons to the default background color
        for x in range(self.game.size):
            for y in range(self.game.size):
                default_bg = self.btn[x][y].cget('bg')
                self.btn[x][y].master.config(highlightbackground=default_bg, highlightthickness=3)

        # highlight_hints the buttons at the specified positions with a different background color
        for position in positions:
            x, y = position
            self.btn[x][y].master.config(highlightbackground="darkorange", highlightthickness=3)


    def click(self, event):
        # Retrieve the clicked button's position on the grid
        info = event.widget.master.grid_info()
        x, y = info["row"], info["column"]

        # If it's the first click in a move sequence
        if self.lastX == None or self.lastY == None:
            # Check if the clicked position is a valid move for the current player
            moves = self.game.nextMoves(self.player)
            found = (x, y) in [move[0] for move in moves]
            if found:
                self.lastX = x
                self.lastY = y
                normal, capture = self.game.nextPositions(x, y)
                positions = normal if len(capture) == 0 else capture
                self.highlight_hints(positions)
            else:
                print("Inavailable position")
            return

        # It's the second click, check if it's a valid move
        normalPositions, capturePositions = self.game.nextPositions(self.lastX, self.lastY)
        positions = normalPositions if (len(capturePositions) == 0) else capturePositions
        if (x,y) not in positions:
            print("Inavailable move")
            if not self.willCapture:
                self.lastX = None
                self.lastY = None
                nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
                self.highlight_hints(nextPositions)
            return

        # Perform the move
        canCapture, removed, _ = self.game.playMove(self.lastX, self.lastY, x, y)
        self.highlight_hints([])
        self.update()
        self.cnt += 1
        self.lastX = None
        self.lastY = None
        self.willCapture = False

        if removed != 0:
            self.cnt = 0
        if canCapture:
            _, nextCaptures = self.game.nextPositions(x, y)
            if len(nextCaptures) != 0:
                self.willCapture = True
                self.lastX = x
                self.lastY = y
                self.highlight_hints(nextCaptures)
                return

        cont, reset = True, False

        """Use minimax with alpha-beta pruning for the AI player's turn"""
        evaluate = EVALUATION_FUNCTION
        cont, reset = self.game.minimax_play(1 - self.player, depthLimit=self.depthLimit, evaluate=evaluate)

        self.cnt += 1
        if not cont:
            messagebox.showinfo(message="You Win!", title="Pieces")
            window.destroy()
            return
        self.update()
        if reset:
            self.cnt = 0

        if self.cnt >= 40:
            messagebox.showinfo(message="Draw!", title="Pieces")
            window.destroy()
            return
        
        nextPositions = [move[0] for move in self.game.nextMoves(self.player)]
        self.highlight_hints(nextPositions)
        if len(nextPositions) == 0:
            messagebox.showinfo(message="You lose!", title="Pieces")
            window.destroy()

        self.history = self.history[:self.historyPtr+1]
        self.history.append(self.game.getBoard())
        self.historyPtr += 1


# set limited (max) depth
DEPTH_LIMIT = difficulty_window()
print("limit depth value:", DEPTH_LIMIT)


# set window
window = tk.Tk()
window.title("Checker")
create_menu(window)

# set parameters and image
CHECKER_SIZE = 8
STARTING_PLAYER = Pieces.BLACK
EVALUATION_FUNCTION = Pieces.evaluate_heuristic
SQUARE_SIZE = 60
b_norm_peice = ImageTk.PhotoImage(Image.open('img/black-normal.png').resize((SQUARE_SIZE, SQUARE_SIZE)))
b_king_peice = ImageTk.PhotoImage(Image.open('img/black-king.png').resize((SQUARE_SIZE, SQUARE_SIZE)))
w_norm_peice = ImageTk.PhotoImage(Image.open('img/white-normal.png').resize((SQUARE_SIZE, SQUARE_SIZE)))
w_king_peice = ImageTk.PhotoImage(Image.open('img/white-king.png').resize((SQUARE_SIZE, SQUARE_SIZE)))
no_piece = ImageTk.PhotoImage(Image.open('img/no-piece.png').resize((SQUARE_SIZE, SQUARE_SIZE)))


# start game
Game()
