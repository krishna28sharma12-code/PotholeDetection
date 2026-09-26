import os
import logging
from fastapi import APIRouter, UploadFile, Form, HTTPException, Request
from backend.models.detection import UploadResponse
from backend.services.detection import call_roboflow, annotate_image, encode_image_base64
from backend.services.severity import calculate_severity, fallback_severity
from backend.services.db import insert_detection

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/api/upload_frame", response_model=UploadResponse)
async def upload_frame(
    request: Request,
    image: UploadFile,
    lat: float = Form(...),
    lon: float = Form(...),
    captured_at: str = Form(...)
):
    try:
        image_bytes = await image.read()
    except Exception as e:
        logger.error(f"Failed to read image: {e}")
        raise HTTPException(status_code=400, detail="Invalid image file")

    # BR-2: Detection acceptance threshold
    threshold_str = os.environ.get("DETECTION_CONFIDENCE_THRESHOLD", "0.5")
    try:
        confidence_threshold = float(threshold_str)
    except ValueError:
        confidence_threshold = 0.5

    try:
        roboflow_data = await call_roboflow(image_bytes)
    except Exception as e:
        raise HTTPException(status_code=502, detail="Failed to call detection API")

    predictions = roboflow_data.get("predictions", [])
    
    # Filter by confidence
    valid_predictions = [p for p in predictions if p.get("confidence", 0) >= confidence_threshold]

    # BR-3: Discard rule
    if not valid_predictions:
        logger.debug("No pothole detected above threshold.")
        return UploadResponse(detected=False)

    # Find the largest bounding box (BR-4)
    # The bounding box area is width * height
    valid_predictions.sort(key=lambda p: p.get("width", 0) * p.get("height", 0), reverse=True)
    largest_pred = valid_predictions[0]
    
    highest_confidence = largest_pred.get("confidence", 0)
    w = largest_pred.get("width")
    h = largest_pred.get("height")
    
    img_metadata = roboflow_data.get("image", {})
    img_w = img_metadata.get("width")
    img_h = img_metadata.get("height")
    
    bbox_area_pct = None
    if w and h and img_w and img_h:
        bbox_area = w * h
        img_area = img_w * img_h
        if img_area > 0:
            bbox_area_pct = (bbox_area / img_area) * 100.0
            severity = calculate_severity(bbox_area_pct)
        else:
            severity = fallback_severity(highest_confidence)
    else:
        severity = fallback_severity(highest_confidence)

    # Encode images
    normal_image_b64 = encode_image_base64(image_bytes)
    annotated_image_b64 = annotate_image(image_bytes, valid_predictions)

    # Parse timestamp
    from datetime import datetime
    try:
        parsed_captured_at = datetime.fromisoformat(captured_at.replace('Z', '+00:00'))
    except Exception:
        # Fallback if invalid format
        parsed_captured_at = datetime.utcnow()

    # Insert into DB
    pool = request.app.state.db_pool
    try:
        row_id = await insert_detection(
            pool,
            captured_at=parsed_captured_at,
            latitude=lat,
            longitude=lon,
            severity=severity,
            confidence=highest_confidence,
            bbox_area_pct=bbox_area_pct,
            normal_image=normal_image_b64,
            annotated_image=annotated_image_b64
        )
        logger.info(f"Pothole detected and stored with ID: {row_id}, Severity: {severity}")
        return UploadResponse(
            detected=True,
            id=row_id,
            severity=severity,
            confidence=highest_confidence
        )
    except Exception as e:
        logger.error(f"Failed to insert into database: {e}")
        raise HTTPException(status_code=500, detail="Database error")
