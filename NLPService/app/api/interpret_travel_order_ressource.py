from flask import request, jsonify, current_app
from flask_restful import Resource
from app.nlp.travel_order_processor import get_origin_and_destination


class InterpretTravelOrder(Resource):
    def post(self):
        # Check if JSON is received with a text field
        if request.is_json:
            data = request.get_json()
            if 'order' not in data:
                return {"message": "The 'order' field is missing."}, 400
            current_app.logger.info(f"data object =  {data} ")
            res = get_origin_and_destination(data['order'])
            current_app.logger.info(f"Returning response {res} ")
            return res, 200
        return {"message": "No order provided."}, 400

