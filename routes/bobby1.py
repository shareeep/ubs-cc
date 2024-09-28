import json
import logging
from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p1', methods=['POST'])
def bugfixer():
    try:
        data = request.get_json()

        # Validate that input data is provided
        if not data:
            return jsonify({"error": "No input data provided"}), 400

        logging.info("Data sent for evaluation: {}".format(data))

        # Extract time and prerequisites from the input
        time = data.get("time")
        prerequisites = data.get("prerequisites")

        # Basic validation
        if time is None:
            return jsonify({"error": "'time' key is missing or has null value"}), 400
        if prerequisites is None:
            return jsonify({"error": "'prerequisites' key is missing or has null value"}), 400

        # Check that both are lists
        if not isinstance(time, list) or not isinstance(prerequisites, list):
            return jsonify({"error": "'time' and 'prerequisites' must be lists"}), 400

        # Ensure 'time' array is not empty
        if len(time) == 0:
            return jsonify({"error": "'time' array is empty"}), 400

        # Call the function to calculate the minimum hours
        result = calculate_min_time(time, prerequisites)

        logging.info("Minimum hours needed: {}".format(result))

        # Return the result as JSON
        return jsonify({"result": result})

    except Exception as e:
        logging.error(f"Unknown error occurred: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500


def calculate_min_time(time, prerequisites):
    n = len(time)

    # Convert prerequisites into a dictionary
    prereq_map = {i: [] for i in range(n)}
    for a, b in prerequisites:
        prereq_map[b - 1].append(a - 1)

    # Memoization to avoid recalculating
    calculated_times = [-1] * n

    # Function to calculate total time for a project
    def get_total_time(project):
        # If the time is already calculated, return it
        if calculated_times[project] != -1:
            return calculated_times[project]

        # If no prerequisites, return its own time
        if not prereq_map[project]:
            calculated_times[project] = time[project]
            return time[project]

        # Otherwise, get the maximum time of its prerequisites
        max_prereq_time = max(get_total_time(pr) for pr in prereq_map[project])
        total_time = time[project] + max_prereq_time

        # Save the result to avoid recalculating
        calculated_times[project] = total_time
        return total_time

    # Calculate the total time for all projects and return the maximum
    return max(get_total_time(i) for i in range(n))
