import sqlite3
import pandas as pd
import statsmodels.api as sm

# Connect to the SQLite database
conn = sqlite3.connect('SQLite.db')

# Query to select relevant data for running backs (RB)
query = '''
SELECT years_played, fantasy_points
FROM offense_weekly_data
WHERE position = 'RB'
'''

# Load data into a pandas DataFrame
rb_data = pd.read_sql_query(query, conn)

# Close the database connection
conn.close()

# Drop any rows with missing values
rb_data = rb_data.dropna()

# Define independent and dependent variables
X = rb_data['years_played']
y = rb_data['fantasy_points']

# Add a constant to the independent variable (for the intercept term)
X = sm.add_constant(X)

# Fit the linear regression model
model = sm.OLS(y, X).fit()

# Print the summary of the regression
print(model.summary())

# Note: Ensure pandas and statsmodels are installed in your environment with:
# pip install pandas statsmodels