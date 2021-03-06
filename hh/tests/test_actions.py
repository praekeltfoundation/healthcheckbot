from datetime import datetime, timedelta, timezone
from unittest import TestCase
from unittest.mock import patch

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from hh.actions.actions import (
    ActionExit,
    ActionSessionStart,
    HealthCheckForm,
    HealthCheckProfileForm,
)


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
            response,
            {
                "destination_province": "ec",
                "university_list": "\n".join(
                    [
                        "*1.* AFDA",
                        "*2.* Boston City Campus & Business College",
                        "*3.* Buffalo City",
                        "*4.* CTU Training Solutions",
                        "*5.* College of Transfiguration NPC",
                        "*6.* Damelin",
                        "*7.* East London Management Institute Pty Ltd",
                        "*8.* Eastcape Midlands",
                        "*9.* Ed-U City Campus (Pty) Ltd",
                        "*10.* Health and Fitness Professionals Academy (HFPA)",
                        "*11.* IQ Academy",
                        "*12.* Ikhala",
                        "*13.* Ingwe",
                        "*14.* King Hintsa",
                        "*15.* King Sabata Dalindyebo (KSD)",
                        "*16.* Lovedale",
                        "*17.* MANCOSA",
                        "*18.* MSC Business College",
                        "*19.* Nelson Mandela University (NMU)",
                        "*20.* Netcare  Education (Pty Ltd)",
                        "*21.* Pearson Instittute of Higher Education",
                        "*22.* Port Elizabeth",
                        "*23.* Production Management Institute of Southern Africa PTY "
                        "LTD / PMI",
                        "*24.* Regent Business School (Pty) Ltd (Learning Centre)",
                        "*25.* Rhodes University (RU)",
                        "*26.* STADIO AFDA",
                        "*27.* Stenden",
                        "*28.* UNISA",
                        "*29.* University of Fort Hare (UFH)",
                        "*30.* Walter Sisulu University (WSU)",
                        "*31.* eta College",
                    ]
                ),
            },
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
        response = form.validate_university("1", dispatcher, tracker, {})
        self.assertEqual(
            response, {"university": "AFDA", "campus_list": "*1.* Cenral"},
        )

    def test_validate_campus(self):
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001",
            {"destination_province": "ec", "university": "AFDA"},
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
                "university": "AFDA",
                "campus": "Cenral",
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
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen",)
        form.send_risk_to_user(dispatcher, "low", tracker)
        [msg] = dispatcher.messages
        self.assertEqual(msg["template"], "utter_risk_low")
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
