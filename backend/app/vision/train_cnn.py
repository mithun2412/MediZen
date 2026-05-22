import os
import numpy as np
import random
import pickle

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Flatten,
    Dense,
    Dropout
)

from tensorflow.keras.utils import to_categorical
from sklearn.model_selection import train_test_split


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────

IMG_SIZE = 64

CLASSES = [

    "Acne",
    "Eczema",
    "Allergy",
    "Infection",
    "Normal"
]

NUM_CLASSES = len(CLASSES)


# ─────────────────────────────────────────────
# GENERATE SYNTHETIC IMAGE DATA
# ─────────────────────────────────────────────

X = []
y = []

for label_index, label in enumerate(CLASSES):

    for _ in range(400):

        # random image

        image = np.random.rand(

            IMG_SIZE,
            IMG_SIZE,
            3
        )

        # add slight class-specific patterns

        if label == "Acne":

            image[:, :, 0] += 0.3

        elif label == "Eczema":

            image[:, :, 1] += 0.3

        elif label == "Allergy":

            image[:, :, 2] += 0.3

        elif label == "Infection":

            image += 0.2

        image = np.clip(
            image,
            0,
            1
        )

        X.append(image)

        y.append(label_index)

X = np.array(X)

y = np.array(y)

y = to_categorical(
    y,
    NUM_CLASSES
)


# ─────────────────────────────────────────────
# TRAIN TEST SPLIT
# ─────────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.2,

    random_state=42
)


# ─────────────────────────────────────────────
# BUILD CNN MODEL
# ─────────────────────────────────────────────

model = Sequential([

    Conv2D(

        32,

        (3, 3),

        activation="relu",

        input_shape=(
            IMG_SIZE,
            IMG_SIZE,
            3
        )
    ),

    MaxPooling2D((2, 2)),


    Conv2D(

        64,

        (3, 3),

        activation="relu"
    ),

    MaxPooling2D((2, 2)),


    Flatten(),


    Dense(

        128,

        activation="relu"
    ),

    Dropout(0.3),


    Dense(

        NUM_CLASSES,

        activation="softmax"
    )
])


# ─────────────────────────────────────────────
# COMPILE MODEL
# ─────────────────────────────────────────────

model.compile(

    optimizer="adam",

    loss="categorical_crossentropy",

    metrics=["accuracy"]
)


# ─────────────────────────────────────────────
# TRAIN MODEL
# ─────────────────────────────────────────────

model.fit(

    X_train,
    y_train,

    epochs=5,

    batch_size=32,

    validation_data=(
        X_test,
        y_test
    )
)


# ─────────────────────────────────────────────
# SAVE MODEL
# ─────────────────────────────────────────────

os.makedirs(
    "app/vision",
    exist_ok=True
)

model.save(
    "app/vision/skin_model.h5"
)

with open(
    "app/vision/labels.pkl",
    "wb"
) as f:

    pickle.dump(
        CLASSES,
        f
    )

print("\n✅ CNN Medical Vision Model Saved")