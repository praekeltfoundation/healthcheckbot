import pytest

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet, Form
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction

from actions.actions import HealthCheckProfileForm, HealthCheckTermsForm
from tests import utils


class TestHealthCheckProfileForm:
    @pytest.mark.asyncio
    async def test_validate_age(self):
        form = HealthCheckProfileForm()

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "1")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", "<18")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "2")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", "18-39")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "3")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", "40-65")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "4")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", ">65")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", ["2", "39"])
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", None)]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "not a number")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("age", None)]


class TestHealthCheckTermsForm:
    @pytest.mark.asyncio
    async def test_validate_terms(self):
        form = HealthCheckTermsForm()

        tracker = utils.get_tracker_for_slot_from_intent(form, "terms", "affirm")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("terms", "yes")]

        tracker = utils.get_tracker_for_slot_from_intent(form, "terms", "more")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [SlotSet("terms", None)]
