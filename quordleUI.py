import tkinter as tk
from tkinter import messagebox
import random
from pathlib import Path

# Load words from text files
def load_words(file_path):
    base_dir = Path(__file__).parent
    file_address = base_dir / file_path
    
    with open(file_address, 'r') as file:
        return [line.strip().lower() for line in file if line.strip()]


# Load solutions and valid words
solutions = load_words("words.txt")
validWords = load_words("valid_words.txt")  # Include solutions as valid guesses

class QuordleGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Quordle")

        # Select random words
        self.target_words = random.sample(solutions, 4)
        self.attempts = [["" for col in range(4)] for row in range(6)]
        self.current_row = 0

        # Track if each word grid is solved
        self.solved = [False] * 4

        # Create the grid for each word
        self.frames = [self.create_grid(frame_index) for frame_index in range(4)]

        # Entry field for guesses
        self.guess_entry = tk.Entry(self.master, font=("Arial", 18))
        self.guess_entry.grid(row=2, column=1, columnspan=2, pady=10)

        # Submit button
        self.submit_button = tk.Button(self.master, text="Submit", font=("Arial", 14), command=self.submit_guess)
        self.submit_button.grid(row=3, column=1, columnspan=2)

    def create_grid(self, frame_index):
        frame = tk.Frame(self.master, padx=5, pady=5)
        frame.grid(row=1, column=frame_index, padx=10)

        tk.Label(frame, text=f"Word {frame_index + 1}", font=("Arial", 16, "bold")).pack()

        grid_frame = tk.Frame(frame)
        grid_frame.pack()

        cells = []
        for r in range(6):
            row_cells = []
            for c in range(5):
                cell = tk.Label(grid_frame, text="", width=2, height=1, font=("Arial", 18), relief="solid", bd=1,
                                bg="white")
                cell.grid(row=r, column=c, padx=2, pady=2)
                row_cells.append(cell)
            cells.append(row_cells)

        return cells

    def submit_guess(self):
        guess = self.guess_entry.get().strip().lower()
        if len(guess) != 5:
            messagebox.showerror("Error", "Guess must be a 5-letter word.")
            return

        if guess not in validWords:
            messagebox.showerror("Error", "Guess is not in the word list.")
            return

        self.update_grid(guess)
        self.guess_entry.delete(0, tk.END)

        if self.current_row == 6:
            messagebox.showinfo("Game Over", "You are out of attempts!")
            return

    def update_grid(self, guess):
        for frame_index, frame in enumerate(self.frames):
            if self.solved[frame_index]:
                continue  # Skip if the word grid is already solved

            word = self.target_words[frame_index]
            word_letter_count = {}

            # Count occurrences of each letter in the target word
            for char in word:
                word_letter_count[char] = word_letter_count.get(char, 0) + 1

            # First pass: Handle greens and adjust counts
            for c, char in enumerate(guess):
                cell = frame[self.current_row][c]
                cell.config(text=char.upper())

                if char == word[c]:
                    cell.config(bg="green", fg="white")
                    word_letter_count[char] -= 1  # Reduce count for exact matches

            # Second pass: Handle yellows
            for c, char in enumerate(guess):
                cell = frame[self.current_row][c]
                # Skip cells already marked green
                if cell.cget("bg") == "green":
                    continue

                # Check if the letter exists in the word and hasn't been fully accounted for
                if char in word_letter_count and word_letter_count[char] > 0:
                    cell.config(bg="yellow", fg="black")
                    word_letter_count[char] -= 1  # Reduce count for yellow matches
                else:
                    cell.config(bg="grey", fg="white")

            # Check if the current grid is solved
            if guess == word:
                self.solved[frame_index] = True
                messagebox.showinfo("Congratulations!", f"You solved Word {frame_index + 1}!")

        self.current_row += 1

        # Check if all words are guessed correctly
        if all(self.solved):
            messagebox.showinfo("Congratulations!", "You solved all the words!")


if __name__ == "__main__":
    root = tk.Tk()
    game = QuordleGame(root)
    root.mainloop()
