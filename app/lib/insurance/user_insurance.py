import typing

from datetime import date
from . import models


class BaseInsurance:
    user: models.UserInfo
    current_date: date

    _base_score_events: typing.List[typing.Tuple[str, float]]

    def __init__(self, user: models.UserInfo, current_date: date = None):
        self.user = user
        self.current_date = current_date or date.today()

    def get_base_events(self, event):
        return filter(lambda param: event == param[0], self._base_score_events)

    def set_initial_score(self):
        self._base_score = 0.0
        self._base_score_events = []
        self.add_to_base_score(sum(self.user.risk_questions), "initial")

    def add_to_base_score(self, value, event):
        if isinstance(self._base_score, float):
            self._base_score += value
        else:
            for idx in range(len(self._base_score)):
                self._base_score[idx] += value

        self._base_score_events.append((f"add:{event}", value))

    def remove_from_base_score(self, value, event):
        if isinstance(self._base_score, float):
            self._base_score -= value
        else:
            for idx in range(len(self._base_score)):
                self._base_score[idx] -= value

        self._base_score_events.append((f"remove:{event}", value))

    @property
    def is_eligible(self):
        raise NotImplementedError

    def apply_generic_risks(self):
        if self.user.age < 30:
            self.remove_from_base_score(2, "age__lt__30")
        elif self.user.age <= 40:
            self.remove_from_base_score(1, "age__lte__40")

        if self.user.income > 200_000:
            self.remove_from_base_score(1, "income__gt__200k")

    def apply_specific_risk(self):
        pass

    def get_score_formatted(self):
        if not self.is_eligible:
            return models.EnumInsuranceLevels.ineligible
        return self.score_to_text(self._base_score)

    def get_insurance_info(self):
        self.set_initial_score()
        if self.is_eligible:
            self.apply_generic_risks()
            self.apply_specific_risk()
        return self.get_score_formatted()

    @classmethod
    def score_to_text(cls, score):
        if score <= 0:
            return models.EnumInsuranceLevels.economic
        if score <= 2:
            return models.EnumInsuranceLevels.regular
        return models.EnumInsuranceLevels.responsible


class AutoInsurance(BaseInsurance):
    def set_initial_score(self):
        self._base_score = [0.0] * len(self.user.vehicles)
        self._base_score_events = []
        self.add_to_base_score(sum(self.user.risk_questions), "initial")

    @property
    def is_eligible(self):
        return bool(self.user.vehicles)

    def apply_specific_risk(self):
        for idx, vehicle in enumerate(self.user.vehicles):
            if (self.current_date.year - vehicle.year) <= 5:
                self._base_score[idx] += 1
                self._base_score_events.append(
                    (f"add:vehicle_year__lge__5:{vehicle.key}", 1)
                )

        if len(self.user.vehicles) == 1:
            self.add_to_base_score(1, "vehicles__eq__1")

    def get_score_formatted(self):
        if not self.is_eligible:
            return []
        result = []
        for score, vehicle in zip(self._base_score, self.user.vehicles):
            data = {"key": vehicle.key, "value": self.score_to_text(score)}
            result.append(data)
        return result


class DisabilityInsurance(BaseInsurance):
    @property
    def is_eligible(self):
        return bool(self.user.income) and self.user.age < 60

    def apply_specific_risk(self):
        for house in self.user.houses:
            if house.ownership_status == models.EnumOwnershipStatus.mortgaged:
                self.add_to_base_score(1, "ownership_status__eg__mortgaged")
                break

        if self.user.dependents:
            self.add_to_base_score(1, "dependents__gt__0")

        if self.user.marital_status == models.EnumMaritalStatus.married:
            self.remove_from_base_score(1, "marital_status__eg__married")


class HomeInsurance(BaseInsurance):
    def set_initial_score(self):
        self._base_score = [0.0] * len(self.user.houses)
        self._base_score_events = []
        self.add_to_base_score(sum(self.user.risk_questions), "initial")

    @property
    def is_eligible(self):
        return bool(self.user.houses)

    def apply_specific_risk(self):
        for idx, house in enumerate(self.user.houses):
            if house.ownership_status == models.EnumOwnershipStatus.mortgaged:
                self._base_score[idx] += 1
                self._base_score_events.append(
                    (f"add:ownership_status__eg__mortgaged:{house.key}", 1)
                )

        if len(self.user.houses) == 1:
            self.add_to_base_score(1, "houses__eq__1")

    def get_score_formatted(self):
        if not self.is_eligible:
            return []
        result = []
        for score, house in zip(self._base_score, self.user.houses):
            data = {"key": house.key, "value": self.score_to_text(score)}
            result.append(data)
        return result


class LifeInsurance(BaseInsurance):
    @property
    def is_eligible(self):
        return self.user.age < 60

    def apply_specific_risk(self):
        if self.user.dependents:
            self.add_to_base_score(1, "dependents__gt__0")

        if self.user.marital_status == models.EnumMaritalStatus.married:
            self.add_to_base_score(1, "marital_status__eg__married")


def _get_umbrella_status(result):
    for status in result.values():
        if status == models.EnumInsuranceLevels.economic:
            return models.EnumInsuranceLevels.regular

        if isinstance(status, list):
            for item in status:
                if item["value"] == models.EnumInsuranceLevels.economic:
                    return models.EnumInsuranceLevels.regular

    return models.EnumInsuranceLevels.ineligible


INSURANCES_AVAILABLE = [
    ("auto", AutoInsurance),
    ("disability", DisabilityInsurance),
    ("home", HomeInsurance),
    ("life", LifeInsurance),
]


def get_user_insurance(user: models.UserInfo) -> models.UserInsurance:
    result = {
        key: InsuranceClass(user).get_insurance_info()
        for key, InsuranceClass in INSURANCES_AVAILABLE
    }
    result["umbrella"] = _get_umbrella_status(result)
    return models.UserInsurance(**result)
