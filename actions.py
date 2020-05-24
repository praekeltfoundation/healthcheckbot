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


class HealthCheckForm(FormAction):
    """HealthCheck form action"""

    def name(self) -> Text:
        """Unique identifier of the form"""

        return "healthcheck_form"

    @staticmethod
    def required_slots(tracker: Tracker) -> List[Text]:
        """A list of required slots that the form has to fill"""

        if tracker.get_slot('user_status') == 'returning':
            return ["cough", "exposure", "tracing"]
        else:
            return ["province", "age", "cough", "exposure", "tracing"]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        return {
            "province": [
                self.from_text(),
            ],
            "age": [
                self.from_text(),
            ],
            "cough": [
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


# class UserDataForm(FormAction):
#     """User data form action"""
#
#     def name(self) -> Text:
#         """Unique identifier of the form"""
#
#         return "userdata_form"
#
#     @staticmethod
#     def required_slots(tracker: Tracker) -> List[Text]:
#         """A list of required slots that the form has to fill"""
#
#         return ["province", "age"]
#
#     def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
#         return {
#             "province": [
#                 self.from_text(),
#             ],
#             "age": [
#                 self.from_text(),
#             ]
#         }

    # def submit(
    #         self,
    #         dispatcher: CollectingDispatcher,
    #         tracker: Tracker,
    #         domain: Dict[Text, Any],
    # ) -> List[Dict]:
    #     """Define what the form has to do
    #         after all required slots are filled"""
    #
    #     # utter submit template
    #     dispatcher.utter_message(template="utter_submit")
    #     return []


class ActionGetUser(Action):

    def name(self) -> Text:
        return "action_get_user"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[SlotSet]:

        age = tracker.get_slot("age")
        province = tracker.get_slot("province")
        validate_slots = [age, province]
        if age is None:
            result = [SlotSet("user_status", "new")]
        else:
            result = [SlotSet("user_status", "returning")]
        # utter submit template
        # dispatcher.utter_message(template="utter_submit")
        return result


class ActionResetAllButFewSlots(Action):

    def name(self):
        return "action_reset_all_but_few_slots"

    def run(self, dispatcher, tracker, domain):
        age = tracker.get_slot("age")
        province = tracker.get_slot("province")
        return [AllSlotsReset(),
                SlotSet("age", age),
                SlotSet("province", province)]

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