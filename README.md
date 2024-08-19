# Auto Data Analyst - Summary

Automation of repetitive tasks of a data analyst, including:
-database creation
-data loading
-data dictionary creation and maintenance

Automation of data analysis by generating SQLite and/or Python code using GPT-4o:
-translate natural language request to appropriate code without exposing row-level data
-log GPT-4o inputs and outputs
-auto-execute generated SQLite code and export to excel
-ticketing system to load Python or SQLite code from log for human editing

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [HelperFiles](#helperfiles)

## Installation

```bash
# Example:
git clone https://github.com/robertkelly024/Auto_Data_Analyst.git
cd Auto_Data_Analyst
pip install -r requirements.txt
```

## Usage

To create a SQLite database, populate DataLoader folder with excel or csv file, and run:
```bash
python az_knowthydata.py
```
*explore console menu options to manage tables and add/edit data dictionary entries

To access the AI data analyst, first setup an environmental variable containing your OpenAI API key:

https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety

Next, run and follow console instructions:
```bash
python ay_askAI.py
```

To load a previous AI output, reference 'query_logs.json' and run:
```bash
python ut_update_tester.py
```
the LLM code output from the associated queryID will output to the appropriate 'ut_Python_tester.py' or 'ut_SQLite_tester.py' file for human revision


## HelperFiles

ut_appender.py - appends multiple scrips to create 'ScriptsForLLM.txt'; used for troubleshooting with an LLM if you are a novice coder like me
ref_OpenAI_StructuredOutput_example.py - gives a sample script of how to call OpenAI's new structured output API route