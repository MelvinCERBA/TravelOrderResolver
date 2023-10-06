from flask import request, jsonify, current_app
from flask_restful import Resource
import requests


class TravelOrderResource(Resource):
    def post(self):
        # Check if JSON is received with a text field
        if request.is_json:
            data = request.get_json()
            if 'order' not in data:
                return {"message": "The 'order' field is missing."}, 400

            return {"message": "Received order: " + data['order']}, 200
        
        file = request.files.get('audio')
        if not file:
            return {"message": "No audio file provided."}, 400
        
        response = requests.post("http://voice-recognition-service:5000/transcribe", files={"audio": (file.filename, file.stream, file.content_type, file.headers)})

        if response.status_code != 200:
            return response.json(), 500
        
        return response.json(), 200

