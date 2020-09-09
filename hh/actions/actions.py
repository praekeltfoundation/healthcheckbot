from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from ruamel.yaml import YAML

from base.actions.actions import ActionExit as BaseActionExit
from base.actions.actions import ActionSessionStart as BaseActionSessionStart
from base.actions.actions import HealthCheckForm as BaseHealthCheckForm
from base.actions.actions import HealthCheckProfileForm as BaseHealthCheckProfileForm
from base.actions.actions import HealthCheckTermsForm


class HealthCheckProfileForm(BaseHealthCheckProfileForm):
    SLOTS = ["first_name", "last_name", "age"]

    PERSISTED_SLOTS = [
        "first_name",
        "last_name",
        "gender",
        "province",
        "location",
        "location_confirm",
        "destination",
        "reason",
        "destination_province",
        "university",
        "campus",
        "medical_condition",
    ]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        mappings = super().slot_mappings()
        mappings["first_name"] = [self.from_text()]
        mappings["last_name"] = [self.from_text()]
        mappings["destination"] = [self.from_entity(entity="number"), self.from_text()]
        mappings["reason"] = [self.from_entity(entity="number"), self.from_text()]
        mappings["destination_province"] = [
            self.from_entity(entity="number"),
            self.from_text(),
        ]
        mappings["university"] = [self.from_entity(entity="number"), self.from_text()]
        mappings["campus"] = [self.from_entity(entity="number"), self.from_text()]
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

    @property
    def institution_data(self) -> Dict[Text, Dict[Text, List[Text]]]:
        with open("hh/actions/university_data.yaml") as f:
            return YAML(typ="safe").load(f)

    @staticmethod
    def make_list(items):
        """
        Given a dictionary of items, returns text for a user selectable list
        """
        return "\n".join([f"*{i}.* {v}" for i, v in items.items()])

    def university_list(self, province):
        return {
            i: v
            for i, v in enumerate(
                sorted(self.institution_data[province].keys()), start=1
            )
        }

    def campus_list(self, province, university):
        return {
            i: v
            for i, v in enumerate(
                sorted(self.institution_data[province][university]), start=1
            )
        }

    def validate_destination_province(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        """
        If a valid destination province is selected, also populate list of universities
        """
        result = self.validate_generic(
            "destination_province", dispatcher, value, self.province_data
        )
        province = result.get("destination_province")
        if province:
            result["university_list"] = self.make_list(self.university_list(province))
        return result

    def validate_university(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        university_data = self.university_list(tracker.get_slot("destination_province"))
        result = self.validate_generic("university", dispatcher, value, university_data)
        university = result.get("university")
        if university:
            province = tracker.get_slot("destination_province")
            result["campus_list"] = self.make_list(
                self.campus_list(province, university)
            )
        return result

    def validate_campus(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        province = tracker.get_slot("destination_province")
        university = tracker.get_slot("university")
        campus_data = self.campus_list(province, university)
        return self.validate_generic("campus", dispatcher, value, campus_data)


class HealthCheckForm(BaseHealthCheckForm):
    def get_eventstore_data(self, tracker: Tracker, risk: Text) -> Dict[Text, Any]:
        data = super().get_eventstore_data(tracker, risk)
        data["first_name"] = tracker.get_slot("first_name")
        data["last_name"] = tracker.get_slot("last_name")
        data["data"]["destination"] = tracker.get_slot("destination")
        data["data"]["reason"] = tracker.get_slot("reason")
        return data

    def send_risk_to_user(
        self, dispatcher: CollectingDispatcher, risk: Text, tracker: Tracker
    ) -> None:
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
