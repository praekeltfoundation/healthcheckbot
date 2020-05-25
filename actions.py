# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/core/actions/#custom-actions/


# This is a simple example for a custom action which utters "Hello World!"

from typing import Dict, Text, Any, List, Union
from rasa_sdk import Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, Action
from rasa_sdk.events import SlotSet, AllSlotsReset
import pymongo


class ActionCalculateRisk(Action):
    """HealthCheck form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "action_calculate_risk"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[SlotSet]:

        risk = None
        sympt_num = 0
        age = tracker.get_slot("age")
        if age is "YES":
            sympt_num += 1
        fever = tracker.get_slot("fever")
        if fever is "YES":
            sympt_num += 1
        cough = tracker.get_slot("cough")
        if cough is "YES":
            sympt_num += 1
        sore_throat = tracker.get_slot("sore_throat")
        if sore_throat is "YES":
            sympt_num += 1

        exposure = tracker.get_slot("exposure")
        if exposure is "YES":
            exposure = True
        else:
            exposure = False

        if sympt_num >= 3:
            risk = 'high'

        if sympt_num is 0:
            if exposure:
                risk = 'low'
            else:
                risk = 'moderate'

        if sympt_num is 1:
            if exposure:
                risk = 'high'
            else:
                risk = 'moderate'

        if sympt_num is 2:
            if exposure:
                risk = 'high'
            else:
                if age is not ">65":
                    risk = 'moderate'
                else:
                    risk = 'high'

        # utter submit template
        dispatcher.utter_message("Your risk is %s" % risk)
        # if risk is 'low':
        #     dispatcher.utter_message(template="utter_risk_low")
        # elif risk is 'moderate':
        #     dispatcher.utter_message(template="utter_risk_moderate")
        # else:
        #     dispatcher.utter_message(template="utter_risk_high")

        return [SlotSet("user_risk", risk)]


class AcceptTermsForm(FormAction):
    """HealthCheck form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "terms_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ['terms_cond']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {

            "terms_cond": [
                self.from_text(),
            ]
        }

    def validate_terms_cond(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]:
        """Validate terms_cond value."""

        if value in ['ACCEPT', 'OTHER', 'MORE']:
            return {'terms_cond': value}
        else:
            dispatcher.utter_message("Please accept T&C.")
            # validation failed, set slot to None
            return {'terms_cond': None}

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        # dispatcher.utter_message(template="utter_submit")
        return []


class HealthCheckForm(FormAction):
    """HealthCheck form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "healthcheck_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ["fever", "cough", 'sore_throat',
                'breathlessness', 'smell', 'exposure', 'tracing']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {

            "fever": [
                self.from_text(),
            ],
            "cough": [
                self.from_text(),
            ],
            "sore_throat": [
                self.from_text(),
            ],
            "breathlessness": [
                self.from_text(),
            ],
            "smell": [
                self.from_text(),
            ],
            "exposure": [
                self.from_text(),
            ],
            "tracing": [
                self.from_text(),
            ]
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_message(template="utter_submit")
        return []


class UserDataForm(FormAction):
    """User data form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "userdata_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        return ['age', 'gender', 'province', 'location', 'obesity', 'diabetes',
                'hypertension', 'cardiovascular', 'pre_existing']

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {

            "age": [
                self.from_text(),
            ],
            "gender": [
                self.from_text(),
            ],
            "province": [
                self.from_text(),
            ],
            "location": [
                self.from_text(),
            ],
            "obesity": [
                self.from_text(),
            ],
            "diabetes": [
                self.from_text(),
            ],
            "hypertension": [
                self.from_text(),
            ],
            "cardiovascular": [
                self.from_text(),
            ],
            "pre_existing": [
                self.from_text(),
            ]
        }

    def submit(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any],
    ) -> List[Dict]:
        """Define what the form has to do
            after all required slots are filled"""

        # utter submit template
        dispatcher.utter_message(template="utter_submit_user")
        return []


class ActionGetUser(Action):

    def name(self) -> Text:
        return "action_get_user"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[SlotSet]:

        # TODO needs different logic
        age = tracker.get_slot("age")
        if age is None:
            result = [SlotSet("user_status", "new")]
        else:
            result = [SlotSet("user_status", "returning")]
        # utter submit template
        # dispatcher.utter_message(template="utter_submit")
        return result


class ActionResetTerms(Action):

    def name(self):
        return "action_reset_terms"

    def run(self, dispatcher, tracker, domain):
        return [SlotSet("terms_cond", None)]


class ActionResetAllButFewSlots(Action):

    def name(self):
        return "action_reset_all_but_few_slots"

    def run(self, dispatcher, tracker, domain):

        age = tracker.get_slot("age")
        gender = tracker.get_slot("gender")
        province = tracker.get_slot("province")
        location = tracker.get_slot("location")
        obesity = tracker.get_slot("obesity")
        diabetes = tracker.get_slot("diabetes")
        hypertension = tracker.get_slot("hypertension")
        cardiovascular = tracker.get_slot("cardiovascular")
        pre_existing = tracker.get_slot("pre_existing")

        return [AllSlotsReset(),
                SlotSet("age", age),
                SlotSet("gender", gender),
                SlotSet("province", province),
                SlotSet("location", location),
                SlotSet("obesity", obesity),
                SlotSet("diabetes", diabetes),
                SlotSet("hypertension", hypertension),
                SlotSet("cardiovascular", cardiovascular),
                SlotSet("pre_existing", pre_existing)]


# class ActionTCCheck(Action):
#
#     def name(self) -> Text:
#         return "action_check_tc"
#
#     def run(self,
#             dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[SlotSet]:
#
#         # user_status = tracker.get_slot("user_status")
#         if user_status is 'new':
#             tc = tracker.get_slot("terms_cond_new")
#             result = [SlotSet("terms_cond_new", "new")]
#         else:
#             result = [SlotSet("user_status", "returning")]
#         # utter submit template
#         # dispatcher.utter_message(template="utter_submit")
#         return result

# class CarAction(Action):
#
#     def name(self) -> Text:
#         return "carAction"
#
#     def run(self, dispatcher, tracker, domain):
#         client = pymongo.MongoClient("localhost", 27017)
#         db = client.rasa
#         res = db.conversations.find({'action': 'CarAction'})
#         print(type(res))
#         for i in res:
#             dispatcher.utter_button_message(i['text'], i['buttons'])
#         return []

# def validate(self,
#              dispatcher: CollectingDispatcher,
#              tracker: Tracker,
#              domain: Dict[Text, Any]) -> List[Dict]:
#     """Validate extracted requested slot
#         else reject the execution of the form action
#     """
#     # extract other slots that were not requested
#     # but set by corresponding entity
#     slot_values = self.extract_other_slots(dispatcher, tracker, domain)
#
#     # extract requested slot
#     slot_to_fill = tracker.get_slot(REQUESTED_SLOT)
#     if slot_to_fill:
#         slot_values.update(self.extract_requested_slot(dispatcher,
#                                                        tracker, domain))
#         if not slot_values:
#             # reject form action execution
#             # if some slot was requested but nothing was extracted
#             # it will allow other policies to predict another action
#             raise ActionExecutionRejection(self.name(),
#                                            "Failed to validate slot {0} "
#                                            "with action {1}"
#                                            "".format(slot_to_fill,
#                                                      self.name()))
#
#     # we'll check when validation failed in order
#     # to add appropriate utterances
#     for slot, value in slot_values.items():
#
#         if slot == 'consent':
#             if isinstance(value, str):
#                 if 'yes' in value:
#                     # convert "out..." to True
#                     slot_values[slot] = True
#                 elif 'no' in value:
#                     # convert "in..." to False
#                     slot_values[slot] = False
#                 else:
#                     dispatcher.utter_template('Please input with yes or no to move ahead',
#                                               tracker)
#                     # validation failed, set slot to None
#                     slot_values[slot] = None
#
#     # validation succeed, set the slots values to the extracted values
#     return [SlotSet(slot, value) for slot, value in slot_values.items()]