from actions import utils


def test_risk_level():
    data = {"exposure": "no"}
    risk = utils.get_risk_level(data)
    assert risk == "low"

    data = {"exposure": "yes"}
    risk = utils.get_risk_level(data)
    assert risk == "moderate"

    data = {"exposure": "no", "symptoms_symptom1": "yes"}
    risk = utils.get_risk_level(data)
    assert risk == "moderate"

    data = {"exposure": "yes", "symptoms_symptom1": "yes"}
    risk = utils.get_risk_level(data)
    assert risk == "high"

    data = {
        "exposure": "no",
        "symptoms_symptom1": "yes",
        "symptoms_symptom2": "yes",
        "age": "18-39",
    }
    risk = utils.get_risk_level(data)
    assert risk == "moderate"

    data = {
        "exposure": "no",
        "symptoms_symptom1": "yes",
        "symptoms_symptom2": "yes",
        "age": ">65",
    }
    risk = utils.get_risk_level(data)
    assert risk == "high"

    data = {
        "exposure": "no",
        "symptoms_symptom1": "yes",
        "symptoms_symptom2": "yes",
        "symptoms_symptom3": "yes",
        "age": "18-39",
    }
    risk = utils.get_risk_level(data)
    assert risk == "high"
