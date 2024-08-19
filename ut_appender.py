import os

def concatenate_files(output_file, extensions, include_files):
    """
    Reads files with given extensions from the current working directory, writes the filename as a header,
    and appends the content into a single output file, including only specified files.

    Args:
    - output_file: File to which the content will be written.
    - extensions: Tuple of file extensions to include.
    - include_files: Tuple of file names to include.
    """
    directory = os.getcwd()  # Get the current working directory
    # Open the output file in write mode
    with open(output_file, 'w') as outfile:
        # Walk through the directory
        for root, dirs, files in os.walk(directory):
            for file in files:
                # Check if the file ends with a desired extension and is in the include list
                if file.endswith(extensions) and file in include_files:
                    file_path = os.path.join(root, file)
                    # Print the name of the file (optional)
                    print('Appending:', file_path)
                    # Write a header with the filename
                    outfile.write(f"----- FILE: {file} -----\n")
                    # Open and read the file
                    with open(file_path, 'r') as infile:
                        outfile.write(infile.read() + '\n\n')  # Append file content and newline for separation

# Usage example
output_file_path = 'ScriptsForLLM.txt'
file_extensions = ('.js', '.css', '.html', '.py')  # Extensions you are interested in
#inclusions = ('az_knowthydata.py', 'fncts_loadData.py', 'fncts_OAI_GenerateDefs.py', 'ay_askAI.py')  #Files to include
inclusions = ('ut_Python_tester.py', 'ut_SQLite_tester.py', 'ut_update_tester.py')
concatenate_files(output_file_path, file_extensions, inclusions)