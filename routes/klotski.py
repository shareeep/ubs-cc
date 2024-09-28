import json
import logging
from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)

class Block:
    def __init__(self, symbol, cells):
        self.symbol = symbol  # Block identifier (e.g., 'A', 'B', etc.)
        self.cells = set(cells)  # Set of (row, col) tuples

    def move(self, direction):
        if direction == 'N':
            return {(r - 1, c) for r, c in self.cells}
        elif direction == 'S':
            return {(r + 1, c) for r, c in self.cells}
        elif direction == 'W':
            return {(r, c - 1) for r, c in self.cells}
        elif direction == 'E':
            return {(r, c + 1) for r, c in self.cells}
        else:
            return self.cells  # No movement


class Board:
    def __init__(self, board_string):
        # Initialize a 5x4 grid from the board string
        self.grid = [list(board_string[i:i+4]) for i in range(0, 20, 4)]
        self.blocks = self.parse_board()

    def parse_board(self):
        block_positions = {}
        # Corrected this line to handle the grid properly
        for i, char in enumerate(''.join(''.join(row) for row in self.grid)):
            if char == '@':
                continue
            row, col = divmod(i, 4)
            if char not in block_positions:
                block_positions[char] = set()
            block_positions[char].add((row, col))
        blocks = {}
        for symbol, cells in block_positions.items():
            blocks[symbol] = Block(symbol, cells)
        return blocks

    def can_move(self, block, direction):
        target_positions = block.move(direction)
        for pos in target_positions:
            r, c = pos
            # Check bounds
            if not (0 <= r < 5 and 0 <= c < 4):
                return False
            current_cell = self.grid[r][c]
            # Check if the target cell is empty or part of the same block
            if current_cell != '@' and current_cell != block.symbol:
                return False
        return True

    def move_block(self, symbol, direction):
        block = self.blocks[symbol]
        if self.can_move(block, direction):
            # Remove block from current positions
            for r, c in block.cells:
                self.grid[r][c] = '@'
            # Compute new positions
            new_positions = block.move(direction)
            # Sort new_positions based on direction to prevent overwriting
            if direction == 'N':
                sorted_positions = sorted(new_positions, key=lambda x: x[0])  # Top to bottom
            elif direction == 'S':
                sorted_positions = sorted(new_positions, key=lambda x: -x[0])  # Bottom to top
            elif direction == 'W':
                sorted_positions = sorted(new_positions, key=lambda x: x[1])  # Left to right
            elif direction == 'E':
                sorted_positions = sorted(new_positions, key=lambda x: -x[1])  # Right to left
            else:
                sorted_positions = new_positions
            # Place block in new positions
            for r, c in sorted_positions:
                self.grid[r][c] = symbol
            # Update block's cells
            block.cells = set(new_positions)

    def serialize(self):
        return ''.join([''.join(row) for row in self.grid])


def klotski_solver(data):
    results = []
    for entry in data:
        board_string = entry['board']
        moves_string = entry['moves']
        board = Board(board_string)
        for i in range(0, len(moves_string), 2):
            symbol = moves_string[i]
            direction = moves_string[i + 1]
            board.move_block(symbol, direction)
        results.append(board.serialize())
    return results

# Flask route to handle the POST request for the Klotski solver
@app.route('/klotski', methods=['POST'])
def klotski_endpoint():
    try:
        # Parse the incoming JSON data from the request
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid input"}), 400

        # Call the klotski_solver function with the parsed data
        results = klotski_solver(data)

        # Return the results as a JSON response
        return jsonify(results)

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
        return jsonify({"error": "An error occurred while processing the request"}), 500
