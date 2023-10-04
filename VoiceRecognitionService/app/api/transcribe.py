from flask import request, jsonify, current_app
from flask_restful import Resource
from app.kaldi_recogniser.transcribe_audio import transcribe_audio   # Importing the utility function
from app.utils.allowed_file import allowed_file


class TranscribeResource(Resource):
    def post(self):
        current_app.logger.debug(f"Inside transcribe ressource.")
        if 'audio' not in request.files:
            return jsonify({'error': 'No audio file provided'}), 400
        
        file = request.files['audio']

        if not bool(file.filename):
            return jsonify({'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            filename = current_app.audio_handler.save(file) 
            transcription = transcribe_audio(f'uploads/audio/{filename}')
            return jsonify({'transcription': transcription})
        
        return jsonify({'error': 'Unsupported audio format'}), 415

