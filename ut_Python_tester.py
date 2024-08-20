# Required libraries
import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# Connect to SQLite database
conn = sqlite3.connect('SQLite.db')

# Query to get the relevant data for running backs
query = '''
SELECT years_played, fantasy_points
FROM offense_weekly_data
WHERE position = 'RB';
'''

# Load the data into a DataFrame
rb_data = pd.read_sql(query, conn)

# Close the database connection
conn.close()

# Add a new column for years_played_excess_4
rb_data['years_played_excess_4'] = rb_data['years_played'] - 4

# Only include entries where years_played > 4
data = rb_data[rb_data['years_played_excess_4'] > 0]

# Define features and target variable
X = data[['years_played_excess_4']]
y = data['fantasy_points']

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Initialize and fit the linear regression model
model = LinearRegression()
model.fit(X_train, y_train)

# Predict on the test set
y_pred = model.predict(X_test)

# Calculate R² score for the model
r2 = r2_score(y_test, y_pred)

# Print the regression coefficients and R² score
print(f'Coefficient for years played in excess of 4: {model.coef_[0]}')
print(f'Intercept: {model.intercept_}')
print(f'R² score: {r2}')

# Note: Ensure that pandas, numpy, and scikit-learn are installed using the command
# pip install pandas numpy scikit-learn