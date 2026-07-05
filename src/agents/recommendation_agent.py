from __future__ import annotations

from dataclasses import dataclass

AQI_BREAKPOINTS = [
    (50, "Good"),
    (100, "Satisfactory"),
    (200, "Moderate"),
    (300, "Poor"),
    (400, "Very Poor"),
    (float("inf"), "Severe"),
]

POLLUTANT_ACTIONS = {
    "PM2.5": "Strengthen dust suppression, construction-site sealing, and public transport prioritization.",
    "PM10": "Control road dust, deploy vacuum sweeping, and enforce site-level particulate barriers.",
    "NO2": "Reduce heavy-vehicle corridors and inspect combustion sources near traffic hotspots.",
    "SO2": "Audit industrial emissions and increase stack monitoring in affected zones.",
    "CO": "Restrict idling, tighten vehicle checks, and monitor dense traffic corridors.",
    "O3": "Limit precursor emissions and issue afternoon health advisories during sunlight peaks.",
}


@dataclass
class InterventionPlan:
    city: str
    predicted_aqi: float
    category: str
    risk_level: str
    interventions: list[str]
    health_advisory: str


def get_aqi_category(predicted_aqi: float) -> str:
    for upper_bound, category in AQI_BREAKPOINTS:
        if predicted_aqi <= upper_bound:
            return category
    return "Severe"


def get_risk_level(category: str) -> str:
    mapping = {
        "Good": "Low",
        "Satisfactory": "Low",
        "Moderate": "Moderate",
        "Poor": "High",
        "Very Poor": "Very High",
        "Severe": "Critical",
    }
    return mapping.get(category, "Moderate")


def generate_recommendations(city: str, predicted_aqi: float, dominant_pollutants: list[tuple[str, float]] | None = None) -> InterventionPlan:
    category = get_aqi_category(predicted_aqi)
    risk_level = get_risk_level(category)

    interventions: list[str] = []
    if predicted_aqi > 300:
        interventions.extend([
            "Reduce construction activity in exposed zones.",
            "Restrict heavy vehicle movement during peak hours.",
            "Increase roadside and industrial pollution monitoring.",
        ])
    elif predicted_aqi >= 200:
        interventions.extend([
            "Trigger traffic control measures and congestion reduction.",
            "Issue health warnings for children, elderly citizens, and sensitive groups.",
            "Activate localized monitoring in high-density corridors.",
        ])
    elif predicted_aqi >= 100:
        interventions.extend([
            "Increase inspection frequency near traffic and industrial clusters.",
            "Promote public transport and anti-idling advisories.",
        ])
    else:
        interventions.append("Maintain routine monitoring and preventive controls.")

    if dominant_pollutants:
        for pollutant, share in dominant_pollutants[:3]:
            action = POLLUTANT_ACTIONS.get(pollutant)
            if action:
                interventions.append(f"{pollutant} ({share:.1f}%) - {action}")

    health_advisory = {
        "Low": "Air quality is manageable. Normal outdoor activity is acceptable.",
        "Moderate": "Sensitive groups should reduce prolonged outdoor exertion.",
        "High": "Limit outdoor activity and use masks in traffic-heavy areas.",
        "Very High": "Avoid outdoor exposure, especially for sensitive groups.",
        "Critical": "Restrict outdoor activity and activate public health alerts immediately.",
    }.get(risk_level, "Monitor local alerts and reduce outdoor exposure.")

    return InterventionPlan(
        city=city,
        predicted_aqi=predicted_aqi,
        category=category,
        risk_level=risk_level,
        interventions=interventions,
        health_advisory=health_advisory,
    )
