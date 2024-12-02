import tkinter as tk
from tkinter import messagebox
import random
from pathlib import Path

import cspSolver as solver

# Load words from text files
def load_words(file_path):
    base_dir = Path(__file__).parent
    file_address = base_dir / file_path
    
    with open(file_address, 'r') as file:
        return [line.strip().lower() for line in file if line.strip()]


# Load solutions and valid words
solutions = load_words("solutions.txt")
validWords = load_words("solutions.txt")  # Include solutions as valid guesses

class QuordleGame:
    def __init__(self, master):
        self.master = master
        self.master.title("Quordle")

        # Select random words
        self.target_words = random.sample(solutions, 4)
        self.attempts = [["" for col in range(4)] for row in range(9)]
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
        for r in range(9):
            row_cells = []
            for c in range(5):
                cell = tk.Label(grid_frame, text="", width=2, height=1, font=("Arial", 18), relief="solid", bd=1,
                                bg="white")
                cell.grid(row=r, column=c, padx=2, pady=2)
                row_cells.append(cell)
            cells.append(row_cells)

        return cells

# method to give feedback to csp solver instance
    def get_feedback_for_csp(self, guess):
        feedback = []
        for frame_index, frame in enumerate(self.frames):
            word_feedback = []
            target_word = self.target_words[frame_index]
            for i, char in enumerate(guess):
                if i >= len(target_word):
                    raise ValueError(f"Target word is too short: '{target_word}'")
                if char == target_word[i]:
                    word_feedback.append((char, "green"))
                elif char in target_word:
                    word_feedback.append((char, "yellow"))
                else:
                    word_feedback.append((char, "grey"))
            if len(word_feedback) != 5:
                raise ValueError(f"Malformed feedback for frame {frame_index}: {word_feedback}")
            feedback.append(word_feedback)
        return feedback

# modified submit_guess method for csp solver
    def submit_guess(self):
        # Generate a guess from the CSP solver
       

        guess = self.guess_entry.get().strip().lower()
        if not guess:
            guess = solver.generate_next_guess() # Replace manual input with CSP-generated guess if there is no manual guess

        # Call the existing submit_guess logic to handle feedback
        if len(guess) != 5:
            messagebox.showerror("Error", "Guess must be a 5-letter word.")
            return
        if guess not in validWords:
            messagebox.showerror("Error", "Guess is not in the word list.")
            return

        # Update the game UI
        self.update_grid(guess)
        self.guess_entry.delete(0, tk.END)

        # Pass feedback to the CSP solver
        feedback = self.get_feedback_for_csp(guess)
        # for i in feedback:
        #     print(i)
        solver.update_constraints(feedback)
        print(f"Domain sizes: {[len(solver.domains[i]) for i in range(4)]}")

        # Check if the game is over
        # if self.current_row == 9:
        #     if not all(self.solved):
        #         messagebox.showinfo("Game Over", "You are out of attempts!")
        #     return


    def update_grid(self, guess):

        # Check if the game is over
        if all(self.solved):
            messagebox.showinfo("Congratulations!", "You solved all the words!")
            self.master.destroy()
        elif self.current_row == 9:
            messagebox.showinfo("Game Over", "You are out of attempts!")
            self.master.destroy()

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
                # messagebox.showinfo("Congratulations!", f"You solved Word {frame_index + 1}!")

        self.current_row += 1

        # Check if all words are guessed correctly
        # if all(self.solved):
        #     messagebox.showinfo("Congratulations!", "You solved all the words!")


if __name__ == "__main__":
    root = tk.Tk()
    solver = solver.CSPQuordleSolver()
    game = QuordleGame(root)
    root.mainloop()
