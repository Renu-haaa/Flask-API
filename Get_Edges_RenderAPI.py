from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import base64
from io import BytesIO
import json
import requests
import cv2

# Globals (shared across sections)

payload = None          # JSON payload for API
img_array = None        # original image as numpy array
crop_box = None         # (x1, y1, x2, y2) stored so later sections know where to overlay
edge_mask = "image_Base64"   #to match api response 

# =============================================================================
# crop region 
#   1. crop region (x1,y1,x2,y2)
#   2. extract crop
#   3. encode crop to base64 PNG
#   4. payload
#   5. show the cropped image wi
# =============================================================================

def on_select(eclick, erelease):
    global payload, crop_box

    try:
        #rectangle coordinates from mouse
        x1, y1 = int(eclick.xdata), int(eclick.ydata) #capturing start points
        x2, y2 = int(erelease.xdata), int(erelease.ydata) #capturing end points

        x1, x2 = sorted([x1, x2])  #make sure x2> x1
        y1, y2 = sorted([y1, y2])  #make sure y2>y1 

        crop_box = (x1, y1, x2, y2)  #save globally

        #crop region 
        cropped = img_array[y1:y2, x1:x2]      #apply the cordinates to the image and get the crop image 

        # Show cropped region
        plt.imshow(cropped)
        plt.title("Cropped Region")
        plt.show()
    

        #convert cropped to base64 
        cropped_img = Image.fromarray(cropped)    #PIL Image
        buffered = BytesIO()
        cropped_img.save(buffered, format="PNG")  #save image into memory
        image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        # payload
        payload = {"image_Base64": image_base64}

        print("Payload created")

    except Exception as e:
        print("Error:", e)

# function to show full image and crop it 
def start_image_cropping(image_path):  #image_path is just a string of characters 
    global img_array   #to use outside of this function #used in on_select function 
    img = Image.open(image_path).convert("RGB")  #Image.open(image_path) loads the actual image file and convert to RGB to ensure it has 3 channels 
    #especially important if we wan tto use it for opencv
    img_array = np.array(img)  #convert the image to numpy array 

#display the image and set up the tool to crop 
    fig, ax = plt.subplots()
    ax.imshow(img_array)
    plt.title("Drag to select region, then close window")

    toggle_selector = RectangleSelector(ax, on_select, useblit=True, button=[1], minspanx=5, minspany=5, 
                                    spancoords='pixels', interactive=True)
    

    plt.show() 

# =============================================================================
# MAIN SCRIPT BEGINS
# user selects region of interest --> triggers on_select() --> sets up payload 
# =============================================================================

print("Starting script...")

original_image_path = "/Users/renuhasreedharan/Desktop/A Masterscan/Verification/12-10 24 RAW IMAGE/LOC - 16 ELB Y.jpg"
start_image_cropping(original_image_path)  #to call the function 

print("Image cropping complete")



# =============================================================================
# API CALL SECTION
# send payload to the API and get back the edge mask (base64 PNG)
# =============================================================================

# API endpoint and headers

url = "https://api-calls-74z2.onrender.com/get_edges"   #endpoint
headers = {                                             #headers
    "x-api-key": "46d526694bf4d342dddd988532f26b23",
    "Content-Type": "application/json"
}


# Send the POST request
response = requests.post(url, headers=headers, json=payload)  #send the cropped base64 image and focus start to the API 

print("Received API response")

print("Status Code:", response.status_code)
print("Response:", response.text)

result = response.json()

# Extract base64 edge mask from response (change key if different)
edge_b64 = result[edge_mask]
edge_bytes = base64.b64decode(edge_b64)
edge_img = Image.open(BytesIO(edge_bytes)).convert("L")  # grayscale
edges = np.array(edge_img)  # (h, w), values 0..255

# resize mask to match crop size
x1, y1, x2, y2 = crop_box
h, w = (y2 - y1), (x2 - x1)
if edges.shape != (h, w):
    edges = cv2.resize(edges, (w, h), interpolation=cv2.INTER_NEAREST)



# =============================================================================
# VISUALISATION SECTION
# =============================================================================

#show mask first 
plt.figure("Edge Mask (from API)")
plt.imshow(edges, cmap='gray')
plt.axis('off')
plt.tight_layout()
plt.show(block=True)  # waits here until you close the mask window

#Overlay -  edges on a copy of the original, inside the crop region only
overlay_image = img_array.copy()
region = overlay_image[y1:y2, x1:x2]
mask = edges > 0
region[mask] = [255, 0, 0]  # red edges

#display overlay
plt.figure("Overlay on Original")
plt.imshow(overlay_image)
plt.axis('off')
plt.tight_layout()
plt.show(block=True)

