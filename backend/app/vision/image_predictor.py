import numpy as np
import pickle

from PIL import Image

from tensorflow.keras.models import load_model


# ─────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────

model = load_model(
    "app/vision/skin_model.h5"
)

with open(
    "app/vision/labels.pkl",
    "rb"
) as f:

    labels = pickle.load(f)


IMG_SIZE = 64


# ─────────────────────────────────────────────
# PREDICT IMAGE
# ─────────────────────────────────────────────

def predict_skin_image(
    image_path: str
):

    image = Image.open(
        image_path
    ).convert("RGB")

    image = image.resize(
        (IMG_SIZE, IMG_SIZE)
    )

    image_array = np.array(
        image
    ) / 255.0

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    predictions = model.predict(
        image_array
    )[0]

    predicted_index = np.argmax(
        predictions
    )

    confidence = float(
        predictions[predicted_index] * 100
    )

    predicted_label = labels[
        predicted_index
    ]

    return {

        "prediction":
            predicted_label,

        "confidence":
            round(confidence, 2),

        "all_probabilities": {

            labels[i]:
                round(float(prob) * 100, 2)

            for i, prob in enumerate(predictions)
        }
    }