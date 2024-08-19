# Auto Data Analyst

## Summary

Automation of repetitive tasks of a data analyst, including:
- Database creation
- Data loading
- Data dictionary creation and maintenance

Automation of data analysis by generating SQLite and/or Python code using GPT-4o:
- Translate natural language requests to appropriate code without exposing row-level data
- Log GPT-4o inputs and outputs
- Auto-execute generated SQLite code and export to Excel

Log retrieval for editing AI code output
- Ticketing system to load Python or SQLite code from log for human editing

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [HelperFiles](#helperfiles)

## Installation

```bash
git clone https://github.com/robertkelly024/Auto_Data_Analyst.git
cd Auto_Data_Analyst
pip install -r requirements.txt
```

## Usage

### 1. To create a SQLite database, populate DataLoader folder with excel or csv file, and run:
```bash
python az_knowthydata.py
```
*explore console menu options to manage tables and add/edit data dictionary entries

### 2. To access the AI data analyst, first setup an environmental variable containing your OpenAI API key:

https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety

Next, run and follow console instructions:
```bash
python ay_askAI.py
```

### 3. To load a previous AI output, reference 'query_logs.json' and run:
```bash
python ut_update_tester.py
```
the LLM code output from the associated queryID will output to the appropriate 'ut_Python_tester.py' or 'ut_SQLite_tester.py' file for human revision


## HelperFiles

- [ut_appender.py](#ut_update_tester.py)
    appends multiple scrips to create 'ScriptsForLLM.txt'; used for troubleshooting with an LLM if you are a novice coder like me
- [ref_OpenAI_StructuredOutput_example.py](#ref_OpenAI_StructuredOutput_example.py)
    gives a sample script of how to call OpenAI's new structured output API route