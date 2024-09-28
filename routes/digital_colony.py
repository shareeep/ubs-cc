import json
import logging
from flask import request, jsonify
from routes import app  # Ensure this import correctly points to your Flask app instance

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def compute_weight(colony: str, generations: int) -> str:
    # Convert colony string to list of integers
    digits = [int(c) for c in colony]
    
    # Initialize pair counts: index = 10*a + b
    pair_counts = [0] * 100
    for i in range(len(digits) - 1):
        a, b = digits[i], digits[i + 1]
        pair_counts[10 * a + b] += 1
    
    # Initialize current weight
    current_weight = sum(digits)
    
    for gen in range(generations):
        W = current_weight % 10
        new_pair_counts = [0] * 100
        sum_new_digits = 0
        
        for a in range(10):
            for b in range(10):
                count = pair_counts[10 * a + b]
                if count == 0:
                    continue
                
                # Calculate signature
                if a > b:
                    s = a - b
                elif a < b:
                    s = 10 - (b - a)
                else:
                    s = 0
                
                # Calculate new digit
                d = (W + s) % 10
                sum_new_digits += count * d
                
                # Update new pair counts
                new_pair_counts[10 * a + d] += count
                new_pair_counts[10 * d + b] += count
        
        # Update current weight
        current_weight += sum_new_digits
        pair_counts = new_pair_counts

    
    return str(current_weight)

@app.route('/digital-colony', methods=['POST'])

def digital_colony():
    try:
        data = request.get_json()
        if not isinstance(data, list) or len(data) != 2:
            return jsonify({"error": "Input must be a JSON array of two objects."}), 400
        
        results = []
        for item in data:
            # Validate input fields
            if not isinstance(item, dict):
                return jsonify({"error": "Each item must be a JSON object."}), 400
            if 'generations' not in item or 'colony' not in item:
                return jsonify({"error": "Each object must contain 'generations' and 'colony' fields."}), 400
            generations = item['generations']
            colony = item['colony']
            if not isinstance(generations, int) or generations < 0:
                return jsonify({"error": "'generations' must be a non-negative integer."}), 400
            if not isinstance(colony, str) or not colony.isdigit() or not (1000 <= int(colony) <= 9999):
                return jsonify({"error": "'colony' must be a string representing a number between 1000 and 9999."}), 400
            
            weight = compute_weight(colony, generations)
            results.append(weight)
        
        return jsonify(results), 200
    
    except Exception as e:
        logger.exception("An error occurred while processing the request.")
        return jsonify({"error": "An internal error occurred."}), 500
