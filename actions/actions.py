import logging
import uuid
from typing import Any, Dict, List, Optional, Text, Union
from urllib.parse import urlencode, urljoin

import httpx
from rasa_sdk import Tracker
from rasa_sdk.events import AllSlotsReset, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action, FormAction

from actions import config, utils

logger = logging.getLogger(__name__)


class BaseFormAction(FormAction):
    def name(self) -> Text:
        """Unique identifier of the form"""

        return "base_form"

    @property
    def yes_no_data(self) -> Dict[int, Text]:
        return {1: "yes", 2: "no"}

    @property
    def yes_no_maybe_data(self) -> Dict[int, Text]:
        return {1: "yes", 2: "no", 3: "not sure"}

    @staticmethod
    def is_int(value: Text) -> bool:
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
    ) -> Dict[Text, Optional[Text]]:
        """
        Validates that the value is either:
        - One of the values
        - An integer that is one of the keys
        """
        if value and value.lower() in data.values():
            return {field: value}
        elif self.is_int(value) and int(value) in data:
            return {field: data[int(value)]}
        else:
            dispatcher.utter_message(template="utter_incorrect_selection")
            return {field: None}


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

        for slot in slots:
            if not tracker.get_slot(slot):
                return [slot]
        return []

    @property
    def province_data(self) -> Dict[int, Text]:
        with open("data/lookup_tables/provinces.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    @property
    def age_data(self) -> Dict[int, Text]:
        with open("data/lookup_tables/ages.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    @property
    def gender_data(self) -> Dict[int, Text]:
        with open("data/lookup_tables/gender.txt") as f:
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
        return self.validate_generic("age", dispatcher, value, self.age_data)

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
                "location": address,
                "latitude": latitude,
                "longitude": longitude,
                "location_confirm": "yes",
            }

        if not value:
            dispatcher.utter_message(template="utter_incorrect_selection")
            return {"location": None}

        if not config.GOOGLE_PLACES_API_KEY:
            return {
                "location": value,
                "latitude": "null",
                "longitude": "null",
            }

        querystring = urlencode(
            {
                "key": config.GOOGLE_PLACES_API_KEY,
                "input": value,
                "language": "en",
                "inputtype": "textquery",
                "fields": "formatted_address,geometry",
            }
        )

        if hasattr(httpx, "AsyncClient"):
            # from httpx>=0.11.0, the async client is a different class
            HTTPXClient = getattr(httpx, "AsyncClient")
        else:
            HTTPXClient = getattr(httpx, "Client")

        async with HTTPXClient() as client:
            response = await client.get(
                (
                    f"https://maps.googleapis.com"
                    f"/maps/api/place/findplacefromtext/json?{querystring}"
                )
            )
            location = response.json()
            if location["candidates"]:
                formatted_address = location["candidates"][0]["formatted_address"]
                geometry = location["candidates"][0]["geometry"]["location"]
                latitude = geometry["lat"]
                longitude = geometry["lng"]
                return {
                    "location": formatted_address,
                    "latitude": latitude,
                    "longitude": longitude,
                }
            else:
                dispatcher.utter_message(template="utter_incorrect_location")
                return {"location": None}

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
        ">65": ">64",
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

    async def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""
        data = {
            slot: tracker.get_slot(slot)
            for slot in self.SLOTS
            if slot.startswith("symptoms_")
        }
        data.update(
            {"exposure": tracker.get_slot("exposure"), "age": tracker.get_slot("age")}
        )

        risk = utils.get_risk_level(data)

        if config.EVENTSTORE_URL and config.EVENTSTORE_TOKEN:
            url = urljoin(config.EVENTSTORE_URL, "/api/v3/covid19triage/")
            if tracker.get_slot("latitude") and tracker.get_slot("longitude"):
                location = (
                    f'{tracker.get_slot("latitude"):+f}'
                    f'{tracker.get_slot("longitude"):+f}/'
                )
            else:
                location = ""

            post_data = {
                "deduplication_id": uuid.uuid4().hex,
                "msisdn": f'+{tracker.sender_id.lstrip("+")}',
                "source": "WhatsApp",
                "province": f'ZA-{tracker.get_slot("province").upper()}',
                "city": tracker.get_slot("location"),
                "age": self.AGE_MAPPING[tracker.get_slot("age")],
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
                "location": location,
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
                        break
                except httpx.HTTPError as e:
                    if i == config.HTTP_RETRIES - 1:
                        raise e
        dispatcher.utter_message(template=f"utter_risk_{risk}")
        return []


class ActionResetAllButFewSlots(Action):
    def name(self):
        return "action_reset_all_but_few_slots"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        if not tracker.get_slot("terms"):
            dispatcher.utter_message(template="utter_welcome")
        else:
            dispatcher.utter_message(template="utter_welcome_back")

        actions = [AllSlotsReset()]
        carry_over_slots = (
            HealthCheckProfileForm.SLOTS
            + HealthCheckProfileForm.CONDITIONS
            + ["latitude", "longitude"]
        )
        for slot in carry_over_slots:
            actions.append(SlotSet(slot, tracker.get_slot(slot)))
        return actions
