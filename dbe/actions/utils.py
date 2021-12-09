from typing import Any, Dict, List, Text
from urllib.parse import urlencode, urljoin

import httpx
import phonenumbers
from rasa_sdk import Tracker
from rasa_sdk.events import SlotSet

from base.actions import config

if hasattr(httpx, "AsyncClient"):
    # from httpx>=0.11.0, the async client is a different class
    HTTPXClient = getattr(httpx, "AsyncClient")
else:
    HTTPXClient = getattr(httpx, "Client")


async def get_learner_profiles(msisdn: Text) -> List[Dict[Text, Any]]:
    """
    Gets the learner profiles for `msisdn` from the data store. Returns an iterator.
    """
    if not (config.EVENTSTORE_URL and config.EVENTSTORE_TOKEN):
        return []
    async with HTTPXClient() as client:
        url = urljoin(config.EVENTSTORE_URL, "/api/v2/dbeonbehalfofprofile/")
        querystring = urlencode({"msisdn": msisdn})
        headers = {
            "Authorization": f"Token {config.EVENTSTORE_TOKEN}",
            "User-Agent": "rasa/dbe-healthcheckbot",
        }
        response = await client.get(f"{url}?{querystring}", headers=headers)
        # Ignore pagination here. Sending more than 1000 options in a message is crazy
        return response.json()["results"]


def option_list_from_profiles(profiles: List[Dict[Text, Any]]) -> Text:
    """
    Given a list of user profiles, returns an option list of the profile names
    """
    profiles = profiles + [{"name": "New HealthCheck"}]
    return "\n".join(
        f"*{i + 1}.* {profile['name']}" for i, profile in enumerate(profiles)
    )


def normalise_msisdn(msisdn: Text) -> Text:
    m = phonenumbers.parse(msisdn, "ZA")
    return phonenumbers.format_number(m, phonenumbers.PhoneNumberFormat.E164)


async def get_learner_profile_slots_dict(tracker: Tracker) -> Dict[Text, Any]:
    msisdn = normalise_msisdn(tracker.sender_id)
    profiles = await get_learner_profiles(msisdn)
    display_profiles = option_list_from_profiles(profiles)
    slots = {
        "learner_profiles": profiles,
        "display_learner_profiles": display_profiles,
    }
    if len(profiles) == 0:
        slots["select_learner_profile"] = "new"
    return slots


async def get_learner_profile_slots(tracker: Tracker) -> List[Dict[Text, Any]]:
    slots = await get_learner_profile_slots_dict(tracker)
    return [SlotSet(k, v) for k, v in slots.items()]
