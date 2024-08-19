#need to make this into a callable function

import os
import pandas as pd
from openai import OpenAI
from pydantic import create_model
from typing import Dict, Any
import sqlite3

# Step 1: Create a dynamic Pydantic model based on the dataset
def create_dynamic_model(fields: Dict[str, Any]):
    return create_model('field_defs', **fields)

def auto_generate_definitions(data_dict, table_name):

    OpenAI.api_key = os.getenv('OPENAI_API_KEY')
    client = OpenAI()

    num_rows = int(input("How many rows do you want to send to OpenAI?  0 will just send the headers, otherwise 5 is a good number\n"))
    # Example table name and dataframe creation
    db_name = 'SQLite.db'
    conn = sqlite3.connect(db_name)
    df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT {num_rows};", conn)
    conn.close()
    df_sample = df.head(num_rows)

    # Step 2: Prepare the dynamic fields for the Pydantic model
    fields = {col: (str, ...) for col in df.columns}

    # Create the dynamic model
    field_defs = create_dynamic_model(fields)

    # Step 3: Use the dynamic model in the OpenAI completion request
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": f"Please provide data dictionary definitions for each field in the following dataset sample, which includes the first five rows of data:\n{df_sample}"},
            {"role": "user", "content": ""},
        ],
        response_format=field_defs,
    )

    event = completion.choices[0].message.parsed
    # Since `event` should be an instance of `field_defs`, access attributes dynamically
    for col_name in fields.keys():
        try:
            # Access the attribute corresponding to the column name
            definition = getattr(event, col_name)
            data_dict[table_name]['columns'][col_name]['definition'] = definition
        except AttributeError:
            print(f"Attribute {col_name} not found in the response.")
            
    return data_dict

