import heapq
import logging
from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)

def max_bugsfixed(bugseq):

    # Sort the bugs by their escalation limit
    sorted_bugs = sorted(bugseq, key=lambda x: x[1])
    
    total_time = 0
    max_heap = []
    
    for bug in sorted_bugs:
        difficulty, limit = bug
        total_time += difficulty
        # Use a max heap by pushing negative difficulty
        heapq.heappush(max_heap, -difficulty)
        
        # If total_time exceeds the current bug's limit, remove the most time-consuming bug
        if total_time > limit:
            removed_bug = -heapq.heappop(max_heap)
            total_time -= removed_bug
    
    return len(max_heap)

@app.route('/bugfixer/p2', methods=['POST'])
def bugfixer_p2():
    try:
        data = request.get_json()
        if not isinstance(data, list):
            logger.error("Input data is not a list.")
            return jsonify({"error": "Input data should be a list of objects or lists."}), 400

        results = []
        
        for index, item in enumerate(data):
            if isinstance(item, dict):
                bugseq = item.get('bugseq', [])
                if not isinstance(bugseq, list):
                    logger.error(f"'bugseq' at index {index} is not a list.")
                    results.append(0)
                    continue
            elif isinstance(item, list):
                bugseq = item
            else:
                logger.error(f"Item at index {index} is neither a dict nor a list.")
                results.append(0)
                continue

            # Validate that bugseq is a list of [difficulty, limit] pairs
            valid = True
            for pair in bugseq:
                if not (isinstance(pair, list) or isinstance(pair, tuple)) or len(pair) != 2:
                    logger.error(f"Invalid bug sequence at index {index}: {pair}")
                    valid = False
                    break
                difficulty, limit = pair
                if not (isinstance(difficulty, int) and isinstance(limit, int)):
                    logger.error(f"Invalid types in bug sequence at index {index}: {pair}")
                    valid = False
                    break
            if not valid:
                results.append(0)
                continue

            result = max_bugsfixed(bugseq)
            results.append(result)
        
        return jsonify(results), 200
    except Exception as e:
        logger.exception("An error occurred while processing the request.")
        return jsonify({"error": str(e)}), 400
