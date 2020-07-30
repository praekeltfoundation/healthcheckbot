from typing import Any, Dict, Text

from rasa_sdk import Tracker

from base.actions.actions import ActionExit, ActionSessionStart
from base.actions.actions import HealthCheckForm as BaseHealthCheckForm
from base.actions.actions import HealthCheckProfileForm as BaseHealthCheckProfileForm
from base.actions.actions import HealthCheckTermsForm


class HealthCheckProfileForm(BaseHealthCheckProfileForm):
    @property
    def age_data(self) -> Dict[int, Text]:
        print("in new ages")
        with open("dbe/data/lookup_tables/ages.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))


class HealthCheckForm(BaseHealthCheckForm):
    AGE_MAPPING = {
        "<18": "<18",
        "18-39": "18-40",
        "40-49": "40-65",
        "50-59": "40-65",
        "60-65": "40-65",
        ">65": ">65",
    }

    def get_eventstore_data(self, tracker: Tracker, risk: Text) -> Dict[Text, Any]:
        # Add the original value for `age` to `data`
        data = super().get_eventstore_data(tracker, risk)
        data["data"]["age"] = tracker.get_slot("age")
        return data


__all__ = [
    "HealthCheckTermsForm",
    "HealthCheckProfileForm",
    "HealthCheckForm",
    "ActionSessionStart",
    "ActionExit",
]
