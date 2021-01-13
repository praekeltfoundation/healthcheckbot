import uuid
from datetime import datetime, timedelta, timezone
from inspect import iscoroutinefunction
from typing import Any, Dict, List, Optional, Text, Tuple, Union

from rasa_sdk import Action, Tracker
from rasa_sdk.events import ActionExecuted, SessionStarted, SlotSet
from rasa_sdk.executor import CollectingDispatcher
from whoosh.index import open_dir
from whoosh.qparser import MultifieldParser, OrGroup, QueryParser
from whoosh.query import FuzzyTerm, Term

from base.actions.actions import YES_NO_DATA
from base.actions.actions import HealthCheckForm as BaseHealthCheckForm
from base.actions.actions import HealthCheckProfileForm as BaseHealthCheckProfileForm
from base.actions.actions import HealthCheckTermsForm
from dbe.actions import utils

REQUESTED_SLOT = "requested_slot"

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

PROFILE_DISPLAY = {
    "educator": "Educator",
    "learner": "Learner",
    "parent": "Parents / Guardian on behalf of learner",
    "actual_parent": "Parent",
    "support": "Support or Admin staff",
    "marker": "Marker/Moderator",
    "exam_assistant": "Exam Assistant (EA)",
    "exam_official": "Exam Officials",
}


def obo_validator(function):
    async def call(*args, **kwargs):
        if iscoroutinefunction(function):
            result = await function(*args, **kwargs)
        else:
            result = function(*args, **kwargs)
        return {f"obo_{k}": v for k, v in result.items()}

    return call


def generic_validator(slot_name, data):
    def validator(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        return self.validate_generic(slot_name, dispatcher, value, data)

    return validator


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

    def request_next_slot(self, dispatcher, tracker, domain):
        for slot in self.required_slots(tracker):
            if self._should_request_slot(tracker, slot):
                if slot in [
                    "school",
                    "school_confirm",
                    "confirm_details",
                    "change_details",
                ] and tracker.get_slot("profile") in [
                    "marker",
                    "exam_assistant",
                    "exam_official",
                ]:
                    kwargs = {
                        "school": tracker.get_slot("school"),
                        "province_display": tracker.get_slot("province_display"),
                        "profile_display": tracker.get_slot("profile_display"),
                    }
                    dispatcher.utter_message(
                        template=f"utter_ask_{slot}_marker", **kwargs
                    )
                    return [SlotSet(REQUESTED_SLOT, slot)]

        return super().request_next_slot(dispatcher, tracker, domain)

    def slot_mappings(self) -> Dict[Text, Union[Dict, List[Dict]]]:
        mappings = super().slot_mappings()
        mappings["school"] = [self.from_text()]
        for field in [
            "school_confirm",
            "confirm_details",
            "medical_condition_asthma",
            "medical_condition_tb",
            "medical_condition_pregnant",
            "medical_condition_respiratory",
            "medical_condition_cardiac",
            "medical_condition_immuno",
        ]:
            mappings[field] = [
                self.from_entity(entity="number"),
                self.from_intent(intent="affirm", value="yes"),
                self.from_intent(intent="deny", value="no"),
                self.from_text(),
            ]
        mappings["change_details"] = [
            self.from_entity(entity="number"),
            self.from_text(),
        ]
        mappings["select_learner_profile"] = [
            self.from_entity(entity="number"),
            self.from_text(),
        ]
        mappings.update({f"obo_{m}": v for m, v in mappings.items()})
        mappings["profile"] = [self.from_entity(entity="number"), self.from_text()]
        mappings["obo_name"] = [self.from_text()]
        return mappings

    @classmethod
    def get_all_slots(cls, tracker: Tracker) -> List[Text]:
        slots = cls.SLOTS + cls.PERSISTED_SLOTS
        if (
            tracker.get_slot("medical_condition") != "no"
            and tracker.get_slot("obo_medical_condition") != "no"
        ):
            slots += cls.CONDITIONS
        if (
            tracker.get_slot("profile") == "learner"
            or tracker.get_slot("profile") == "parent"
        ):
            slots += ["medical_condition_asthma", "medical_condition_tb"]
            try:
                if (
                    int(tracker.get_slot("age")) >= 12
                    and tracker.get_slot("gender") == "FEMALE"
                ):
                    slots += ["medical_condition_pregnant"]
            except (TypeError, ValueError):
                pass
            try:
                if (
                    int(tracker.get_slot("obo_age")) >= 12
                    and tracker.get_slot("obo_gender") == "FEMALE"
                ):
                    slots += ["medical_condition_pregnant"]
            except (TypeError, ValueError):
                pass

            slots += [
                "medical_condition_respiratory",
                "medical_condition_cardiac",
                "medical_condition_immuno",
            ]

        # Use on behalf of slots for parent profile
        if tracker.get_slot("profile") == "parent":
            slots = ["select_learner_profile", "profile", "obo_name"] + [
                f"obo_{s}" for s in slots[1:]
            ]
        elif tracker.get_slot("returning_user") == "yes":
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
        return slots

    @classmethod
    def required_slots(cls, tracker: Tracker) -> List[Text]:
        for slot in cls.get_all_slots(tracker):
            if not tracker.get_slot(slot):
                return [slot]
        return []

    def validate_select_learner_profile(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        profiles = tracker.get_slot("learner_profiles")
        data = {
            i + 1: profile["name"].lower().strip() for i, profile in enumerate(profiles)
        }
        data[len(data) + 1] = new_learner = object()
        results = self.validate_generic(
            "select_learner_profile", dispatcher, value, data
        )
        user_answer = results["select_learner_profile"] or ""
        if user_answer == new_learner:
            return {
                "select_learner_profile": "new",
                "obo_name": None,
                "obo_age": None,
                "obo_gender": None,
                "obo_province": None,
                "obo_location": None,
                "obo_location_confirm": None,
                "obo_location_coords": None,
                "obo_city_location_coords": None,
                "obo_school": None,
                "obo_school_confirm": None,
                "obo_school_emis": None,
                "obo_medical_condition": None,
                "obo_medical_condition_obesity": None,
                "obo_medical_condition_diabetes": None,
                "obo_medical_condition_hypertension": None,
                "obo_medical_condition_cardio": None,
                "obo_medical_condition_asthma": None,
                "obo_medical_condition_tb": None,
                "obo_medical_condition_pregnant": None,
                "obo_medical_condition_respiratory": None,
                "obo_medical_condition_cardiac": None,
                "obo_medical_condition_immuno": None,
            }
        if user_answer:
            [profile] = filter(
                lambda p: p.get("name", "").lower().strip()
                == user_answer.lower().strip(),
                profiles,
            )
            gender_mappings = {v: k for k, v in HealthCheckForm.GENDER_MAPPING.items()}
            yes_no_mappings = {v: k for k, v in HealthCheckForm.YES_NO_MAPPING.items()}
            yes_no_maybe_mappings = {
                v: k for k, v in HealthCheckForm.YES_NO_MAYBE_MAPPING.items()
            }
            results.update(
                {
                    "obo_name": profile["name"],
                    "obo_age": profile["age"],
                    "obo_gender": gender_mappings[profile["gender"]],
                    "obo_province": profile["province"][3:].lower(),
                    "obo_location": profile["city"],
                    "obo_location_confirm": "yes",
                    "obo_location_coords": profile["location"],
                    "obo_city_location_coords": profile["city_location"],
                    "obo_school": profile["school"],
                    "obo_school_confirm": "yes",
                    "obo_school_emis": profile["school_emis"],
                    "obo_medical_condition": yes_no_maybe_mappings[
                        profile["preexisting_condition"]
                    ],
                    "obo_medical_condition_obesity": yes_no_mappings.get(
                        profile["obesity"]
                    ),
                    "obo_medical_condition_diabetes": yes_no_mappings.get(
                        profile["diabetes"]
                    ),
                    "obo_medical_condition_hypertension": yes_no_mappings.get(
                        profile["hypertension"]
                    ),
                    "obo_medical_condition_cardio": yes_no_mappings.get(
                        profile["cardio"]
                    ),
                    "obo_medical_condition_asthma": yes_no_mappings.get(
                        profile["asthma"]
                    ),
                    "obo_medical_condition_tb": yes_no_mappings.get(profile["tb"]),
                    "obo_medical_condition_pregnant": yes_no_mappings.get(
                        profile["pregnant"]
                    ),
                    "obo_medical_condition_respiratory": yes_no_mappings.get(
                        profile["respiratory"]
                    ),
                    "obo_medical_condition_cardiac": yes_no_mappings.get(
                        profile["cardiac"]
                    ),
                    "obo_medical_condition_immuno": yes_no_mappings.get(
                        profile["immuno"]
                    ),
                }
            )
        return results

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
            "change_details",
            dispatcher,
            value,
            {1: "school name", 2: "province", 3: "role"},
        )
        if result["change_details"] == "school name":
            result["school"] = None
            result["school_confirm"] = None
        elif result["change_details"] == "province":
            result["province"] = None
        elif result["change_details"] == "role":
            return {
                "confirm_details": None,
                "change_details": None,
                "returning_user": None,
                "profile": None,
                "profile_display": None,
                "age": None,
                "gender": None,
                "province": None,
                "province_display": None,
                "location": None,
                "location_confirm": None,
                "location_coords": None,
                "city_location_coords": None,
                "school": None,
                "school_confirm": None,
                "school_emis": None,
                "medical_condition": None,
                "medical_condition_obesity": None,
                "medical_condition_diabetes": None,
                "medical_condition_hypertension": None,
                "medical_condition_cardio": None,
                "medical_condition_asthma": None,
                "medical_condition_tb": None,
                "medical_condition_pregnant": None,
                "medical_condition_respiratory": None,
                "medical_condition_cardiac": None,
                "medical_condition_immuno": None,
                "symptoms_fever": None,
                "symptoms_cough": None,
                "symptoms_sore_throat": None,
                "symptoms_difficulty_breathing": None,
                "symptoms_taste_smell": None,
                "exposure": None,
                "tracing": None,
                "learner_profiles": None,
                "select_learner_profile": None,
                "display_learner_profiles": None,
                "obo_name": None,
                "obo_age": None,
                "obo_gender": None,
                "obo_province": None,
                "obo_location": None,
                "obo_location_confirm": None,
                "obo_location_coords": None,
                "obo_city_location_coords": None,
                "obo_school": None,
                "obo_school_confirm": None,
                "obo_school_emis": None,
                "obo_medical_condition": None,
                "obo_medical_condition_obesity": None,
                "obo_medical_condition_diabetes": None,
                "obo_medical_condition_hypertension": None,
                "obo_medical_condition_cardio": None,
                "obo_medical_condition_asthma": None,
                "obo_medical_condition_tb": None,
                "obo_medical_condition_pregnant": None,
                "obo_medical_condition_respiratory": None,
                "obo_medical_condition_cardiac": None,
                "obo_medical_condition_immuno": None,
                "obo_symptoms_fever": None,
                "obo_symptoms_cough": None,
                "obo_symptoms_sore_throat": None,
                "obo_symptoms_difficulty_breathing": None,
                "obo_symptoms_taste_smell": None,
                "obo_exposure": None,
                "obo_tracing": None,
            }
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

        province = tracker.get_slot("obo_province") or tracker.get_slot("province")

        if tracker.get_slot("profile") in ["marker", "exam_assistant", "exam_official"]:
            ix = open_dir("dbe/actions/marking_centre_index")

            parser = QueryParser("name", ix.schema, termclass=FuzzyTerm)
        elif tracker.get_slot("profile") in ["dbe_staff"]:
            schools: List[Tuple[float, Text, Optional[Text]]] = []
            ix = open_dir("dbe/actions/marking_centre_index")
            parser = QueryParser("name", ix.schema, termclass=FuzzyTerm, group=OrGroup)
            query = parser.parse(value)
            with ix.searcher() as s:
                results = s.search(query, limit=1, filter=Term("province", province))
                for result in results:
                    schools.append((result.score, result["name"], None))
            ix = open_dir("dbe/actions/emis_index")
            parser = MultifieldParser(
                ["name", "emis"], ix.schema, termclass=FuzzyTerm, group=OrGroup
            )
            query = parser.parse(value)
            with ix.searcher() as s:
                results = s.search(query, limit=1, filter=Term("province", province))
                for result in results:
                    schools.append((result.score, result["name"], result["emis"]))
            schools.sort(key=lambda r: r[0], reverse=True)
            if schools:
                school = schools[0]
                return {
                    "school": school[1],
                    "school_emis": school[2],
                }
            else:
                dispatcher.utter_message(template="utter_incorrect_school")
                return {"school": None, "province": None}
        else:
            ix = open_dir("dbe/actions/emis_index")

            parser = MultifieldParser(
                ["name", "emis"], ix.schema, termclass=FuzzyTerm, group=OrGroup
            )

        query = parser.parse(value)

        with ix.searcher() as s:
            results = s.search(query, limit=1, filter=Term("province", province))
            if results:
                result = results[0]
                return {
                    "school": result["name"],
                    "school_emis": result.get("emis"),
                }
            else:
                if tracker.get_slot("profile") in [
                    "marker",
                    "exam_assistant",
                    "exam_official",
                ]:
                    dispatcher.utter_message(template="utter_incorrect_school_marker")
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

    async def validate_profile(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        results = self.validate_generic(
            "profile", dispatcher, value, self.profile_data, accept_labels=False
        )
        if (
            isinstance(results["profile"], str)
            and results["profile"] in PROFILE_DISPLAY.keys()
        ):
            results["profile_display"] = PROFILE_DISPLAY[results["profile"]]
        if results.get("profile") == "parent":
            results.update(await utils.get_learner_profile_slots_dict(tracker))

        return results

    def validate_medical_condition_pregnant(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        result = self.validate_generic(
            "medical_condition_pregnant", dispatcher, value, YES_NO_DATA
        )
        if result["medical_condition_pregnant"] == "yes":
            dispatcher.utter_message(template="utter_pregnant_yes")
        return result

    def validate_obo_medical_condition_pregnant(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Optional[Text]]:
        result = self.validate_generic(
            "obo_medical_condition_pregnant", dispatcher, value, YES_NO_DATA
        )
        if result["obo_medical_condition_pregnant"] == "yes":
            dispatcher.utter_message(template="utter_obo_pregnant_yes")
        return result

    def get_province(self, tracker):
        if tracker.get_slot("profile") == "parent":
            return tracker.get_slot("obo_province")
        return tracker.get_slot("province")

    validate_medical_condition_asthma = generic_validator(
        "medical_condition_asthma", YES_NO_DATA
    )
    validate_medical_condition_tb = generic_validator(
        "medical_condition_tb", YES_NO_DATA
    )
    validate_medical_condition_respiratory = generic_validator(
        "medical_condition_respiratory", YES_NO_DATA
    )
    validate_medical_condition_cardiac = generic_validator(
        "medical_condition_cardiac", YES_NO_DATA
    )
    validate_medical_condition_immuno = generic_validator(
        "medical_condition_immuno", YES_NO_DATA
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
    validate_obo_medical_condition_asthma = obo_validator(
        validate_medical_condition_asthma
    )
    validate_obo_medical_condition_tb = obo_validator(validate_medical_condition_tb)
    validate_obo_medical_condition_respiratory = obo_validator(
        validate_medical_condition_respiratory
    )
    validate_obo_medical_condition_cardiac = obo_validator(
        validate_medical_condition_cardiac
    )
    validate_obo_medical_condition_immuno = obo_validator(
        validate_medical_condition_immuno
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
                    "asthma": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_asthma")
                    ),
                    "tb": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_tb")
                    ),
                    "pregnant": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_pregnant")
                    ),
                    "respiratory": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_respiratory")
                    ),
                    "cardiac": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_cardiac")
                    ),
                    "immuno": self.YES_NO_MAPPING.get(
                        tracker.get_slot("obo_medical_condition_immuno")
                    ),
                },
            }
        # Add the original value for `age` to `data`
        data = super().get_eventstore_data(tracker, risk)
        data["data"]["age"] = tracker.get_slot("age")
        data["data"]["school_name"] = tracker.get_slot("school")
        data["data"]["school_emis"] = tracker.get_slot("school_emis")
        data["data"]["profile"] = tracker.get_slot("profile")
        data["data"]["asthma"] = self.YES_NO_MAPPING.get(
            tracker.get_slot("medical_condition_asthma")
        )
        data["data"]["tb"] = self.YES_NO_MAPPING.get(
            tracker.get_slot("medical_condition_tb")
        )
        data["data"]["pregnant"] = self.YES_NO_MAPPING.get(
            tracker.get_slot("medical_condition_pregnant")
        )
        data["data"]["respiratory"] = self.YES_NO_MAPPING.get(
            tracker.get_slot("medical_condition_respiratory")
        )
        data["data"]["cardiac"] = self.YES_NO_MAPPING.get(
            tracker.get_slot("medical_condition_cardiac")
        )
        data["data"]["immuno"] = self.YES_NO_MAPPING.get(
            tracker.get_slot("medical_condition_immuno")
        )
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
        elif tracker.get_slot("profile") in [
            "support",
            "marker",
            "exam_assistant",
            "exam_official",
            "educator",
        ]:
            template = f"utter_risk_{risk}_support"
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


class ActionSessionStart(Action):
    def name(self) -> Text:
        return "action_session_start"

    async def get_carry_over_slots(self, tracker: Tracker) -> List[Dict[Text, Any]]:
        actions = [SessionStarted()]
        carry_over_slots = (
            HealthCheckTermsForm.SLOTS
            + HealthCheckProfileForm.PERSISTED_SLOTS
            + HealthCheckProfileForm.CONDITIONS
            + ["location_coords", "city_location_coords"]
            + ["school", "school_confirm", "school_emis", "profile"]
            + [
                "medical_condition_asthma",
                "medical_condition_tb",
                "medical_condition_pregnant",
                "medical_condition_respiratory",
                "medical_condition_cardiac",
                "medical_condition_immuno",
            ]
        )
        for slot in carry_over_slots:
            actions.append(SlotSet(slot, tracker.get_slot(slot)))
        if tracker.get_slot("profile") in PROFILE_DISPLAY.keys():
            actions.append(SlotSet("returning_user", "yes"))
            actions.append(
                SlotSet("profile_display", PROFILE_DISPLAY[tracker.get_slot("profile")])
            )
        if tracker.get_slot("province") in PROVINCE_DISPLAY.keys():
            actions.append(
                SlotSet(
                    "province_display", PROVINCE_DISPLAY[tracker.get_slot("province")]
                )
            )
        if tracker.get_slot("profile") == "parent":
            actions.extend(await utils.get_learner_profile_slots(tracker))
        return actions

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        actions = await self.get_carry_over_slots(tracker)
        actions.append(ActionExecuted("action_listen"))
        return actions


class ActionExit(Action):
    def name(self) -> Text:
        return "action_exit"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(template="utter_exit")
        return await ActionSessionStart().get_carry_over_slots(tracker)


class ActionSetProfileObo(Action):
    def name(self) -> Text:
        return "action_set_profile_obo"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        actions = [SlotSet("profile", "parent")]
        actions.extend(await utils.get_learner_profile_slots(tracker))
        return actions


__all__ = [
    "HealthCheckTermsForm",
    "HealthCheckProfileForm",
    "HealthCheckForm",
    "ActionSessionStart",
    "ActionExit",
    "ActionSessionStart",
]
