from datetime import datetime
import pytz

import json
import logging
from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)

@app.route('/mailtime', methods=['POST'])

# Helper function to parse and convert timestamps to UTC
def parse_time(time_str):
    return datetime.fromisoformat(time_str[:-6] + time_str[-6:])

# Calculate response time in seconds
def calculate_response_time(sent_time, received_time):
    delta = sent_time - received_time
    return delta.total_seconds()

# Sorting emails by timeSent field
def sort_emails_by_time(emails):
    return sorted(emails, key=lambda email: parse_time(email['timeSent']))

# Main function to calculate response times
def calculate_response_times(data):
    emails = sort_emails_by_time(data['emails'])
    response_times = {}
    
    # Iterate through the emails to calculate response times
    for i in range(1, len(emails)):
        sender = emails[i]['sender']
        previous_email_time = parse_time(emails[i - 1]['timeSent'])
        current_email_time = parse_time(emails[i]['timeSent'])
        
        # Calculate response time
        response_time = calculate_response_time(current_email_time, previous_email_time)
        
        # Add the response time to the sender's total
        if sender not in response_times:
            response_times[sender] = []
        response_times[sender].append(response_time)
    
    # Calculate the average response time for each user
    avg_response_times = {user: sum(times) / len(times) for user, times in response_times.items()}
    
    return avg_response_times

# # Example data input
# data = {
#     "emails": [
#         {
#           "subject": "subject",
#           "sender": "Alice",
#           "receiver": "Bob",
#           "timeSent": "2024-01-12T15:00:00+01:00"
#         },
#         {
#           "subject": "RE: subject",
#           "sender": "Bob",
#           "receiver": "Alice",
#           "timeSent": "2024-01-15T09:00:00+08:00"
#         },
#         {
#           "subject": "RE: RE: subject",
#           "sender": "Alice",
#           "receiver": "Bob",
#           "timeSent": "2024-01-16T09:05:00+01:00"
#         }
#     ],
#     "users": [
#         {
#           "name": "Alice",
#           "officeHours": {
#             "timeZone": "Europe/Paris",
#             "start": 9,
#             "end": 18
#           }
#         },
#         {
#           "name": "Bob",
#           "officeHours": {
#             "timeZone": "Asia/Singapore",
#             "start": 8,
#             "end": 17
#           }
#         }
#     ]
# }

# # Output the calculated response times
# print(calculate_response_times(data))
