from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import patch

import pytest
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from base.actions import config
from base.tests import utils
from hh.actions.actions import (
    ActionAssignStudyBArm,
    ActionExit,
    ActionSessionStart,
    HealthCheckForm,
    HealthCheckProfileForm,
    HonestyCheckForm,
)


@pytest.fixture
def mock_env_studyb(monkeypatch):
    monkeypatch.setattr(config, "STUDY_B_ENABLED", True)


class HealthCheckProfileFormTests(TestCase):
    def test_slot_mappings(self):
        """
        Ensures that the additional school fields are in the slot mappings
        """
        form = HealthCheckProfileForm()
        mappings = form.slot_mappings()
        self.assertIn("first_name", mappings)
        self.assertIn("last_name", mappings)
        self.assertIn("destination", mappings)
        self.assertIn("reason", mappings)
        self.assertIn("destination_province", mappings)
        self.assertIn("university", mappings)
        self.assertIn("vaccine_uptake", mappings)

    def test_validate_destination(self):
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_destination("campus", dispatcher, tracker, {})
        self.assertEqual(response, {"destination": "campus"})

    def test_validate_reason(self):
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_reason("student", dispatcher, tracker, {})
        self.assertEqual(response, {"reason": "student"})

    def test_validate_destination_province(self):
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_destination_province("1", dispatcher, tracker, {})
        self.assertEqual(
            response, {"destination_province": "ec"},
        )

    def test_validate_university(self):
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001",
            {"destination_province": "ec"},
            {},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        dispatcher = CollectingDispatcher()
        response = form.validate_university("afda", dispatcher, tracker, {})
        self.assertEqual(
            response,
            {
                "university": "afda",
                "university_list": "\n".join(
                    [
                        "*1.* AFDA",
                        "*2.* STADIO AFDA",
                        "*3.* Ikhala",
                        "*4.* MANCOSA",
                        "*5.* Damelin",
                    ]
                ),
            },
        )

    def test_validate_university_confirm(self):
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001",
            {"destination_province": "ec", "university": "afda"},
            {},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        dispatcher = CollectingDispatcher()
        response = form.validate_university_confirm("1", dispatcher, tracker, {})
        self.assertEqual(
            response, {"university_confirm": "AFDA", "campus_list": "*1.* Cenral"},
        )

    def test_validate_campus(self):
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001",
            {"destination_province": "ec", "university_confirm": "AFDA"},
            {},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        dispatcher = CollectingDispatcher()
        response = form.validate_campus("1", dispatcher, tracker, {})
        self.assertEqual(
            response, {"campus": "Cenral"},
        )

    @patch("hh.actions.actions.CollectingDispatcher.utter_message")
    def test_validate_vaccine_uptake(self, mock_utter):
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001",
            {"destination_province": "ec", "university": "afda", "campus": "Cenral"},
            {},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        dispatcher = CollectingDispatcher()
        response = form.validate_vaccine_uptake("3", dispatcher, tracker, {})
        self.assertEqual(
            response, {"vaccine_uptake": "NOT"},
        )
        mock_utter.assert_called_once_with(template="utter_not_vaccinated")


class HealthCheckFormTests(TestCase):
    def test_eventstore_data(self):
        """
        The data is transformed from the tracker store into the event store format
        """
        form = HealthCheckForm()
        tracker = Tracker(
            "27820001001",
            {
                "province": "wc",
                "first_name": "test first",
                "last_name": "test last",
                "age": "40-65",
                "symptoms_fever": "no",
                "symptoms_cough": "yes",
                "symptoms_sore_throat": "no",
                "symptoms_difficulty_breathing": "no",
                "symptoms_taste_smell": "no",
                "medical_condition": "not sure",
                "exposure": "not sure",
                "tracing": "yes",
                "gender": "OTHER",
                "location": "Long Street, Cape Town",
                "medical_condition_obesity": "no",
                "medical_condition_diabetes": "no",
                "medical_condition_hypertension": "yes",
                "medical_condition_cardio": "no",
                "destination": "campus",
                "reason": "student",
                "destination_province": "ec",
                "university_confirm": "AFDA",
                "campus": "Cenral",
                "vaccine_uptake": "PARTIALLY",
                "study_b_arm": "T1",
                "honesty_t1": "yes",
            },
            {},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        data = form.get_eventstore_data(tracker, "low")
        self.assertTrue(data.pop("deduplication_id"))
        self.maxDiff = None
        self.assertEqual(
            data,
            {
                "first_name": "test first",
                "last_name": "test last",
                "province": "ZA-WC",
                "age": "40-65",
                "fever": False,
                "cough": True,
                "sore_throat": False,
                "difficulty_breathing": False,
                "smell": False,
                "preexisting_condition": "not_sure",
                "exposure": "not_sure",
                "tracing": True,
                "gender": "other",
                "city": "Long Street, Cape Town",
                "city_location": "",
                "location": "",
                "msisdn": "+27820001001",
                "risk": "low",
                "source": "WhatsApp",
                "data": {
                    "cardio": False,
                    "diabetes": False,
                    "hypertension": True,
                    "obesity": False,
                    "destination": "campus",
                    "reason": "student",
                    "destination_province": "ZA-EC",
                    "university": {"name": "AFDA"},
                    "campus": {"name": "Cenral"},
                    "vaccine_uptake": "PARTIALLY",
                    "hcs_study_b_arm": "T1",
                    "hcs_study_b_honesty": "yes",
                },
            },
        )

    @patch("hh.actions.actions.datetime")
    def test_send_risk_to_user(self, dt):
        """
        The message to the user has the relevant variables filled
        """
        form = HealthCheckForm()
        dispatcher = CollectingDispatcher()
        dt.now.return_value = datetime(
            2020, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=2))
        )
        tracker = Tracker(
            "27820001001",
            {
                "first_name": "test first",
                "last_name": "test last",
                "destination": "campus",
                "reason": "student",
            },
            {},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        form.send_risk_to_user(dispatcher, "low", tracker)
        [msg] = dispatcher.messages
        self.assertEqual(msg["template"], "utter_risk_low")
        self.assertEqual(msg["name"], "test first test last")
        self.assertEqual(msg["issued"], "January 2, 2020, 3:04 AM")
        self.assertEqual(msg["expired"], "January 3, 2020, 3:04 AM")

    @patch("hh.actions.actions.datetime")
    def test_send_risk_to_user_minor(self, dt):
        """
        The message to the user should not include the name
        as it was not captured in the case of minors
        """
        form = HealthCheckForm()
        dispatcher = CollectingDispatcher()
        dt.now.return_value = datetime(
            2020, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=2))
        )
        tracker = Tracker(
            "27820001001",
            {"destination": "campus", "reason": "student"},
            {},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        form.send_risk_to_user(dispatcher, "low", tracker)
        [msg] = dispatcher.messages
        self.assertEqual(msg["template"], "utter_risk_low")
        self.assertEqual(msg["name"], "Not captured")
        self.assertEqual(msg["issued"], "January 2, 2020, 3:04 AM")
        self.assertEqual(msg["expired"], "January 3, 2020, 3:04 AM")


class ActionSessionStartTests(TestCase):
    def test_additional_details_copied(self):
        """
        Should copy over the hh additional details to the new session
        """
        action = ActionSessionStart()
        events = action.get_carry_over_slots(
            Tracker(
                "27820001001",
                {
                    "first_name": "test first",
                    "last_name": "test last",
                    "destination": "campus",
                    "reason": "student",
                },
                {},
                [],
                False,
                None,
                {},
                "action_listen",
            )
        )
        self.assertIn(SlotSet("first_name", "test first"), events)
        self.assertIn(SlotSet("last_name", "test last"), events)
        self.assertIn(SlotSet("destination", "campus"), events)
        self.assertIn(SlotSet("reason", "student"), events)


class ActionExitTests(TestCase):
    def test_additional_details_copied(self):
        """
        Should copy over the name details when exiting
        """
        action = ActionExit()
        dispatcher = CollectingDispatcher()
        events = action.run(
            dispatcher,
            Tracker(
                "27820001001",
                {
                    "first_name": "test first",
                    "last_name": "test last",
                    "destination": "campus",
                    "reason": "student",
                },
                {},
                [],
                False,
                None,
                {},
                "action_listen",
            ),
            {},
        )
        self.assertIn(SlotSet("first_name", "test first"), events)
        self.assertIn(SlotSet("last_name", "test last"), events)
        self.assertIn(SlotSet("destination", "campus"), events)
        self.assertIn(SlotSet("reason", "student"), events)


class TestActionAssignStudyBArm:
    @pytest.mark.asyncio
    async def test_assign_study_b_arm(self, mock_env_studyb):
        """
        Should set the study b arm
        """
        action = ActionAssignStudyBArm()
        dispatcher = CollectingDispatcher()

        action.call_event_store = utils.AsyncMock()
        action.call_event_store.return_value = {
            "msisdn": "+27820001001",
            "source": "WhatsApp",
            "timestamp": "2022-03-09T07:33:29.046948Z",
            "created_by": "whatsapp-healthcheck",
            "province": "ZA-GT",
            "study_b_arm": "T1",
        }
        events = await action.run(
            dispatcher,
            Tracker(
                "27820001001",
                {
                    "first_name": "test first",
                    "last_name": "test last",
                    "destination": "campus",
                    "province": "gt",
                    "reason": "student",
                },
                {},
                [],
                False,
                None,
                {},
                "action_listen",
            ),
            {},
        )
        assert SlotSet("study_b_arm", "T1") in events


@pytest.mark.asyncio
class TestHonestyCheckForm:
    async def test_honesty_check_messages(self):
        """
        The correct study b utterance is shown.
        """

        for arm in ["T1", "T2", "T3"]:
            tracker = Tracker(
                "default",
                {"study_b_arm": arm},
                {"text": "test"},
                [],
                False,
                None,
                {},
                "action_listen",
            )
            dispatcher = CollectingDispatcher()
            await HonestyCheckForm().run(dispatcher, tracker, {})

            [message] = dispatcher.messages
            assert message["template"] == f"utter_ask_honesty_{arm.lower()}"

    async def test_honesty_check_control(self):
        """
        Should not send message for the control arm.
        """

        tracker = Tracker(
            "default",
            {"study_b_arm": "C"},
            {"text": "test"},
            [],
            False,
            None,
            {},
            "action_listen",
        )
        dispatcher = CollectingDispatcher()
        form = HonestyCheckForm()
        assert form.required_slots(tracker) == []

        await form.run(dispatcher, tracker, {})

        assert dispatcher.messages == []
