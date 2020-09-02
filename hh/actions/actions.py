from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Text, Union

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
        "destination",
        "reason",
        "medical_condition",
    ]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        mappings = super().slot_mappings()
        mappings["first_name"] = [self.from_text()]
        mappings["last_name"] = [self.from_text()]
        mappings["destination"] = [self.from_entity(entity="number"), self.from_text()]
        mappings["reason"] = [self.from_entity(entity="number"), self.from_text()]
        return mappings

    @property
    def destination_data(self) -> Dict[int, Text]:
        with open("hh/data/lookup_tables/destinations.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    def validate_destination(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "destination", dispatcher, value, self.destination_data
        )

    @property
    def reason_data(self) -> Dict[int, Text]:
        with open("hh/data/lookup_tables/reasons.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    def validate_reason(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic("reason", dispatcher, value, self.reason_data)


class HealthCheckForm(BaseHealthCheckForm):
    def get_eventstore_data(self, tracker: Tracker, risk: Text) -> Dict[Text, Any]:
        data = super().get_eventstore_data(tracker, risk)
        data["first_name"] = tracker.get_slot("first_name")
        data["last_name"] = tracker.get_slot("last_name")
        data["data"]["destination"] = tracker.get_slot("destination")
        data["data"]["reason"] = tracker.get_slot("reason")
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
        carry_over_slots = ("first_name", "last_name", "destination", "reason")
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
