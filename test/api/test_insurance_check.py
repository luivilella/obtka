import datetime
import json
import pytest

from starlette.testclient import TestClient

from api import app


@pytest.fixture
def payload():
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
        "vehicles": [{"key": 1, "year": datetime.date.today().year}],
    }


class TestPost:
    URL = "/insurance/check"

    def _post(self, data):
        return TestClient(app).post(self.URL, json.dumps(data))

    def test_when_post_valid_payload_returns_200(self, payload):
        response = self._post(payload)
        assert response.status_code == 200

    def test_when_post_valid_payload_returns_json_data(self, payload):
        response = self._post(payload)
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
        assert response.json() == expected_value

    def test_when_post_is_invalid_returns_status_422(self, payload):
        payload.pop("age")
        response = self._post(payload)
        assert response.status_code == 422

    def test_when_post_is_invalid_returns_error_detail(self, payload):
        payload.pop("age")
        response = self._post(payload)
        expected_value = {
            "detail": [
                {
                    "loc": ["body", "user", "age"],
                    "msg": "field required",
                    "type": "value_error.missing",
                }
            ]
        }
        assert response.json() == expected_value
