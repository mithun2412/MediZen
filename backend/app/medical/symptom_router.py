def detect_symptom_category(
    symptom: str
):

    symptom = symptom.lower()

    categories = {

        "chest pain": [

            "chest pain",
            "chest tightness",
            "heart pain",
            "tight chest",
            "pressure in chest"
        ],

        "breathing": [

            "shortness of breath",
            "breathing problem",
            "difficulty breathing",
            "breathless",
            "asthma",
            "wheezing",
            "can't breathe"
        ],

        "headache": [

            "headache",
            "migraine",
            "head pain"
        ],

        "fever": [

            "fever",
            "temperature",
            "cold",
            "flu",
            "chills"
        ],

        "stomach": [

            "stomach",
            "vomit",
            "nausea",
            "diarrhea",
            "abdominal pain"
        ],

        "mental_health": [

            "stress",
            "anxiety",
            "panic",
            "depression"
        ]
    }

    for category, keywords in categories.items():

        for keyword in keywords:

            if keyword in symptom:

                return category

    return "default"