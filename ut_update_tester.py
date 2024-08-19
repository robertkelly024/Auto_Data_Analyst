import json

# Load the query_logs.json file
def load_query_logs(file_name='query_logs.json'):
    with open(file_name, 'r') as json_file:
        return json.load(json_file)

# Load a tester script content
def load_tester_script(file_name):
    with open(file_name, 'r') as file:
        return file.readlines()

# Save the updated tester script
def save_tester_script(file_name, lines=None):
    if lines is None:
        lines = []
    with open(file_name, 'w') as file:
        file.writelines(lines)

# Main function to update the tester scripts
def update_tester_script(query_logs_file='query_logs.json', sqlite_tester_file='ut_SQLite_tester.py', python_tester_file='ut_Python_tester.py'):
    query_logs = load_query_logs(query_logs_file)

    # Display available queryIDs and prompt user to select one
    print("Available queryIDs:")
    for query_id in query_logs:
        print(query_id)

    selected_query_id = input("Enter the queryID you want to include in the tester script: ")

    # Retrieve the corresponding code based on the Code_Type
    code_type = query_logs.get(selected_query_id, {}).get("Code_Type", [])
    code = query_logs.get(selected_query_id, {}).get("code", "")

    if not code:
        print(f"No code found for queryID: {selected_query_id}")
        return

    # Check if the Code_Type is Python or SQLite and update the corresponding tester file
    if "Python" in code_type:
        tester_file = python_tester_file
    elif "SQLite" in code_type:
        tester_file = sqlite_tester_file
    else:
        print(f"Unknown Code_Type for queryID: {selected_query_id}")
        return

    # Load the tester script
    lines = load_tester_script(tester_file)

    # Replace the appropriate code variable in the tester script
    new_lines = []
    in_code_block = False
    code_variable_name = 'python_code' if 'Python' in code_type else 'sqlite_code'

    for line in lines:
        if line.strip().startswith(f'{code_variable_name} = """'):
            in_code_block = True
            new_lines.append(f'{code_variable_name} = """\n')
            new_lines.append(code + '\n')
            new_lines.append('"""\n')
        elif in_code_block:
            if line.strip().endswith('"""'):
                in_code_block = False
            # Skip all lines within the existing code block
            continue
        else:
            new_lines.append(line)

    # Save the updated script
    save_tester_script(tester_file, new_lines)
    print(f"Updated {tester_file} with {code_type[0]} code from queryID {selected_query_id}.")

# Run the update process
if __name__ == "__main__":
    update_tester_script()