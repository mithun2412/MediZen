"""Deterministic health analytics.  The LLM receives results, never raw records."""
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session

from app.models.models import HealthAnalytics, MedicationLog, Report, SymptomHistory, SymptomTrend

SEVERITY = {"low": 1, "mild": 1, "moderate": 2, "medium": 2, "high": 3, "severe": 3}


def _severity(value): return SEVERITY.get((value or "low").lower(), 1)
def _trend(values):
    if len(values) < 2: return "Stable"
    recent, previous = sum(values[-7:]) / min(7, len(values)), sum(values[:-7] or values) / len(values[:-7] or values)
    return "Improving" if recent < previous - .15 else "Worsening" if recent > previous + .15 else "Stable"


def _period(logs, days):
    cutoff = datetime.utcnow() - timedelta(days=days)
    selected = [log for log in logs if log.scheduled_time >= cutoff]
    total = len(selected); taken = sum(log.status == "Taken" for log in selected)
    return {"period_days": days, "total": total, "taken": taken, "missed": sum(log.status == "Missed" for log in selected), "pending": sum(log.status == "Pending" for log in selected), "adherence": round(taken / total * 100, 1) if total else 0}


def _streaks(logs):
    # A day counts only when it has at least one scheduled dose and none were missed/pending.
    days = defaultdict(list)
    for log in logs: days[log.scheduled_time.date()].append(log.status)
    complete = sorted(day for day, statuses in days.items() if statuses and all(status == "Taken" for status in statuses))
    current = longest = run = 0; previous = None
    for day in complete:
        run = run + 1 if previous and (day - previous).days == 1 else 1
        longest = max(longest, run); previous = day
    today = datetime.utcnow().date()
    while today in complete:
        current += 1; today -= timedelta(days=1)
    return current, longest


def _report_history(db, user_id):
    reports = db.query(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()).all()
    result = []
    for report in reports[:10]:
        result.append({"id": report.id, "report_date": report.created_at.isoformat(), "report_type": report.title or "Medical report", "summary": report.content or "", "detected_severity": _extract_severity(report.content)})
    return result


def _extract_severity(text):
    text = (text or "").lower()
    return "High" if "high risk" in text or "severe" in text else "Moderate" if "moderate" in text else "Low" if text else None


def calculated_analytics(db: Session, user_id: int):
    logs = db.query(MedicationLog).filter(MedicationLog.user_id == user_id).order_by(MedicationLog.scheduled_time).all()
    symptoms = db.query(SymptomHistory).filter(SymptomHistory.user_id == user_id).order_by(SymptomHistory.started_at).all()
    if not symptoms: symptoms = db.query(SymptomTrend).filter(SymptomTrend.user_id == user_id).order_by(SymptomTrend.recorded_date).all()
    active_symptoms = [s for s in symptoms if getattr(s, "status", "Active") == "Active"]
    names = [(getattr(s, "symptom", None) or getattr(s, "symptom_name", "Unspecified")).strip() for s in symptoms]
    frequency = Counter(names); severities = [_severity(s.severity) for s in symptoms]
    total = len(logs); taken = sum(l.status == "Taken" for l in logs); missed = sum(l.status == "Missed" for l in logs); pending = sum(l.status == "Pending" for l in logs)
    adherence = round(taken / total * 100, 1) if total else 0
    active_severities = [_severity(s.severity) for s in active_symptoms]
    severity_trend = _trend(active_severities); recovery_trend = {"Improving": "Improving", "Worsening": "Declining", "Stable": "Stable"}[severity_trend]
    current, longest = _streaks(logs)
    reports = _report_history(db, user_id)
    symptom_component = 100 - ((sum(active_severities) / len(active_severities) - 1) / 2 * 100) if active_severities else 100
    recovery_component = {"Improving": 100, "Stable": 70, "Worsening": 30}[severity_trend]
    report_component = 100
    health_score = round(max(0, min(100, adherence * .40 + symptom_component * .30 + recovery_component * .20 + report_component * .10)))
    risk = "High" if (active_severities and active_severities[-1] >= 3) or missed >= 5 or severity_trend == "Worsening" else "Medium" if missed >= 2 or (active_severities and active_severities[-1] >= 2) else "Low"
    history = [{"id": s.id, "symptom": getattr(s, "symptom", getattr(s, "symptom_name", "Unspecified")), "status": getattr(s, "status", "Active"), "started_at": (getattr(s, "started_at", None) or getattr(s, "created_at", None)).isoformat(), "resolved_at": s.resolved_at.isoformat() if getattr(s, "resolved_at", None) else None, "recovery_days": (s.resolved_at - (s.started_at or s.created_at)).days if getattr(s, "resolved_at", None) else None} for s in symptoms]
    current_health = [{"id": s.id, "symptom": s.symptom, "severity": s.severity, "started_at": (s.started_at or s.created_at).isoformat()} for s in active_symptoms]
    return {"health_score": health_score, "adherence": adherence, "current_symptoms": current_health, "symptom_history": history, "symptom_frequency": dict(frequency), "symptom_recurrence": [{"symptom": name, "count": count} for name, count in frequency.most_common()], "most_frequent_symptoms": [{"symptom": n, "count": c} for n, c in frequency.most_common(5)], "severity_trend": severity_trend, "recovery_trend": recovery_trend, "risk_level": risk, "medication_statistics": {"total": total, "taken": taken, "missed": missed, "pending": pending, "adherence": adherence, "current_streak": current, "longest_streak": longest}, "weekly_summary": _period(logs, 7), "monthly_summary": _period(logs, 30), "recent_reports": reports}


def generate_ai_insights(calculated):
    """The payload is already calculated; the model is constrained to wording only."""
    fallback = {"summary": f"Medication adherence is {calculated['adherence']}% and symptom severity is {calculated['severity_trend'].lower()}.", "insights": [f"{calculated['medication_statistics']['missed']} medication dose(s) are missed.", f"Risk level is {calculated['risk_level']}."], "recommendations": ["Continue following your clinician's treatment plan."], "risk_explanation": "Risk is based on recorded symptom severity, trend, and missed medication doses."}
    try:
        from app.llm.groq_client import client
        response = client.chat.completions.create(model="llama-3.3-70b-versatile", temperature=0.2, max_tokens=350, messages=[{"role": "system", "content": "You only write supportive, non-diagnostic wording from supplied calculated analytics. Do not calculate, add facts, diagnose, or change numbers. Return JSON with summary, insights, recommendations, risk_explanation."}, {"role": "user", "content": json.dumps(calculated, default=str)}])
        data = json.loads(response.choices[0].message.content.strip().strip("` ").removeprefix("json"))
        return {key: data.get(key, fallback[key]) for key in fallback}
    except Exception: return fallback


def calculate_dashboard(db: Session, user_id: int):
    data = calculated_analytics(db, user_id)
    snapshot = db.query(HealthAnalytics).filter(HealthAnalytics.user_id == user_id).first() or HealthAnalytics(user_id=user_id)
    snapshot.health_score, snapshot.adherence_percentage, snapshot.risk_level = data["health_score"], data["adherence"], data["risk_level"]
    db.add(snapshot); db.commit()
    data["ai_insights"] = generate_ai_insights(data)
    return data


MISSED_DOSE_GRACE_PERIOD = timedelta(minutes=5)


def mark_overdue_medication_logs(db: Session, now=None):
    """Mark a dose missed once it has remained pending for five minutes."""
    # Reminder times are stored as local, timezone-naive datetimes. Compare
    # against the same clock so an IST reminder is not delayed by UTC offset.
    missed_after = (now or datetime.now()) - MISSED_DOSE_GRACE_PERIOD
    changed = db.query(MedicationLog).filter(
        MedicationLog.status == "Pending",
        MedicationLog.scheduled_time <= missed_after,
    ).update({MedicationLog.status: "Missed"}, synchronize_session=False)
    db.commit()
    return changed
