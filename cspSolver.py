from collections import defaultdict
from pathlib import Path
import random

# Load words from text files
def load_words(file_path):
    base_dir = Path(__file__).parent
    file_address = base_dir / file_path
    
    with open(file_address, 'r') as file:
        return [line.strip().lower() for line in file if line.strip()]


# Load solutions and valid words
solutions = load_words("solutions.txt")
validWords = load_words("solutions.txt")

class CSPQuordleSolver:
    def __init__(self):
        self.domains = {var: set(validWords) for var in range(4)}  # All valid words
        self.constraints = defaultdict(list)  # No initial binary constraints
        self.feedback = {var: [] for var in range(4)}  # Store feedback per word
        self.used_guesses = set()  # Track already used guesses
    
    def generate_next_guess(self):
        if len(self.used_guesses) == 0:
            guess = random.choice(list(set(validWords)))
        
        # Return a domain if it is solved
        single_domain = next((domain for domain in self.domains.values() if len(domain) == 1), None)
        if single_domain:
            guess = list(single_domain)[0]
        else:
            # Use domain intersection to find a common valid guess for all frames

            for domain in self.domains.values():
                if len(domain) == 1:
                    guess = list(domain)[0];
                    for i in range(4):
                        if guess in self.domains[i]:
                            self.domains[i].remove(guess)
                    self.used_guesses.add(guess)
                    return guess

            word_count = defaultdict(int)

            for domain in self.domains.values():
                for word in domain:
                    word_count[word] += 1

            max_domains = max(word_count.values(), default=0)
            most_common_words = [word for word, count in word_count.items() if count == max_domains]
            guess = random.choice(most_common_words) if most_common_words else random.choice(list(set(validWords)))

        # Remove the guess from the domains
        for i in range(4):
            if guess in self.domains[i]:
                self.domains[i].remove(guess)
        self.used_guesses.add(guess)
        return guess
    
    def update_constraints(self, feedback):

        """Prune domains based on node and arc consistency."""

        # Iterate over each feedback (assuming feedback is a list of lists for each word)
        for i in range(4):
            grey_letters = {char for char, status in feedback[i] if status == 'grey'}
            yellow_constraints = [(char, pos) for pos, (char, status) in enumerate(feedback[i]) if status == 'yellow']
            green_constraints = [(char, pos) for pos, (char, status) in enumerate(feedback[i]) if status == 'green']

            # Prune based on grey letters
            self.domains[i] = {
                word for word in self.domains[i]
                if not any(letter in grey_letters for letter in word)
            }

            # Prune based on yellow letters
            self.domains[i] = {
                word for word in self.domains[i]
                if all(
                    word[pos] != char and char in word for char, pos in yellow_constraints
                ) and all(
                    word.count(char) >= 1 for char, pos in yellow_constraints
                )
            }

            # Prune based on green letters
            self.domains[i] = {
                word for word in self.domains[i]
                if all(word[pos] == char for char, pos in green_constraints)
            }
            # print(f"Domain sizes after filtering: {len(self.domains[i])}")
            # print(f"Feedback for domain {i}: {feedback[i]}")

        # print(f"Domain sizes: {[len(self.domains[i]) for i in range(4)]}")
        return
    
def simulate_solver():
    """Simulate the CSP solver for a Quordle game."""
    # Step 1: Randomly select target words
    target_words = random.sample(solutions, 4)
    # print(f"Target words: {target_words}")

    # Step 2: Initialize the CSP solver
    solver = CSPQuordleSolver()

    # Step 3: Simulate the game
    for attempt in range(9):
        # Generate a guess
        guess = solver.generate_next_guess()

        # success = ''
        # if guess in target_words:
        #     success = 'successfully'
        # print(f"Attempt {attempt + 1}: Solver guessed '{guess}' {success}")

        # Generate feedback for each target word
        feedback = []
        for target_word in target_words:
            word_feedback = []
            for i, char in enumerate(guess):
                if char == target_word[i]:
                    word_feedback.append((char, "green"))
                elif char in target_word:
                    word_feedback.append((char, "yellow"))
                else:
                    word_feedback.append((char, "grey"))
            feedback.append(word_feedback)

        # Update solver with feedback
        solver.update_constraints(feedback)

        # Check if the solver has solved all words
        if all(len(solver.domains[i]) == 0 for i in range(4)):
            # print("Solver successfully solved all words!")
            # print(f"Solved words: {target_words}")
            return 1

    # print("Solver failed to solve all words within 9 attempts.")
    # print(f"Unsolved target words: {target_words}")
    return 0

if __name__ == "__main__":

    import sys

    # Get the number of games from the command-line arguments
    if len(sys.argv) > 1:
        try:
            games = int(sys.argv[1])
            if games <= 0:
                raise ValueError("Number of games must be a positive integer.")
        except ValueError as e:
            print(f"Invalid input for number of games: {e}")
            sys.exit(1)
    else:
        games = 100  # Default number of games if no input is provided
    
    results = []
    for i in range(games):
        results.append(simulate_solver())
    print(f"Results: {sum(results)}/{games} games won")