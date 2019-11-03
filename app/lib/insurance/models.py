import enum
import typing

import pydantic


class EnumBool(enum.IntEnum):
    true = 1
    false = 0


class EnumOwnershipStatus(str, enum.Enum):
    owned = "owned"
    mortgaged = "mortgaged"


class EnumMaritalStatus(str, enum.Enum):
    single = "single"
    married = "married"


class EnumInsuranceLevels(str, enum.Enum):
    economic = "economic"
    regular = "regular"
    responsible = "responsible"
    ineligible = "ineligible"


class HouseInfo(pydantic.BaseModel):
    key: int
    ownership_status: EnumOwnershipStatus


class VehicleInfo(pydantic.BaseModel):
    key: int
    year: pydantic.confloat(ge=1885)  # first car was invented


class UserInfo(pydantic.BaseModel):
    age: pydantic.confloat(ge=0)
    dependents: pydantic.confloat(ge=0)
    houses: typing.List[HouseInfo]
    income: pydantic.confloat(ge=0)
    marital_status: EnumMaritalStatus
    risk_questions: typing.Tuple[EnumBool, EnumBool, EnumBool]
    vehicles: typing.List[VehicleInfo]


class InsuranceLineItem(pydantic.BaseModel):
    key: int
    value: EnumInsuranceLevels


class UserInsurance(pydantic.BaseModel):
    auto: typing.List[InsuranceLineItem]
    disability: EnumInsuranceLevels
    home: typing.List[InsuranceLineItem]
    life: EnumInsuranceLevels
    umbrella: EnumInsuranceLevels
