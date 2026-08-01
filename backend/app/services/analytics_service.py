from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import Counter
from sqlalchemy.orm import Session  # <-- ADD THIS IMPORT
import statistics

def generate_health_analytics(history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate health analytics from symptom history
    """
    try:
        if not history:
            return {
                "success": True,
                "total_records": 0,
                "message": "No health records found for analytics",
                "analytics": {
                    "severity_distribution": {},
                    "most_common_symptoms": [],
                    "trend": [],
                    "overall_severity": "Unknown"
                }
            }
        
        # Extract data from history
        symptoms = [record.get("symptom", "") for record in history]
        severities = [record.get("severity", "") for record in history]
        dates = [record.get("created_at", "") for record in history]
        
        # Severity distribution
        severity_counts = Counter(severities)
        severity_distribution = {
            "High": severity_counts.get("High", 0) + severity_counts.get("HIGH", 0),
            "Moderate": severity_counts.get("Moderate", 0) + severity_counts.get("MODERATE", 0),
            "Low": severity_counts.get("Low", 0) + severity_counts.get("LOW", 0)
        }
        
        # Most common symptoms
        symptom_counts = Counter(symptoms)
        most_common_symptoms = [
            {"symptom": s, "count": c} 
            for s, c in symptom_counts.most_common(5)
        ]
        
        # Trend analysis (simplified)
        trend = []
        for i, record in enumerate(history[:10]):  # Last 10 records
            trend.append({
                "index": i + 1,
                "severity": record.get("severity", "Unknown"),
                "symptom": record.get("symptom", "")[:30] + "...",
                "date": record.get("created_at", "")
            })
        
        # Overall severity assessment
        severity_scores = {
            "High": 3,
            "Moderate": 2,
            "Low": 1
        }
        
        total_score = sum(severity_scores.get(sev.upper(), 1) for sev in severities)
        avg_severity = total_score / len(severities) if severities else 1
        
        if avg_severity >= 2.5:
            overall_severity = "High"
        elif avg_severity >= 1.5:
            overall_severity = "Moderate"
        else:
            overall_severity = "Low"
        
        return {
            "success": True,
            "total_records": len(history),
            "analytics": {
                "severity_distribution": severity_distribution,
                "most_common_symptoms": most_common_symptoms,
                "trend": trend,
                "overall_severity": overall_severity,
                "average_severity_score": round(avg_severity, 2)
            },
            "message": "Analytics generated successfully"
        }
        
    except Exception as e:
        print(f"Generate health analytics error: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to generate analytics",
            "analytics": {}
        }

def calculate_severity_score(history: List[Dict[str, Any]]) -> float:
    """
    Calculate an overall severity score
    """
    try:
        if not history:
            return 0.0
        
        severity_map = {"HIGH": 3, "MODERATE": 2, "LOW": 1}
        scores = [
            severity_map.get(record.get("severity", "").upper(), 1)
            for record in history
        ]
        
        return sum(scores) / len(scores) if scores else 0.0
        
    except Exception as e:
        print(f"Calculate severity score error: {e}")
        return 0.0

def get_symptom_frequency(history: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Get frequency of symptoms
    """
    try:
        symptoms = [record.get("symptom", "") for record in history]
        return dict(Counter(symptoms))
        
    except Exception as e:
        print(f"Get symptom frequency error: {e}")
        return {}

def get_recent_trend(
    history: List[Dict[str, Any]],
    days: int = 30
) -> List[Dict[str, Any]]:
    """
    Get recent trend analysis
    """
    try:
        # Filter records within the date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_records = [
            record for record in history
            if record.get("created_at") and 
            datetime.fromisoformat(record.get("created_at")) >= cutoff_date
        ]
        
        # Group by date
        daily_counts = {}
        for record in recent_records:
            date_str = record.get("created_at", "").split("T")[0] if record.get("created_at") else ""
            if date_str:
                if date_str not in daily_counts:
                    daily_counts[date_str] = 0
                daily_counts[date_str] += 1
        
        return [
            {"date": date, "count": count}
            for date, count in sorted(daily_counts.items())
        ]
        
    except Exception as e:
        print(f"Get recent trend error: {e}")
        return []

def get_health_summary(
    user_id: int,
    db: Session
) -> Dict[str, Any]:
    """
    Get a comprehensive health summary for a user
    """
    try:
        # Get user health history
        from app.services.adherence_service import get_user_health_history
        history_result = get_user_health_history(db, user_id)
        
        if not history_result.get("success"):
            return {
                "success": False,
                "error": "Failed to fetch health history"
            }
        
        history = history_result.get("history", [])
        
        # Generate analytics
        analytics = generate_health_analytics(history)
        
        return {
            "success": True,
            "user_id": user_id,
            "total_records": len(history),
            "summary": {
                "most_recent_symptom": history[0].get("symptom", "None") if history else "None",
                "most_common_symptom": analytics.get("analytics", {}).get("most_common_symptoms", [{}])[0].get("symptom", "None") if analytics.get("analytics", {}).get("most_common_symptoms") else "None",
                "overall_severity": analytics.get("analytics", {}).get("overall_severity", "Unknown"),
                "records_last_30_days": len([r for r in history if r.get("created_at") and datetime.fromisoformat(r.get("created_at")) >= datetime.utcnow() - timedelta(days=30)])
            },
            "analytics": analytics.get("analytics", {})
        }
        
    except Exception as e:
        print(f"Get health summary error: {e}")
        return {
            "success": False,
            "error": str(e)
        }