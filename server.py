import json
import sqlite3
import requests

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# serve index.html
@app.route('/')
def index():
    return render_template("index.html")

def get_db_connection():
    conn = sqlite3.connect('credit_card_data.db')
    conn.row_factory = sqlite3.Row  
    return conn


# Helper func
def load_json_or_empty_dict(json_string):
    try:
        return json.loads(json_string) if json_string else {}
    except json.JSONDecodeError:
        return {}


@app.route('/summary', methods=['GET'])
def get_summary():

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM credit_card_state')
    row = c.fetchone()
    conn.close() 

    if row is None:
        return jsonify({"error": "Data not found"}), 404

    available_credit = row['available_credit']
    payable_balance = row['payable_balance']
    pending_transactions = json.loads(row['pending_transactions'])
    submitted_transactions = json.loads(row['submitted_transactions'])
    final_times = json.loads(row['final_times'])

    summary_output = {
        "Available credit": available_credit,
        "Payable balance": payable_balance,
        "Pending transactions": pending_transactions,
        "Settled transactions": submitted_transactions,
        "Final times": final_times
    }
    return jsonify(summary_output)


@app.route('/event', methods=['POST'])
def submit_event():
    data = request.json
    event_type = data["eventType"]
    event_id = data["txnId"]
    event_time = int(data["eventTime"])
    amount = int(data.get("amount", 0))
    

    conn = get_db_connection()
    c = conn.cursor()
    c.execute('SELECT * FROM credit_card_state')
    row = c.fetchone()
    
    if row is None:
        conn.close()
        return jsonify({"error": "Credit card state not found"}), 404
    
    available_credit = row['available_credit']
    payable_balance = row['payable_balance']
    pending_transactions = load_json_or_empty_dict(row['pending_transactions'])
    settled_transactions = load_json_or_empty_dict(row['submitted_transactions'])
    initial_times = load_json_or_empty_dict(row['initial_times'])
    final_times = load_json_or_empty_dict(row['final_times'])
    initial_amounts = load_json_or_empty_dict(row['initial_amounts'])

    if event_type == "TXN_AUTHED":
        if available_credit >= amount:
            available_credit -= amount
            pending_transactions[event_id] = {
                "eventType": event_type,
                "eventTime": event_time,
                "txnId": event_id,
                "amount": amount
            }
            initial_times[event_id] = event_time
            initial_amounts[event_id] = amount

    elif event_type == "TXN_SETTLED":
        if event_id in pending_transactions:
            original_amount = initial_amounts.get(event_id)
            available_credit += (original_amount - amount)
            payable_balance += amount
            final_times[event_id] = event_time
            settled_transactions[event_id] = pending_transactions.pop(event_id)
            initial_times.pop(event_id, None)
            initial_amounts.pop(event_id, None)

    elif event_type == "TXN_AUTH_CLEARED":
        if event_id in pending_transactions:
            available_credit += initial_amounts[event_id]
            pending_transactions.pop(event_id, None)
            initial_times.pop(event_id, None)
            initial_amounts.pop(event_id, None)

    elif event_type == "PAYMENT_INITIATED":
        payable_balance -= amount
        pending_transactions[event_id] = {
            "eventType": event_type,
            "eventTime": event_time,
            "txnId": event_id,
            "amount": amount
        }
        initial_times[event_id] = event_time
        initial_amounts[event_id] = amount

    elif event_type == "PAYMENT_POSTED":
        if event_id in pending_transactions:
            available_credit += amount
            final_times[event_id] = event_time
            settled_transactions[event_id] = pending_transactions.pop(event_id)
            initial_times.pop(event_id, None)
            initial_amounts.pop(event_id, None)

    elif event_type == "PAYMENT_CANCELED":
        if event_id in pending_transactions:
            payable_balance += initial_amounts[event_id]
            pending_transactions.pop(event_id, None)
            initial_times.pop(event_id, None)
            initial_amounts.pop(event_id, None)

    # Update the database with the new state
    c.execute('''
        UPDATE credit_card_state SET 
        available_credit = ?, 
        payable_balance = ?, 
        pending_transactions = ?, 
        submitted_transactions = ?, 
        initial_times = ?, 
        final_times = ?, 
        initial_amounts = ?
        WHERE id = ?
    ''', (
        available_credit, 
        payable_balance, 
        json.dumps(pending_transactions), 
        json.dumps(settled_transactions), 
        json.dumps(initial_times), 
        json.dumps(final_times), 
        json.dumps(initial_amounts), 
        row['id']
    ))

    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 200


@app.route('/reset', methods=['POST'])
def update_state():
    data = request.json
    try:
        new_available_credit = int(data.get('available_credit'))
        if new_available_credit is None:
            return jsonify({"error": "Invalid or missing 'available_credit' in request"}), 400
    except Exception as err:
            return jsonify({"error": str(err)}), 400
    
    conn = get_db_connection()
    c = conn.cursor()
    try:
        c.execute('''
            UPDATE credit_card_state SET 
            available_credit = ?, 
            payable_balance = 0, 
            initial_amounts = '{}', 
            initial_times = '{}', 
            final_times = '{}', 
            pending_transactions = '{}', 
            submitted_transactions = '{}'
        ''', (new_available_credit,))

        conn.commit()
    except sqlite3.Error as e:
        conn.close()
        return jsonify({"error": str(e)}), 500
    
    conn.close()
    return jsonify({"status": "state updated successfully"}), 200



if __name__ == '__main__':
    app.run(debug=True, port=8000)
