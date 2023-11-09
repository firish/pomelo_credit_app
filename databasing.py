import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('credit_card_data.db')
c = conn.cursor()

# Create a new table
c.execute('DROP TABLE IF EXISTS credit_card_state')
c.execute('''
    CREATE TABLE credit_card_state (
        id INTEGER PRIMARY KEY,
        available_credit REAL,
        payable_balance REAL,
        initial_amounts TEXT,  -- Expected to store JSON serialized data
        initial_times TEXT,    -- Expected to store JSON serialized data
        final_times TEXT,      -- Expected to store JSON serialized data
        pending_transactions TEXT,  -- Expected to store JSON serialized data
        submitted_transactions TEXT -- Expected to store JSON serialized data
    )
''')

# Insert initial data
c.execute('''
    INSERT INTO credit_card_state (
        available_credit, payable_balance, 
        initial_amounts, initial_times, final_times,
        pending_transactions, submitted_transactions)
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', (1000.0, 0.0, '{}', '{}', '{}', '{}', '{}'))

# Commit and close
conn.commit()
conn.close()
print('Database instance created.')
