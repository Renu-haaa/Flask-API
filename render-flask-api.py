from flask import Flask, request, jsonify
import numpy as np
import base64
import cv2
from io import BytesIO
from PIL import Image
import os
from dotenv import load_dotenv  #dot environment 

# Load API key from .env
load_dotenv()  
API_KEY = os.getenv("API_KEY")

app = Flask(__name__)

#function to create edge mask 
def get_edge_mask(cropped):
    edges = cv2.Canny(cropped, threshold1=0, threshold2=255, L2gradient=False, apertureSize=7)
    edge_img = Image.fromarray(edges)
    buffered = BytesIO()
    edge_img.save(buffered, format="PNG")
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return {"image_Base64": image_base64}


#GET: Root endpoint with API key
@app.route("/", methods=["GET"])
def home():
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify({"message": "Welcome with a valid API key"})

# POST: Edge detection

@app.route("/get_edges", methods=["POST"])
def edge_det_func():
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        image_base64 = data["image_base64"].split(",")[-1]
        image_bytes = base64.b64decode(image_base64)
        np_arr = np.frombuffer(image_bytes, np.uint8)
        cropped = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        mask_edges = get_edge_mask(cropped)
        return jsonify(mask_edges)
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
