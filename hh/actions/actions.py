from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action

from base.actions.actions import (
    ActionExit as BaseActionExit,
    ActionSessionStart as BaseActionSessionStart,
    HealthCheckForm as BaseHealthCheckForm,
    HealthCheckProfileForm as BaseHealthCheckProfileForm,
    HealthCheckTermsForm,
)

class HealthCheckProfileForm(BaseHealthCheckProfileForm):
    PERSISTED_SLOTS = [
        "first_name",
        "last_name",
        "gender",
        "province",
        "location",
        "location_confirm",
        "medical_condition",
    ]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        mappings = super().slot_mappings()
        mappings["first_name"] = [self.from_text()]
        mappings["last_name"] = [self.from_text()]
        return mappings


class HealthCheckForm(BaseHealthCheckForm):
    def get_eventstore_data(self, tracker: Tracker, risk: Text) -> Dict[Text, Any]:
        data = super().get_eventstore_data(tracker, risk)
        data["first_name"] = tracker.get_slot("first_name")
        data["last_name"] = tracker.get_slot("last_name")
        return data

class ActionSessionStart(BaseActionSessionStart):
    def get_carry_over_slots(self, tracker: Tracker) -> List[Dict[Text, Any]]:
        actions = super().get_carry_over_slots(tracker)
        carry_over_slots = ("first_name", "last_name")
        for slot in carry_over_slots:
            actions.append(SlotSet(slot, tracker.get_slot(slot)))
        return actions

class ActionExit(BaseActionExit):
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_exit")
        return ActionSessionStart().get_carry_over_slots(tracker)

__all__ = [
    "HealthCheckTermsForm",
    "HealthCheckProfileForm",
    "HealthCheckForm",
    "ActionSessionStart",
    "ActionExit",
]
