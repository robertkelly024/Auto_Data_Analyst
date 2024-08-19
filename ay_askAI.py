from openai import OpenAI
import json
import os
from pydantic import BaseModel
from enum import Enum
from typing import List
import sqlite3
from datetime import datetime
import pandas as pd

OpenAI.api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI()

#get data dictionary and make it a string
def load_data_dictionary(file_name='data_dictionary.json'):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)

def data_dictionary_to_string(data_dict):
    result = []
    for table_name, table_info in data_dict.items():
        result.append(f"Table: {table_name}\n")
        result.append(f"  Stats:\n")
        for stat_name, stat_value in table_info.get('stats', {}).items():
            result.append(f"    {stat_name}: {stat_value}\n")
        result.append(f"  Columns:\n")
        for column_name, column_info in table_info.get('columns', {}).items():
            result.append(f"    Column: {column_name}\n")
            for key, value in column_info.items():
                result.append(f"      {key}: {value}\n")
        result.append("\n")  # Add a newline between tables for readability
    return ''.join(result)

# load and convert to string
data_dict = load_data_dictionary('data_dictionary.json')
data_dict_string = data_dictionary_to_string(data_dict)

class code_type(str, Enum):
    python = "Python"
    sqlite = "SQLite"

class Answer(BaseModel):
    Context: str
    Code_Type: code_type
    code: str

# Function to get the next queryID
def get_next_query_id(log_file_name="query_logs.json"):
    try:
        with open(log_file_name, "r") as log_file:
            entries = json.load(log_file)
            if entries:
                last_query_id = int(list(entries.keys())[-1])
                return last_query_id + 1
    except (FileNotFoundError, IndexError, KeyError, ValueError):
        return 100001  # Start with 100001 if file doesn't exist or is empty
    
def query_log(event, user_msg, query_id):
            # Prepare the log entry as a JSON object
        log_entry = {
            "queryID": str(query_id),
            "timestamp": datetime.now().isoformat(),
            "user_msg": user_msg,
            "Context": event.Context,
            "Code_Type": event.Code_Type,
            "code": event.code
        }

        # Load existing log file or create a new dict if the file doesn't exist
        try:
            with open("query_logs.json", "r") as log_file:
                log_data = json.load(log_file)
        except (FileNotFoundError, json.JSONDecodeError):
            log_data = {}
        # Add the new log entry using the queryID as the key
        log_data[str(query_id)] = log_entry

        # Write the updated log back to the file
        with open("query_logs.json", "w") as log_file:
            json.dump(log_data, log_file, indent=4)

sys_msg = f"""You are a data analyst expert.
Please provide a brief explanation in Context, the type of code (Python or SQLite) you are outputting in Code_Type, and ONLY that code output in code.
You have access to a database called 'SQLite.db', but do not have permission to directly alter the database.
Always assume that your code will be run directly without modification, and include notes if any packages need to be installed.
Here is the database schema:\n{data_dict_string}
"""
user_msg = input("What analysis do you want to run? ")
completion = client.beta.chat.completions.parse(
    model="gpt-4o-2024-08-06",
    messages=[
        {"role": "system", "content": f"{sys_msg}"},
        {"role": "user", "content": f"{user_msg}"},
    ],
    response_format=Answer,
)

event = completion.choices[0].message.parsed
print(event)
# Generate the queryID
query_id = get_next_query_id()
query_log(event, user_msg, query_id)
print("========================\n")

if event.Code_Type == 'SQLite':
    # Extract and print only the SQLite_code from the event object
    sqlite_code = event.code
    print("Generated code:")
    print(sqlite_code)

    conn = sqlite3.connect('SQLite.db')
    cursor = conn.cursor()

    # Execute sqlite code and generate results file
    try:
        cursor.execute(sqlite_code)

        # Fetch the results and load them into a pandas DataFrame
        results = cursor.fetchall()
        columns = [description[0] for description in cursor.description]  # Get column names
        df = pd.DataFrame(results, columns=columns)

        # Export the DataFrame to Excel
        filename = f"results/AnalysisResult_{query_id}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Query results exported to {filename}")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")

    # Close the connection
    conn.close()

elif event.Code_Type == 'Python':
    # Write the Python code to 'ut_Python_tester.py'
    python_code = event.code
    with open("ut_Python_tester.py", "w") as python_file:
        python_file.write(python_code)
    print("Python code has been written to 'ut_Python_tester.py'.")