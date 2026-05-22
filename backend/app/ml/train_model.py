import pandas as pd
import random
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier


# ─────────────────────────────────────────────
# GENERATE SAMPLE HEALTHCARE DATASET
# ─────────────────────────────────────────────

data = []

diseases = [

    "Flu",
    "Migraine",
    "Common Cold",
    "COVID",
    "Anxiety",
    "Heart Disease"
]

for _ in range(2000):

    fever = random.randint(0, 1)

    cough = random.randint(0, 1)

    fatigue = random.randint(0, 1)

    headache = random.randint(0, 1)

    chest_pain = random.randint(0, 1)

    breathing_issue = random.randint(0, 1)

    stress = random.randint(0, 1)

    sleep_issue = random.randint(0, 1)

    age = random.randint(18, 70)

    # ─────────────────────────────────────────
    # SIMPLE RULE-BASED LABELING
    # ─────────────────────────────────────────

    if fever and cough and fatigue:

        disease = "Flu"

    elif headache and stress:

        disease = "Migraine"

    elif cough and not fever:

        disease = "Common Cold"

    elif fever and breathing_issue:

        disease = "COVID"

    elif stress and sleep_issue:

        disease = "Anxiety"

    elif chest_pain and breathing_issue:

        disease = "Heart Disease"

    else:

        disease = random.choice(diseases)

    data.append({

        "fever": fever,

        "cough": cough,

        "fatigue": fatigue,

        "headache": headache,

        "chest_pain": chest_pain,

        "breathing_issue": breathing_issue,

        "stress": stress,

        "sleep_issue": sleep_issue,

        "age": age,

        "disease": disease
    })


# ─────────────────────────────────────────────
# CREATE DATAFRAME
# ─────────────────────────────────────────────

df = pd.DataFrame(data)

print(df.head())


# ─────────────────────────────────────────────
# FEATURES + LABEL
# ─────────────────────────────────────────────

X = df.drop("disease", axis=1)

y = df["disease"]


# ─────────────────────────────────────────────
# LABEL ENCODING
# ─────────────────────────────────────────────

label_encoder = LabelEncoder()

y_encoded = label_encoder.fit_transform(y)


# ─────────────────────────────────────────────
# TRAIN TEST SPLIT
# ─────────────────────────────────────────────

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y_encoded,

    test_size=0.2,

    random_state=42
)


# ─────────────────────────────────────────────
# TRAIN XGBOOST MODEL
# ─────────────────────────────────────────────

model = XGBClassifier(

    n_estimators=100,

    max_depth=5,

    learning_rate=0.1,

    objective="multi:softmax",

    num_class=len(label_encoder.classes_)
)

model.fit(

    X_train,
    y_train
)


# ─────────────────────────────────────────────
# EVALUATE MODEL
# ─────────────────────────────────────────────

predictions = model.predict(X_test)

accuracy = accuracy_score(

    y_test,
    predictions
)

print(f"\nModel Accuracy: {accuracy * 100:.2f}%")


# ─────────────────────────────────────────────
# SAVE MODEL
# ─────────────────────────────────────────────

joblib.dump(

    model,

    "app/ml/model.pkl"
)

joblib.dump(

    label_encoder,

    "app/ml/label_encoder.pkl"
)

print("\n✅ Model saved successfully")