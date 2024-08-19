import sqlite3
import pandas as pd
import statsmodels.api as sm

# Connect to the SQLite database
conn = sqlite3.connect('SQLite.db')

# Query to load necessary data
data_query = '''
SELECT years_played, (offense_pct * 17.0) as games_played_percentage
FROM offense_weekly_data
WHERE years_played IS NOT NULL AND offense_pct IS NOT NULL;
'''

data_df = pd.read_sql_query(data_query, conn)

# Close the database connection
conn.close()

# Prepare the data for the regression model
X = data_df['years_played']  # Independent variable
X = sm.add_constant(X)  # Adds a constant term to the predictor
Y = data_df['games_played_percentage']  # Dependent variable

# Fit the regression model
model = sm.OLS(Y, X).fit()

# Print the summary of the regression
print(model.summary())

# Note: Ensure that 'pandas' and 'statsmodels' libraries are installed in your environment.