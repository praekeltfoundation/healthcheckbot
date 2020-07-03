from typing import Any, Dict, Text


def get_risk_level(data: Dict[Any, Any]) -> Text:
    symptoms = 0
    for key, value in data.items():
        if "symptoms_" in key and value == "yes":
            symptoms += 1

    if symptoms >= 3:
        return "high"
    elif symptoms == 2:
        if data["exposure"] == "yes" or data["age"] == ">65":
            return "high"
        else:
            return "moderate"
    elif symptoms == 1:
        if data["exposure"] == "yes":
            return "high"
        else:
            return "moderate"
    else:
        if data["exposure"] == "yes":
            return "moderate"
        else:
            return "low"
