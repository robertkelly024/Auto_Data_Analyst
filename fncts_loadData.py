import pandas as pd
import sqlite3
import os
import shutil
import json
import datetime

def import_files_to_sqlite(data_folder='DataLoader', loaded_folder='Loaded'):
    # Define the database name
    db_name = 'SQLite.db'
    
    # Create the Loaded folder if it doesn't exist
    if not os.path.exists(loaded_folder):
        os.makedirs(loaded_folder)

    # Connect to the SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect(db_name)

    # Load existing data dictionary
    data_dict = load_data_dictionary()

    # Loop through each file in the DataLoader folder
    for filename in os.listdir(data_folder):
        file_path = os.path.join(data_folder, filename)
        # Determine the file type and read the file into a pandas DataFrame
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith('.xlsx') or filename.endswith('.xls'):
            df = pd.read_excel(file_path)
        else:
            print(f"Skipping unsupported file type: {filename}")
            continue
        # Define a table name based on the file name (without extension)
        table_name = os.path.splitext(filename)[0]
        print(f"Loading {table_name}")
        # Import the DataFrame into the SQLite database
        df.to_sql(table_name, conn, if_exists='replace', index=False)

        # Update data dictionary entry for this table
        data_dict = generate_DD_entry_for_table(table_name, data_dict, db_name)
        print(f"Successfully created data dictionary entry for {table_name}.")

        # Move the file to the Loaded folder
        shutil.move(file_path, os.path.join(loaded_folder, filename))
        
        print(f"Successfully loaded '{filename}' into the '{db_name}' database in the '{table_name}' table.")

    # Save the updated data dictionary
    save_data_dictionary(data_dict)

    # Commit the transaction and close the connection
    conn.commit()
    conn.close()

    print(f"All files have been processed and moved to the '{loaded_folder}' folder.")

def load_data_dictionary(file_name='data_dictionary.json'):
    try:
        with open(file_name, 'r') as json_file:
            return json.load(json_file)
    except FileNotFoundError:
        return {}

def generate_DD_entry_for_table(table_name, existing_dict=None, db_name='SQLite.db'):
    conn = sqlite3.connect(db_name)
    
    data_dictionary = existing_dict if existing_dict else {}
    df = pd.read_sql(f"SELECT * FROM {table_name};", conn)
    
    # Get or create the table dictionary
    table_dict = data_dictionary.get(table_name, {
        'stats': {},
        'columns': {}
    })

    # Update the stats section for this specific table
    table_dict['stats'] = {
        'count': len(df),
        'data_last_loaded': datetime.datetime.now().isoformat()
    }

    # Update or create the columns section
    for column in df.columns:
        unique_count = df[column].nunique()
        total_count = len(df)
        is_unique = unique_count == total_count
        
        picklist = []
        if unique_count / total_count < 0.8:
            picklist = df[column].value_counts().index.tolist()

        inferred_dtype = pd.api.types.infer_dtype(df[column], skipna=True)

        column_dict = table_dict['columns'].get(column, {
            'picklist': picklist,
            'unique_values_YN': "Yes" if is_unique else "No",
            'data_type': inferred_dtype,
            'definition': "",  # Placeholder for user-provided definition
            'ActiveColumnYN': "Yes"  # Mark as active since it exists in the current table
        })

        # Update column stats and mark as active
        column_dict['picklist'] = picklist
        column_dict['unique_values_YN'] = "Yes" if is_unique else "No"
        column_dict['data_type'] = inferred_dtype
        column_dict['ActiveColumnYN'] = "Yes"

        # Preserve the existing definition if already present
        table_dict['columns'][column] = column_dict

    # After processing all columns in the current table, mark any columns not in the current table as inactive
    existing_columns = set(table_dict['columns'].keys())
    current_columns = set(df.columns)
    
    for col in existing_columns - current_columns:
        table_dict['columns'][col]['ActiveColumnYN'] = "No"

    # Update the main dictionary with the table's data
    data_dictionary[table_name] = table_dict
    
    conn.close()

    return data_dictionary

def save_data_dictionary(data_dict, file_name='data_dictionary.json'):
    with open(file_name, 'w') as json_file:
        json.dump(data_dict, json_file, indent=4)
    print(f"Data dictionary saved to {file_name}")