# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import AllSlotsReset, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import Action, FormAction


class HealthCheckForm(FormAction):
    """HealthCheck form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "healthcheck_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""
        slots = ["province", "age", "cough", "exposure", "tracing"]
        # This is a strange workaround
        # Rasa wants to fill all the slots with every question
        # To prevent that, we just tell Rasa with each message that the slots
        # that it's required to fill is just a single slot, the first
        # slot that hasn't been filled yet.
        for slot in slots:
            if not tracker.get_slot(slot):
                return [slot]
        return []

    @property
    def province_data(self) -> Dict[int, Text]:
        with open("data/lookup_tables/provinces.txt") as f:
            return dict(enumerate(f.readlines(), start=1))

    @property
    def age_data(self) -> Dict[int, Text]:
        with open("data/lookup_tables/ages.txt") as f:
            return dict(enumerate(f.readlines(), start=1))

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

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "province": [
                self.from_entity(entity="number"),
                self.from_entity(intent="inform", entity="province"),
                self.from_text(),
            ],
            "age": [self.from_entity(entity="number"), self.from_text()],
            "cough": [
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

    def validate_generic(
        self, dispatcher: CollectingDispatcher, value: Text, data: Dict[int, Text],
    ) -> Dict[Text, Optional[Text]]:
        """
        Validates that the value is either:
        - One of the values
        - An integer that is one of the keys
        """
        if value and value.lower() in data.values():
            return {"province": value}
        elif self.is_int(value) and int(value) in data:
            return {"province": data[int(value)]}
        else:
            dispatcher.utter_message(template="utter_incorrect_selection")
            return {"province": None}

    def validate_province(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(dispatcher, value, self.province_data)

    def validate_age(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(dispatcher, value, self.age_data)

    def validate_cough(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(dispatcher, value, self.yes_no_data)

    def validate_exposure(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(dispatcher, value, self.yes_no_maybe_data)

    def validate_tracing(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(dispatcher, value, self.yes_no_data)

    def submit(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_message(template="utter_submit")
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
        age = tracker.get_slot("age")
        province = tracker.get_slot("province")
        return [AllSlotsReset(), SlotSet("age", age), SlotSet("province", province)]