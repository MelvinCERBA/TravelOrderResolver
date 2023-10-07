from flask import request, jsonify, current_app
from flask_restful import Resource
from app.kaldi_recogniser.transcribe_audio import transcribe_audio   # Importing the utility function
from flask_uploads import AUDIO

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AUDIO

class TranscribeResource(Resource):
    def post(self):
        if 'audio' not in request.files:
            return {'error': 'No audio file provided'}, 400
        
        file = request.files['audio']

        if not bool(file.filename):
            return {'error': 'No selected file'}, 400
        
        if not allowed_file(file.filename):
            error = f"File format not allowed. Use one of those : {AUDIO}"
            return {'error': error}, 400
        
        if file:

            try:
                filename = current_app.audio_handler.save(file) 
            except Exception as e:
                current_app.logger.error(f"Server couldn't save file : {e}")

            transcription = transcribe_audio(f'uploads/audio/{filename}')
            return {'transcription': transcription}, 200
        
        return {"error": 'Unsupported audio format'}, 415

