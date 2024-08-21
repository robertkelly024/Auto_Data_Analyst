import sqlite3
import pandas as pd
import statsmodels.api as sm

# Connect to SQLite database
conn = sqlite3.connect('SQLite.db')

# Query to fetch necessary data for regression
query = '''
SELECT years_played, fantasy_points
FROM offense_weekly_data
WHERE position = 'RB' AND years_played > 4
'''

# Load queried data into a DataFrame
data = pd.read_sql_query(query, conn)

# Close the connection
conn.close()

# Create a new column for 'years_played_excess_of_4'
data['years_played_excess_of_4'] = data['years_played'] - 4

# Prepare the independent (X) and dependent (Y) variables
X = data['years_played_excess_of_4']
Y = data['fantasy_points']

# Add a constant to the independent variable
X = sm.add_constant(X)

# Perform linear regression
model = sm.OLS(Y, X).fit()

# Print the regression result summary
print(model.summary())

# Note: Ensure pandas and statsmodels packages are installed before running this code.