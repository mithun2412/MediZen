from collections import Counter
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.models import (
    SymptomHistory,
    MedicineReminder,
    DoseLog
)


# ─────────────────────────────────────────────
# COMMON SYMPTOMS
# ─────────────────────────────────────────────
COMMON_SYMPTOMS = [

    "headache",
    "migraine",
    "fever",
    "cough",
    "cold",
    "fatigue",
    "dizziness",
    "nausea",
    "vomiting",
    "stress",
    "anxiety",
    "depression",
    "chest pain",
    "stomach pain",
    "back pain",
    "allergy",
    "rash",
    "breathing problem",
    "asthma",
    "sleep problem",
]


# ─────────────────────────────────────────────
# EXTRACT SYMPTOMS FROM TEXT
# ─────────────────────────────────────────────
def extract_symptoms(
    text: str
):

    text = text.lower()

    found = []

    for symptom in COMMON_SYMPTOMS:

        if symptom in text:
            found.append(symptom)

    return found


# ─────────────────────────────────────────────
# GET USER SYMPTOM HISTORY
# ─────────────────────────────────────────────
def get_user_symptom_history(
    db: Session,
    user_id: int
):

    history = db.query(
        SymptomHistory
    ).filter(
        SymptomHistory.user_id == user_id
    ).all()

    return history


# ─────────────────────────────────────────────
# RECURRING SYMPTOMS
# ─────────────────────────────────────────────
def get_recurring_symptoms(
    db: Session,
    user_id: int
):

    history = get_user_symptom_history(
        db,
        user_id
    )

    symptom_counter = Counter()

    for item in history:

        symptoms = extract_symptoms(
            item.symptom
        )

        symptom_counter.update(symptoms)

    recurring = []

    for symptom, count in symptom_counter.items():

        if count >= 2:

            recurring.append({

                "symptom": symptom,
                "count": count
            })

    recurring.sort(
        key=lambda x: x["count"],
        reverse=True
    )

    return recurring


# ─────────────────────────────────────────────
# SYMPTOM FREQUENCY
# ─────────────────────────────────────────────
def get_symptom_frequency(
    db: Session,
    user_id: int,
    days: int = 30
):

    since_date = (
        datetime.utcnow()
        - timedelta(days=days)
    )

    history = db.query(
        SymptomHistory
    ).filter(
        SymptomHistory.user_id == user_id,
        SymptomHistory.created_at >= since_date
    ).all()

    frequency = Counter()

    for item in history:

        symptoms = extract_symptoms(
            item.symptom
        )

        frequency.update(symptoms)

    return dict(frequency)


# ─────────────────────────────────────────────
# STRESS TREND
# ─────────────────────────────────────────────
def get_stress_trend(
    db: Session,
    user_id: int
):

    history = get_user_symptom_history(
        db,
        user_id
    )

    stress_keywords = [

        "stress",
        "anxiety",
        "panic",
        "depression",
        "overthinking"
    ]

    stress_count = 0

    for item in history:

        text = item.symptom.lower()

        if any(
            word in text
            for word in stress_keywords
        ):

            stress_count += 1

    if stress_count >= 10:

        level = "High"

    elif stress_count >= 5:

        level = "Moderate"

    else:

        level = "Low"

    return {

        "stress_mentions": stress_count,
        "stress_level": level
    }


# ─────────────────────────────────────────────
# MEDICINE ADHERENCE
# ─────────────────────────────────────────────
def get_medicine_adherence(
    db: Session,
    user_id: int
):

    logs = db.query(
        DoseLog
    ).filter(
        DoseLog.user_id == user_id
    ).all()

    if not logs:

        return {

            "adherence_percentage": 100,
            "taken": 0,
            "missed": 0
        }

    taken = len([
        log for log in logs
        if log.status == "taken"
    ])

    missed = len([
        log for log in logs
        if log.status == "skipped"
    ])

    total = taken + missed

    adherence = (
        (taken / total) * 100
        if total > 0
        else 100
    )

    return {

        "adherence_percentage": round(
            adherence,
            2
        ),

        "taken": taken,

        "missed": missed
    }


# ─────────────────────────────────────────────
# HEALTH INSIGHTS
# ─────────────────────────────────────────────
def generate_health_insights(
    db: Session,
    user_id: int
):

    recurring = get_recurring_symptoms(
        db,
        user_id
    )

    stress = get_stress_trend(
        db,
        user_id
    )

    adherence = get_medicine_adherence(
        db,
        user_id
    )

    insights = []

    # Recurring symptom insights
    for item in recurring[:3]:

        insights.append(
            f"You reported "
            f"{item['symptom']} "
            f"{item['count']} times recently."
        )

    # Stress insight
    if stress["stress_level"] == "High":

        insights.append(
            "Your stress-related symptoms "
            "appear to be increasing."
        )

    # Medicine adherence insight
    if adherence["adherence_percentage"] < 70:

        insights.append(
            "Your medicine adherence "
            "is below recommended levels."
        )

    if not insights:

        insights.append(
            "Your recent health trends "
            "appear stable."
        )

    return insights