import os
import io
import base64
import logging
import httpx
from PIL import Image, ImageDraw

logger = logging.getLogger(__name__)

async def call_roboflow(image_bytes: bytes) -> dict:
    """
    Sends the image to the Roboflow API for pothole detection.
    """
    api_key = os.environ.get("ROBOFLOW_API_KEY")
    model_id = os.environ.get("ROBOFLOW_MODEL_ID")

    if not api_key or not model_id:
        raise ValueError("ROBOFLOW_API_KEY and ROBOFLOW_MODEL_ID must be set")

    # The Roboflow API endpoint
    url = f"https://detect.roboflow.com/{model_id}"

    async with httpx.AsyncClient() as client:
        try:
            # Base64 encode the image bytes as expected by the API
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            response = await client.post(
                url,
                params={"api_key": api_key},
                content=base64_image,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            data = response.json()
            return data
        except httpx.HTTPStatusError as e:
            logger.error(f"Roboflow API error: {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Failed to call Roboflow API: {e}")
            raise

def annotate_image(image_bytes: bytes, predictions: list) -> str:
    """
    Draws bounding boxes on the image and returns it as a base64 string.
    """
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(image)
        
        for pred in predictions:
            # Roboflow usually returns center x, center y, width, height
            x = pred.get("x")
            y = pred.get("y")
            w = pred.get("width")
            h = pred.get("height")
            if x is not None and y is not None and w is not None and h is not None:
                # Convert center to top-left and bottom-right
                x0 = x - (w / 2)
                y0 = y - (h / 2)
                x1 = x + (w / 2)
                y1 = y + (h / 2)
                
                # Draw a red rectangle (width=3 for visibility)
                draw.rectangle([x0, y0, x1, y1], outline="red", width=3)
                
        # Save to buffer and encode
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to annotate image: {e}")
        # In case of failure, just return original image base64
        return base64.b64encode(image_bytes).decode("utf-8")

def encode_image_base64(image_bytes: bytes) -> str:
    """
    Simply returns the image as a base64 string.
    """
    return base64.b64encode(image_bytes).decode("utf-8")
