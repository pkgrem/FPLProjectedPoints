import pandas as pd
from scipy.stats import poisson

# Load data
data = pd.read_csv('merged_filtered_player_data (1).csv')

# Filter data based on minutes played
filtered_data = data[data['minutes'] > 500]

# Adjust 'now_cost' to reflect actual cost in millions and add prefix "£"
filtered_data['now_cost'] = "£" + (filtered_data['now_cost'] / 10).astype(str)

# Points for goals and clean sheets by position
points_for_goal = {'GK': 6, 'DEF': 6, 'MID': 5, 'FWD': 4}
points_for_clean_sheet = {'GK': 4, 'DEF': 4, 'MID': 1, 'FWD': 0}

# Function to calculate projected points per 90 with Poisson estimate for clean sheets using both goals_conceded_per_90 and expected_goals_conceded_per90
def calculate_projected_points_poisson_both(row):
    # Points from playing 90 minutes
    points = 2

    # Points from goals (weighted value between goals_per_90 and expected_goals_per_90)
    goals = 0.5 * (row['goals_per_90'] + row['expected_goals_per90'])
    points += goals * points_for_goal[row['element_type']]

    # Points from assists (weighted value between assists_per_90 and expected_assists_per_90)
    assists = 0.5 * (row['assists_per_90'] + row['expected_assists_per90'])
    points += 3 * assists

    # Points from clean sheets (for goalkeepers and defenders only)
    if row['element_type'] in ['GK', 'DEF']:
        # Calculate clean sheet probability using Poisson distribution for both goals_conceded_per_90 and expected_goals_conceded_per90
        clean_sheet_probability_goals = poisson.pmf(0, row['goals_conceded_per_90'])
        clean_sheet_probability_expected = poisson.pmf(0, row['expected_goals_conceded_per90'])
        
        # Take the average of the two probabilities
        clean_sheet_probability = 0.5 * (clean_sheet_probability_goals + clean_sheet_probability_expected)
        points += clean_sheet_probability * points_for_clean_sheet[row['element_type']]

    return points

# Calculate projected points per 90 using the new function
filtered_data['projected_points_per_90'] = filtered_data.apply(calculate_projected_points_poisson_both, axis=1)

# Save the data to a CSV file
filtered_data.to_csv('projected_player_points.csv', index=False)