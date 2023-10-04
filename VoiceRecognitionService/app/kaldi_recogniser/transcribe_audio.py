import sys, os
import subprocess
import json
from vosk import Model, KaldiRecognizer
import wave
from flask import current_app

def enforceValidFormat(input_path, output_path):
    """ Runs this command: "ffmpeg -i <input_path> -ac 1 -ar 16000 -acodec pcm_s16le <output_path>" """
    current_app.logger.debug(f"Converting file {input_path} to file {output_path}...")
    command = [
        'ffmpeg', 
        '-i', input_path, 
        '-ac', '1',             # 1 audio channel
        '-ar', '16000',         # 16,000 Hz sample rate
        '-acodec', 'pcm_s16le', # 16-bit PCM codec
        output_path
    ]
    subprocess.run(command)


def transcribe_audio(file_path):
    """ Takes in any format of french audio and returns its transcription """
    current_app.logger.debug(f"Transcribing audio of file {file_path}... ")

    # Convert input audio to required WAV format
    output_path = os.path.splitext(file_path)[0] + "_converted.wav"
    try:
        enforceValidFormat(file_path, output_path)
    except Exception as e:
        current_app.logger.debug("Could not reformat file:", e)
        return None

    wf = wave.open(output_path, "rb")

    # Load model and recognizer
    script_dir = os.path.dirname(os.path.realpath(__file__))  # Gets the directory where transcribe_audio.py resides.
    model_path = os.path.join(script_dir, "models/vosk-model-small-fr-0.22")  # Generates the full path to the model.
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, wf.getframerate())

    # Transcribe audio chunk after chunk
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            results.append(json.loads(recognizer.Result()))
    results.append(json.loads(recognizer.FinalResult()))

    texts = [ res['text'] for res in results]
    return ' '.join(texts)