import asyncio
import logging
import re
import uuid
from typing import Any, Dict, List, Optional, Text, Union
from urllib.parse import urlencode, urljoin

import httpx
import sentry_sdk
from rasa_sdk import Tracker
from rasa_sdk.events import ActionExecuted, SessionStarted, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action, FormAction
from sentry_sdk.integrations.logging import LoggingIntegration
from sentry_sdk.integrations.sanic import SanicIntegration

from . import config, utils

logger = logging.getLogger(__name__)

if config.SENTRY_DSN:
    sentry_logging = LoggingIntegration(level=logging.INFO, event_level=logging.ERROR)
    sentry_sdk.init(
        dsn=config.SENTRY_DSN, integrations=[sentry_logging, SanicIntegration()]
    )

YES_NO_DATA = {1: "yes", 2: "no"}


class BaseFormAction(FormAction):
    def name(self) -> Text:
        return "base_form"

    @property
    def yes_no_data(self) -> Dict[int, Text]:
        return YES_NO_DATA

    @property
    def yes_no_maybe_data(self) -> Dict[int, Text]:
        return {1: "yes", 2: "no", 3: "not sure"}

    @staticmethod
    def is_int(value: Text) -> bool:
        if not isinstance(value, str):
            return False

        try:
            int(value)
            return True
        except ValueError:
            return False

    def validate_generic(
        self,
        field: Text,
        dispatcher: CollectingDispatcher,
        value: Text,
        data: Dict[int, Text],
        accept_labels=True,
    ) -> Dict[Text, Optional[Text]]:
        """
        Validates that the value is either:
        - One of the values
        - An integer that is one of the keys
        """
        if (
            accept_labels
            and value
            and isinstance(value, str)
            and value.lower() in data.values()
        ):
            return {field: value}
        elif self.is_int(value) and int(value) in data:
            return {field: data[int(value)]}
        else:
            dispatcher.utter_message(template="utter_incorrect_selection")
            return {field: None}

    @staticmethod
    def format_location(latitude: float, longitude: float) -> Text:
        """
        Returns the location in ISO6709 format
        """

        def fractional_part(f):
            if not f % 1:
                return ""
            parts = str(f).split(".")
            return f".{parts[1]}"

        # latitude integer part must be fixed width 2, longitude 3
        return (
            f"{int(latitude):+03d}"
            f"{fractional_part(latitude)}"
            f"{int(longitude):+04d}"
            f"{fractional_part(longitude)}"
            "/"
        )

    @staticmethod
    def fix_location_format(text: Text) -> Text:
        """
        Previously there was a bug that caused the location to not be stored in
        proper ISO6709 format. This function extracts the latitude and longitude from
        either the incorrect or correct format, and then returns a properly formatted
        ISO6709 string
        """
        if not text:
            return ""
        regex = re.compile(
            r"""
            ^
            (?P<latitude>[\+|-]\d+\.?\d*)
            (?P<longitude>[\+|-]\d+\.?\d*)
            """,
            flags=re.VERBOSE,
        )
        match = regex.match(text)
        if not match:
            raise ValueError(f"Invalid location {text}")
        data = match.groupdict()
        return BaseFormAction.format_location(
            float(data["latitude"]), float(data["longitude"])
        )


class HealthCheckTermsForm(BaseFormAction):
    """HealthCheck form action"""

    SLOTS = [
        "terms",
    ]

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "healthcheck_terms_form"

    @classmethod
    def required_slots(cls, tracker: Tracker) -> List[Text]:
        for slot in cls.SLOTS:
            if not tracker.get_slot(slot):
                return [slot]
        return []

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "terms": [
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="more", value="more"),
                self.from_text(),
            ]
        }

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

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []


class HealthCheckProfileForm(BaseFormAction):
    """HealthCheck form action"""

    SLOTS = ["age"]

    PERSISTED_SLOTS = [
        "gender",
        "province",
        "location",
        "location_confirm",
        "medical_condition",
    ]

    MINOR_SKIP_SLOTS = [
        "location",
        "location_confirm",
        "medical_condition_obesity",
        "medical_condition_diabetes",
        "medical_condition_hypertension",
        "medical_condition_cardio",
    ]

    CONDITIONS = [
        "medical_condition_obesity",
        "medical_condition_diabetes",
        "medical_condition_hypertension",
        "medical_condition_cardio",
    ]

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "healthcheck_profile_form"

    @classmethod
    def required_slots(cls, tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        slots = cls.SLOTS + cls.PERSISTED_SLOTS
        # This is a strange workaround
        # Rasa wants to fill all the slots with every question
        # To prevent that, we just tell Rasa with each message that the slots
        # that it's required to fill is just a single slot, the first
        # slot that hasn't been filled yet.

        # expanded questions when user has underlying medical conditions
        if tracker.get_slot("medical_condition") != "no":
            slots = cls.SLOTS + cls.PERSISTED_SLOTS + cls.CONDITIONS

        if tracker.get_slot("age") == "<18":
            for slot in cls.MINOR_SKIP_SLOTS:
                if slot in slots:
                    slots.remove(slot)

        for slot in slots:
            if not tracker.get_slot(slot):
                return [slot]
        return []

    @property
    def province_data(self) -> Dict[int, Text]:
        with open("base/data/lookup_tables/provinces.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    @property
    def age_data(self) -> Dict[int, Text]:
        with open("base/data/lookup_tables/ages.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    @property
    def gender_data(self) -> Dict[int, Text]:
        with open("base/data/lookup_tables/gender.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "age": [self.from_entity(entity="number"), self.from_text()],
            "gender": [self.from_entity(entity="number"), self.from_text()],
            "province": [
                self.from_entity(entity="number"),
                self.from_entity(intent="inform", entity="province"),
                self.from_text(),
            ],
            "location": [self.from_text()],
            "location_confirm": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "medical_condition": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_intent(intent="maybe", value="not sure"),
                self.from_text(),
            ],
            "medical_condition_obesity": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "medical_condition_diabetes": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "medical_condition_hypertension": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "medical_condition_cardio": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
        }

    def validate_age(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        result = self.validate_generic("age", dispatcher, value, self.age_data)
        if result.get("age") == "<18":
            result["location"] = "<not collected>"
        return result

    def validate_gender(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic("gender", dispatcher, value, self.gender_data)

    def validate_province(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic("province", dispatcher, value, self.province_data)

    async def places_lookup(self, client, search_text, session_token, province):
        locationbias = {
            "ec": "-32.2968402,26.419389",
            "fs": "-28.4541105,26.7967849",
            "gt": "-26.2707593,28.1122679",
            "lp": "-23.4012946,29.4179324",
            "mp": "-25.565336,30.5279096",
            "nc": "-29.0466808,21.8568586",
            "nl": "-28.5305539,30.8958242",
            "nw": "-26.6638599,25.2837585",
            "wc": "-33.2277918,21.8568586",
        }[province]
        querystring = urlencode(
            {
                "key": config.GOOGLE_PLACES_API_KEY,
                "input": search_text,
                "sessiontoken": session_token,
                "language": "en",
                "components": "country:za",
                "location": locationbias,
            }
        )
        url = (
            "https://maps.googleapis.com/maps/api/place/autocomplete/json"
            f"?{querystring}"
        )
        response = (await client.get(url)).json()
        if not response["predictions"]:
            return None
        place_id = response["predictions"][0]["place_id"]

        querystring = urlencode(
            {
                "key": config.GOOGLE_PLACES_API_KEY,
                "place_id": place_id,
                "sessiontoken": session_token,
                "language": "en",
                "fields": "formatted_address,geometry",
            }
        )
        url = f"https://maps.googleapis.com/maps/api/place/details/json?{querystring}"
        response = (await client.get(url)).json()
        return response["result"]

    def get_province(self, tracker):
        return tracker.get_slot("province")

    async def validate_location(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        latest_message = tracker.get_last_event_for("user")
        metadata = latest_message.get("metadata")

        # Use location pin data if submitted
        if metadata and metadata.get("type") == "location":
            latitude = metadata["location"]["latitude"]
            longitude = metadata["location"]["longitude"]
            address = metadata["location"].get("address")
            if not address:
                address = f"GPS: {latitude}, {longitude}"
            return {
                "location_coords": self.format_location(latitude, longitude),
                "location": address,
                "location_confirm": "yes",
            }

        if not value:
            dispatcher.utter_message(template="utter_incorrect_selection")
            return {"location": None}

        if not config.GOOGLE_PLACES_API_KEY:
            return {
                "location": value,
            }

        session_token = uuid.uuid4().hex
        province = self.get_province(tracker)

        if hasattr(httpx, "AsyncClient"):
            # from httpx>=0.11.0, the async client is a different class
            HTTPXClient = getattr(httpx, "AsyncClient")
        else:
            HTTPXClient = getattr(httpx, "Client")

        async with HTTPXClient() as client:
            location = None
            for _ in range(3):
                try:
                    location = await self.places_lookup(
                        client, value, session_token, province
                    )
                    break
                except Exception:
                    pass
            if not location:
                dispatcher.utter_message(template="utter_incorrect_location")
                return {"location": None}
            geometry = location["geometry"]["location"]
            return {
                "location": location["formatted_address"],
                "city_location_coords": self.format_location(
                    geometry["lat"], geometry["lng"]
                ),
            }

    def validate_location_confirm(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        loc_confirm = self.validate_generic(
            "location_confirm", dispatcher, value, self.yes_no_data
        )
        if loc_confirm["location_confirm"] and loc_confirm["location_confirm"] == "no":
            return {"location_confirm": None, "location": None}
        return loc_confirm

    def validate_medical_condition(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "medical_condition", dispatcher, value, self.yes_no_maybe_data
        )

    def validate_medical_condition_obesity(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "medical_condition_obesity", dispatcher, value, self.yes_no_data
        )

    def validate_medical_condition_diabetes(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "medical_condition_diabetes", dispatcher, value, self.yes_no_data
        )

    def validate_medical_condition_hypertension(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "medical_condition_hypertension", dispatcher, value, self.yes_no_data
        )

    def validate_medical_condition_cardio(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "medical_condition_cardio", dispatcher, value, self.yes_no_data
        )

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        return []


class HealthCheckForm(BaseFormAction):
    """HealthCheck form action"""

    SLOTS = [
        "symptoms_fever",
        "symptoms_cough",
        "symptoms_sore_throat",
        "symptoms_difficulty_breathing",
        "symptoms_taste_smell",
        "exposure",
        "tracing",
    ]

    GENDER_MAPPING = {
        "MALE": "male",
        "FEMALE": "female",
        "OTHER": "other",
        "RATHER NOT SAY": "not_say",
    }

    AGE_MAPPING = {
        "<18": "<18",
        "18-39": "18-40",
        "40-65": "40-65",
        ">65": ">65",
    }

    YES_NO_MAYBE_MAPPING = {
        "yes": "yes",
        "no": "no",
        "not sure": "not_sure",
    }

    YES_NO_MAPPING = {
        "yes": True,
        "no": False,
    }

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "healthcheck_form"

    @classmethod
    def required_slots(cls, tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        # This is a strange workaround
        # Rasa wants to fill all the slots with every question
        # To prevent that, we just tell Rasa with each message that the slots
        # that it's required to fill is just a single slot, the first
        # slot that hasn't been filled yet.

        for slot in cls.SLOTS:
            if not tracker.get_slot(slot):
                return [slot]
        return []

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "symptoms_fever": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "symptoms_cough": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "symptoms_sore_throat": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "symptoms_difficulty_breathing": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "symptoms_taste_smell": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
            "exposure": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_intent(intent="maybe", value="not sure"),
                self.from_text(),
            ],
            "tracing": [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ],
        }

    def validate_symptoms_fever(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "symptoms_fever", dispatcher, value, self.yes_no_data
        )

    def validate_symptoms_cough(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "symptoms_cough", dispatcher, value, self.yes_no_data
        )

    def validate_symptoms_sore_throat(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "symptoms_sore_throat", dispatcher, value, self.yes_no_data
        )

    def validate_symptoms_difficulty_breathing(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "symptoms_difficulty_breathing", dispatcher, value, self.yes_no_data
        )

    def validate_symptoms_taste_smell(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "symptoms_taste_smell", dispatcher, value, self.yes_no_data
        )

    def validate_exposure(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "exposure", dispatcher, value, self.yes_no_maybe_data
        )

    def validate_tracing(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic("tracing", dispatcher, value, self.yes_no_data)

    def map_age(self, value: Text) -> Text:
        return self.AGE_MAPPING[value]

    def get_eventstore_data(self, tracker: Tracker, risk: Text) -> Dict[Text, Any]:
        """
        Formats the data from the tracker into the format expected by the event store
        """
        return {
            "deduplication_id": uuid.uuid4().hex,
            "msisdn": f'+{tracker.sender_id.lstrip("+")}',
            "source": "WhatsApp",
            "province": f'ZA-{tracker.get_slot("province").upper()}',
            "city": tracker.get_slot("location"),
            "age": self.map_age(tracker.get_slot("age")),
            "fever": self.YES_NO_MAPPING[tracker.get_slot("symptoms_fever")],
            "cough": self.YES_NO_MAPPING[tracker.get_slot("symptoms_cough")],
            "sore_throat": self.YES_NO_MAPPING[
                tracker.get_slot("symptoms_sore_throat")
            ],
            "difficulty_breathing": self.YES_NO_MAPPING[
                tracker.get_slot("symptoms_difficulty_breathing")
            ],
            "exposure": self.YES_NO_MAYBE_MAPPING[tracker.get_slot("exposure")],
            "tracing": self.YES_NO_MAPPING[tracker.get_slot("tracing")],
            "risk": risk,
            "gender": self.GENDER_MAPPING[tracker.get_slot("gender")],
            "location": self.fix_location_format(tracker.get_slot("location_coords")),
            "city_location": self.fix_location_format(
                tracker.get_slot("city_location_coords")
            ),
            "smell": self.YES_NO_MAPPING[tracker.get_slot("symptoms_taste_smell")],
            "preexisting_condition": self.YES_NO_MAYBE_MAPPING[
                tracker.get_slot("medical_condition")
            ],
            # TODO: Put these 4 fields as columns on the table for a v4 API
            "data": {
                "obesity": self.YES_NO_MAPPING.get(
                    tracker.get_slot("medical_condition_obesity")
                ),
                "diabetes": self.YES_NO_MAPPING.get(
                    tracker.get_slot("medical_condition_diabetes")
                ),
                "hypertension": self.YES_NO_MAPPING.get(
                    tracker.get_slot("medical_condition_hypertension")
                ),
                "cardio": self.YES_NO_MAPPING.get(
                    tracker.get_slot("medical_condition_cardio")
                ),
            },
        }

    def send_risk_to_user(
        self, dispatcher: CollectingDispatcher, risk: Text, tracker: Tracker
    ) -> None:
        dispatcher.utter_message(template=f"utter_risk_{risk}")

    def send_post_risk_prompts(
        self, dispatcher: CollectingDispatcher, risk: Text, tracker: Tracker
    ):
        self.send_tbconnect_prompts(dispatcher, risk, tracker)

    def send_tbconnect_prompts(
        self, dispatcher: CollectingDispatcher, risk: Text, tracker: Tracker
    ):
        if risk == "high":
            return
        if risk == "moderate":
            if tracker.get_slot("symptoms_cough") == "yes":
                dispatcher.utter_message(template="utter_tb_prompt_cough")
            elif tracker.get_slot("symptoms_fever") == "yes":
                dispatcher.utter_message(template="utter_tb_prompt_fever")
            dispatcher.utter_message(template="utter_tb_prompt_moderate")
        if risk == "low":
            dispatcher.utter_message(template="utter_tb_prompt_low_risk_1")
            dispatcher.utter_message(template="utter_tb_prompt_low_risk_2")

    def get_risk_data(self, tracker: Tracker) -> Dict:
        data = {
            slot: tracker.get_slot(slot)
            for slot in self.SLOTS
            if slot.startswith("symptoms_")
        }
        data.update(
            {"exposure": tracker.get_slot("exposure"), "age": tracker.get_slot("age")}
        )
        return data

    async def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        data = self.get_risk_data(tracker)
        risk = utils.get_risk_level(data)
        study_a_arm = None

        if config.EVENTSTORE_URL and config.EVENTSTORE_TOKEN:
            url = urljoin(config.EVENTSTORE_URL, "/api/v5/covid19triage/")

            post_data = self.get_eventstore_data(tracker, risk)
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
                        resp = await client.post(url, json=post_data, headers=headers)
                        resp.raise_for_status()
                        study_a_arm = (
                            resp.json().get("profile", {}).get("hcs_study_a_arm", {})
                        )
                        break
                except httpx.HTTPError as e:
                    if i == config.HTTP_RETRIES - 1:
                        raise e
        self.send_risk_to_user(dispatcher, risk, tracker)
        self.send_post_risk_prompts(dispatcher, risk, tracker)

        return [SlotSet("study_a_arm", study_a_arm)]


class ActionSendStudyMessages(Action):
    def name(self) -> Text:
        return "action_send_study_messages"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        study_a_arm = tracker.get_slot("study_a_arm")
        if study_a_arm and study_a_arm != "C":
            await asyncio.sleep(config.STUDY_A_MESSAGE_DELAY)
            dispatcher.utter_message(template=f"utter_study_a_{study_a_arm}")
        return []


class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    def get_carry_over_slots(self, tracker: Tracker) -> List[Dict[Text, Any]]:
        actions = [SessionStarted()]
        carry_over_slots = (
            HealthCheckTermsForm.SLOTS
            + HealthCheckProfileForm.PERSISTED_SLOTS
            + HealthCheckProfileForm.CONDITIONS
            + ["location_coords", "city_location_coords"]
        )
        for slot in carry_over_slots:
            actions.append(SlotSet(slot, tracker.get_slot(slot)))
        return actions

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        actions = self.get_carry_over_slots(tracker)
        actions.append(ActionExecuted("action_listen"))
        return actions


class ActionExit(Action):
    def name(self) -> Text:
        return "action_exit"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_exit")
        return ActionSessionStart().get_carry_over_slots(tracker)
