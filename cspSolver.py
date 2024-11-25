from collections import defaultdict

class CSPQuordleSolver:
    def __init__(self, target_words, valid_words):
        self.variables = [f"word{i}" for i in range(4)]  # Four words to guess
        self.domains = {var: set(valid_words) for var in self.variables}  # All valid words
        self.constraints = defaultdict(list)  # No initial binary constraints
        self.feedback = {var: [] for var in self.variables}  # Store feedback per word
        self.target_words = target_words  # Target words for simulation
        self.used_guesses = set()  # Track already used guesses

    def is_consistent(self, variable, value, feedback):
        """Check if a value is consistent with the given feedback."""
        for i, (char, status) in enumerate(feedback):
            if status == "green" and value[i] != char:
                return False
            if status == "yellow" and (value[i] == char or char not in value):
                return False
            if status == "grey" and char in value:
                return False
        return True

    def enforce_node_consistency(self):
        """Prune domains based on node consistency."""
        for var in self.variables:
            self.domains[var] = {
                word for word in self.domains[var]
                if all(self.is_consistent(var, word, feedback) for feedback in self.feedback[var])
            }

    def enforce_arc_consistency(self):
        """Prune domains using arc consistency."""
        arcs = [(x, y) for x in self.variables for y in self.variables if x != y]
        while arcs:
            x, y = arcs.pop(0)
            revised = False
            for word in set(self.domains[x]):
                if not any(self.is_consistent(y, other_word, self.feedback[x]) for other_word in self.domains[y]):
                    self.domains[x].remove(word)
                    revised = True
            if revised:
                for z in self.variables:
                    if z != x:
                        arcs.append((z, x))

    def backtracking_search(self, assignment={}):
        """Backtracking algorithm to find solutions."""
        if len(assignment) == len(self.variables):
            return assignment

        unassigned = [var for var in self.variables if var not in assignment]
        var = unassigned[0]

        for value in self.domains[var]:
            local_assignment = assignment.copy()
            local_assignment[var] = value
            self.feedback[var] = self.get_feedback(var, value)
            self.enforce_node_consistency()
            self.enforce_arc_consistency()

            result = self.backtracking_search(local_assignment)
            if result:
                return result

        return None
    
    # def generate_next_guess(self):
    #     """
    #     Generate the next guess based on the CSP's current state.

    #     Returns:
    #         str: A valid 5-letter word guess.
    #     """
    #     # Select the variable with the smallest domain (MRV heuristic)
    #     min_var = None
    #     min_domain_size = float('inf')
        
    #     for var in self.variables:
    #         if len(self.domains[var]) > 0 and len(self.domains[var]) < min_domain_size:
    #             min_var = var
    #             min_domain_size = len(self.domains[var])
        
    #     # If all domains are empty, we cannot generate a guess
    #     # if min_var is None:
    #     #     raise ValueError("No valid guesses remaining in any domain!")
    #     if min_var is None:
    #         # Fallback: Random guess from all valid words
    #         guess = random.choice(list(set(valid_words) - self.used_guesses))

    #     # Choose a word from the selected variable's domain
    #     # For simplicity, pick the first word in the domain
    #     guess = next(iter(self.domains[min_var]))

    #     while guess in self.used_guesses:
    #         guess = next(iter(self.domains[min_var]))  # Select the next word in the domain
    #     self.used_guesses.add(guess)

    #     return guess

    def generate_next_guess(self):
        """
        Generate the next guess based on the CSP's current state.

        Returns:
            str: A valid 5-letter word guess.
        """
        # Select the variable with the smallest domain (MRV heuristic)
        min_var = None
        min_domain_size = float('inf')

        for var in self.variables:
            if len(self.domains[var]) > 0 and len(self.domains[var]) < min_domain_size:
                min_var = var
                min_domain_size = len(self.domains[var])

        # If no valid domains exist, fallback to a random word from unused valid words
        if min_var is None or all(len(self.domains[var]) == 0 for var in self.variables):
            fallback_guess = list(set(validWords) - self.used_guesses)
            if not fallback_guess:
                raise ValueError("No valid guesses remaining!")
            guess = random.choice(fallback_guess)
        else:
            # Use domain intersection to find a common valid guess for all frames
            combined_domain = set.intersection(*[self.domains[var] for var in self.variables if len(self.domains[var]) > 0])

            # If the combined domain is empty, fallback to the smallest domain
            if combined_domain:
                guess = next(iter(combined_domain))
            else:
                guess = next(iter(self.domains[min_var]))

        # Avoid repeating guesses
        while guess in self.used_guesses:
            guess = random.choice(list(set(validWords) - self.used_guesses))
        self.used_guesses.add(guess)

        return guess



    def get_feedback(self, variable, guess):
        """Simulate feedback for a guess."""
        feedback = []
        target = self.target_words[self.variables.index(variable)]
        word_letter_count = defaultdict(int)
        for char in target:
            word_letter_count[char] += 1

        # Green feedback
        for i, char in enumerate(guess):
            if char == target[i]:
                feedback.append((char, "green"))
                word_letter_count[char] -= 1

        # Yellow and Grey feedback
        for i, char in enumerate(guess):
            if (char, "green") not in feedback:
                if word_letter_count[char] > 0:
                    feedback.append((char, "yellow"))
                    word_letter_count[char] -= 1
                else:
                    feedback.append((char, "grey"))

        return feedback

    def solve(self):
        """Solve the Quordle puzzle."""
        self.enforce_node_consistency()
        self.enforce_arc_consistency()
        return self.backtracking_search()
    
    def update_constraints(self, feedback):
        for var, word_feedback in zip(self.variables, feedback):
            self.feedback[var].append(word_feedback)
        self.enforce_node_consistency()
        self.enforce_arc_consistency()

# Example Integration with UI
if __name__ == "__main__":
    # Assume solutions.txt and valid_words.txt are loaded as lists
    target_words = random.sample(solutions, 4)
    solver = CSPQuordleSolver(target_words, validWords)
    solution = solver.solve()

    if solution:
        print("Solution found:", solution)
    else:
        print("No solution found.")
