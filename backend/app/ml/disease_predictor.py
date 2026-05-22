import joblib
import numpy as np


# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────

model = joblib.load(
    "app/ml/model.pkl"
)

label_encoder = joblib.load(
    "app/ml/label_encoder.pkl"
)


# ─────────────────────────────────────────────
# PREDICT DISEASE
# ─────────────────────────────────────────────

def predict_disease(data: dict):

    features = np.array([[
        data.get("fever", 0),
        data.get("cough", 0),
        data.get("fatigue", 0),
        data.get("headache", 0),
        data.get("chest_pain", 0),
        data.get("breathing_issue", 0),
        data.get("stress", 0),
        data.get("sleep_issue", 0),
        data.get("age", 25),
    ]])

    prediction = model.predict(
        features
    )[0]

    probabilities = model.predict_proba(
        features
    )[0]

    disease = label_encoder.inverse_transform(
        [prediction]
    )[0]

    confidence = float(
        max(probabilities) * 100
    )

    return {

        "predicted_disease":
            disease,

        "confidence":
            round(confidence, 2),

        "all_probabilities": {

            label_encoder.classes_[i]:
                round(float(prob) * 100, 2)

            for i, prob in enumerate(probabilities)
        }
    }