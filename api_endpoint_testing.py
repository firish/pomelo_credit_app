import requests
import json


with open('input_case.txt') as f:
    json_data = json.load(f)

# set-up the start state
credit_limit = json_data["creditLimit"]
url = 'http://localhost:8000/reset'
data = {
    "available_credit": credit_limit
}
response = requests.post(url, json=data)
print(response.json())

# change state based on trnx events
events = json_data["events"]
url = 'http://localhost:8000/event'
for event in events:
    amount = 0
    if len(event) == 4:
        amount = event["amount"]
    data = {
        "eventType": event["eventType"],
        "eventTime": event["eventTime"],
        "txnId": event["txnId"],
        "amount": amount
    }
    response = requests.post(url, json=data)
    print(event, response.json())

# get the final summary
response = requests.get('http://localhost:8000/summary')
print(response.json())

print("Success ...")