import json
import logging
from flask import request, jsonify
from collections import defaultdict, deque
from routes import app

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p1', methods=['POST'])

def bugfixer():
    data = request.get_json()
    
    logging.info("Data sent for evaluation: {}".format(data))
    
    time = data.get("time", [])
    prerequisites = data.get("prerequisites", [])
    
    def min_hours_to_resolve_bugs(time, prerequisites):
        n = len(time)
        
        graph = defaultdict(list)
        in_degree = [0] * n
        
        for a, b in prerequisites:
            graph[a-1].append(b-1)
            in_degree[b-1] += 1
        
        queue = deque()
        
        min_time = [0] * n
        
        for i in range(n):
            if in_degree[i] == 0:
                queue.append(i)
                min_time[i] = time[i]
        
        while queue:
            current = queue.popleft()
            
            for neighbor in graph[current]:
                min_time[neighbor] = max(min_time[neighbor], min_time[current] + time[neighbor])
                in_degree[neighbor] -= 1
                
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return max(min_time)

    result = min_hours_to_resolve_bugs(time, prerequisites)
    
    logging.info("Minimum hours needed: {}".format(result))
    

    return jsonify({"result": result})
