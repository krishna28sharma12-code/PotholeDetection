def calculate_severity(bbox_area_pct: float) -> str:
    """
    Computes severity bucket based on bounding box area percentage.
    BR-4: < 5% -> Low, 5% - 15% -> Medium, > 15% -> High
    """
    if bbox_area_pct < 5.0:
        return "Low"
    elif bbox_area_pct <= 15.0:
        return "Medium"
    else:
        return "High"

def fallback_severity(confidence: float) -> str:
    """
    Computes severity bucket based on confidence if bbox area isn't available.
    """
    if confidence < 0.6:
        return "Low"
    elif confidence <= 0.8:
        return "Medium"
    else:
        return "High"
