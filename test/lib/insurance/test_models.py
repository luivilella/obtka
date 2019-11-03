import pytest

from pydantic import ValidationError

from lib.insurance.models import UserInfo


@pytest.fixture
def user_data():
    return {
        "age": 35,
        "dependents": 2,
        "houses": [
            {"key": 1, "ownership_status": "owned"},
            {"key": 2, "ownership_status": "mortgaged"},
        ],
        "income": 0,
        "marital_status": "married",
        "risk_questions": [0, 1, 0],
        "vehicles": [{"key": 1, "year": 2018}],
    }


class TestUserInfo:
    def test_when_user_info_is_valid_it_creates_an_intance(self, user_data):
        UserInfo(**user_data)

    def test_when_age_is_missing_it_raises_an_error(self, user_data):
        user_data.pop("age")
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_age_is_negative_it_raises_an_error(self, user_data):
        user_data["age"] = -1
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_n_dependents_is_missing_it_raises_an_error(self, user_data):
        user_data.pop("dependents")
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_n_dependents_is_negative_it_raises_an_error(self, user_data):
        user_data["dependents"] = -1
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_house_is_valid_it_creates_an_instance(self, user_data):
        user_data["houses"] = [
            {"key": 1, "ownership_status": "owned"},
            {"key": 2, "ownership_status": "mortgaged"},
        ]
        UserInfo(**user_data)

    def test_when_house_is_missing_it_raises_an_error(self, user_data):
        user_data.pop("houses")
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_house_key_is_missing_it_raises_an_error(self, user_data):
        user_data["houses"] = [
            {"ownership_status": "mortgaged"},
            {"key": 2, "ownership_status": "mortgaged"},
        ]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_house_onership_status_is_missing_it_raises_an_error(
        self, user_data
    ):
        user_data["houses"] = [
            {"key": 1},
            {"key": 2, "ownership_status": "mortgaged"},
        ]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_house_onership_status_is_invalid_it_raises_an_error(
        self, user_data
    ):
        user_data["houses"] = [
            {"key": 1, "ownership_status": "!@#$@$"},
            {"key": 2, "ownership_status": "mortgaged"},
        ]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_income_is_missing_it_raises_an_error(self, user_data):
        user_data.pop("income")
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_income_is_negative_it_raises_an_error(self, user_data):
        user_data["income"] = -1
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_marital_status_is_single_it_creates_an_instance(
        self, user_data
    ):
        user_data["marital_status"] = "single"

    def test_when_marital_status_is_married_it_creates_an_instance(
        self, user_data
    ):
        user_data["marital_status"] = "married"

    def test_when_marital_status_is_missing_it_raises_an_error(
        self, user_data
    ):  # noqa: E501
        user_data.pop("marital_status")
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_marital_status_is_negative_it_raises_an_error(
        self, user_data
    ):
        user_data["marital_status"] = "dead"
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_risk_questions_is_missing_it_raises_an_error(
        self, user_data
    ):  # noqa: E501
        user_data.pop("risk_questions")
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_risk_questions_is_missing_a_value_it_raises_an_error(
        self, user_data
    ):
        user_data["risk_questions"] = [True, False]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_risk_questions_have_an_invalid_value_it_raises_an_error(
        self, user_data
    ):
        user_data["risk_questions"] = [True, False, 100]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_vehicles_is_missing_it_raises_an_error(self, user_data):
        user_data.pop("vehicles")
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_vehicle_key_is_missing_it_raises_an_error(self, user_data):
        user_data["vehicles"] = [{"year": 2018}]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_vehicle_year_is_missing_it_raises_an_error(self, user_data):
        user_data["vehicles"] = [{"key": 1}]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)

    def test_when_vehicle_year_is_invalid_it_raises_an_error(self, user_data):
        user_data["vehicles"] = [{"key": 1, "year": -1}]
        with pytest.raises(ValidationError):
            UserInfo(**user_data)
