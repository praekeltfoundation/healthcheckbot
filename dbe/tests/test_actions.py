from datetime import datetime, timedelta, timezone
from unittest import TestCase, mock

import pytest
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher

from dbe.actions.actions import (
    ActionExit,
    ActionSessionStart,
    HealthCheckForm,
    HealthCheckProfileForm,
)


class HealthCheckProfileFormTests(TestCase):
    def test_validate_age(self):
        """
        Should be an age between 0 and 150
        """
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001", {"province": "wc"}, {}, [], False, None, {}, "action_listen"
        )
        response = form.validate_age("1", CollectingDispatcher(), tracker, {})
        self.assertEqual(response, {"age": "1"})
        response = form.validate_age("0", CollectingDispatcher(), tracker, {})
        self.assertEqual(response, {"age": None})
        response = form.validate_age("150", CollectingDispatcher(), tracker, {})
        self.assertEqual(response, {"age": None})
        response = form.validate_age("abc", CollectingDispatcher(), tracker, {})
        self.assertEqual(response, {"age": None})

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

    def test_validate_school_other(self):
        """
        Stores the school as other and moves on
        """
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001", {"province": "wc"}, {}, [], False, None, {}, "action_listen"
        )
        response = form.validate_school("OthER ", CollectingDispatcher(), tracker, {})
        self.assertEqual(
            response, {"school": "OTHER", "school_emis": None, "school_confirm": "yes"}
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

    def test_validate_profile(self):
        """
        Get the profile of the user. Should not accept labels.
        """
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_profile("4", dispatcher, tracker, {})
        self.assertEqual(response, {"profile": "actual_parent"})

        response = form.validate_profile("parent", dispatcher, tracker, {})
        self.assertEqual(response, {"profile": None})

    def test_validate_confirm_details(self):
        """
        Confirms the returning user details are correct
        """
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_confirm_details("yes", dispatcher, tracker, {})
        self.assertEqual(response, {"confirm_details": "yes"})

    def test_validate_province(self):
        """
        Should also update the province_display slot
        """
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        dispatcher = CollectingDispatcher()
        response = form.validate_province("wc", dispatcher, tracker, {})
        self.assertEqual(
            response, {"province": "wc", "province_display": "WESTERN CAPE"}
        )

    def test_slot_mappings(self):
        """
        Ensures that the additional fields are in the slot mappings
        """
        form = HealthCheckProfileForm()
        mappings = form.slot_mappings()
        self.assertIn("school", mappings)
        self.assertIn("school_confirm", mappings)
        self.assertIn("profile", mappings)
        self.assertIn("obo_name", mappings)
        self.assertIn("obo_age", mappings)
        self.assertIn("obo_gender", mappings)
        self.assertIn("obo_location", mappings)
        self.assertIn("obo_location_confirm", mappings)
        self.assertIn("obo_medical_condition", mappings)
        self.assertIn("obo_medical_condition_cardio", mappings)
        self.assertIn("obo_medical_condition_diabetes", mappings)
        self.assertIn("obo_medical_condition_hypertension", mappings)
        self.assertIn("obo_medical_condition_obesity", mappings)
        self.assertIn("obo_province", mappings)
        self.assertIn("obo_school", mappings)
        self.assertIn("obo_school_confirm", mappings)

    def test_required_slots_not_parent(self):
        """
        If no profile selected, or a profile other than parent is selected, then we
        should return the usual slots
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        slots = HealthCheckProfileForm.required_slots(tracker)
        self.assertEqual(slots, ["profile"])

        tracker.slots["profile"] = "educator"
        slots = HealthCheckProfileForm.required_slots(tracker)
        self.assertEqual(slots, ["age"])

    def test_required_slots_parent(self):
        """
        For the parent profile, we should use the on behalf of slots
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["profile"] = "parent"
        slots = HealthCheckProfileForm.required_slots(tracker)
        self.assertEqual(slots, ["obo_name"])

    def test_required_slots_returning_user(self):
        """
        For returning users, we should confirm details
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["province_display"] = "WESTERN CAPE"
        tracker.slots["school"] = "BERGVLIET HIGH SCHOOL"
        tracker.slots["returning_user"] = "yes"
        slots = HealthCheckProfileForm.required_slots(tracker)
        self.assertEqual(slots, ["confirm_details"])

    def test_required_slots_returning_user_additional(self):
        """
        For returning users, after confirming information, if there are any additional
        slots that we still need to fill, we should ask them
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["province_display"] = "WESTERN CAPE"
        tracker.slots["school"] = "BERGVLIET HIGH SCHOOL"
        tracker.slots["returning_user"] = "yes"
        tracker.slots["confirm_details"] = "yes"
        tracker.slots["profile"] = "learner"
        slots = HealthCheckProfileForm.required_slots(tracker)
        self.assertEqual(slots, ["age"])

    def test_end_of_form_parent(self):
        """
        For the parent profile, if all the fields are filled, then we should return
        an empty list
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["profile"] = "parent"
        tracker.slots["obo_name"] = "Thabo"
        tracker.slots["obo_age"] = "23"
        tracker.slots["obo_gender"] = "male"
        tracker.slots["obo_province"] = "wc"
        tracker.slots["obo_location"] = "cape town"
        tracker.slots["obo_location_confirm"] = "yes"
        tracker.slots["obo_school"] = "BERGVLIET HIGH SCHOOL"
        tracker.slots["obo_school_confirm"] = "yes"
        tracker.slots["obo_medical_condition"] = "no"
        slots = HealthCheckProfileForm.required_slots(tracker)
        self.assertEqual(slots, [])


@pytest.mark.asyncio
class TestHealthCheckProfileFormAsync:
    async def test_obo_validator_sync(self):
        """
        Should change a validator from a normal slot to an obo slot, for sync functions
        """
        form = HealthCheckProfileForm()
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        result = await form.validate_obo_age("22", CollectingDispatcher(), tracker, {})
        assert result == {"obo_age": "22"}

    async def test_obo_validator_async(self):
        """
        Should change a validator from a normal slot to an obo slot, for sync functions
        """
        form = HealthCheckProfileForm()
        tracker = Tracker(
            "27820001001", {}, {}, [{"event": "user"}], False, None, {}, "action_listen"
        )
        result = await form.validate_obo_location(
            "cape town", CollectingDispatcher(), tracker, {}
        )
        assert result == {"obo_location": "cape town"}


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
                "age": "43",
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
                "profile": "learner",
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
                    "age": "43",
                    "cardio": False,
                    "diabetes": False,
                    "hypertension": True,
                    "obesity": False,
                    "school_name": "BERGVLIET HIGH SCHOOL",
                    "school_emis": "105310201",
                    "profile": "learner",
                },
            },
        )

    def test_eventstore_data_parent(self):
        """
        The data is transformed from the tracker store into the event store format
        from the on behalf of fields
        """
        form = HealthCheckForm()
        tracker = Tracker(
            "27820001001",
            {
                "obo_name": "Thabo",
                "obo_province": "wc",
                "obo_age": "43",
                "obo_symptoms_fever": "no",
                "obo_symptoms_cough": "yes",
                "obo_symptoms_sore_throat": "no",
                "obo_symptoms_difficulty_breathing": "no",
                "obo_symptoms_taste_smell": "no",
                "obo_medical_condition": "not sure",
                "obo_exposure": "not sure",
                "obo_tracing": "yes",
                "obo_gender": "OTHER",
                "obo_location": "Long Street, Cape Town",
                "obo_medical_condition_obesity": "no",
                "obo_medical_condition_diabetes": "no",
                "obo_medical_condition_hypertension": "yes",
                "obo_medical_condition_cardio": "no",
                "obo_school": "BERGVLIET HIGH SCHOOL",
                "obo_school_emis": "105310201",
                "profile": "parent",
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
                    "age": "43",
                    "name": "Thabo",
                    "cardio": False,
                    "diabetes": False,
                    "hypertension": True,
                    "obesity": False,
                    "school_name": "BERGVLIET HIGH SCHOOL",
                    "school_emis": "105310201",
                    "profile": "parent",
                },
            },
        )

    @mock.patch("dbe.actions.actions.datetime")
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

    @mock.patch("dbe.actions.actions.datetime")
    def test_send_risk_to_user_parent_profile(self, dt):
        """
        The message to the user has the relevant variables filled, and use the on behalf
        of template
        """
        form = HealthCheckForm()
        dispatcher = CollectingDispatcher()
        dt.now.return_value = datetime(
            2020, 1, 2, 3, 4, 5, tzinfo=timezone(timedelta(hours=2))
        )
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["profile"] = "parent"
        form.send_risk_to_user(dispatcher, "low", tracker)
        [msg] = dispatcher.messages
        self.assertEqual(msg["template"], "utter_obo_risk_low")
        self.assertEqual(msg["issued"], "January 2, 2020, 3:04 AM")
        self.assertEqual(msg["expired"], "January 3, 2020, 3:04 AM")

    def test_map_age(self):
        """
        Should map to one of the age buckets
        """
        form = HealthCheckForm()
        self.assertEqual(form.map_age("3"), "<18")
        self.assertEqual(form.map_age("18"), "18-40")
        self.assertEqual(form.map_age("65"), "40-65")
        self.assertEqual(form.map_age("66"), ">65")

    def test_required_slots_not_parent(self):
        """
        Should return the normal slots for profiles that are not parent
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["profile"] = "educator"
        slots = HealthCheckForm.required_slots(tracker)
        self.assertEqual(slots, ["symptoms_fever"])

    def test_required_slots_parent(self):
        """
        Should return the normal slots for profiles that are not parent
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["profile"] = "parent"
        slots = HealthCheckForm.required_slots(tracker)
        self.assertEqual(slots, ["obo_symptoms_fever"])
        tracker.slots["obo_symptoms_fever"] = "no"
        slots = HealthCheckForm.required_slots(tracker)
        self.assertEqual(slots, ["obo_symptoms_cough"])

    def test_required_slots_parent_complete(self):
        """
        If there are no more slots to fulfill, should return an empty list
        """
        tracker = Tracker("27820001001", {}, {}, [], False, None, {}, "action_listen")
        tracker.slots["profile"] = "parent"
        tracker.slots["obo_symptoms_fever"] = "no"
        tracker.slots["obo_symptoms_cough"] = "no"
        tracker.slots["obo_symptoms_sore_throat"] = "no"
        tracker.slots["obo_symptoms_difficulty_breathing"] = "no"
        tracker.slots["obo_symptoms_taste_smell"] = "no"
        tracker.slots["obo_exposure"] = "no"
        tracker.slots["obo_tracing"] = "no"
        slots = HealthCheckForm.required_slots(tracker)
        self.assertEqual(slots, [])

    def test_slot_mappings(self):
        """
        Should have the on behalf of mappings
        """
        mappings = HealthCheckForm().slot_mappings()
        self.assertIn("obo_exposure", mappings)
        self.assertIn("obo_symptoms_cough", mappings)
        self.assertIn("obo_symptoms_difficulty_breathing", mappings)
        self.assertIn("obo_symptoms_fever", mappings)
        self.assertIn("obo_symptoms_sore_throat", mappings)
        self.assertIn("obo_symptoms_taste_smell", mappings)
        self.assertIn("obo_tracing", mappings)


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

    def test_province_display(self):
        """
        Should set province_display if returning user
        """
        action = ActionSessionStart()
        events = action.get_carry_over_slots(
            Tracker(
                "27820001001",
                {"province": "wc"},
                {},
                [],
                False,
                None,
                {},
                "action_listen",
            )
        )
        self.assertIn(SlotSet("province_display", "WESTERN CAPE"), events)


class ActionExitTests(TestCase):
    def test_school_details_copied(self):
        """
        Should copy over the school details to the new session
        """
        action = ActionExit()
        events = action.run(
            CollectingDispatcher(),
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
            ),
            {},
        )
        self.assertIn(SlotSet("school", "BERGVLIET HIGH SCHOOL"), events)
        self.assertIn(SlotSet("school_emis", "105310201"), events)
        self.assertIn(SlotSet("school_confirm", "yes"), events)
