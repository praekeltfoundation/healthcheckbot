import json
from typing import Any, Dict, Optional, Text
from urllib.parse import urlencode

import httpx
import pytest
import respx
from rasa_sdk import Tracker
from rasa_sdk.events import ActionExecuted, Form, SessionStarted, SlotSet
from rasa_sdk.executor import CollectingDispatcher

import base.actions.actions
from base.actions.actions import (
    ActionExit,
    ActionSessionStart,
    HealthCheckForm,
    HealthCheckProfileForm,
    HealthCheckTermsForm,
)
from base.tests import utils


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

    def get_tracker_for_text_slot_with_message(
        self, slot_name: Text, text: Text, msg: Optional[Dict[Text, Any]] = None
    ):
        msgs = [{"event": "user", "metadata": msg or dict()}]

        return Tracker(
            "default",
            {"requested_slot": slot_name},
            {"text": text},
            msgs,
            False,
            None,
            {},
            "action_listen",
        )

    def test_required_slots_end(self):
        """
        If there are no more slots to fill, should return an empty list
        """
        form = HealthCheckProfileForm()
        tracker = utils.get_tracker_for_number_slot_with_value(
            form,
            "age",
            "1",
            {
                "age": "18-40",
                "gender": "male",
                "province": "wc",
                "location": "Cape Town, South Africa",
                "location_confirm": "yes",
                "medical_condition": "no",
            },
        )
        assert form.required_slots(tracker) == []

    @pytest.mark.asyncio
    async def test_validate_age(self):
        form = HealthCheckProfileForm()
        dispatcher = CollectingDispatcher()

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "1")
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [SlotSet("age", "<18"), SlotSet("requested_slot", "gender")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "2")
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [SlotSet("age", "18-39"), SlotSet("requested_slot", "gender")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "3")
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [SlotSet("age", "40-65"), SlotSet("requested_slot", "gender")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", "4")
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [SlotSet("age", ">65"), SlotSet("requested_slot", "gender")]

        tracker = utils.get_tracker_for_number_slot_with_value(form, "age", ["2", "39"])
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [SlotSet("age", None), SlotSet("requested_slot", "age")]

        tracker = utils.get_tracker_for_number_slot_with_value(
            form, "age", "not a number"
        )
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [SlotSet("age", None), SlotSet("requested_slot", "age")]

    @pytest.mark.asyncio
    async def test_validate_gender(self):
        form = HealthCheckProfileForm()
        dispatcher = CollectingDispatcher()

        tracker = utils.get_tracker_for_number_slot_with_value(
            form, "gender", "1", {"age": "18-39"}
        )
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [
            SlotSet("gender", "MALE"),
            SlotSet("requested_slot", "province"),
        ]

        tracker = utils.get_tracker_for_number_slot_with_value(
            form, "gender", "2", {"age": "18-39"}
        )
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [
            SlotSet("gender", "FEMALE"),
            SlotSet("requested_slot", "province"),
        ]

        tracker = utils.get_tracker_for_number_slot_with_value(
            form, "gender", "3", {"age": "18-39"}
        )
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [
            SlotSet("gender", "OTHER"),
            SlotSet("requested_slot", "province"),
        ]

        tracker = utils.get_tracker_for_number_slot_with_value(
            form, "gender", "4", {"age": "18-39"}
        )
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [
            SlotSet("gender", "RATHER NOT SAY"),
            SlotSet("requested_slot", "province"),
        ]

    @pytest.mark.asyncio
    async def test_validate_province(self):
        form = HealthCheckProfileForm()
        dispatcher = CollectingDispatcher()

        i = 1
        for p in ["ec", "fs", "gt", "nl", "lp", "mp", "nw", "nc", "wc"]:
            tracker = utils.get_tracker_for_number_slot_with_value(
                form, "province", str(i), {"age": "18-39", "gender": "MALE"}
            )
            events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
            assert events == [
                SlotSet("province", p),
                SlotSet("requested_slot", "location"),
            ]
            i += 1

    def test_format_location(self):
        """
        Ensures that the location pin is returned in ISO6709 format
        """
        assert HealthCheckProfileForm.format_location(0, 0) == "+00+000/"
        assert HealthCheckProfileForm.format_location(-1, -1) == "-01-001/"
        assert (
            HealthCheckProfileForm.format_location(1.234, -5.678) == "+01.234-005.678/"
        )
        assert (
            HealthCheckProfileForm.format_location(-12.34, 123.456) == "-12.34+123.456/"
        )
        assert (
            HealthCheckProfileForm.format_location(51.481845, 7.216236)
            == "+51.481845+007.216236/"
        )

    def test_fix_location_format(self):
        """
        Ensures that both correct and incorrect location pins are returned in ISO6709
        format
        """
        test_pairs = (
            ("+0+0/", "+00+000/"),
            ("-1-1/", "-01-001/"),
            ("+1.234-5.678/", "+01.234-005.678/"),
            ("-12.34+123.456/", "-12.34+123.456/"),
            ("+51.481845+7.216236/", "+51.481845+007.216236/"),
        )
        for (invalid, valid) in test_pairs:
            assert HealthCheckProfileForm.fix_location_format(invalid) == valid
            assert HealthCheckProfileForm.fix_location_format(valid) == valid

        error = None
        try:
            HealthCheckProfileForm.fix_location_format("invalid")
        except ValueError as e:
            error = e
        assert error

    @pytest.mark.asyncio
    async def test_validate_location_pin(self):
        """
        If a location pin is sent, it should be stored
        """
        form = HealthCheckProfileForm()

        tracker = self.get_tracker_for_text_slot_with_message(
            "location",
            "",
            {"type": "location", "location": {"latitude": 1.23, "longitude": 4.56}},
        )
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [
            SlotSet("location", "GPS: 1.23, 4.56"),
            SlotSet("location_coords", "+01.23+004.56/"),
            SlotSet("location_confirm", "yes"),
        ]

    @pytest.mark.asyncio
    async def test_validate_location_blank_text(self):
        """
        If a message without text content is sent, the error message should be displayed
        """
        form = HealthCheckProfileForm()

        tracker = self.get_tracker_for_text_slot_with_message("location", "")
        dispatcher = CollectingDispatcher()
        events = await form.validate(dispatcher, tracker, {})
        assert events == [
            SlotSet("location", None),
        ]
        [message] = dispatcher.messages
        assert message["template"] == "utter_incorrect_selection"

    @pytest.mark.asyncio
    async def test_validate_location_text(self):
        """
        If there's no google places API credentials, then just use the text
        """
        form = HealthCheckProfileForm()

        tracker = self.get_tracker_for_text_slot_with_message("location", "Cape Town",)

        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [
            SlotSet("location", "Cape Town"),
        ]

    @respx.mock
    @pytest.mark.asyncio
    async def test_validate_location_google_places(self):
        """
        If there's are google places API credentials, then do a lookup
        """
        base.actions.actions.config.GOOGLE_PLACES_API_KEY = "test_key"
        querystring = urlencode(
            {
                "key": "test_key",
                "input": "Cape Town",
                "language": "en",
                "inputtype": "textquery",
                "fields": "formatted_address,geometry",
            }
        )
        request = respx.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
            f"{querystring}",
            content=json.dumps(
                {
                    "candidates": [
                        {
                            "formatted_address": "Cape Town, South Africa",
                            "geometry": {"location": {"lat": 1.23, "lng": 4.56}},
                        }
                    ]
                }
            ),
        )
        form = HealthCheckProfileForm()

        tracker = self.get_tracker_for_text_slot_with_message("location", "Cape Town",)

        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [
            SlotSet("location", "Cape Town, South Africa"),
            SlotSet("city_location_coords", "+01.23+004.56/"),
        ]
        assert request.called

        base.actions.actions.config.GOOGLE_PLACES_API_KEY = None

    @respx.mock
    @pytest.mark.asyncio
    async def test_validate_location_google_places_no_results(self):
        """
        If there are no results, then display error message and ask again
        """
        base.actions.actions.config.GOOGLE_PLACES_API_KEY = "test_key"
        querystring = urlencode(
            {
                "key": "test_key",
                "input": "Cape Town",
                "language": "en",
                "inputtype": "textquery",
                "fields": "formatted_address,geometry",
            }
        )
        request = respx.get(
            "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"
            f"{querystring}",
            content=json.dumps({"candidates": []}),
        )
        form = HealthCheckProfileForm()

        tracker = self.get_tracker_for_text_slot_with_message("location", "Cape Town",)

        dispatcher = CollectingDispatcher()
        events = await form.validate(dispatcher, tracker, {})
        assert events == [
            SlotSet("location", None),
        ]
        assert request.called

        [message] = dispatcher.messages
        assert message["template"] == "utter_incorrect_location"

        base.actions.actions.config.GOOGLE_PLACES_API_KEY = None

    @pytest.mark.asyncio
    async def test_validate_location_confirm(self):
        """
        Should reset answers if user selects no
        """
        form = HealthCheckProfileForm()
        tracker = self.get_tracker_for_text_slot_with_message("location_confirm", "yes")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [
            SlotSet("location_confirm", "yes"),
        ]

        tracker = self.get_tracker_for_text_slot_with_message("location_confirm", "no")
        events = await form.validate(CollectingDispatcher(), tracker, {})
        assert events == [
            SlotSet("location_confirm", None),
            SlotSet("location", None),
        ]

    @pytest.mark.asyncio
    async def test_validate_yes_no_maybe(self):
        """
        Tests that yes no maybe slots validate correctly
        """
        form = HealthCheckProfileForm()
        for slot in ["medical_condition"]:
            tracker = self.get_tracker_for_text_slot_with_message(slot, "yes")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "yes"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "no")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "no"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "not sure")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "not sure"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "Invalid")
            dispatcher = CollectingDispatcher()
            events = await form.validate(dispatcher, tracker, {})
            assert events == [
                SlotSet(slot, None),
            ]
            [message] = dispatcher.messages
            assert message["template"] == "utter_incorrect_selection"

    @pytest.mark.asyncio
    async def test_validate_yes_no(self):
        """
        Tests that yes no slots validate correctly
        """
        form = HealthCheckProfileForm()
        for slot in [
            "medical_condition_obesity",
            "medical_condition_diabetes",
            "medical_condition_hypertension",
            "medical_condition_cardio",
        ]:
            tracker = self.get_tracker_for_text_slot_with_message(slot, "yes")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "yes"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "no")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "no"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "Invalid")
            dispatcher = CollectingDispatcher()
            events = await form.validate(dispatcher, tracker, {})
            assert events == [
                SlotSet(slot, None),
            ]
            [message] = dispatcher.messages
            assert message["template"] == "utter_incorrect_selection"

    def test_complete_form(self):
        """
        Should do nothing
        """
        form = HealthCheckProfileForm()
        dispatcher = CollectingDispatcher()
        tracker = utils.get_tracker_for_slot_from_intent(
            form, "medical_condition", "no",
        )
        result = form.submit(dispatcher, tracker, {})
        assert result == []


class TestHealthCheckTermsForm:
    @pytest.mark.asyncio
    async def test_validate_terms(self):
        form = HealthCheckTermsForm()
        dispatcher = CollectingDispatcher()

        tracker = utils.get_tracker_for_slot_from_intent(form, "terms", "affirm")
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert form.required_slots(tracker) == ["terms"]
        assert events == [
            SlotSet("terms", "yes"),
            Form(None),
            SlotSet("requested_slot", None),
        ]

        tracker = utils.get_tracker_for_slot_from_intent(form, "terms", "more")
        events = await form.run(dispatcher=dispatcher, tracker=tracker, domain=None)
        assert events == [SlotSet("terms", None), SlotSet("requested_slot", "terms")]


class TestHealthCheckForm:
    def get_tracker_for_text_slot_with_message(
        self, slot_name: Text, text: Text, msg: Optional[Dict[Text, Any]] = None
    ):
        msgs = [{"event": "user", "metadata": msg or dict()}]

        return Tracker(
            "default",
            {"requested_slot": slot_name},
            {"text": text},
            msgs,
            False,
            None,
            {},
            "action_listen",
        )

    def test_required_slots_end(self):
        """
        If there are no more slots to fill, should return an empty list
        """
        form = HealthCheckForm()
        tracker = utils.get_tracker_for_number_slot_with_value(
            form,
            "age",
            "1",
            {
                "symptoms_fever": "no",
                "symptoms_cough": "no",
                "symptoms_sore_throat": "no",
                "symptoms_difficulty_breathing": "no",
                "symptoms_taste_smell": "no",
                "exposure": "no",
                "tracing": "yes",
            },
        )
        assert form.required_slots(tracker) == []

    @respx.mock
    @pytest.mark.asyncio
    async def test_submit_to_eventstore(self):
        """
        Submits the data to the eventstore in the correct format
        """
        base.actions.actions.config.EVENTSTORE_URL = "https://eventstore"
        base.actions.actions.config.EVENTSTORE_TOKEN = "token"

        request = respx.post("https://eventstore/api/v3/covid19triage/")

        form = HealthCheckForm()
        dispatcher = CollectingDispatcher()
        tracker = utils.get_tracker_for_slot_from_intent(
            form,
            "tracing",
            "affirm",
            {
                "province": "wc",
                "age": "18-39",
                "symptoms_fever": "no",
                "symptoms_cough": "no",
                "symptoms_sore_throat": "yes",
                "symptoms_difficulty_breathing": "no",
                "symptoms_taste_smell": "no",
                "exposure": "not sure",
                "tracing": "yes",
                "gender": "RATHER NOT SAY",
                "medical_condition": "not sure",
                "city_location_coords": "+1.2-3.4",
                "location_coords": "+3.4-1.2",
                "location": "Cape Town, South Africa",
            },
        )
        await form.submit(dispatcher, tracker, {})

        assert request.called
        [(request, response)] = request.calls
        data = json.loads(request.stream.body)
        assert data.pop("deduplication_id")
        assert data == {
            "province": "ZA-WC",
            "age": "18-40",
            "fever": False,
            "cough": False,
            "sore_throat": True,
            "difficulty_breathing": False,
            "smell": False,
            "exposure": "not_sure",
            "tracing": True,
            "gender": "not_say",
            "preexisting_condition": "not_sure",
            "city_location": "+01.2-003.4/",
            "location": "+03.4-001.2/",
            "city": "Cape Town, South Africa",
            "msisdn": "+default",
            "risk": "moderate",
            "source": "WhatsApp",
            "data": {
                "cardio": None,
                "diabetes": None,
                "hypertension": None,
                "obesity": None,
            },
        }

        base.actions.actions.config.EVENTSTORE_URL = None
        base.actions.actions.config.EVENTSTORE_TOKEN = None

    @respx.mock
    @pytest.mark.asyncio
    async def test_submit_to_eventstore_retries(self):
        """
        Should retry on HTTP failures
        """
        base.actions.actions.config.EVENTSTORE_URL = "https://eventstore"
        base.actions.actions.config.EVENTSTORE_TOKEN = "token"

        request = respx.post(
            "https://eventstore/api/v3/covid19triage/", status_code=500
        )

        form = HealthCheckForm()
        dispatcher = CollectingDispatcher()
        tracker = utils.get_tracker_for_slot_from_intent(
            form,
            "tracing",
            "affirm",
            {
                "province": "wc",
                "age": "18-39",
                "symptoms_fever": "no",
                "symptoms_cough": "no",
                "symptoms_sore_throat": "yes",
                "symptoms_difficulty_breathing": "no",
                "symptoms_taste_smell": "no",
                "exposure": "not sure",
                "tracing": "yes",
                "gender": "RATHER NOT SAY",
                "medical_condition": "not sure",
                "city_location_coords": "+1.2-3.4",
                "location_coords": "+3.4-1.2",
                "location": "Cape Town, South Africa",
            },
        )
        error = None
        try:
            await form.submit(dispatcher, tracker, {})
        except httpx.HTTPError as e:
            error = e

        assert error
        assert len(request.calls) == 3

        base.actions.actions.config.EVENTSTORE_URL = None
        base.actions.actions.config.EVENTSTORE_TOKEN = None

    @pytest.mark.asyncio
    async def test_validate_yes_no(self):
        """
        Tests that yes no slots validate correctly
        """
        form = HealthCheckForm()
        for slot in [
            "symptoms_fever",
            "symptoms_cough",
            "symptoms_sore_throat",
            "symptoms_difficulty_breathing",
            "symptoms_taste_smell",
            "tracing",
        ]:
            tracker = self.get_tracker_for_text_slot_with_message(slot, "yes")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "yes"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "no")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "no"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "Invalid")
            dispatcher = CollectingDispatcher()
            events = await form.validate(dispatcher, tracker, {})
            assert events == [
                SlotSet(slot, None),
            ]
            [message] = dispatcher.messages
            assert message["template"] == "utter_incorrect_selection"

    @pytest.mark.asyncio
    async def test_validate_yes_no_maybe(self):
        """
        Tests that yes no maybe slots validate correctly
        """
        form = HealthCheckForm()
        for slot in ["exposure"]:
            tracker = self.get_tracker_for_text_slot_with_message(slot, "yes")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "yes"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "no")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "no"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "not sure")
            events = await form.validate(CollectingDispatcher(), tracker, {})
            assert events == [
                SlotSet(slot, "not sure"),
            ]

            tracker = self.get_tracker_for_text_slot_with_message(slot, "Invalid")
            dispatcher = CollectingDispatcher()
            events = await form.validate(dispatcher, tracker, {})
            assert events == [
                SlotSet(slot, None),
            ]
            [message] = dispatcher.messages
            assert message["template"] == "utter_incorrect_selection"


class TestActionSessionStart:
    def test_carry_over_slots(self):
        """
        Should set all the carry over slots, and then add a listen at the end
        """
        dispatcher = CollectingDispatcher()
        tracker = Tracker("", {}, None, [], False, None, None, None)
        actions = ActionSessionStart().run(dispatcher, tracker, {})
        assert actions[0] == SessionStarted()
        assert actions[-1] == ActionExecuted("action_listen")
        assert len(actions) > 2


class TestActionExit:
    def test_carry_over_slots(self):
        """
        Should send the exit message, and then return all the carry over slots
        """
        dispatcher = CollectingDispatcher()
        tracker = Tracker("", {}, None, [], False, None, None, None)
        actions = ActionExit().run(dispatcher, tracker, {})
        assert actions[0] == SessionStarted()
        assert len(actions) > 1
        [msg] = dispatcher.messages
        assert msg["template"] == "utter_exit"
