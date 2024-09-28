import json
import logging

from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)


@app.route('/coolcodehack', methods=['POST'])

def greet():
    return jsonify({
            "username": "bagelHouse800",
            "password": "weloveChad01"
        })

