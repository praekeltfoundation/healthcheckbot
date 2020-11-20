import json

import pytest
import respx
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher

import base.actions.actions
from base.tests import utils
from dbe.actions.actions import HealthCheckForm, HealthCheckProfileForm


class TestHealthCheckForm:
    @respx.mock
    @pytest.mark.asyncio
    async def test_submit_to_eventstore_low(self):
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
                "obo_name": "Thabo",
                "obo_province": "wc",
                "obo_age": "43",
                "obo_symptoms_fever": "no",
                "obo_symptoms_cough": "no",
                "obo_symptoms_sore_throat": "no",
                "obo_symptoms_difficulty_breathing": "no",
                "obo_symptoms_taste_smell": "no",
                "obo_medical_condition": "not sure",
                "obo_exposure": "not sure",
                "obo_tracing": "no",
                "obo_gender": "OTHER",
                "obo_location": "Long Street, Cape Town",
                "obo_location_coords": "+03.4-001.2/",
                "obo_city_location_coords": "+01.2-003.4/",
                "obo_medical_condition_obesity": "no",
                "obo_medical_condition_diabetes": "no",
                "obo_medical_condition_hypertension": "no",
                "obo_medical_condition_cardio": "no",
                "obo_school": "BERGVLIET HIGH SCHOOL",
                "obo_school_emis": "105310201",
                "profile": "parent",
            },
        )
        await form.submit(dispatcher, tracker, {})

        assert request.called
        [(request, response)] = request.calls
        data = json.loads(request.stream.body)
        assert data.pop("deduplication_id")
        assert data == {
            "province": "ZA-WC",
            "age": "40-65",
            "fever": False,
            "cough": False,
            "sore_throat": False,
            "difficulty_breathing": False,
            "smell": False,
            "exposure": "not_sure",
            "tracing": False,
            "gender": "other",
            "preexisting_condition": "not_sure",
            "city_location": "+01.2-003.4/",
            "location": "+03.4-001.2/",
            "city": "Long Street, Cape Town",
            "msisdn": "+default",
            "risk": "low",
            "source": "WhatsApp",
            "data": {
                "age": "43",
                "name": "Thabo",
                "cardio": False,
                "diabetes": False,
                "hypertension": False,
                "obesity": False,
                "school_name": "BERGVLIET HIGH SCHOOL",
                "school_emis": "105310201",
                "asthma": None,
                "tb": None,
                "pregnant": None,
                "respiratory": None,
                "cardiac": None,
                "immuno": None,
                "profile": "parent",
            },
        }

        base.actions.actions.config.EVENTSTORE_URL = None
        base.actions.actions.config.EVENTSTORE_TOKEN = None

    @respx.mock
    @pytest.mark.asyncio
    async def test_submit_to_eventstore_moderate(self):
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
                "obo_name": "Thabo",
                "obo_province": "wc",
                "obo_age": "43",
                "obo_symptoms_fever": "no",
                "obo_symptoms_cough": "no",
                "obo_symptoms_sore_throat": "yes",
                "obo_symptoms_difficulty_breathing": "no",
                "obo_symptoms_taste_smell": "no",
                "obo_medical_condition": "not sure",
                "obo_exposure": "not sure",
                "obo_tracing": "yes",
                "obo_gender": "OTHER",
                "obo_location": "Long Street, Cape Town",
                "obo_location_coords": "+03.4-001.2/",
                "obo_city_location_coords": "+01.2-003.4/",
                "obo_medical_condition_obesity": "no",
                "obo_medical_condition_diabetes": "no",
                "obo_medical_condition_hypertension": "yes",
                "obo_medical_condition_cardio": "no",
                "obo_school": "BERGVLIET HIGH SCHOOL",
                "obo_school_emis": "105310201",
                "profile": "parent",
            },
        )
        await form.submit(dispatcher, tracker, {})

        assert request.called
        [(request, response)] = request.calls
        data = json.loads(request.stream.body)
        assert data.pop("deduplication_id")
        assert data == {
            "province": "ZA-WC",
            "age": "40-65",
            "fever": False,
            "cough": False,
            "sore_throat": True,
            "difficulty_breathing": False,
            "smell": False,
            "exposure": "not_sure",
            "tracing": True,
            "gender": "other",
            "preexisting_condition": "not_sure",
            "city_location": "+01.2-003.4/",
            "location": "+03.4-001.2/",
            "city": "Long Street, Cape Town",
            "msisdn": "+default",
            "risk": "moderate",
            "source": "WhatsApp",
            "data": {
                "age": "43",
                "name": "Thabo",
                "cardio": False,
                "diabetes": False,
                "hypertension": True,
                "obesity": False,
                "school_name": "BERGVLIET HIGH SCHOOL",
                "school_emis": "105310201",
                "asthma": None,
                "tb": None,
                "pregnant": None,
                "respiratory": None,
                "cardiac": None,
                "immuno": None,
                "profile": "parent",
            },
        }

        base.actions.actions.config.EVENTSTORE_URL = None
        base.actions.actions.config.EVENTSTORE_TOKEN = None

    @respx.mock
    @pytest.mark.asyncio
    async def test_submit_to_eventstore_high(self):
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
                "obo_name": "Thabo",
                "obo_province": "wc",
                "obo_age": "43",
                "obo_symptoms_fever": "yes",
                "obo_symptoms_cough": "yes",
                "obo_symptoms_sore_throat": "yes",
                "obo_symptoms_difficulty_breathing": "no",
                "obo_symptoms_taste_smell": "no",
                "obo_medical_condition": "not sure",
                "obo_exposure": "not sure",
                "obo_tracing": "yes",
                "obo_gender": "OTHER",
                "obo_location": "Long Street, Cape Town",
                "obo_location_coords": "+03.4-001.2/",
                "obo_city_location_coords": "+01.2-003.4/",
                "obo_medical_condition_obesity": "no",
                "obo_medical_condition_diabetes": "no",
                "obo_medical_condition_hypertension": "yes",
                "obo_medical_condition_cardio": "no",
                "obo_school": "BERGVLIET HIGH SCHOOL",
                "obo_school_emis": "105310201",
                "profile": "parent",
            },
        )
        await form.submit(dispatcher, tracker, {})

        assert request.called
        [(request, response)] = request.calls
        data = json.loads(request.stream.body)
        assert data.pop("deduplication_id")
        assert data == {
            "province": "ZA-WC",
            "age": "40-65",
            "fever": True,
            "cough": True,
            "sore_throat": True,
            "difficulty_breathing": False,
            "smell": False,
            "exposure": "not_sure",
            "tracing": True,
            "gender": "other",
            "preexisting_condition": "not_sure",
            "city_location": "+01.2-003.4/",
            "location": "+03.4-001.2/",
            "city": "Long Street, Cape Town",
            "msisdn": "+default",
            "risk": "high",
            "source": "WhatsApp",
            "data": {
                "age": "43",
                "name": "Thabo",
                "cardio": False,
                "diabetes": False,
                "hypertension": True,
                "obesity": False,
                "school_name": "BERGVLIET HIGH SCHOOL",
                "school_emis": "105310201",
                "profile": "parent",
                "asthma": None,
                "tb": None,
                "pregnant": None,
                "respiratory": None,
                "cardiac": None,
                "immuno": None,
            },
        }

        base.actions.actions.config.EVENTSTORE_URL = None
        base.actions.actions.config.EVENTSTORE_TOKEN = None

    @respx.mock
    @pytest.mark.asyncio
    async def test_submit_to_eventstore_moderate_age(self):
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
                "obo_name": "Thabo",
                "obo_province": "wc",
                "obo_age": "67",
                "obo_symptoms_fever": "yes",
                "obo_symptoms_cough": "yes",
                "obo_symptoms_sore_throat": "no",
                "obo_symptoms_difficulty_breathing": "no",
                "obo_symptoms_taste_smell": "no",
                "obo_medical_condition": "not sure",
                "obo_exposure": "no",
                "obo_tracing": "yes",
                "obo_gender": "OTHER",
                "obo_location": "Long Street, Cape Town",
                "obo_location_coords": "+03.4-001.2/",
                "obo_city_location_coords": "+01.2-003.4/",
                "obo_medical_condition_obesity": "no",
                "obo_medical_condition_diabetes": "no",
                "obo_medical_condition_hypertension": "no",
                "obo_medical_condition_cardio": "no",
                "obo_school": "BERGVLIET HIGH SCHOOL",
                "obo_school_emis": "105310201",
                "profile": "parent",
            },
        )
        await form.submit(dispatcher, tracker, {})

        assert request.called
        [(request, response)] = request.calls
        data = json.loads(request.stream.body)
        assert data.pop("deduplication_id")
        assert data == {
            "province": "ZA-WC",
            "age": ">65",
            "fever": True,
            "cough": True,
            "sore_throat": False,
            "difficulty_breathing": False,
            "smell": False,
            "exposure": "no",
            "tracing": True,
            "gender": "other",
            "preexisting_condition": "not_sure",
            "city_location": "+01.2-003.4/",
            "location": "+03.4-001.2/",
            "city": "Long Street, Cape Town",
            "msisdn": "+default",
            "risk": "high",
            "source": "WhatsApp",
            "data": {
                "age": "67",
                "name": "Thabo",
                "cardio": False,
                "diabetes": False,
                "hypertension": False,
                "obesity": False,
                "school_name": "BERGVLIET HIGH SCHOOL",
                "school_emis": "105310201",
                "profile": "parent",
                "asthma": None,
                "tb": None,
                "pregnant": None,
                "respiratory": None,
                "cardiac": None,
                "immuno": None,
            },
        }

        base.actions.actions.config.EVENTSTORE_URL = None
        base.actions.actions.config.EVENTSTORE_TOKEN = None


class TestHealthCheckProfileForm:
    def test_get_province(self):
        """
        Should return obo province if obo profile, otherwise province
        """
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001",
            {"profile": "parent", "obo_province": "wc"},
            None,
            [],
            False,
            None,
            None,
            None,
        )
        assert form.get_province(tracker) == "wc"

        tracker = Tracker(
            "27820001001",
            {"profile": "learner", "province": "wc"},
            None,
            [],
            False,
            None,
            None,
            None,
        )
        assert form.get_province(tracker) == "wc"
