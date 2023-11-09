# Pomelo Take Home Coding Challenge - Bonus Section

> **Note**: I have developed a full-stack application (front-end, back-end, and DB) for the Pomelo Take Home Coding Challenge. For a comprehensive understanding of the application, please watch the demo video: `Rishi_Gulati_Pomelo_Demo.mp4`.

## Overview

The project consists of several components working together to simulate a credit card transaction system:

- `solution.py`: Contains the solution I submitted to HackerRank.
- `databasing.py`: Creates an SQLite database to ensure that results are durable and persistent across sessions.
- `server.py`: A Flask server with three main REST APIs:
  1. `reset` - Resets the database to its initial state.
  2. `event` - Registers an event, modifies the credit card state, and writes these changes to the database.
  3. `get` - Retrieves a summary of the credit card state.

- `input_test.txt`: Contains an input test case (specifically, HackerRank test case 4) for illustration purposes. This can be replaced with any custom test case.

- `api_endpoint_testing.py`: Utilizes the three APIs in `server.py` to test any custom test case provided in `input_test.txt` and outputs the final summary.

- `credit_card_data.db`: The SQLite database file created for the application, ensuring data durability.

- `requirements.txt`: Lists all the necessary pip module requirements. To replicate this environment, I recommend using a `venv` with Python 3.10+ and running `pip install -r requirements.txt`.

- `/templates`: Contains `index.html`, which provides a form that can be used to input test cases through a GUI-based interface. An additional benefit is the ability to check pending and settled transactions for a credit card after each transaction.

- `dev_details`: Contains my contact details for any further inquiries or collaboration opportunities.

Thank you for reading this documentation. I encourage you to view the short (~6min) demo video I have created, which explains the application's functionalities in detail.
