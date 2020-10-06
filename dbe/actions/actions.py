import uuid
from datetime import datetime, timedelta, timezone
from inspect import iscoroutinefunction
from typing import Any, Dict, List, Optional, Text, Union

from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser
from whoosh.query import FuzzyTerm, Term

from base.actions.actions import ActionExit as BaseActionExit
from base.actions.actions import ActionSessionStart as BaseActionSessionStart
from base.actions.actions import HealthCheckForm as BaseHealthCheckForm
from base.actions.actions import HealthCheckProfileForm as BaseHealthCheckProfileForm
from base.actions.actions import HealthCheckTermsForm

PROVINCE_DISPLAY = {
    "ec": "EASTERN CAPE",
    "fs": "FREE STATE",
    "gt": "GAUTENG",
    "nl": "KWAZULU NATAL",
    "lp": "LIMPOPO",
    "mp": "MPUMALANGA",
    "nw": "NORTH WEST",
    "nc": "NORTHERN CAPE",
    "wc": "WESTERN CAPE",
}


def obo_validator(function):
    async def call(*args, **kwargs):
        if iscoroutinefunction(function):
            result = await function(*args, **kwargs)
        else:
            result = function(*args, **kwargs)
        return {f"obo_{k}": v for k, v in result.items()}

    return call


class HealthCheckProfileForm(BaseHealthCheckProfileForm):
    SLOTS = ["profile", "age"]

    PERSISTED_SLOTS = [
        "gender",
        "province",
        "location",
        "location_confirm",
        "school",
        "school_confirm",
        "medical_condition",
    ]

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        mappings = super().slot_mappings()
        mappings["school"] = [self.from_text()]
        mappings["school_confirm"] = [
            self.from_entity(entity="number"),
            self.from_intent(intent="affirm", value="yes"),
            self.from_intent(intent="deny", value="no"),
            self.from_text(),
        ]
        mappings["confirm_details"] = [
            self.from_entity(entity="number"),
            self.from_intent(intent="affirm", value="yes"),
            self.from_intent(intent="deny", value="no"),
            self.from_text(),
        ]
        mappings["change_details"] = [
            self.from_entity(entity="number"),
            self.from_text(),
        ]
        mappings.update({f"obo_{m}": v for m, v in mappings.items()})
        mappings["profile"] = [self.from_entity(entity="number"), self.from_text()]
        mappings["obo_name"] = [self.from_text()]
        return mappings

    @classmethod
    def required_slots(cls, tracker: Tracker) -> List[Text]:
        slots = super().required_slots(tracker)
        if tracker.get_slot("returning_user") == "yes":
            if tracker.get_slot("change_details"):
                slots = [
                    "province",
                    "school",
                    "school_confirm",
                    "confirm_details",
                ] + slots
            elif tracker.get_slot("confirm_details") == "no":
                slots = ["change_details"] + slots
            elif not tracker.get_slot("confirm_details"):
                slots = ["confirm_details"] + slots
        # Use on behalf of slots for parent profile
        if tracker.get_slot("profile") == "parent":
            slots = ["profile", "obo_name", "obo_age"] + [
                f"obo_{s}" for s in cls.PERSISTED_SLOTS
            ]
            if tracker.get_slot("obo_medical_condition") != "no":
                slots += [f"obo_{s}" for s in cls.CONDITIONS]

        for slot in slots:
            if not tracker.get_slot(slot):
                return [slot]
        return []

    def validate_confirm_details(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        result = self.validate_generic(
            "confirm_details", dispatcher, value, self.yes_no_data
        )
        if result["confirm_details"] == "no":
            result["change_details"] = None
        return result

    def validate_change_details(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        result = self.validate_generic(
            "change_details", dispatcher, value, {1: "school name", 2: "province"}
        )
        if result["change_details"] == "school name":
            result["school"] = None
            result["school_confirm"] = None
        elif result["change_details"] == "province":
            result["province"] = None
        result["confirm_details"] = None
        return result

    def validate_age(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        if self.is_int(value) and int(value) > 0 and int(value) < 150:
            return {"age": value}
        return {"age": None}

    def validate_school(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        if value and isinstance(value, str) and value.strip().lower() == "other":
            return {"school": "OTHER", "school_emis": None, "school_confirm": "yes"}
        ix = open_dir("dbe/actions/emis_index")
        parser = MultifieldParser(["name", "emis"], ix.schema, termclass=FuzzyTerm)
        query = parser.parse(value)

        province = tracker.get_slot("obo_province") or tracker.get_slot("province")

        with ix.searcher() as s:
            results = s.search(query, limit=1, filter=Term("province", province))
            if results:
                result = results[0]
                return {
                    "school": result["name"],
                    "school_emis": result["emis"],
                }
            else:
                dispatcher.utter_message(template="utter_incorrect_school")
                return {"school": None, "province": None}

    def validate_school_confirm(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        school_confirm = self.validate_generic(
            "school_confirm", dispatcher, value, self.yes_no_data
        )
        if (
            school_confirm["school_confirm"]
            and school_confirm["school_confirm"] == "no"
        ):
            return {"school_confirm": None, "school": None}
        return school_confirm

    def validate_province(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        result = self.validate_generic(
            "province", dispatcher, value, self.province_data
        )
        if (
            isinstance(result["province"], str)
            and result["province"] in PROVINCE_DISPLAY.keys()
        ):
            result["province_display"] = PROVINCE_DISPLAY[result["province"]]
        return result

    @property
    def profile_data(self) -> Dict[int, Text]:
        with open("dbe/data/lookup_tables/profiles.txt") as f:
            return dict(enumerate(f.read().splitlines(), start=1))

    def validate_profile(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(
            "profile", dispatcher, value, self.profile_data, accept_labels=False
        )

    validate_obo_age = obo_validator(validate_age)
    validate_obo_gender = obo_validator(BaseHealthCheckProfileForm.validate_gender)
    validate_obo_province = obo_validator(BaseHealthCheckProfileForm.validate_province)
    validate_obo_location = obo_validator(BaseHealthCheckProfileForm.validate_location)
    validate_obo_location_confirm = obo_validator(
        BaseHealthCheckProfileForm.validate_location_confirm
    )
    validate_obo_school = obo_validator(validate_school)
    validate_obo_school_confirm = obo_validator(validate_school_confirm)
    validate_obo_medical_condition = obo_validator(
        BaseHealthCheckProfileForm.validate_medical_condition
    )
    validate_obo_medical_condition_obesity = obo_validator(
        BaseHealthCheckProfileForm.validate_medical_condition_obesity
    )
    validate_obo_medical_condition_diabetes = obo_validator(
        BaseHealthCheckProfileForm.validate_medical_condition_diabetes
    )
    validate_obo_medical_condition_hypertension = obo_validator(
        BaseHealthCheckProfileForm.validate_medical_condition_hypertension
    )
    validate_obo_medical_condition_cardio = obo_validator(
        BaseHealthCheckProfileForm.validate_medical_condition_cardio
    )


class HealthCheckForm(BaseHealthCheckForm):
    @classmethod
    def required_slots(cls, tracker: Tracker) -> List[Text]:
        slots = super().required_slots(tracker)
        if tracker.get_slot("profile") == "parent":
            for slot in cls.SLOTS:
                slot = f"obo_{slot}"
                if not tracker.get_slot(slot):
                    return [slot]
            return []
        return slots

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        mappings = super().slot_mappings()
        mappings.update({f"obo_{m}": v for m, v in mappings.items()})
        return mappings

    def map_age(self, value: Text):
        age = int(value)
        if age < 18:
            return "<18"
        if age < 40:
            return "18-40"
        if age <= 65:
            return "40-65"
        return ">65"

    def get_eventstore_data(self, tracker: Tracker, risk: Text) -> Dict[Text, Any]:
        if tracker.get_slot("profile") == "parent":
            return {
                "deduplication_id": uuid.uuid4().hex,
                "msisdn": f'+{tracker.sender_id.lstrip("+")}',
                "source": "WhatsApp",
                "province": f'ZA-{tracker.get_slot("obo_province").upper()}',
                "city": tracker.get_slot("obo_location"),
                "age": self.map_age(tracker.get_slot("obo_age")),
                "fever": self.YES_NO_MAPPING[tracker.get_slot("obo_symptoms_fever")],
                "cough": self.YES_NO_MAPPING[tracker.get_slot("obo_symptoms_cough")],
                "sore_throat": self.YES_NO_MAPPING[
                    tracker.get_slot("obo_symptoms_sore_throat")
                ],
                "difficulty_breathing": self.YES_NO_MAPPING[
                    tracker.get_slot("obo_symptoms_difficulty_breathing")
                ],
                "exposure": self.YES_NO_MAYBE_MAPPING[tracker.get_slot("obo_exposure")],
                "tracing": self.YES_NO_MAPPING[tracker.get_slot("obo_tracing")],
                "risk": risk,
                "gender": self.GENDER_MAPPING[tracker.get_slot("obo_gender")],
                "location": self.fix_location_format(
                    tracker.get_slot("obo_location_coords")
                ),
                "city_location": self.fix_location_format(
                    tracker.get_slot("obo_city_location_coords")
                ),
                "smell": self.YES_NO_MAPPING[
                    tracker.get_slot("obo_symptoms_taste_smell")
                ],
                "preexisting_condition": self.YES_NO_MAYBE_MAPPING[
                    tracker.get_slot("obo_medical_condition")
                ],
                # TODO: Put these 4 fields as columns on the table for a v4 API
                "data": {
                    "obesity": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_obesity")
                    ),
                    "diabetes": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_diabetes")
                    ),
                    "hypertension": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_hypertension")
                    ),
                    "cardio": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_cardio")
                    ),
                    "age": tracker.get_slot("obo_age"),
                    "school_name": tracker.get_slot("obo_school"),
                    "school_emis": tracker.get_slot("obo_school_emis"),
                    "profile": tracker.get_slot("profile"),
                    "name": tracker.get_slot("obo_name"),
                },
            }
        # Add the original value for `age` to `data`
        data = super().get_eventstore_data(tracker, risk)
        data["data"]["age"] = tracker.get_slot("age")
        data["data"]["school_name"] = tracker.get_slot("school")
        data["data"]["school_emis"] = tracker.get_slot("school_emis")
        data["data"]["profile"] = tracker.get_slot("profile")
        return data

    def get_risk_data(self, tracker: Tracker) -> Dict:
        if tracker.get_slot("profile") == "parent":
            data = {
                slot: tracker.get_slot(f"obo_{slot}")
                for slot in self.SLOTS
                if slot.startswith("symptoms_")
            }
            data.update(
                {
                    "exposure": tracker.get_slot("obo_exposure"),
                    "age": self.map_age(tracker.get_slot("obo_age")),
                }
            )
            return data
        return super().get_risk_data(tracker)

    def send_risk_to_user(self, dispatcher, risk, tracker):
        template = f"utter_risk_{risk}"
        if tracker.get_slot("profile") == "parent":
            template = f"utter_obo_risk_{risk}"
        elif tracker.get_slot("profile") == "actual_parent":
            template = f"utter_risk_{risk}_parent"
        # ZA timezone
        issued = datetime.now(tz=timezone(timedelta(hours=2)))
        expired = issued + timedelta(days=1)
        date_format = "%B %-d, %Y, %-I:%M %p"
        dispatcher.utter_message(
            template=template,
            issued=issued.strftime(date_format),
            expired=expired.strftime(date_format),
        )

    validate_obo_symptoms_fever = obo_validator(
        BaseHealthCheckForm.validate_symptoms_fever
    )
    validate_obo_symptoms_cough = obo_validator(
        BaseHealthCheckForm.validate_symptoms_cough
    )
    validate_obo_symptoms_sore_throat = obo_validator(
        BaseHealthCheckForm.validate_symptoms_sore_throat
    )
    validate_obo_symptoms_difficulty_breathing = obo_validator(
        BaseHealthCheckForm.validate_symptoms_difficulty_breathing
    )
    validate_obo_symptoms_taste_smell = obo_validator(
        BaseHealthCheckForm.validate_symptoms_taste_smell
    )
    validate_obo_exposure = obo_validator(BaseHealthCheckForm.validate_exposure)
    validate_obo_tracing = obo_validator(BaseHealthCheckForm.validate_tracing)


class ActionSessionStart(BaseActionSessionStart):
    def get_carry_over_slots(self, tracker: Tracker) -> List[Dict[Text, Any]]:
        actions = super().get_carry_over_slots(tracker)
        carry_over_slots = (
            "school",
            "school_confirm",
            "school_emis",
            "profile",
            "province_display",
        )
        for slot in carry_over_slots:
            actions.append(SlotSet(slot, tracker.get_slot(slot)))
        if tracker.get_slot("profile"):
            actions.append(SlotSet("returning_user", "yes"))
        if tracker.get_slot("province") in PROVINCE_DISPLAY.keys():
            actions.append(
                SlotSet(
                    "province_display", PROVINCE_DISPLAY[tracker.get_slot("province")]
                )
            )
        return actions


class ActionExit(BaseActionExit):
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_exit")
        return ActionSessionStart().get_carry_over_slots(tracker)


__all__ = [
    "HealthCheckTermsForm",
    "HealthCheckProfileForm",
    "HealthCheckForm",
    "ActionSessionStart",
    "ActionExit",
    "ActionSessionStart",
]
