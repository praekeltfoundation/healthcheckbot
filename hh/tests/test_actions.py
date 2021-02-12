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
                        "*2.* Betshwana",
                        "*3.* Blythswood",
                        "*4.* Bofolo",
                        "*5.* Bokamoso",
                        "*6.* Boston City Campus & Business College",
                        "*7.* Buffalo City",
                        "*8.* CTU Training Solutions",
                        "*9.* Cecilia Makiwane",
                        "*10.* College of Transfiguration NPC",
                        "*11.* Damelin",
                        "*12.* East London Management Institute Pty Ltd",
                        "*13.* Eastcape Midlands",
                        "*14.* Eastern Cape CET College",
                        "*15.* Ed-U City Campus (Pty) Ltd",
                        "*16.* Equleni",
                        "*17.* Frere Hospital",
                        "*18.* Health and Fitness Professionals Academy (HFPA)",
                        "*19.* IQ Academy",
                        "*20.* Ikhala",
                        "*21.* Ingwe",
                        "*22.* Jeffrey’s Bay",
                        "*23.* Kalerato",
                        "*24.* Khanya",
                        "*25.* Khanyisa",
                        "*26.* King Hintsa",
                        "*27.* King Sabata Dalindyebo (KSD)",
                        "*28.* Lovedale",
                        "*29.* MANCOSA",
                        "*30.* MSC Business College",
                        "*31.* Makanaskop",
                        "*32.* Mangquzu",
                        "*33.* Masizakhe",
                        "*34.* Mgobozi Commercial",
                        "*35.* Msobomvu",
                        "*36.* Nelson Mandela University (NMU)",
                        "*37.* Netcare  Education (Pty Ltd)",
                        "*38.* Ngqeleni",
                        "*39.* Ntukayi",
                        "*40.* Osborn",
                        "*41.* Pearson Instittute of Higher Education",
                        "*42.* Phakamile (Phaphani)",
                        "*43.* Port Elizabeth",
                        "*44.* Port St Johns",
                        "*45.* Production Management Institute of Southern Africa PTY "
                        "LTD / PMI",
                        "*46.* Qoqodala",
                        "*47.* Qumbu",
                        "*48.* Regent Business School (Pty) Ltd (Learning Centre)",
                        "*49.* Rhodes University (RU)",
                        "*50.* STADIO AFDA",
                        "*51.* Sinethemba",
                        "*52.* Sofunda",
                        "*53.* Soweto-On-Sea",
                        "*54.* St Dennis",
                        "*55.* Stenden",
                        "*56.* UNISA",
                        "*57.* University of Fort Hare (UFH)",
                        "*58.* Vorster",
                        "*59.* Walter Sisulu University (WSU)",
                        "*60.* Zimele",
                        "*61.* Zwelakhe",
                        "*62.* eta College",
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
        self.assertEqual(response, {"university": "AFDA", "campus_list": "*1.* Cenral"})

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
        self.assertEqual(response, {"campus": "Cenral"})


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
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
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
