import json
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Car Price Prediction API")

# --- Artefakte beim Start laden ---
model = joblib.load("model.joblib")
scaler = joblib.load("scaler.joblib")

with open("feature_columns.json") as f:
    FEATURE_COLUMNS = json.load(f)

with open("category_values.json") as f:
    CATEGORY_VALUES = json.load(f)

with open("numeric_columns.json") as f:
    NUMERIC_COLUMNS = json.load(f)

CAT_COLS = list(CATEGORY_VALUES.keys())


class CarInput(BaseModel):
    brand: str = Field(..., description="z.B. 'volkswagen'")
    model: str = Field(..., description="z.B. 'Volkswagen Golf'")
    color: str = Field(..., description="z.B. 'black'")
    year: int = Field(..., description="Baujahr, z.B. 2018")
    power_ps: int = Field(..., description="Leistung in PS, z.B. 150")
    transmission_type: str = Field(..., description="z.B. 'Manual' oder 'Automatic'")
    fuel_type: str = Field(..., description="z.B. 'Petrol', 'Diesel'")
    mileage_in_km: float = Field(..., description="Kilometerstand, z.B. 70000")


@app.get("/")
def root():
    return {"status": "ok", "message": "Car Price Prediction API is running"}


@app.get("/valid-values")
def valid_values():
    """Zeigt an, welche kategorischen Werte das Modell kennt (für n8n-Validierung/Sprachsteuerung nützlich)."""
    return CATEGORY_VALUES


@app.post("/predict")
def predict(car: CarInput):
    # 1. Validierung: kennt das Modell diese Kategorie-Werte?
    input_dict = car.dict()
    warnings = []
    for col in CAT_COLS:
        value = input_dict[col]
        known_values = CATEGORY_VALUES.get(col, [])
        if value not in known_values:
            warnings.append(
                f"'{value}' ist für '{col}' nicht im Training vorgekommen. "
                f"Vorhersage könnte ungenau sein."
            )

    # 2. Einzeiligen DataFrame bauen
    row = pd.DataFrame([input_dict])

    # 3. Dummies erzeugen, genau wie im Training
    row_dummies = pd.get_dummies(row, columns=CAT_COLS, drop_first=False)

    # 4. Auf exakt dieselben Spalten wie beim Training bringen
    #    (fehlende Spalten -> 0, überflüssige -> verworfen, Reihenfolge -> wie beim Training)
    row_aligned = row_dummies.reindex(columns=FEATURE_COLUMNS, fill_value=0)

    # 5. Skalieren mit demselben, bereits gefitteten Scaler
    row_scaled = scaler.transform(row_aligned)

    # 6. Vorhersage
    prediction = model.predict(row_scaled)[0]

    return {
        "predicted_price_eur": round(float(prediction), 2),
        "warnings": warnings,
        "input": input_dict,
    }

import sklearn
print(sklearn.__version__)
