import difflib
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Text, Union
from urllib.parse import urlencode, urljoin

import httpx
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action
from ruamel.yaml import YAML

from base.actions.actions import BaseFormAction
from base.actions.actions import ActionExit as BaseActionExit
from base.actions.actions import ActionSessionStart as BaseActionSessionStart
from base.actions.actions import HealthCheckForm as BaseHealthCheckForm
from base.actions.actions import HealthCheckProfileForm as BaseHealthCheckProfileForm
from base.actions.actions import HealthCheckTermsForm as BaseHealthCheckTermsForm
from base.actions import config


class HealthCheckTermsForm(BaseHealthCheckTermsForm):
    def validate_terms(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        if value == "more":
            dispatcher.utter_message(template="utter_more_terms")
            dispatcher.utter_message(template="utter_more_terms_doc")
            return {"terms": None}

        return self.validate_generic("terms", dispatcher, value, {1: "yes"})


class HealthCheckProfileForm(BaseHealthCheckProfileForm):
    SLOTS = ["age"]

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
        "university_confirm",
        "campus",
        "medical_condition",
        "vaccine_uptake",
    ]
    MINOR_SKIP_SLOTS = ["first_name", "last_name", "location", "location_confirm"]

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
        mappings["university"] = [self.from_text()]
        mappings["university_confirm"] = [
            self.from_entity(entity="number"),
            self.from_text(),
        ]
        mappings["campus"] = [self.from_entity(entity="number"), self.from_text()]
        mappings["vaccine_uptake"] = [
            self.from_entity(entity="number"),
            self.from_text(),
        ]
        return mappings

    @property
    def destination_data(self) -> Dict[int, Text]:
        with open("hh/data/lookup_tables/destinations.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    @property
    def vaccine_uptake_data(self) -> Dict[int, Text]:
        return {1: "partially", 2: "fully", 3: "not"}

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

    def university_list(self, province, search_term):
        # Use this mapping, so that we can do a lower case comparison
        universities = {v.lower(): v for v in self.institution_data[province].keys()}
        matches = difflib.get_close_matches(search_term.lower(), universities, 5, 0.0)
        return {i: universities[v] for i, v in enumerate(matches, start=1)}

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
        return self.validate_generic(
            "destination_province", dispatcher, value, self.province_data
        )

    def validate_university(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        university_data = self.university_list(
            tracker.get_slot("destination_province"), value
        )
        return {"university": value, "university_list": self.make_list(university_data)}

    def validate_university_confirm(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        province = tracker.get_slot("destination_province")
        university_data = self.university_list(province, tracker.get_slot("university"))
        data = self.validate_generic(
            "university_confirm", dispatcher, value, university_data
        )
        if data.get("university_confirm"):
            campus_data = self.campus_list(province, data["university_confirm"])
            data["campus_list"] = self.make_list(campus_data)
        return data

    def validate_vaccine_uptake(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        data = self.validate_generic(
            "vaccine_uptake", dispatcher, value, self.vaccine_uptake_data
        )
        if data.get("vaccine_uptake") == "not":
            dispatcher.utter_message(template="utter_not_vaccinated")
        # Convert to uppercase to be consistent with other channels
        # Check that it's a string first for safety
        if isinstance(data["vaccine_uptake"], str):
            data["vaccine_uptake"] = data["vaccine_uptake"].upper()
        return data

    def validate_campus(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        province = tracker.get_slot("destination_province")
        university = tracker.get_slot("university_confirm")
        campus_data = self.campus_list(province, university)
        return self.validate_generic("campus", dispatcher, value, campus_data)


class HealthCheckForm(BaseHealthCheckForm):
    def get_eventstore_data(self, tracker: Tracker, risk: Text) -> Dict[Text, Any]:
        data = super().get_eventstore_data(tracker, risk)
        data["first_name"] = tracker.get_slot("first_name")
        data["last_name"] = tracker.get_slot("last_name")
        data["data"]["destination"] = tracker.get_slot("destination")
        data["data"]["reason"] = tracker.get_slot("reason")
        data["data"][
            "destination_province"
        ] = f'ZA-{tracker.get_slot("destination_province").upper()}'
        data["data"]["university"] = {"name": tracker.get_slot("university_confirm")}
        data["data"]["campus"] = {"name": tracker.get_slot("campus")}
        data["data"]["vaccine_uptake"] = tracker.get_slot("vaccine_uptake")
        study_b_data = self.get_study_b_data(tracker)
        if study_b_data:
            data["data"].update(study_b_data)
        return data

    def send_risk_to_user(
        self, dispatcher: CollectingDispatcher, risk: Text, tracker: Tracker
    ) -> None:
        # ZA timezone
        issued = datetime.now(tz=timezone(timedelta(hours=2)))
        expired = issued + timedelta(days=1)
        date_format = "%B %-d, %Y, %-I:%M %p"
        if tracker.get_slot("first_name") and tracker.get_slot("last_name"):
            full_name = (
                tracker.get_slot("first_name") + " " + tracker.get_slot("last_name")
            )
        else:
            full_name = "Not captured"
        dispatcher.utter_message(
            template=f"utter_risk_{risk}",
            name=full_name,
            issued=issued.strftime(date_format),
            expired=expired.strftime(date_format),
        )

    def get_study_b_data(self, tracker: Tracker):
        arm = tracker.get_slot("study_b_arm")
        if arm:
            honesty = tracker.get_slot(f"honesty_{arm.lower()}")
            return {
                "hcs_study_b_arm": arm,
                "hcs_study_b_honesty": honesty
            }

    def send_post_risk_prompts(
        self, dispatcher: CollectingDispatcher, risk: Text, tracker: Tracker
    ):
        self.send_tbconnect_prompts(dispatcher, risk, tracker)


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


class HonestyCheckForm(BaseFormAction):
    """HonestyCheck form action"""

    SLOTS = [
        "honesty_t1",
        "honesty_t2",
        "honesty_t3",
    ]

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "honesty_check_form"

    @classmethod
    def required_slots(cls, tracker: Tracker) -> List[Text]:
        arm = tracker.get_slot("study_b_arm")
        if arm:
            arm = arm.lower()
            if arm == "c":
                return []
            return [f"honesty_{arm}"]
        return []

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "honesty_t1": [
                self.from_intent(intent="affirm", value="yes"),
                self.from_text(),
            ],
            "honesty_t2": [
                self.from_intent(intent="affirm", value="yes"),
                self.from_text(),
            ],
            "honesty_t3": [
                self.from_intent(intent="affirm", value="yes"),
                self.from_text(),
            ],
        }

    def validate_honesty_t1(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:

        return self.validate_generic(
            "honesty_t1", dispatcher, value, self.yes_no_data
        )

    def validate_honesty_t2(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:

        return self.validate_generic(
            "honesty_t2", dispatcher, value, self.yes_no_data
        )

    def validate_honesty_t3(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:

        return self.validate_generic(
            "honesty_t3", dispatcher, value, self.yes_no_data
        )

    async def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        return []


class ActionAssignStudyBArm(Action):
    def name(self) -> Text:
        return "action_assign_study_b_arm"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        arm = tracker.get_slot("study_b_arm")
        if not arm:
            data = {
                # "msisdn": f'+{tracker.sender_id.lstrip("+")}'
                "source": "WhatsApp",
                "msisdn": "+27726078747",
                "province": f'ZA-{tracker.get_slot("destination_province").upper()}',
            }
            resp = await self.call_event_store(data)
            arm = resp.get("study_b_arm")
            return [SlotSet("study_b_arm", arm)]
        return []

    async def call_event_store(self, data):
        if config.EVENTSTORE_URL and config.EVENTSTORE_TOKEN:
            url = urljoin(config.EVENTSTORE_URL, "/api/v2/hcsstudybrandomarm/")

            headers = {
                "Authorization": f"Token {config.EVENTSTORE_TOKEN}",
                "User-Agent": "rasa/covid19-healthcheckbot",
            }

            if hasattr(httpx, "AsyncClient"):
                # from httpx>=0.11.0, the async client is a different class
                HTTPXClient = getattr(httpx, "AsyncClient")
            else:
                HTTPXClient = getattr(httpx, "Client")

            for i in range(config.HTTP_RETRIES):
                try:
                    async with HTTPXClient() as client:
                        resp = await client.post(url, json=data, headers=headers)
                        resp.raise_for_status()
                        return resp.json()
                except httpx.HTTPError as e:
                    if i == config.HTTP_RETRIES - 1:
                        raise e


class ActionSendStudyMessages(Action):
    def name(self) -> Text:
        return "action_send_study_messages"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        return []


__all__ = [
    "HealthCheckTermsForm",
    "HealthCheckProfileForm",
    "HonestyCheckForm",
    "HealthCheckForm",
    "ActionSendStudyMessages",
    "ActionSessionStart",
    "ActionExit",
]
