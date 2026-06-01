import tensorflow as tf
import cv2
import numpy as np
import pickle

MODEL_PATH = "app/vision/skin_model.h5"

LABELS_PATH = "app/vision/labels.pkl"

model = tf.keras.models.load_model(
    MODEL_PATH
)

with open(
    LABELS_PATH,
    "rb"
) as f:

    labels = pickle.load(f)

index_to_label = {
    v: k
    for k, v in labels.items()
}

def predict_skin_image(
    image_path
):

    image = cv2.imread(
        image_path
    )

    image = cv2.resize(
        image,
        (64, 64)
    )

    image = image / 255.0

    image = np.expand_dims(
        image,
        axis=0
    )

    prediction = model.predict(
        image
    )[0]

    predicted_class = (
        np.argmax(
            prediction
        )
    )

    confidence = float(
        prediction[
            predicted_class
        ] * 100
    )

    disease = (
        index_to_label[
            predicted_class
        ]
    )

    return {

        "prediction":
            disease,

        "confidence":
            round(
                confidence,
                2
            ),

        "severity":
            "Moderate"
    }