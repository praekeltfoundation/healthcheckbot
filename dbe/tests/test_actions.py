from unittest import TestCase

from rasa_sdk import Tracker

from dbe.actions.actions import HealthCheckForm, HealthCheckProfileForm


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
                },
            },
        )
