from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class SlopeInput(BaseModel):
    cohesion: float
    friction_angle: float
    unit_weight: float
    slope_height: float
    slope_angle: float

@app.get("/")
def home():
    return {"message": "Slope Stability API running"}

@app.post("/analyze")
def analyze_slope(data: SlopeInput):

    # example calculation
    fos = (data.cohesion + data.unit_weight) / (data.slope_height + 1)

    return {
        "factor_of_safety": fos,
        "status": "Safe" if fos > 1.5 else "Unsafe"
    }


@app.get("/health")
def health_check():
    return {"status": "Backend running"}


@app.get("/methods")
def get_methods():
    return {
        "methods": [
            "Bishop Method"
        ]
    }


@app.post("/safety-check")
def safety_check(data: SlopeInput):

    fos = (data.cohesion + data.unit_weight) / (data.slope_height + 1)

    if fos < 1:
        condition = "Failure"
    elif fos < 1.5:
        condition = "Marginally Safe"
    else:
        condition = "Safe"

    return {
        "factor_of_safety": fos,
        "condition": condition
    }
