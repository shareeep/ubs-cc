import json
import logging
from flask import request, jsonify
from routes import app  # Assuming your Flask app is defined in routes.py
import random

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/wordle-game', methods=['POST'])
def solve():
    data = request.get_json()

    # Load the word dictionary
    try:
        with open('routes/wordDict.json', 'r') as file:
            wordDict = json.load(file)
    except FileNotFoundError:
        logger.error("wordDict.json file not found in routes directory.")
        return jsonify({"error": "Word dictionary not found."}), 500
    except json.JSONDecodeError:
        logger.error("wordDict.json contains invalid JSON.")
        return jsonify({"error": "Invalid word dictionary format."}), 500

    guessHistory = data.get("guessHistory", [])
    evaluationHistory = data.get("evaluationHistory", [])

    # Input validation
    if len(guessHistory) != len(evaluationHistory):
        logger.error("guessHistory and evaluationHistory lengths do not match.")
        return jsonify({"error": "Invalid input data."}), 400

    # Check if the last guess was correct
    if guessHistory and evaluationHistory:
        last_evaluation = evaluationHistory[-1]
        if is_correct_guess(last_evaluation):
            last_guess = guessHistory[-1]
            logger.debug(f"Last guess '{last_guess}' was correct. Game completed.")
            return jsonify({
                "status": "success",
                "message": f"The word '{last_guess}' was guessed correctly!"
            })

    # Initial Guess
    if not guessHistory:
        guess = "slate"  # Based on your examples
        logger.debug(f"No previous guesses. Initial guess: {guess}")
        return jsonify({"guess": guess})

    # Find the next candidate based on history
    guess = findCandidates(guessHistory, evaluationHistory, wordDict)
    logger.debug(f"Next guess: {guess}")
    return jsonify({"guess": guess})


def is_correct_guess(evaluation):
    """
    Determines if the evaluation string indicates a correct guess.
    All symbols in the evaluation must be 'O' for a correct guess.
    """
    return all(symbol == 'O' for symbol in evaluation)


def findCandidates(guessHistory, evaluationHistory, wordDict):
    excluded_letters = set()
    present_letters = set()
    correct_positions = {}  # position -> letter
    excluded_positions = {}  # letter -> set of positions where it cannot be

    # Process all previous guesses and evaluations
    for guess, evaluation in zip(guessHistory, evaluationHistory):
        for i, (g, e) in enumerate(zip(guess, evaluation)):
            if e == 'O':
                # Correct letter in the correct position
                correct_positions[i] = g
                present_letters.add(g)
            elif e == 'X':
                # Correct letter but in the wrong position
                present_letters.add(g)
                if g in excluded_positions:
                    excluded_positions[g].add(i)
                else:
                    excluded_positions[g] = {i}
            elif e == '-':
                # Letter not in the word, unless it's already confirmed as present
                if g not in present_letters:
                    excluded_letters.add(g)
            elif e == '?':
                # Masked feedback; no information can be derived
                pass
            else:
                logger.warning(f"Unknown evaluation symbol '{e}' encountered.")

    # Debugging statements
    logger.debug(f"Excluded Letters (globally excluded): {excluded_letters}")
    logger.debug(f"Present Letters: {present_letters}")
    logger.debug(f"Correct Positions: {correct_positions}")
    logger.debug(f"Excluded Positions for Present Letters: {excluded_positions}")

    possibleWords = []
    for word in wordDict:
        word = word.lower()

        # Skip words that have been guessed already
        if word in guessHistory:
            continue

        # Check excluded letters
        if any(letter in excluded_letters for letter in word):
            continue

        # Check correct positions
        match = True
        for pos, letter in correct_positions.items():
            if pos >= len(word) or word[pos] != letter:
                match = False
                break
        if not match:
            continue

        # Check present letters and their excluded positions
        for letter in present_letters:
            if letter not in word:
                match = False
                break
            # Ensure the letter is not in any of its excluded positions
            for pos in excluded_positions.get(letter, set()):
                if pos < len(word) and word[pos] == letter:
                    match = False
                    break
            if not match:
                break
        if not match:
            continue

        # All checks passed
        possibleWords.append(word)

    logger.debug(f"Possible Words Count: {len(possibleWords)}")
    logger.debug(f"Possible Words: {possibleWords}")

    if not possibleWords:
        # Fallback if no words are found
        logger.debug("No possible words found after filtering. Falling back to unguessed words.")
        possibleWords = [word.lower() for word in wordDict if word.lower() not in guessHistory]
        if not possibleWords:
            logger.error("No words available to guess.")
            return "slate"  # Default guess if no words are available
        else:
            logger.debug(f"Fallback Possible Words Count: {len(possibleWords)}")
            logger.debug(f"Fallback Possible Words: {possibleWords}")

    # Select a random word from possible words
    return random.choice(possibleWords) if possibleWords else "slate"