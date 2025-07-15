from flask import Flask, request, abort
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env

API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

def require_api_key(func):
    def wrapper(*args, **kwargs):
        key = request.headers.get('x-api-key')
        if key != API_KEY:
            abort(401, description="Unauthorized")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

@app.route("/")
@require_api_key
def home():
    return "Welcome with a valid API key!"
