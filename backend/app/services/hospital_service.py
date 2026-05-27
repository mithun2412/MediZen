import requests


# ─────────────────────────────────────────────
# DETERMINE HOSPITAL SPECIALIZATION
# ─────────────────────────────────────────────

def detect_specialization(

    symptom_text: str
):

    symptom_text = symptom_text.lower()

    # CARDIOLOGY
    if any(word in symptom_text for word in [

        "chest pain",
        "heart",
        "cardiac",
        "palpitations"
    ]):

        return "cardiology"

    # DERMATOLOGY
    if any(word in symptom_text for word in [

        "skin",
        "rash",
        "acne",
        "eczema",
        "infection",
        "allergy"
    ]):

        return "dermatology"

    # PULMONOLOGY
    if any(word in symptom_text for word in [

        "breathing",
        "asthma",
        "lungs",
        "cough",
        "oxygen"
    ]):

        return "pulmonology"

    # ORTHOPEDIC
    if any(word in symptom_text for word in [

        "bone",
        "fracture",
        "joint",
        "leg pain",
        "back pain"
    ]):

        return "orthopedic"

    # NEUROLOGY
    if any(word in symptom_text for word in [

        "headache",
        "seizure",
        "brain",
        "numbness",
        "dizziness"
    ]):

        return "neurology"

    # DEFAULT
    return "hospital"


# ─────────────────────────────────────────────
# GET NEARBY HOSPITALS
# ─────────────────────────────────────────────

def get_nearby_hospitals(

    latitude: float,

    longitude: float,

    symptoms: str
):

    try:

        # DETECT SPECIALIZATION
        specialization = detect_specialization(
            symptoms
        )

        radius = 5000

        overpass_url = (

            "https://overpass-api.de/api/interpreter"
        )

        # SEARCH QUERY
        query = f"""

        [out:json];

        (
          node
            ["amenity"="hospital"]
            (around:{radius},{latitude},{longitude});

          way
            ["amenity"="hospital"]
            (around:{radius},{latitude},{longitude});

          relation
            ["amenity"="hospital"]
            (around:{radius},{latitude},{longitude});
        );

        out center;
        """

        response = requests.get(

            overpass_url,

            params={"data": query},

            timeout=20
        )

        data = response.json()

        hospitals = []

        for element in data.get(
            "elements",
            []
        )[:15]:

            tags = element.get(
                "tags",
                {}
            )

            hospital_name = tags.get(
                "name",
                "Unknown Hospital"
            )

            lat = element.get("lat")

            lon = element.get("lon")

            # CENTER FOR WAY/RELATION
            if not lat:

                center = element.get(
                    "center",
                    {}
                )

                lat = center.get("lat")

                lon = center.get("lon")

            address_parts = [

                tags.get("addr:street", ""),

                tags.get("addr:city", ""),

                tags.get("addr:state", "")
            ]

            address = ", ".join(

                part for part in address_parts

                if part
            )

            # GOOGLE MAP LINK
            map_link = (

                f"https://www.google.com/maps?q="
                f"{lat},{lon}"
            )

            # HOSPITAL SPECIALIZATION MATCH
            hospital_info = (

                hospital_name.lower()
                + " "
                + str(tags).lower()
            )

            # PRIORITIZE MATCHING SPECIALIZATION
            priority = 0

            if specialization in hospital_info:

                priority = 1

            hospitals.append({

                "name":
                    hospital_name,

                "address":
                    address if address
                    else "Address unavailable",

                "latitude":
                    lat,

                "longitude":
                    lon,

                "map_link":
                    map_link,

                "specialization":
                    specialization,

                "priority":
                    priority
            })

        # SORT SPECIALIZED FIRST
        hospitals = sorted(

            hospitals,

            key=lambda x: x["priority"],

            reverse=True
        )

        return hospitals[:10]

    except Exception as e:

        print(
            "Hospital Service Error:",
            e
        )

        return []