import tensorflow as tf
import numpy as np
import cv2
import pickle
import os

# ─────────────────────────────────────────────
# LOAD MODEL + LABELS
# ─────────────────────────────────────────────

MODEL_PATH = "app/vision/skin_model.h5"

LABELS_PATH = "app/vision/labels.pkl"

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"Model not found: {MODEL_PATH}"
    )

if not os.path.exists(LABELS_PATH):

    raise FileNotFoundError(
        f"Labels file not found: {LABELS_PATH}"
    )

# LOAD MODEL
model = tf.keras.models.load_model(
    MODEL_PATH
)

# LOAD LABELS
with open(LABELS_PATH, "rb") as f:

    labels = pickle.load(f)

print("Loaded Labels:", labels)


# ─────────────────────────────────────────────
# HUMANIZED MEDICAL RESPONSES
# ─────────────────────────────────────────────

medical_advice = {

    "Acne": {

        "severity": "Low",

        "summary":
        "Possible acne-related skin condition detected.",

        "advice": [

            "Keep skin clean and oil-free",

            "Avoid touching affected areas frequently",

            "Drink enough water daily",

            "Use mild skin care products",
        ]
    },

    "Eczema": {

        "severity": "Moderate",

        "summary":
        "Possible eczema or skin irritation detected.",

        "advice": [

            "Keep skin moisturized",

            "Avoid harsh soaps and allergens",

            "Avoid scratching affected areas",

            "Consult dermatologist if irritation increases",
        ]
    },

    "Allergy": {

        "severity": "Moderate",

        "summary":
        "Possible allergic skin reaction detected.",

        "advice": [

            "Avoid possible allergens",

            "Monitor redness or swelling",

            "Use clean clothing and bedding",

            "Seek medical advice if symptoms worsen",
        ]
    },

    "Infection": {

        "severity": "High",

        "summary":
        "Possible skin infection detected.",

        "advice": [

            "Keep affected area clean and dry",

            "Avoid touching or scratching",

            "Maintain proper hygiene",

            "Consult a healthcare professional",

            "Seek immediate care if swelling or pain increases",
        ]
    },

    "Normal": {

        "severity": "Low",

        "summary":
        "No major visible skin abnormalities detected.",

        "advice": [

            "Maintain healthy skin hygiene",

            "Continue regular skin care",

            "Monitor for future irritation",
        ]
    },

    # LOW CONFIDENCE CATEGORY
    "Uncertain": {

        "severity": "Moderate",

        "summary":
        "AI confidence is low for this image. A clear medical assessment could not be determined.",

        "advice": [

            "Upload a clearer image",

            "Ensure proper lighting",

            "Seek professional medical advice",
        ]
    }
}


# ─────────────────────────────────────────────
# IMAGE PREDICTION
# ─────────────────────────────────────────────

def predict_skin_image(image_path):

    try:

        # READ IMAGE
        image = cv2.imread(image_path)

        if image is None:

            raise ValueError(
                "Unable to read image."
            )

        # RESIZE TO TRAINED SIZE
        image = cv2.resize(
            image,
            (64, 64)
        )

        # NORMALIZE
        image = image.astype(
            np.float32
        ) / 255.0

        # ADD BATCH DIMENSION
        image = np.expand_dims(
            image,
            axis=0
        )

        # PREDICT
        predictions = model.predict(
            image,
            verbose=0
        )[0]

        predicted_index = int(
            np.argmax(predictions)
        )

        # SAFETY CHECK
        if predicted_index >= len(labels):

            predicted_label = "Normal"

        else:

            predicted_label = labels[
                predicted_index
            ]

        confidence = float(
            predictions[predicted_index] * 100
        )

        # ALL PROBABILITIES
        all_probabilities = {

            labels[i]:
            round(
                float(predictions[i] * 100),
                2
            )

            for i in range(
                min(
                    len(labels),
                    len(predictions)
                )
            )
        }

        # ─────────────────────────────
        # LOW CONFIDENCE CHECK
        # ─────────────────────────────

        if confidence < 75:

            predicted_label = "Uncertain"

        # GET MEDICAL RESPONSE
        info = medical_advice.get(

            predicted_label,

            medical_advice["Uncertain"]
        )

        # RETURN RESULT
        return {

            "prediction":
                predicted_label,

            "confidence":
                round(confidence, 2),

            "severity":
                info["severity"],

            "summary":
                info["summary"],

            "precautions":
                info["advice"],

            "all_probabilities":
                all_probabilities,
        }

    except Exception as e:

        return {

            "prediction":
                "Unknown",

            "confidence":
                0,

            "severity":
                "Moderate",

            "summary":
                f"Image analysis failed: {str(e)}",

            "precautions": [

                "Please upload a clearer image",

                "Ensure proper lighting",

                "Consult healthcare professional if symptoms persist",
            ],

            "all_probabilities": {},
        }