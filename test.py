from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import RectangleSelector
import base64
from io import BytesIO
import json
import requests

payload = None
overlay_image = None
img_array = None

def on_select(eclick, erelease):
    global payload, overlay_image

    try:
        # 2.1 get rectangle coordinates
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        x1, x2 = sorted([x1, x2])
        y1, y2 = sorted([y1, y2])

        # 2.2 crop from original
        cropped = img_array[y1:y2, x1:x2]    # HxW[x,y], RGB
        h, w = cropped.shape[:2]

        # 2.3 encode crop → base64 (PNG)
        cropped_img = Image.fromarray(cropped)
        buf = BytesIO()
        cropped_img.save(buf, format="PNG")
        image_base64 = base64.b64encode(buf.getvalue()).decode("utf-8")

        # 2.4 build payload (adjust to your API contract)
        payload = {
            "image_base64": image_base64
            # "focus_start": [y1, x1],   # include if your API needs it
        }

        # =========================
        # === API CALL SECTION ===
        # =========================
        url = "https://api-calls-74z2.onrender.com/get_edges"
        headers = {
            "x-api-key": "46d526694bf4d342dddd988532f26b23",
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()

        # 2.5 parse API response (decide exact keys!)
        data = response.json()
        # if your server returns the edge mask as "image_Base64" (capital B):
        edge_b64 = data["image_Base64"]   # <-- confirm this key name matches server
        edge_bytes = base64.b64decode(edge_b64)
        edge_img = Image.open(BytesIO(edge_bytes)).convert("L")  # grayscale
        edges = np.array(edge_img)                               # (h, w) 0/255

        # sanity: ensure mask matches crop size
        if edges.shape != (h, w):
            # If API resized, bring it back to the crop size
            import cv2
            edges = cv2.resize(edges, (w, h), interpolation=cv2.INTER_NEAREST)

        # ===============================
        # === OVERLAY & VISUALIZATION ===
        # ===============================
        # color edge pixels red on a copy of original
        base = img_array.copy()
        region = base[y1:y2, x1:x2]
        mask = edges > 0
        region[mask] = [255, 0, 0]
        overlay_image = base

        # show mask and overlay
        plt.figure(figsize=(12,5))
        plt.subplot(1,2,1)
        plt.title("Edge Mask (API)")
        plt.imshow(edges, cmap='gray')
        plt.axis('off')

        plt.subplot(1,2,2)
        plt.title("Overlay on Original")
        plt.imshow(overlay_image)
        plt.axis('off')
        plt.show()

    except Exception as e:
        print("Error in on_select:", e)

def start_image_cropping(image_path):
    global img_array
    img = Image.open(image_path).convert("RGB")
    img_array = np.array(img)

    fig, ax = plt.subplots()
    ax.imshow(img_array)
    plt.title("Drag to select region, then close window")

    toggle_selector = RectangleSelector(
        ax, on_select,
        useblit=True,
        button=[1],
        minspanx=5, minspany=5,
        spancoords='pixels',
        interactive=True
    )

    plt.show()


# ====== RUN ======
image_path = "/Users/renuhasreedharan/Desktop/A Masterscan/Verification/12-10 24 RAW IMAGE/LOC - 14 A.jpg"
start_image_cropping(image_path)
