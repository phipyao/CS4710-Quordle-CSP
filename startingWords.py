from collections import Counter

def find_best_starting_words(words, top_n=100):
    # Step 2: Calculate letter frequencies for each position
    position_frequencies = [Counter() for _ in range(5)]
    for word in words:
        for i, letter in enumerate(word):
            position_frequencies[i][letter] += 1

    # Step 3: Score each word
    word_scores = []
    for word in words:
        score = 0
        used_letters = set()
        for i, letter in enumerate(word):
            # Add frequency score for the position
            score += position_frequencies[i][letter]
            # Penalize duplicate letters
            if letter in used_letters:
                score -= 10  # Penalty for duplicate letters
            used_letters.add(letter)
        word_scores.append((word, score))

    # Step 4: Sort words by score
    word_scores.sort(key=lambda x: x[1], reverse=True)

    # Step 5: Select top N words
    best_words = [word for word, _ in word_scores[:top_n]]

    return best_words



if __name__ == "__main__":
    from pathlib import Path

    def load_words(file_path):
        base_dir = Path(__file__).parent
        file_address = base_dir / file_path
        
        with open(file_address, 'r') as file:
            return [line.strip().lower() for line in file if line.strip()]


    # Load solutions and find valid words
    solutions = load_words("solutions.txt")
    n = 30
    top_words = find_best_starting_words(solutions, n)
    print(f"Top {n} Best Starting Words:")
    print(top_words)