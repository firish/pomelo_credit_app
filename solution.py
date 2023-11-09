#!/bin/python3

import math
import os
import random
import re
import sys


# TEST CASES
i0 = {"creditLimit":1000,"events":[{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123}]}
i1 = {"creditLimit":1000,"events":[{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_AUTH_CLEARED","eventTime":2,"txnId":"t1"}]}
i2 = {"creditLimit":1000,"events":[{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456}]}
i3 = {"creditLimit":1000,"events":[{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"PAYMENT_INITIATED","eventTime":3,"txnId":"p1","amount":-456}]}
i4 = {"creditLimit":1000,"events":[{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"PAYMENT_INITIATED","eventTime":3,"txnId":"p1","amount":-456},{"eventType":"PAYMENT_CANCELED","eventTime":4,"txnId":"p1"}]}
i5 = {"creditLimit":1000,"events":[{"eventType":"TXN_AUTHED","eventTime":1,"txnId":"t1","amount":123},{"eventType":"TXN_SETTLED","eventTime":2,"txnId":"t1","amount":456},{"eventType":"PAYMENT_INITIATED","eventTime":3,"txnId":"p1","amount":-456},{"eventType":"PAYMENT_POSTED","eventTime":4,"txnId":"p1"}]}

#
# Complete the 'summarize' function below.
#
# The function is expected to return a STRING.
# The function accepts STRING inputJSON as parameter.
#

# Imports
import json


def summarize(inputJSON):
    # Reading input data
    data = json.loads(inputJSON)
    credit_limit = data["creditLimit"]
    events = data["events"]
    
    # output states
    available_credit, payable_balance = credit_limit, 0
    pending_transactions, settled_transactions = {}, {}
    
    # additional variables to keep track of current function state
    initial_times, final_times, initial_amounts = {}, {}, {}
    
    # processing each event
    for event in events:
        # reading event-level details
        event_type = event["eventType"]
        event_id = event["txnId"]
        event_time = event["eventTime"]
        if event_type not in ["PAYMENT_POSTED", "PAYMENT_CANCELED", "TXN_AUTH_CLEARED"]:
            amount = event["amount"]
        
        # Switch-case for the 6 event types
        if event_type == "TXN_AUTHED":
            if available_credit >= amount:
                available_credit -= amount
                pending_transactions[event_id] = event
                initial_times[event_id] = event_time
                initial_amounts[event_id] = amount
        
        elif event_type == "TXN_SETTLED":
            original_amount = initial_amounts.pop(event_id, amount)
            available_credit += (original_amount - amount)
            payable_balance += amount
            final_times[event_id] = event_time
            pending_transactions.pop(event_id, None)
            settled_transactions[event_id] = event
        
        elif event_type == "TXN_AUTH_CLEARED":
            if event_id in pending_transactions:
                original_amount = initial_amounts.pop(event_id, amount)
                available_credit += original_amount
                pending_transactions.pop(event_id, None)
                initial_times.pop(event_id, None)
        
        elif event_type == "PAYMENT_INITIATED":
            payable_balance += amount
            initial_amounts[event_id] = amount
            initial_times[event_id] = event_time
            pending_transactions[event_id] = event
        
        elif event_type == "PAYMENT_POSTED":
            original_payment_amount = initial_amounts.pop(event_id, 0)
            available_credit += abs(original_payment_amount)
            final_times[event_id] = event_time
            pending_transactions.pop(event_id, None)
            settled_transactions[event_id] = {
                "eventType": "PAYMENT_POSTED",
                "eventTime": event_time,
                "txnId": event_id,
                "amount": original_payment_amount
            }
        
        elif event_type == "PAYMENT_CANCELED":
            if event_id in pending_transactions:
                original_payment_amount = initial_amounts.pop(event_id, 0)
                payable_balance -= original_payment_amount
                pending_transactions.pop(event_id, None)
                initial_times.pop(event_id, None)
    
    # sorting based on initial and final times of transactions
    pending_transactions_sorted = sorted(
        pending_transactions.values(),
        key=lambda x: initial_times[x["txnId"]], 
        reverse=True)
        
    settled_transactions_sorted = sorted(
        settled_transactions.values(),
        key=lambda x: initial_times[x["txnId"]],
        reverse=True)[:3]
    
    # Formatting output into the desired form
    pending_summary = '\n'.join(
        f"{t['txnId']}: ${t['amount']} @ time {initial_times.get(t['txnId'], 'N/A')}"
        if t["amount"] >= 0 else
        f"{t['txnId']}: -${abs(t['amount'])} @ time {initial_times.get(t['txnId'], 'N/A')}"
        for t in pending_transactions_sorted)
    
    settled_summary = '\n'.join(
        f"{t['txnId']}: ${abs(t['amount'])} @ time {initial_times.get(t['txnId'], 'N/A')} "
        f"(finalized @ time {final_times.get(t['txnId'], 'N/A')})"
        if t["amount"] >= 0 else
        f"{t['txnId']}: -${abs(t['amount'])} @ time {initial_times.get(t['txnId'], 'N/A')} "
        f"(finalized @ time {final_times.get(t['txnId'], 'N/A')})"
        for t in settled_transactions_sorted)

    # Creating the required summary
    if available_credit >= 0:
        summary_output = (
            f"Available credit: ${available_credit}\n"
            f"Payable balance: ${abs(payable_balance)}"
        )
    else:
        summary_output = (
            f"Available credit: -${abs(available_credit)}\n"
            f"Payable balance: ${abs(payable_balance)}"
        )
    
    # Adding the pending and settled transactions to the summary
    summary_output += "\n\nPending transactions:"
    if pending_summary:
        summary_output += "\n"
        summary_output += pending_summary

    summary_output += "\n\nSettled transactions:\n"
    if settled_summary:
        summary_output += settled_summary
        
    summary_output = summary_output.strip()
    return summary_output
                

if __name__ == '__main__':
    fptr = open(os.environ['OUTPUT_PATH'], 'w')
    inputJSON = input()
    result = summarize(inputJSON)
    fptr.write(result + '\n')
    fptr.close()