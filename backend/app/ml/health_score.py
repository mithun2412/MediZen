from app.medical.symptom_analytics import (
    get_recurring_symptoms,
    get_stress_trend,
    get_medicine_adherence
)


# ─────────────────────────────────────────────
# HEALTH SCORE ENGINE
# ─────────────────────────────────────────────
def calculate_health_score(
    db,
    user_id: int
):

    score = 100

    insights = []

    # =========================================
    # RECURRING SYMPTOMS
    # =========================================
    recurring = get_recurring_symptoms(
        db,
        user_id
    )

    recurring_count = len(recurring)

    if recurring_count >= 5:

        score -= 25

        insights.append(
            "Multiple recurring symptoms detected."
        )

    elif recurring_count >= 3:

        score -= 15

        insights.append(
            "Several recurring health issues found."
        )

    elif recurring_count >= 1:

        score -= 5

        insights.append(
            "Minor recurring symptoms observed."
        )

    # =========================================
    # STRESS TREND
    # =========================================
    stress = get_stress_trend(
        db,
        user_id
    )

    if stress["stress_level"] == "High":

        score -= 20

        insights.append(
            "Stress levels appear high."
        )

    elif stress["stress_level"] == "Moderate":

        score -= 10

        insights.append(
            "Moderate stress patterns detected."
        )

    # =========================================
    # MEDICINE ADHERENCE
    # =========================================
    adherence = get_medicine_adherence(
        db,
        user_id
    )

    adherence_percentage = adherence[
        "adherence_percentage"
    ]

    if adherence_percentage < 50:

        score -= 25

        insights.append(
            "Medicine adherence is very low."
        )

    elif adherence_percentage < 75:

        score -= 10

        insights.append(
            "Medicine adherence needs improvement."
        )

    # =========================================
    # SCORE LIMITS
    # =========================================
    score = max(0, min(score, 100))

    # =========================================
    # RISK LEVEL
    # =========================================
    if score >= 85:

        risk_level = "Low"

    elif score >= 65:

        risk_level = "Moderate"

    elif score >= 40:

        risk_level = "High"

    else:

        risk_level = "Critical"

    # =========================================
    # STRESS SCORE
    # =========================================
    stress_score = max(

        0,

        100 - (
            stress["stress_mentions"] * 5
        )
    )

    # =========================================
    # FINAL RESPONSE
    # =========================================
    return {

        "health_score": score,

        "risk_level": risk_level,

        "stress_score": stress_score,

        "medicine_adherence": adherence_percentage,

        "recurring_symptoms": recurring,

        "insights": insights
    }