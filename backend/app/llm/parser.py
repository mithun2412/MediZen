import json
import re


# ─────────────────────────────────────────────
# CLEAN JSON RESPONSE
# ─────────────────────────────────────────────
def clean_json_response(
    raw: str
):

    try:

        # remove markdown blocks
        raw = re.sub(
            r"```json",
            "",
            raw
        )

        raw = re.sub(
            r"```",
            "",
            raw
        )

        raw = raw.strip()

        # find first {
        start = raw.find("{")

        # find last }
        end = raw.rfind("}")

        if start == -1 or end == -1:

            return {}

        raw = raw[start:end + 1]

        return json.loads(raw)

    except Exception as e:

        print(
            "JSON CLEAN ERROR:",
            e
        )

        print(
            "RAW RESPONSE:",
            raw
        )

        return {}


# ─────────────────────────────────────────────
# VALIDATE ANALYSIS
# ─────────────────────────────────────────────
def validate_analysis(
    analysis: dict
):

    if not isinstance(
        analysis,
        dict
    ):

        analysis = {}

    return {

        "possible_conditions":
            analysis.get(
                "possible_conditions",
                []
            ),

        "severity":
            analysis.get(
                "severity",
                "Low"
            ),

        "is_emergency":
            analysis.get(
                "is_emergency",
                False
            ),

        "medications":
            analysis.get(
                "medications",
                []
            ),

        "remedies":
            analysis.get(
                "remedies",
                []
            ),

        "when_to_see_doctor":
            analysis.get(
                "when_to_see_doctor",
                ""
            ),

        "doctor_advice":
            analysis.get(
                "doctor_advice",
                ""
            ),

        "tests":
            analysis.get(
                "tests",
                []
            )
    }