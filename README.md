# obtka

## Local setup

### Running the project with Docker

In order to run this project using `Docker` make sure that you have [Docker](https://docs.docker.com/install/) installed on you machine then run the command:

    make build && make up

The app should be running at http://localhost:8000/docs

### Manual installation

In order to run this project manually make sure that you have python 3.7 installed on you machine then run the following commands:

    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r app/requirements.txt
    cd app && uvicorn api:app --reload


## API

Check the API result using curl:

    curl -X POST "http://localhost:8000/insurance/check" -H "accept: application/json" -H "Content-Type: application/json" -d "{\"age\":35,\"dependents\":2,\"houses\":[{\"key\":1,\"ownership_status\":\"owned\"},{\"key\":2,\"ownership_status\":\"mortgaged\"}],\"income\":0,\"marital_status\":\"married\",\"risk_questions\":[0,1,0],\"vehicles\":[{\"key\":1,\"year\":2018}]}"


## Tests

Running the tests:

```
$ make test
obtka
======================================== test session starts ========================================
platform linux -- Python 3.7.3, pytest-5.2.2, py-1.8.0, pluggy-0.13.0
rootdir: /deploy
collected 54 items

../test/api/test_insurance_check.py ....                                                      [  7%]
../test/lib/insurance/test_models.py .......................                                  [ 50%]
../test/lib/insurance/test_user_insurance.py ...........................                      [100%]

======================================== 54 passed in 0.98s =========================================
```
