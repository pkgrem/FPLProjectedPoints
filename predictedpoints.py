import pandas as pd
import numpy as np
from scipy.stats import poisson

def calculate_projected_points_poisson_both(row):
    # Calculate points from goals
    goal_points = (row['goals_scored_per_90'] + row['expected_goals_per_90']) / 2
    if row['element_type'] == 'FWD':
        goal_points *= 4
    elif row['element_type'] == 'MID':
        goal_points *= 5
    else:
        goal_points *= 6

    # Calculate points from assists
    assist_points = (row['assists_per_90'] + row['expected_assists_per_90']) / 2 * 3

    # Calculate points from clean sheets
    if row['element_type'] == 'GK' or row['element_type'] == 'DEF':
        # Use Poisson distribution to calculate the probability of a clean sheet
        avg_goals_conceded = (row['goals_conceded_per_90'] + row['expected_goals_conceded_per90']) / 2
        clean_sheet_prob = poisson.pmf(0, avg_goals_conceded)
        clean_sheet_points = clean_sheet_prob * 4
    else:
        clean_sheet_points = 0

    # Calculate points from minutes played
    minutes_points = 2 # assuming the player plays at least 60 minutes

    # Sum up all points
    total_points = goal_points + assist_points + clean_sheet_points + minutes_points

    return total_points

# Load the data
data = pd.read_csv('projected_player_points.csv')

# Calculate projected points per 90
data['projected_points_per_90'] = data.apply(calculate_projected_points_poisson_both, axis=1)

# Calculate the proportion of games a player starts out of the games they're involved in
data['start_proportion'] = data['starts'] / data['Involved']

# Calculate expected minutes per game
def calculate_expected_minutes_per_game(row):
    if row['element_type'] == 'GK':
        return 90 * row['start_proportion'] + 20 * (1 - row['start_proportion'])
    elif row['element_type'] == 'DEF':
        return 80 * row['start_proportion'] + 20 * (1 - row['start_proportion'])
    else:
        return 70 * row['start_proportion'] + 20 * (1 - row['start_proportion'])
data['expected_minutes_per_game'] = data.apply(calculate_expected_minutes_per_game, axis=1)

# Calculate weighted projected points per game
data['weighted_projected_points_per_game'] = data['projected_points_per_90'] * (data['expected_minutes_per_game'] / 90)
