from flask import Flask

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello from the NLP service!</p>"