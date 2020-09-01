from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from base.actions.actions import ActionExit as BaseActionExit
from base.actions.actions import ActionSessionStart as BaseActionSessionStart
from base.actions.actions import HealthCheckForm as BaseHealthCheckForm
from base.actions.actions import HealthCheckProfileForm as BaseHealthCheckProfileForm
from base.actions.actions import HealthCheckTermsForm


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

    def send_risk_to_user(self, dispatcher: CollectingDispatcher, risk: Text) -> None:
        # ZA timezone
        issued = datetime.now(tz=timezone(timedelta(hours=2)))
        expired = issued + timedelta(days=1)
        date_format = "%B %-d, %Y, %-I:%M %p"
        dispatcher.utter_message(
            template=f"utter_risk_{risk}",
            issued=issued.strftime(date_format),
            expired=expired.strftime(date_format),
        )


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
