from flask import request, jsonify, current_app
from flask_restful import Resource
from app.optimizer.travel_optimizer import optimize_travel


class TravelPlanResource(Resource):
    def post(self):
        # Get the order from json or audio
        if request.is_json: 
            data = request.get_json()
            if ('origin' not in data) or ('destination' not in data):
                return {"message": "Origin or destination is missing."}, 400
            current_app.logger.info("Received json travel_order: " + str(data))
            origin = data['origin']
            destination = data['destination']
            travel_plan = optimize_travel(origin, destination)
        else: 
            return {"message": "No travel order received."}, 400

        return travel_plan, 200

