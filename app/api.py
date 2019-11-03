from fastapi import FastAPI

from lib import insurance

app = FastAPI()


@app.post("/insurance/check")
def insurance_check(user: insurance.UserInfo) -> insurance.UserInsurance:
    return insurance.get_user_insurance(user)
