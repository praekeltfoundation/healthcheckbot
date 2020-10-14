import json
from urllib.parse import urlencode

import pytest
import respx
from rasa_sdk import Tracker

from dbe.actions import utils
from dbe.actions.utils import config


class TestOptionListFromProfiles:
    def test_result(self):
        """
        Should return a human readable string of the list of options of profile names
        """
        options = utils.option_list_from_profiles(
            [{"name": "name 1"}, {"name": "name 2"}]
        )
        result = "\n".join(["*1.* name 1", "*2.* name 2"])
        assert options == result


class TestNormalizeMsisdn:
    def test_no_plus(self):
        """
        If there's no plus, it should be added
        """
        assert utils.normalise_msisdn("27820001001") == "+27820001001"


@pytest.mark.asyncio
class TestGetLearnerProfiles:
    @respx.mock
    async def test_get_learner_profiles(self):
        """
        Should return the list of learner profiles
        """
        config.EVENTSTORE_URL = "https://eventstore"
        config.EVENTSTORE_TOKEN = "testtoken"
        querystring = urlencode({"msisdn": "+27820001001"})
        respx.get(
            url=f"https://eventstore/api/v2/dbeonbehalfofprofile/?{querystring}",
            content=json.dumps({"results": [{"name": "name1"}]}),
            content_type="application/json",
        )
        profiles = await utils.get_learner_profiles("+27820001001")
        assert profiles == [{"name": "name1"}]


@pytest.mark.asyncio
class TestGetLearnerProfilesSlotsDict:
    @respx.mock
    async def test_get_learner_profiles_dict(self):
        """
        Should return a dictionary of slots that should be filled with profile data
        """
        config.EVENTSTORE_URL = "https://eventstore"
        config.EVENTSTORE_TOKEN = "testtoken"
        querystring = urlencode({"msisdn": "+27820001001"})
        respx.get(
            url=f"https://eventstore/api/v2/dbeonbehalfofprofile/?{querystring}",
            content=json.dumps({"results": [{"name": "name1"}]}),
            content_type="application/json",
        )
        tracker = Tracker("27820001001", {}, {}, [], False, None, None, None)
        slots = await utils.get_learner_profile_slots_dict(tracker)
        assert slots == {
            "learner_profiles": [{"name": "name1"}],
            "display_learner_profiles": "*1.* name1",
        }

    @respx.mock
    async def test_get_learner_profiles_dict_no_results(self):
        """
        Sets the select_learner_profile so that question gets skipped
        """
        config.EVENTSTORE_URL = "https://eventstore"
        config.EVENTSTORE_TOKEN = "testtoken"
        querystring = urlencode({"msisdn": "+27820001001"})
        respx.get(
            url=f"https://eventstore/api/v2/dbeonbehalfofprofile/?{querystring}",
            content=json.dumps({"results": []}),
            content_type="application/json",
        )
        tracker = Tracker("27820001001", {}, {}, [], False, None, None, None)
        slots = await utils.get_learner_profile_slots_dict(tracker)
        assert slots == {
            "learner_profiles": [],
            "display_learner_profiles": "",
            "select_learner_profile": "new",
        }
