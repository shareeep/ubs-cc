import json
import logging
from flask import request
from routes import app
import random

logger = logging.getLogger(__name__)

@app.route('/wordle-game', methods=['POST'])

#     data = {
#    "guessHistory": ["slate"], 
#    "evaluationHistory": ["?-X-X"]
#     }

def solve():
    data = request.get_json()
    with open('routes/wordDict.json', 'r') as file:
        wordDict = json.load(file)
    guessHistory = data.get("guessHistory")
    evaluationHistory = data.get("evaluationHistory")

    #Initial Guess
    if guessHistory == []:
        guess = "arose"
        return json.dumps({"guess": guess})
    
    else:
        guess = findCandidates(guessHistory, evaluationHistory, wordDict)
        return json.dumps({"guess": guess})
    

def findCandidates(guessHistory, evaluationHistory, wordDict):

    letterPositions = {0:"", 1:"", 2:"", 3:"", 4:""}
    possibleLetters = []
    possibleWords = []

    for i in range(len(guessHistory)):
        guess = guessHistory[i]
        evaluation = evaluationHistory[i]
        letterPositions = findCorrectPositions(guess, evaluation, letterPositions)
    possibleLetters = removeSetLetters(letterPositions,findPossibleLetters(guess, evaluation, possibleLetters))
    print(letterPositions)
    print(possibleLetters)

    for word in wordDict:
        if all(letter in list(word) for letter in possibleLetters):
            possibleWords.append(word)
    
    required_letters = {key: value for key, value in letterPositions.items() if value}

# Populate newPossibleWords based on matching values
    newPossibleWords = []
    if len(required_letters) != 0:
        for word in possibleWords:
            # Check if the word is long enough
            if len(word) > max(required_letters.keys()):
                matches = True
                index = 0  # Initialize an index for the while loop
                while index < len(required_letters):
                    key = list(required_letters.keys())[index]  # Get the key based on the index
                    letter = required_letters[key]
                    if word[key] != letter:
                        matches = False
                        break
                    index += 1  # Move to the next index

                if matches:
                    newPossibleWords.append(word)

    # Print the filtered words
    # print(newPossibleWords)
    possibleLettersWrongPosition = findPossibleLetterWrongPosition(possibleLetters, evaluationHistory, guessHistory)
    print(possibleLettersWrongPosition)

    if newPossibleWords == []:
        newPossibleWords = possibleWords[:]

    updatedNewPossibleWords = newPossibleWords[:]
    print(newPossibleWords)
    for candidate in newPossibleWords:
        for i in range(len(candidate)):
            letter = candidate[i]
            if letter in possibleLettersWrongPosition and i in possibleLettersWrongPosition[letter]:
                updatedNewPossibleWords.remove(candidate)
                break

    print(updatedNewPossibleWords)
    updatedNewPossibleWords = [item for item in updatedNewPossibleWords if item not in guessHistory]
    return updatedNewPossibleWords[random.randint(0, len(updatedNewPossibleWords)-1)]


def findCorrectPositions(guess, evaluation, letterPositions):
    for i in range(len(evaluation)):
        scoring = evaluation[i]
        if scoring == "O":
            letterPositions[i] = guess[i]
    return letterPositions

def findPossibleLetters(guess, evaluation, possibleLetters):
        for i in range(len(evaluation)):
            scoring = evaluation[i]
            if scoring == "X":
                possibleLetters.append(guess[i])
        return possibleLetters

def findPossibleLetterWrongPosition(possibleLetters, evaluationHistory, guessHistory):
    new_dict = {letter: set() for letter in possibleLetters}
    for letter in possibleLetters:
        for i in range(len(evaluationHistory)):
            guess = guessHistory[i]
            evaluation = evaluationHistory[i]
            for i in range(len(guess)):
                if guess[i] == letter and evaluation[i] == "X":
                    new_dict[letter].add(i)
    return new_dict

def removeSetLetters(letterPositions, possibleLetters):
    for letter in letterPositions:
        if letter in possibleLetters:
            possibleLetters.remove(letter)
    return possibleLetters