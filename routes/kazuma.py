import json
import logging

from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)

def compute_efficiency(monsters):
    n = len(monsters)
    # Initialize previous DP states: [State0, State1, State2]
    # State0: Not prepared
    # State1: Prepared (circle drawn at t-1, ready to attack at t)
    # State2: Cooldown (just attacked at t-1)
    dp_prev = [0, -monsters[0] if n > 0 else float('-inf'), float('-inf')]
    
    for t in range(1, n):
        dp_current = [float('-inf')] * 3
        for state in range(3):
            if dp_prev[state] == float('-inf'):
                continue
            if state == 0:
                # Action: Prepare at t, pay monsters[t], move to State1 for t+1
                dp_current[1] = max(dp_current[1], dp_prev[0] - monsters[t])
                # Action: Move to rear, stay in State0
                dp_current[0] = max(dp_current[0], dp_prev[0])
            elif state == 1:
                # Action: Attack at t, gain monsters[t], move to State2
                dp_current[2] = max(dp_current[2], dp_prev[1] + monsters[t])
                # Action: Move to rear, stay in State1
                dp_current[1] = max(dp_current[1], dp_prev[1])
            elif state == 2:
                # Action: Cooldown ends, move to State0
                dp_current[0] = max(dp_current[0], dp_prev[2])
        dp_prev = dp_current
    
    # After all time frames, consider possible states
    return max(dp_prev[0], dp_prev[1], dp_prev[2], 0)  # Ensure at least 0

@app.route('/efficient-hunter-kazuma', methods=['POST'])
def efficient_hunter_kazuma():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            return jsonify({"error": "Input should be a list of objects."}), 400
        results = []
        for item in data:
            if "monsters" not in item or not isinstance(item["monsters"], list):
                return jsonify({"error": "Each object must have a 'monsters' list."}), 400
            monsters = item["monsters"]
            # Validate that all elements are non-negative integers
            if not all(isinstance(m, int) and m >= 0 for m in monsters):
                return jsonify({"error": "'monsters' list must contain non-negative integers."}), 400
            if not monsters:
                results.append({"efficiency": 0})
                continue
            efficiency = compute_efficiency(monsters)
            results.append({"efficiency": efficiency})
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return jsonify({"error": "Internal server error."}), 500
