from flask import request, jsonify, current_app
from flask_restful import Resource
import requests


class TravelOrderResource(Resource):
    def post(self):
        # Get the order from json or audio
        if request.is_json: 
            data = request.get_json()
            if 'order' not in data:
                return {"message": "The 'order' field is missing."}, 400
            order = data['order']
            current_app.logger.info("Received json order: " + order)

        else:
            file = request.files.get('audio')
            if not file:
                return {"message": "No audio file provided."}, 400
            current_app.logger.info("Received file " + file.filename)
            transcription_response = requests.post("http://voice-recognition-service:5000/transcribe", files={"audio": (file.filename, file.stream, file.content_type, file.headers)})
            if transcription_response.status_code != 200:
                return transcription_response.json(), 500
            order = transcription_response.json()['transcription']
            current_app.logger.info("Computed transcription :" + order)
        
        # Get the origin and destination
        nlp_response = requests.post("http://nlp-service:5000/interpretTravelOrder", json={'order': order})
        if nlp_response.status_code != 200:
            return nlp_response.json(), 500
        travel_order = nlp_response.json()
        current_app.logger.info("Interpreted travel order " + str(travel_order))
        
        # Get travel plan
        optimizer_response = requests.post("http://travel-optimizer-service:5000/fastest_route_mock", json=travel_order)
        if optimizer_response.status_code != 200:
            return optimizer_response.json(), 500
        
        current_app.logger.info("Optimized travel plan computed " + str(optimizer_response.json()))
        return optimizer_response.json(), 200

