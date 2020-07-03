import json
from typing import Any, Dict, Optional, Text
from urllib.parse import urlencode

import pytest
import respx
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

import actions.actions
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
        actions.actions.config.GOOGLE_PLACES_API_KEY = "test_key"
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

        actions.actions.config.GOOGLE_PLACES_API_KEY = None