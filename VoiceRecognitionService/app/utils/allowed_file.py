from flask_uploads import AUDIO

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in AUDIO