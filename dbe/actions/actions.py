from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.query import FuzzyTerm, Term

from base.actions.actions import ActionExit
from base.actions.actions import ActionSessionStart as BaseActionSessionStart
from base.actions.actions import HealthCheckForm as BaseHealthCheckForm
from base.actions.actions import HealthCheckProfileForm as BaseHealthCheckProfileForm
from base.actions.actions import HealthCheckTermsForm


class HealthCheckProfileForm(BaseHealthCheckProfileForm):
    PERSISTED_SLOTS = [
        "profile",
        "gender",
        "province",
        "location",
        "location_confirm",
        "school",
        "school_confirm",
        "medical_condition",
    ]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        mappings = super().slot_mappings()
        mappings["school"] = [self.from_text()]
        mappings["school_confirm"] = [
            self.from_entity(entity="number"),
            self.from_intent(intent="affirm", value="yes"),
            self.from_intent(intent="deny", value="no"),
            self.from_text(),
        ]
        mappings["profile"] = [self.from_entity(entity="number"), self.from_text()]
        return mappings

    @property
    def age_data(self) -> Dict[int, Text]:
        with open("dbe/data/lookup_tables/ages.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    def validate_school(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        ix = open_dir("dbe/actions/emis_index")
        parser = MultifieldParser(["name", "emis"], ix.schema, termclass=FuzzyTerm)
        query = parser.parse(value)

        with ix.searcher() as s:
            results = s.search(
                query, limit=1, filter=Term("province", tracker.get_slot("province"))
            )
            if results:
                result = results[0]
                return {
                    "school": result["name"],
                    "school_emis": result["emis"],
                }
            else:
                dispatcher.utter_message(template="utter_incorrect_school")
                return {"school": None, "province": None}

    def validate_school_confirm(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        school_confirm = self.validate_generic(
            "school_confirm", dispatcher, value, self.yes_no_data
        )
        if (
            school_confirm["school_confirm"]
            and school_confirm["school_confirm"] == "no"
        ):
            return {"school_confirm": None, "school": None}
        return school_confirm

    @property
    def profile_data(self) -> Dict[int, Text]:
        with open("dbe/data/lookup_tables/profiles.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    def validate_profile(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic("profile", dispatcher, value, self.profile_data)


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
        data["data"]["school_name"] = tracker.get_slot("school")
        data["data"]["school_emis"] = tracker.get_slot("school_emis")
        data["data"]["profile"] = tracker.get_slot("profile")
        return data

    def send_risk_to_user(self, dispatcher, risk):
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
        carry_over_slots = ("school", "school_confirm", "school_emis")
        for slot in carry_over_slots:
            actions.append(SlotSet(slot, tracker.get_slot(slot)))
        return actions


__all__ = [
    "HealthCheckTermsForm",
    "HealthCheckProfileForm",
    "HealthCheckForm",
    "ActionSessionStart",
    "ActionExit",
    "ActionSessionStart",
]
