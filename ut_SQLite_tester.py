import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('SQLite.db')
cursor = conn.cursor()

sqlite_code = """
SELECT Position,
       AVG(CASE WHEN DateofHire < '2023-01-01' THEN Salary END) AS Avg_Salary_Before_2023,
       AVG(CASE WHEN DateofHire >= '2023-01-01' THEN Salary END) AS Avg_Salary_After_2023
FROM HRDataset_v14
GROUP BY Position;
"""

# Execute sqlite code and generate results file
try:
    cursor.execute(sqlite_code)

    # Step 4: Fetch the results and load them into a pandas DataFrame
    results = cursor.fetchall()
    columns = [description[0] for description in cursor.description]  # Get column names
    df = pd.DataFrame(results, columns=columns)

    # Step 5: Export the DataFrame to Excel
    today = datetime.today().strftime('%Y-%m-%d')  # Format date as 'YYYY-MM-DD'
    filename = f"results/AnalysisResult_{today}.xlsx"
    df.to_excel(filename, index=False)
    print(f"Query results exported to {filename}")

except sqlite3.Error as e:
    print(f"An error occurred: {e}")

# Step 6: Close the connection
conn.close()