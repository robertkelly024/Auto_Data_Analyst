import sqlite3
import pandas as pd
import json
import sys

from fncts_loadData import import_files_to_sqlite, save_data_dictionary, load_data_dictionary
from fncts_OAI_GenerateDefs import auto_generate_definitions

def main_menu():
    while True:
        print("\nMain Menu:")
        print("1. Load Data")
        print("2. Edit Data Dictionary")
        print("3. Delete Data and Dictionary Entries")
        print("Q. Quit")

        choice = input("Select an option: ").strip().lower()

        if choice == '1':
            load_data()
        elif choice == '2':
            edit_data_dictionary()
        elif choice == '3':
            delete_data()
        elif choice == 'q':
            print("Exiting program.")
            sys.exit()
        else:
            print("Invalid option. Please try again.")

def load_data():
    print("\nLoading Data...")
    # Prompt user about overwriting existing tables
    confirmation = input("This will overwrite existing tables with the same name. Continue? (Y/N): ").strip().lower()
    if confirmation == 'y':
        import_files_to_sqlite()
        print("Data loaded successfully. Returning to main menu.")
    else:
        print("Data load aborted. Returning to main menu.")

def edit_data_dictionary():
    while True:
        # Display tables and allow selection
        data_dict = load_data_dictionary()
        print("\nSelect a table to edit definitions:")
        for idx, table_name in enumerate(data_dict.keys(), start=1):
            print(f"{idx}. {table_name}")
        print("B. Back to Main Menu")

        choice = input("Select a table: ").strip().lower()
        if choice == 'b':
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(data_dict):
            table_name = list(data_dict.keys())[int(choice) - 1]
            edit_table_definitions(table_name, data_dict)
        else:
            print("Invalid option. Please try again.")

def edit_table_definitions(table_name, data_dict):
    while True:
        print(f"\nEditing definitions for {table_name}...")
        print("1. Auto-generate definitions with OpenAI")
        print("2. Edit individual field definitions")
        print("B. Back to previous menu")

        choice = input("Select an option: ").strip().lower()

        if choice == '1':
            data_dict = auto_generate_definitions(data_dict, table_name)
            save_data_dictionary(data_dict)
        elif choice == '2':
            edit_individual_fields(table_name, data_dict)
        elif choice == 'b':
            break
        else:
            print("Invalid option. Please try again.")

def edit_individual_fields(table_name, data_dict):
    while True:
        # Display fields and allow editing
        fields = data_dict[table_name]['columns']
        print(f"\nFields in {table_name}:")
        for idx, field_name in enumerate(fields.keys(), start=1):
            print(f"{idx}. {field_name}: {fields[field_name].get('definition', 'No definition')}")

        print("B. Back to previous menu")

        choice = input("Select a field to edit: ").strip().lower()

        if choice == 'b':
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(fields):
            field_name = list(fields.keys())[int(choice) - 1]
            
            # Fetch the current information
            current_definition = fields[field_name].get('definition', 'No definition')
            picklist = fields[field_name].get('picklist', None)  # Assuming picklist is stored as a list
            data_type = fields[field_name].get('data_type', 'Unknown')
            unique_values_YN = fields[field_name].get('unique_values', 'Unknown')
            ActiveColumnYN = fields[field_name].get('active', 'Unknown')  
            
            # Display the current information
            print(f"\nCurrent definition: '{current_definition}'")
            print(f"Active Column (Y/N): {ActiveColumnYN}")
            print(f"Data Type: {data_type}")
            print(f"Unique Values (Y/N): {unique_values_YN}")
            
            if picklist:
                # Convert all items in the picklist to strings before joining
                picklist_str = ', '.join(str(item) for item in picklist[:5])
                print(f"Picklist (Sample Values): {picklist_str}")  # Show a sample of the picklist (e.g., first 5 values)
            else:
                print("Picklist: None")
            
            # Prompt for new definition
            new_definition = input(f"\nEnter new definition for {field_name}: ").strip()
            if new_definition:
                fields[field_name]['definition'] = new_definition
            
            save_data_dictionary(data_dict)
        else:
            print("Invalid option. Please try again.")

def delete_data():
    while True:
        # Display tables and allow deletion
        data_dict = load_data_dictionary()
        print("\nSelect a table to delete:")
        for idx, table_name in enumerate(data_dict.keys(), start=1):
            print(f"{idx}. {table_name}")
        print("B. Back to Main Menu")

        choice = input("Select a table: ").strip().lower()
        if choice == 'b':
            break
        elif choice.isdigit() and 1 <= int(choice) <= len(data_dict):
            table_name = list(data_dict.keys())[int(choice) - 1]
            confirmation = input(f"Are you sure you want to delete {table_name}? (Y/N): ").strip().lower()
            if confirmation == 'y':
                delete_table_and_dictionary_entry(table_name, data_dict)
                print(f"{table_name} deleted successfully.")
        else:
            print("Invalid option. Please try again.")

def delete_table_and_dictionary_entry(table_name, data_dict):
    conn = sqlite3.connect('SQLite.db')
    cursor = conn.cursor()
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    conn.commit()
    conn.close()
    del data_dict[table_name]
    save_data_dictionary(data_dict)

def main():
    print("Welcome to your database assistant v0.2\n")
    main_menu()

if __name__ == "__main__":
    main()
