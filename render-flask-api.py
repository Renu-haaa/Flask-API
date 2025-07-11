from flask import Flask 

app = Flask(__name__)

@app.rpute("/")
def home():
    return "Hello from Render!"