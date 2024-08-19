import sqlite3
import pandas as pd
from datetime import datetime

conn = sqlite3.connect('SQLite.db')
cursor = conn.cursor()

sqlite_code = """
SELECT team, season, 
       SUM(CASE WHEN position = 'QB' THEN fantasy_points ELSE NULL END) AS avg_fp_qb,
       SUM(CASE WHEN position = 'WR' THEN fantasy_points ELSE NULL END) AS avg_fp_wr,
       SUM(CASE WHEN position = 'RB' THEN fantasy_points ELSE NULL END) AS avg_fp_rb,
       SUM(CASE WHEN position = 'TE' THEN fantasy_points ELSE NULL END) AS avg_fp_te
FROM offense_weekly_data
WHERE season IN (2023, 2022) -- Filter by the two specific seasons
GROUP BY team, season
ORDER BY team, season;
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