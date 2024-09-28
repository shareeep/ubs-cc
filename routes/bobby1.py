from collections import defaultdict, deque

def min_hours_to_resolve_bugs(projects):
    time = projects['time']
    prerequisites = projects['prerequisites']
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
        
        # Process all the neighbors
        for neighbor in graph[current]:
            # Update the time for the dependent project
            min_time[neighbor] = max(min_time[neighbor], min_time[current] + time[neighbor])
            in_degree[neighbor] -= 1
            
            # If in-degree becomes zero, add it to the queue
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    # The total time will be the maximum time taken to complete any project
    return max(min_time)

# Example usage
projects = {
    "time": [1, 2, 3, 4, 5],
    "prerequisites": [(1, 2), (3, 4), (2, 5), (4, 5)]
}

print(min_hours_to_resolve_bugs(projects))  # Output should be 12
