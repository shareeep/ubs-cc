import json
import logging
from flask import request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p1', methods=['POST'])
def bugfixer():
    data = request.get_json()

    # Validate that the input data is provided
    if not data:
        return jsonify({"error": "No input data provided"}), 400

    logging.info("Data sent for evaluation: {}".format(data))
    
    # Extract time and prerequisites from the input
    time = data.get("time")
    prerequisites = data.get("prerequisites")
    
    # Check if time and prerequisites are valid
    if time is None or prerequisites is None:
        return jsonify({"error": "Missing 'time' or 'prerequisites' in the input"}), 400

    if not isinstance(time, list) or not isinstance(prerequisites, list):
        return jsonify({"error": "'time' must be a list and 'prerequisites' must be a list"}), 400
    
    # Ensure time array is not empty
    if len(time) == 0:
        return jsonify({"error": "'time' array is empty"}), 400

    # Function to calculate the minimum hours to resolve all bugs
    def min_hours_to_resolve_bugs(time, prerequisites):
        n = len(time)
        
        # Create graph and in-degree array
        graph = defaultdict(list)
        in_degree = [0] * n
        
        # Build the graph
        for a, b in prerequisites:
            graph[a-1].append(b-1)
            in_degree[b-1] += 1
        
        # Queue for topological sort
        queue = deque()
        
        # Dynamic array to store the minimum time to complete each project
        min_time = [0] * n
        
        # Initialize queue with projects that have no prerequisites
        for i in range(n):
            if in_degree[i] == 0:
                queue.append(i)
                min_time[i] = time[i]
        
        # Topological sort and calculate the minimum time for each project
        while queue:
            current = queue.popleft()
            
            # Process all the neighbors (dependent projects)
            for neighbor in graph[current]:
                # Update the time for the dependent project
                min_time[neighbor] = max(min_time[neighbor], min_time[current] + time[neighbor])
                in_degree[neighbor] -= 1
                
                # If in-degree becomes zero, add it to the queue
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # The total time will be the maximum time taken to complete any project
        return max(min_time)

    # Call the function to calculate the minimum hours
    result = min_hours_to_resolve_bugs(time, prerequisites)
    
    logging.info("Minimum hours needed: {}".format(result))
    
    # Return the result as JSON
    return jsonify({"result": result})
