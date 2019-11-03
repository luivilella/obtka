import datetime

import pytest

from lib.insurance.models import UserInfo
from lib.insurance import user_insurance
from lib.insurance.user_insurance import _get_umbrella_status


@pytest.fixture
def user_data():
    return {
        "age": 35,
        "dependents": 2,
        "houses": [
            {"key": 1, "ownership_status": "owned"},
            {"key": 2, "ownership_status": "mortgaged"},
        ],
        "income": 100_000,
        "marital_status": "married",
        "risk_questions": [0, 1, 0],
        "vehicles": [{"key": 1, "year": datetime.date.today().year}],
    }


class TestGetUserInsurance:
    def test_returns_all_possible_insurance(self, user_data):
        user_data["income"] = 0
        insurance = user_insurance.get_user_insurance(UserInfo(**user_data))
        expected_value = {
            "auto": [{"key": 1, "value": "regular"}],
            "disability": "ineligible",
            "home": [
                {"key": 1, "value": "economic"},
                {"key": 2, "value": "regular"},
            ],
            "life": "regular",
            "umbrella": "regular",
        }
        assert insurance.dict() == expected_value


class TestAutoInsurance:
    def _get_insurance(self, user_data):
        return user_insurance.AutoInsurance(UserInfo(**user_data))

    def test_when_vehicles_is_empty_returns_empty(self, user_data):
        user_data["vehicles"] = []
        insurance = self._get_insurance(user_data)
        assert insurance.get_insurance_info() == []

    def test_when_vehicle_is_new_add_risk(self, user_data):
        user_data["vehicles"] = [
            {"key": 1, "year": 2000},
            {"key": 2, "year": datetime.date.today().year},
        ]
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("add:vehicle_year__lge__5:2")
        assert value == 1

    def test_when_only_one_vehicle_add_risk(self, user_data):
        user_data["vehicles"] = [{"key": 1, "year": 2000}]
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("add:vehicles__eq__1")
        assert value == 1


class TestDisabilityInsurance:
    def _get_insurance(self, user_data):
        return user_insurance.DisabilityInsurance(UserInfo(**user_data))

    def test_when_income_is_zero_returns_ineligible(self, user_data):
        user_data["income"] = 0
        insurance = self._get_insurance(user_data)
        assert insurance.get_insurance_info() == "ineligible"

    def test_when_over_60_returns_ineligible(self, user_data):
        user_data["age"] = 61
        insurance = self._get_insurance(user_data)
        assert insurance.get_insurance_info() == "ineligible"

    def test_under_30_deduct_risk(self, user_data):
        user_data["age"] = 29
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("remove:age__lt__30")
        assert value == 2

    def test_under_40_deduct_risk(self, user_data):
        user_data["age"] = 40
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("remove:age__lte__40")
        assert value == 1

    def test_when_income_above_200k_deduct_risk(self, user_data):
        user_data["income"] = 201_000
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("remove:income__gt__200k")
        assert value == 1

    def test_when_house_mortgaged_add_risk(self, user_data):
        user_data["houses"] = [
            {"key": 1, "ownership_status": "owned"},
            {"key": 2, "ownership_status": "mortgaged"},
        ]
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events(
            "add:ownership_status__eg__mortgaged"
        )
        assert value == 1

    def test_when_has_dependents_add_risk(self, user_data):
        user_data["dependents"] = 1
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("add:dependents__gt__0")
        assert value == 1

    def test_when_married_deduc_risk(self, user_data):
        user_data["marital_status"] = "married"
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events(
            "remove:marital_status__eg__married"
        )
        assert value == 1


class TestHomeInsurance:
    def _get_insurance(self, user_data):
        return user_insurance.HomeInsurance(UserInfo(**user_data))

    def test_when_houses_is_empty_returns_empty(self, user_data):
        user_data["houses"] = []
        insurance = self._get_insurance(user_data)
        assert insurance.get_insurance_info() == []

    def test_when_house_mortgaged_add_risk(self, user_data):
        user_data["houses"] = [
            {"key": 1, "ownership_status": "owned"},
            {"key": 2, "ownership_status": "mortgaged"},
        ]
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events(
            "add:ownership_status__eg__mortgaged:2"
        )
        assert value == 1

    def test_when_only_one_house_add_risk(self, user_data):
        user_data["houses"] = [
            {"key": 1, "ownership_status": "owned"},
        ]
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("add:houses__eq__1")
        assert value == 1


class TestLifeInsurance:
    def _get_insurance(self, user_data):
        return user_insurance.LifeInsurance(UserInfo(**user_data))

    def test_when_over_60_returns_ineligible(self, user_data):
        user_data["age"] = 61
        insurance = self._get_insurance(user_data)
        assert insurance.get_insurance_info() == "ineligible"

    def test_under_30_deduct_risk(self, user_data):
        user_data["age"] = 29
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("remove:age__lt__30")
        assert value == 2

    def test_under_40_deduct_risk(self, user_data):
        user_data["age"] = 40
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("remove:age__lte__40")
        assert value == 1

    def test_when_income_above_200k_deduct_risk(self, user_data):
        user_data["income"] = 201_000
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("remove:income__gt__200k")
        assert value == 1

    def test_when_has_dependents_add_risk(self, user_data):
        user_data["dependents"] = 1
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events("add:dependents__gt__0")
        assert value == 1

    def test_when_married_add_risk(self, user_data):
        user_data["marital_status"] = "married"
        insurance = self._get_insurance(user_data)
        insurance.get_insurance_info()
        [(*_, value)] = insurance.get_base_events(
            "add:marital_status__eg__married"
        )
        assert value == 1


class TestUmbrella:
    def test_when_life_is_economic_allow_umbrella(self):
        insurance = _get_umbrella_status({"life": "economic"})
        assert insurance == "regular"

    def test_when_disability_is_economic_allow_umbrella(self):
        insurance = _get_umbrella_status({"disability": "economic"})
        assert insurance == "regular"

    def test_when_home_has_economic_allow_umbrella(self):
        insurance = _get_umbrella_status(
            {
                "home": [
                    {"key": 1, "value": "economic"},
                    {"key": 2, "value": "regular"},
                ],
            }
        )
        assert insurance == "regular"

    def test_when_auto_has_economic_allow_umbrella(self):
        insurance = _get_umbrella_status({"disability": "economic"})
        assert insurance == "regular"

    def test_when_economic_in_disability_allow_umbrella(self):
        insurance = _get_umbrella_status(
            {"auto": [{"key": 1, "value": "economic"}]}
        )
        assert insurance == "regular"

    def test_when_there_is_no_economic_returns_ineligible(self):
        result = {
            "auto": [{"key": 1, "value": "regular"}],
            "disability": "ineligible",
            "home": [
                {"key": 1, "value": "responsible"},
                {"key": 2, "value": "regular"},
            ],
            "life": "regular",
            "umbrella": "regular",
        }
        assert _get_umbrella_status(result) == "ineligible"
