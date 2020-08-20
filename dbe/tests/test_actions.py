from unittest import TestCase

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from dbe.actions.actions import (
    ActionSessionStart,
    HealthCheckForm,
    HealthCheckProfileForm,
)


class HealthCheckProfileFormTests(TestCase):
    def test_age_data(self):
        """
        Correct age categories is returned
        """
        form = HealthCheckProfileForm()
        self.assertEqual(
            form.age_data,
            {1: "<18", 2: "18-39", 3: "40-49", 4: "50-59", 5: "60-65", 6: ">65"},
        )

    def test_validate_school(self):
        """
        Stores first search result
        """
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001", {"province": "wc"}, {}, [], False, None, {}, "action_listen"
        )
        response = form.validate_school(
            "bergvleet", CollectingDispatcher(), tracker, {}
        )
        self.assertEqual(
            response, {"school": "BERGVLIET HIGH SCHOOL", "school_emis": "105310201"}
        )

    def test_validate_school_no_results(self):
        """
        Returns error message and clears value for province
        """
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001", {"province": "gt"}, {}, [], False, None, {}, "action_listen"
        )
        dispatcher = CollectingDispatcher()
        response = form.validate_school("bergvleet", dispatcher, tracker, {})
        self.assertEqual(response, {"school": None, "province": None})
        [message] = dispatcher.messages
        self.assertEqual(message["template"], "utter_incorrect_school")

    def test_validate_school_confirm_no(self):
        """
        Try again getting the name of the school
        """
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_school_confirm("no", dispatcher, tracker, {})
        self.assertEqual(response, {"school": None, "school_confirm": None})

    def test_validate_school_confirm_yes(self):
        """
        Confirms the name of the school
        """
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_school_confirm("yes", dispatcher, tracker, {})
        self.assertEqual(response, {"school_confirm": "yes"})

    def test_slot_mappings(self):
        """
        Ensures that the additional school fields are in the slot mappings
        """
        form = HealthCheckProfileForm()
        mappings = form.slot_mappings()
        self.assertIn("school", mappings)
        self.assertIn("school_confirm", mappings)


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
                "age": "40-49",
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
                "school": "BERGVLIET HIGH SCHOOL",
                "school_emis": "105310201",
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
        self.assertEqual(
            data,
            {
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
                    "age": "40-49",
                    "cardio": False,
                    "diabetes": False,
                    "hypertension": True,
                    "obesity": False,
                    "school_name": "BERGVLIET HIGH SCHOOL",
                    "school_emis": "105310201",
                },
            },
        )


class ActionSessionStartTests(TestCase):
    def test_school_details_copied(self):
        """
        Should copy over the school details to the new session
        """
        action = ActionSessionStart()
        events = action.get_carry_over_slots(
            Tracker(
                "27820001001",
                {
                    "school": "BERGVLIET HIGH SCHOOL",
                    "school_emis": "105310201",
                    "school_confirm": "yes",
                },
                {},
                [],
                False,
                None,
                {},
                "action_listen",
            )
        )
        self.assertIn(SlotSet("school", "BERGVLIET HIGH SCHOOL"), events)
        self.assertIn(SlotSet("school_emis", "105310201"), events)
        self.assertIn(SlotSet("school_confirm", "yes"), events)
