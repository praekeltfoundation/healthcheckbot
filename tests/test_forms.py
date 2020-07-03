import pytest

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet, Form
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.actions import HealthCheckProfileForm


class TestHealthCheckProfileForm:
    def get_tracker_for_number_slot_with_value(self, slot_name, value):
        return Tracker(
            "default",
            {"requested_slot": slot_name},
            {"entities": [{"entity": "number", "value": value}]},
            [],
            False,
            None,
            {},
            "action_listen",
        )

    @pytest.mark.asyncio
    async def test_validate_age(self):
        form = HealthCheckProfileForm()

        tracker = self.get_tracker_for_number_slot_with_value("age", "1")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", "<18")]

        tracker = self.get_tracker_for_number_slot_with_value("age", "2")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", "18-39")]

        tracker = self.get_tracker_for_number_slot_with_value("age", "3")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", "40-65")]

        tracker = self.get_tracker_for_number_slot_with_value("age", "4")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", ">65")]

        tracker = self.get_tracker_for_number_slot_with_value("age", ["2", "39"])
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", None)]
